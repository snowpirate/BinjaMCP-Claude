"""
Binary Ninja MCP Plugin
Exposes Binary Ninja functionality via HTTP API for MCP integration
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import binaryninja as bn
from binaryninja import PluginCommand


class BinaryNinjaMCPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Binary Ninja MCP API"""
    
    bv = None  # Will be set by the plugin
    
    def log_message(self, format, *args):
        """Override to use Binary Ninja logging"""
        bn.log_info(f"BinaryNinjaMCP: {format % args}")
    
    def _send_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_text_response(self, text, status=200):
        """Send plain text response"""
        self.send_response(status)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        # Extract offset and limit for pagination
        offset = int(params.get('offset', [0])[0])
        limit = int(params.get('limit', [100])[0])
        
        try:
            if path == '/health':
                self._send_response({'status': 'ok', 'binary': self.bv.file.filename if self.bv else None})
            
            elif path == '/methods' or path == '/functions':
                if not self.bv:
                    self._send_response({'error': 'No binary loaded'}, 400)
                    return
                
                functions = list(self.bv.functions)
                total = len(functions)
                paginated = functions[offset:offset+limit]
                
                result = [f.name for f in paginated]
                self._send_text_response('\n'.join(result))
            
            elif path == '/classes' or path == '/types':
                if not self.bv:
                    self._send_response({'error': 'No binary loaded'}, 400)
                    return
                
                types = list(self.bv.types.keys())
                total = len(types)
                paginated = types[offset:offset+limit]
                
                self._send_text_response('\n'.join(paginated))
            
            elif path == '/imports':
                if not self.bv:
                    self._send_response({'error': 'No binary loaded'}, 400)
                    return
                
                imports = []
                for symbol in self.bv.symbols.values():
                    if symbol.type == bn.SymbolType.ImportedFunctionSymbol:
                        imports.append(symbol.name)
                
                paginated = imports[offset:offset+limit]
                self._send_text_response('\n'.join(paginated))
            
            elif path == '/exports':
                if not self.bv:
                    self._send_response({'error': 'No binary loaded'}, 400)
                    return
                
                exports = []
                for symbol in self.bv.symbols.values():
                    if symbol.type in [bn.SymbolType.FunctionSymbol, bn.SymbolType.DataSymbol]:
                        if symbol.binding == bn.SymbolBinding.GlobalBinding:
                            exports.append(symbol.name)
                
                paginated = exports[offset:offset+limit]
                self._send_text_response('\n'.join(paginated))
            
            elif path == '/strings':
                if not self.bv:
                    self._send_response({'error': 'No binary loaded'}, 400)
                    return
                
                strings = []
                for string in self.bv.strings:
                    strings.append(f"0x{string.start:x}: {string.value}")
                
                paginated = strings[offset:offset+limit]
                self._send_text_response('\n'.join(paginated))
            
            elif path == '/xrefs':
                if not self.bv:
                    self._send_response({'error': 'No binary loaded'}, 400)
                    return
                
                name = params.get('name', [None])[0]
                if not name:
                    self._send_response({'error': 'Missing name parameter'}, 400)
                    return
                
                # Find the function or data variable
                target_addr = None
                for func in self.bv.functions:
                    if func.name == name:
                        target_addr = func.start
                        break
                
                if target_addr is None:
                    for var in self.bv.data_vars:
                        symbol = self.bv.get_symbol_at(var)
                        if symbol and symbol.name == name:
                            target_addr = var
                            break
                
                if target_addr is None:
                    self._send_text_response(f"Could not find '{name}'")
                    return
                
                # Get cross-references
                refs = self.bv.get_code_refs(target_addr)
                result = []
                for ref in refs:
                    func = self.bv.get_function_at(ref.address)
                    if func:
                        result.append(f"0x{ref.address:x} (in {func.name})")
                    else:
                        result.append(f"0x{ref.address:x}")
                
                self._send_text_response('\n'.join(result) if result else f"No cross-references found for '{name}'")
            
            else:
                self._send_response({'error': f'Unknown endpoint: {path}'}, 404)
        
        except Exception as e:
            bn.log_error(f"BinaryNinjaMCP Error: {str(e)}")
            self._send_response({'error': str(e)}, 500)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8').strip()
        
        try:
            if path == '/decompile':
                if not self.bv:
                    self._send_text_response('No binary loaded', 400)
                    return
                
                func_name = body
                if not func_name:
                    self._send_text_response('Missing function name in body', 400)
                    return
                
                # Find function by name
                target_func = None
                for func in self.bv.functions:
                    if func.name == func_name:
                        target_func = func
                        break
                
                if not target_func:
                    self._send_text_response(f"Function '{func_name}' not found")
                    return
                
                # Get decompiled code
                try:
                    # Use HLIL (High Level IL) as decompiled output
                    hlil = target_func.hlil
                    if hlil:
                        decompiled = str(hlil)
                    else:
                        decompiled = "// HLIL not available for this function\n"
                        # Fall back to MLIL
                        mlil = target_func.mlil
                        if mlil:
                            decompiled += str(mlil)
                        else:
                            decompiled += "// No intermediate representation available"
                    
                    self._send_text_response(decompiled)
                except Exception as e:
                    self._send_text_response(f"Error decompiling function: {str(e)}")
            
            elif path == '/rename':
                if not self.bv:
                    self._send_text_response('No binary loaded', 400)
                    return
                
                # Parse body as JSON for rename operations
                try:
                    data = json.loads(body)
                    old_name = data.get('old_name')
                    new_name = data.get('new_name')
                    
                    if not old_name or not new_name:
                        self._send_text_response('Missing old_name or new_name', 400)
                        return
                    
                    # Find and rename the function
                    renamed = False
                    for func in self.bv.functions:
                        if func.name == old_name:
                            func.name = new_name
                            renamed = True
                            break
                    
                    if not renamed:
                        # Try data variables
                        for var_addr in self.bv.data_vars:
                            symbol = self.bv.get_symbol_at(var_addr)
                            if symbol and symbol.name == old_name:
                                self.bv.define_user_symbol(bn.Symbol(
                                    symbol.type,
                                    var_addr,
                                    new_name
                                ))
                                renamed = True
                                break
                    
                    if renamed:
                        self._send_text_response(f"Renamed '{old_name}' to '{new_name}'")
                    else:
                        self._send_text_response(f"Could not find '{old_name}'")
                
                except json.JSONDecodeError:
                    self._send_text_response('Invalid JSON in request body', 400)
            
            elif path == '/analyze':
                if not self.bv:
                    self._send_text_response('No binary loaded', 400)
                    return
                
                # Trigger analysis update
                self.bv.update_analysis_and_wait()
                self._send_text_response('Analysis updated')
            
            else:
                self._send_response({'error': f'Unknown endpoint: {path}'}, 404)
        
        except Exception as e:
            bn.log_error(f"BinaryNinjaMCP Error: {str(e)}")
            self._send_text_response(f'Error: {str(e)}', 500)


class BinaryNinjaMCPServer:
    """HTTP server for Binary Ninja MCP"""
    
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self, bv):
        """Start the HTTP server"""
        if self.server:
            bn.log_warn("BinaryNinjaMCP: Server already running")
            return
        
        # Set the BinaryView for the handler
        BinaryNinjaMCPHandler.bv = bv
        
        try:
            self.server = HTTPServer(('localhost', self.port), BinaryNinjaMCPHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            bn.log_info(f"BinaryNinjaMCP: HTTP server started on http://localhost:{self.port}")
        except Exception as e:
            bn.log_error(f"BinaryNinjaMCP: Failed to start server: {str(e)}")
    
    def stop(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server = None
            self.thread = None
            bn.log_info("BinaryNinjaMCP: HTTP server stopped")


# Global server instance
mcp_server = BinaryNinjaMCPServer()


def start_mcp_server(bv):
    """Plugin command to start MCP server"""
    mcp_server.start(bv)
    bn.show_message_box(
        "Binary Ninja MCP",
        f"MCP server started on http://localhost:8080\n\n"
        f"You can now connect Claude Desktop to this Binary Ninja instance.",
        bn.MessageBoxButtonSet.OKButtonSet,
        bn.MessageBoxIcon.InformationIcon
    )


def stop_mcp_server(bv):
    """Plugin command to stop MCP server"""
    mcp_server.stop()
    bn.show_message_box(
        "Binary Ninja MCP",
        "MCP server stopped.",
        bn.MessageBoxButtonSet.OKButtonSet,
        bn.MessageBoxIcon.InformationIcon
    )


# Register plugin commands
PluginCommand.register(
    "Binary Ninja MCP\\Start Server",
    "Start the MCP HTTP server for this binary",
    start_mcp_server
)

PluginCommand.register(
    "Binary Ninja MCP\\Stop Server",
    "Stop the MCP HTTP server",
    stop_mcp_server
)

bn.log_info("Binary Ninja MCP plugin loaded. Use 'Plugins > Binary Ninja MCP > Start Server' to begin.")

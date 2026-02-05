# Binary Ninja MCP

A Model Context Protocol (MCP) server for Binary Ninja, allowing LLMs like Claude to autonomously reverse engineer binaries through Binary Ninja.

Inspired by [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) by LaurieWired.

## Features

- 🔍 **Decompile Functions**: Get high-level IL decompilation of any function
- 📋 **List Analysis Results**: Browse functions, types, imports, exports, and strings
- ✏️ **Rename Symbols**: Automatically rename functions and data based on analysis
- 🔗 **Cross-References**: Find all references to functions and data
- 🔄 **Live Analysis**: Trigger re-analysis after making changes

## Architecture

Binary Ninja MCP consists of two components:

1. **Binary Ninja Plugin** (`binaryninja_mcp_plugin.py`): Runs inside Binary Ninja and exposes an HTTP API
2. **MCP Bridge** (`bridge_mcp_binaryninja.py`): Python script that translates between MCP and the Binary Ninja HTTP API

```
┌─────────────────┐          ┌──────────────────┐          ┌─────────────────┐
│  Claude Desktop │ ◄──MCP──►│   MCP Bridge     │ ◄──HTTP──►│  Binary Ninja   │
│                 │          │  (Python script) │          │    (Plugin)     │
└─────────────────┘          └──────────────────┘          └─────────────────┘
```

## Prerequisites

- Binary Ninja 5.2.8722 (or compatible version)
- Python 3.8 or higher
- Claude Desktop (or another MCP-compatible client)

## Installation

### Step 1: Install the Binary Ninja Plugin

1. Copy `binaryninja_mcp_plugin.py` to your Binary Ninja plugins directory:
   - **macOS**: `~/Library/Application Support/Binary Ninja/plugins/`
   - **Linux**: `~/.binaryninja/plugins/`
   - **Windows**: `%APPDATA%\Binary Ninja\plugins\`

2. Restart Binary Ninja

3. The plugin will automatically load. You should see a log message: 
   ```
   Binary Ninja MCP plugin loaded. Use 'Plugins > Binary Ninja MCP > Start Server' to begin.
   ```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install mcp fastmcp requests
```

### Step 3: Configure Claude Desktop

Edit your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following configuration:

```json
{
  "mcpServers": {
    "binaryninja": {
      "command": "python",
      "args": [
        "/ABSOLUTE/PATH/TO/bridge_mcp_binaryninja.py",
        "--binaryninja-server",
        "http://127.0.0.1:8080/"
      ]
    }
  }
}
```

**Important**: Replace `/ABSOLUTE/PATH/TO/` with the actual path to your `bridge_mcp_binaryninja.py` file.

### Step 4: Restart Claude Desktop

Close and restart Claude Desktop for the configuration to take effect.

## Usage

### Starting the Server

1. Open a binary in Binary Ninja
2. Go to **Plugins → Binary Ninja MCP → Start Server**
3. You should see a confirmation dialog that the server is running on `http://localhost:8080`

### Using with Claude Desktop

Once the server is running and Claude Desktop is configured, you can start asking Claude to analyze your binary:

**Example prompts:**
- "What functions are in this binary?"
- "Decompile the main function"
- "Find all cross-references to the authenticate function"
- "List all imported functions"
- "What strings are in this binary?"
- "Rename function_1234 to parse_config"

### Stopping the Server

Go to **Plugins → Binary Ninja MCP → Stop Server**

## Available MCP Tools

The following tools are exposed to Claude:

| Tool | Description |
|------|-------------|
| `list_functions` | List all function names with pagination |
| `list_types` | List all type names with pagination |
| `list_imports` | List all imported functions |
| `list_exports` | List all exported symbols |
| `list_strings` | List strings found in the binary |
| `decompile_function` | Decompile a function to High Level IL |
| `rename_function` | Rename a function or symbol |
| `get_cross_references` | Get xrefs to a function/symbol |
| `update_analysis` | Trigger re-analysis of the binary |
| `check_connection` | Verify connection to Binary Ninja |

## Advanced Configuration

### Using SSE Transport (for other MCP clients)

If you want to use a different MCP client that supports SSE transport:

```bash
python bridge_mcp_binaryninja.py \
  --transport sse \
  --mcp-host 127.0.0.1 \
  --mcp-port 8081 \
  --binaryninja-server http://127.0.0.1:8080/
```

Then configure your MCP client to connect to `http://127.0.0.1:8081/sse`

### Changing the Binary Ninja Server Port

If you need to change the port that Binary Ninja listens on, you'll need to modify the plugin code. Edit `binaryninja_mcp_plugin.py` and change:

```python
mcp_server = BinaryNinjaMCPServer(port=8080)  # Change 8080 to your desired port
```

Then update the `--binaryninja-server` argument in your Claude Desktop config accordingly.

## API Endpoints

The Binary Ninja plugin exposes the following HTTP endpoints:

### GET Endpoints

- `GET /health` - Server health check
- `GET /functions?offset=0&limit=100` - List functions
- `GET /types?offset=0&limit=100` - List types
- `GET /imports?offset=0&limit=100` - List imports
- `GET /exports?offset=0&limit=100` - List exports
- `GET /strings?offset=0&limit=100` - List strings
- `GET /xrefs?name=function_name` - Get cross-references

### POST Endpoints

- `POST /decompile` - Decompile function (body: function name)
- `POST /rename` - Rename symbol (body: JSON with `old_name` and `new_name`)
- `POST /analyze` - Trigger analysis update

## Troubleshooting

### "No binary loaded" error

Make sure you have a binary open in Binary Ninja before starting the MCP server.

### Connection refused

1. Verify the Binary Ninja plugin is running (check the log console in Binary Ninja)
2. Make sure you've started the server via **Plugins → Binary Ninja MCP → Start Server**
3. Check that the port (default: 8080) is not being used by another application

### Claude Desktop not showing Binary Ninja tools

1. Verify your `claude_desktop_config.json` is correctly formatted
2. Restart Claude Desktop after making changes
3. Check the Claude Desktop logs for any errors
4. Verify the path to `bridge_mcp_binaryninja.py` is absolute and correct

### Plugin not loading in Binary Ninja

1. Check Binary Ninja's log console for error messages
2. Verify the plugin is in the correct plugins directory
3. Ensure Binary Ninja has read permissions for the plugin file
4. Try restarting Binary Ninja

## Example Workflow

Here's a typical analysis workflow using Binary Ninja MCP:

1. Open a binary in Binary Ninja
2. Start the MCP server
3. Ask Claude: "What are the main functions in this binary?"
4. Ask Claude: "Decompile the main function and explain what it does"
5. Ask Claude: "Find suspicious functions that might contain vulnerabilities"
6. Ask Claude: "Rename any functions you've identified to more descriptive names"
7. Ask Claude: "Find all functions that call malloc and check for potential memory issues"

## Differences from GhidraMCP

While inspired by GhidraMCP, Binary Ninja MCP has some differences:

- Uses Binary Ninja's HLIL (High Level IL) for decompilation instead of Ghidra's decompiler
- Plugin is a simple Python script instead of a Java plugin (easier to install)
- Directly uses Binary Ninja's Python API
- Slightly different endpoint naming to match Binary Ninja conventions

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is released under the Apache 2.0 License, similar to GhidraMCP.

## Credits

- Inspired by [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) by [LaurieWired](https://twitter.com/lauriewired)
- Built for [Binary Ninja](https://binary.ninja) by Vector 35
- Uses Anthropic's [Model Context Protocol](https://modelcontextprotocol.io/)

## Support

For issues related to:
- **Binary Ninja MCP**: Open an issue on this repository
- **Binary Ninja**: Visit [binary.ninja](https://binary.ninja)
- **MCP Protocol**: Visit [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **Claude Desktop**: Visit [claude.ai](https://claude.ai)

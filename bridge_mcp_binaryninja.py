#!/usr/bin/env python3
"""
Binary Ninja MCP Bridge
Connects MCP clients (like Claude Desktop) to Binary Ninja via HTTP
"""

import argparse
import asyncio
import logging
import requests
from typing import Any
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("binaryninja-mcp")

# Global Binary Ninja server URL
binaryninja_server_url = "http://127.0.0.1:8080"

# Initialize FastMCP server
mcp = FastMCP("binaryninja-mcp")


def safe_get(endpoint: str, params: dict = None) -> list:
    """
    Perform a GET request to Binary Ninja server.
    Returns response as list of lines.
    """
    if params is None:
        params = {}
    
    # Build query string
    query_parts = [f"{k}={v}" for k, v in params.items()]
    query_string = "&".join(query_parts)
    url = f"{binaryninja_server_url}/{endpoint}"
    if query_string:
        url += "?" + query_string
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        if response.ok:
            return response.text.splitlines()
        else:
            return [f"Error {response.status_code}: {response.text.strip()}"]
    except Exception as e:
        return [f"Request failed: {str(e)}"]


def safe_post(endpoint: str, data: str) -> str:
    """
    Perform a POST request to Binary Ninja server.
    Returns response as string.
    """
    try:
        response = requests.post(
            f"{binaryninja_server_url}/{endpoint}",
            data=data.encode("utf-8"),
            headers={"Content-Type": "text/plain; charset=utf-8"},
            timeout=30
        )
        response.encoding = 'utf-8'
        if response.ok:
            return response.text.strip()
        else:
            return f"Error {response.status_code}: {response.text.strip()}"
    except Exception as e:
        return f"Request failed: {str(e)}"


@mcp.tool()
def list_functions(offset: int = 0, limit: int = 100) -> list:
    """
    List all function names in the binary with pagination.
    
    Args:
        offset: Starting index (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        List of function names
    """
    return safe_get("functions", {"offset": offset, "limit": limit})


@mcp.tool()
def list_types(offset: int = 0, limit: int = 100) -> list:
    """
    List all type names in the binary with pagination.
    
    Args:
        offset: Starting index (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        List of type names
    """
    return safe_get("types", {"offset": offset, "limit": limit})


@mcp.tool()
def list_imports(offset: int = 0, limit: int = 100) -> list:
    """
    List all imported functions in the binary with pagination.
    
    Args:
        offset: Starting index (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        List of imported function names
    """
    return safe_get("imports", {"offset": offset, "limit": limit})


@mcp.tool()
def list_exports(offset: int = 0, limit: int = 100) -> list:
    """
    List all exported symbols in the binary with pagination.
    
    Args:
        offset: Starting index (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        List of exported symbol names
    """
    return safe_get("exports", {"offset": offset, "limit": limit})


@mcp.tool()
def list_strings(offset: int = 0, limit: int = 100) -> list:
    """
    List strings found in the binary with pagination.
    
    Args:
        offset: Starting index (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        List of strings with their addresses
    """
    return safe_get("strings", {"offset": offset, "limit": limit})


@mcp.tool()
def decompile_function(name: str) -> str:
    """
    Decompile a specific function by name and return the decompiled code.
    
    Args:
        name: Name of the function to decompile
    
    Returns:
        Decompiled function code (High Level IL)
    """
    return safe_post("decompile", name)


@mcp.tool()
def rename_function(old_name: str, new_name: str) -> str:
    """
    Rename a function or symbol in the binary.
    
    Args:
        old_name: Current name of the function/symbol
        new_name: New name to assign
    
    Returns:
        Status message indicating success or failure
    """
    import json
    data = json.dumps({"old_name": old_name, "new_name": new_name})
    return safe_post("rename", data)


@mcp.tool()
def get_cross_references(name: str) -> list:
    """
    Get cross-references (xrefs) to a function or symbol.
    
    Args:
        name: Name of the function/symbol to find references to
    
    Returns:
        List of addresses that reference the specified function/symbol
    """
    return safe_get("xrefs", {"name": name})


@mcp.tool()
def update_analysis() -> str:
    """
    Trigger a re-analysis of the binary.
    This is useful after making changes like renaming functions.
    
    Returns:
        Status message
    """
    return safe_post("analyze", "")


@mcp.tool()
def check_connection() -> dict:
    """
    Check if the connection to Binary Ninja is working.
    
    Returns:
        Status information about the connection
    """
    try:
        response = requests.get(f"{binaryninja_server_url}/health", timeout=5)
        if response.ok:
            return response.json()
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    """Main entry point for the MCP bridge"""
    parser = argparse.ArgumentParser(
        description="Binary Ninja MCP Bridge - Connect Claude Desktop to Binary Ninja"
    )
    parser.add_argument(
        "--binaryninja-server",
        default="http://127.0.0.1:8080/",
        help="Binary Ninja HTTP server URL (default: http://127.0.0.1:8080/)"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport type (default: stdio)"
    )
    parser.add_argument(
        "--mcp-host",
        default="127.0.0.1",
        help="MCP server host for SSE transport (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--mcp-port",
        type=int,
        default=8081,
        help="MCP server port for SSE transport (default: 8081)"
    )
    
    args = parser.parse_args()
    
    # Set global server URL
    global binaryninja_server_url
    binaryninja_server_url = args.binaryninja_server.rstrip("/")
    
    logger.info(f"Binary Ninja MCP Bridge starting...")
    logger.info(f"Connecting to Binary Ninja at: {binaryninja_server_url}")
    
    # Run the MCP server
    if args.transport == "stdio":
        logger.info("Using stdio transport (for Claude Desktop)")
        mcp.run()
    else:  # sse
        mcp.settings.host = args.mcp_host
        mcp.settings.port = args.mcp_port
        logger.info(f"Starting MCP server on http://{mcp.settings.host}:{mcp.settings.port}/sse")
        logger.info(f"Using transport: {args.transport}")
        mcp.run(transport="sse")


if __name__ == "__main__":
    main()

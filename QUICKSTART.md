# Binary Ninja MCP - Quick Start Guide

Get up and running with Binary Ninja MCP in 5 minutes!

## TL;DR Installation (macOS/Linux)

```bash
# 1. Run the installation script
./install.sh

# 2. Restart Binary Ninja
# 3. Open a binary in Binary Ninja
# 4. Plugins → Binary Ninja MCP → Start Server
# 5. Restart Claude Desktop
# 6. Start chatting with Claude about your binary!
```

## Manual Installation

### 1. Install the Binary Ninja Plugin (2 minutes)

Copy the plugin to your Binary Ninja plugins directory:

**macOS:**
```bash
cp binaryninja_mcp_plugin.py ~/Library/Application\ Support/Binary\ Ninja/plugins/
```

**Linux:**
```bash
cp binaryninja_mcp_plugin.py ~/.binaryninja/plugins/
```

**Windows:**
```cmd
copy binaryninja_mcp_plugin.py %APPDATA%\Binary Ninja\plugins\
```

### 2. Install Python Dependencies (1 minute)

```bash
pip install mcp fastmcp requests
```

### 3. Configure Claude Desktop (2 minutes)

Edit your config file and add:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "binaryninja": {
      "command": "python",
      "args": [
        "/full/path/to/bridge_mcp_binaryninja.py",
        "--binaryninja-server",
        "http://127.0.0.1:8080/"
      ]
    }
  }
}
```

**Linux:** `~/.config/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "binaryninja": {
      "command": "python",
      "args": [
        "/full/path/to/bridge_mcp_binaryninja.py",
        "--binaryninja-server",
        "http://127.0.0.1:8080/"
      ]
    }
  }
}
```

Replace `/full/path/to/` with the actual path!

### 4. Start Using It!

1. **Restart Binary Ninja** (if it was open)
2. **Open a binary** you want to analyze
3. **Start the server**: Plugins → Binary Ninja MCP → Start Server
4. **Restart Claude Desktop**
5. **Start chatting**: Ask Claude about your binary!

## Example Conversation

```
You: What functions are in this binary?

Claude: [Uses list_functions tool]
I found 42 functions in this binary. The main functions include:
- main
- init_config
- parse_arguments
- process_data
...

You: Decompile the process_data function

Claude: [Uses decompile_function tool]
Here's the decompiled code for process_data:
[Shows HLIL decompilation]

This function appears to be processing user input...
```

## Verification

To verify everything is working:

1. In Binary Ninja, check the log console for:
   ```
   BinaryNinjaMCP: HTTP server started on http://localhost:8080
   ```

2. In Claude Desktop, you should see Binary Ninja tools available (look for the tools icon)

3. Try asking Claude: "Are you connected to Binary Ninja?"

## Troubleshooting

**Plugin not loading?**
- Check Binary Ninja's log console (View → Log Console)
- Verify plugin is in the correct directory
- Make sure file permissions allow reading

**Claude can't connect?**
- Verify the server is started in Binary Ninja
- Check the path in claude_desktop_config.json is absolute and correct
- Restart Claude Desktop after config changes

**Port conflict?**
- Another app might be using port 8080
- Edit the plugin to use a different port
- Update your Claude config accordingly

## Next Steps

Check out the full [README.md](README.md) for:
- Advanced configuration options
- Complete API documentation
- Detailed troubleshooting guide
- Example analysis workflows

## Getting Help

- Review the full [README.md](README.md)
- Check Binary Ninja's log console for errors
- Review Claude Desktop's logs
- Make sure all paths are absolute (not relative)

Happy reversing! 🎉

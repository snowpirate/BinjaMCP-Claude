# Binary Ninja MCP Setup - Complete Package

This package contains everything you need to connect Binary Ninja to Claude Desktop via the Model Context Protocol (MCP).

## 📦 What's Included

```
BinaryNinjaMCP/
├── binaryninja_mcp_plugin.py    # Binary Ninja plugin (HTTP API server)
├── bridge_mcp_binaryninja.py    # MCP bridge script
├── requirements.txt              # Python dependencies
├── install.sh                    # Automated installation script (macOS/Linux)
├── README.md                     # Complete documentation
├── QUICKSTART.md                # 5-minute setup guide
├── EXAMPLES.md                  # Usage examples and workflows
├── LICENSE                      # Apache 2.0 license
└── .gitignore                   # Git ignore rules
```

## 🚀 Quick Setup (5 minutes)

### Automatic Installation (macOS/Linux)
```bash
cd BinaryNinjaMCP
./install.sh
```

### Manual Installation

**1. Install the Binary Ninja Plugin**
```bash
# macOS
cp binaryninja_mcp_plugin.py ~/Library/Application\ Support/Binary\ Ninja/plugins/

# Linux
cp binaryninja_mcp_plugin.py ~/.binaryninja/plugins/

# Windows
copy binaryninja_mcp_plugin.py %APPDATA%\Binary Ninja\plugins\
```

**2. Install Python Dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure Claude Desktop**

Edit your config file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration (replace `/ABSOLUTE/PATH/TO/` with your actual path):
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

**4. Start Using**
1. Restart Binary Ninja
2. Open a binary
3. Plugins → Binary Ninja MCP → Start Server
4. Restart Claude Desktop
5. Start chatting with Claude about your binary!

## 🎯 Key Features

- **Decompile Functions**: Get HLIL decompilation of any function
- **List Everything**: Browse functions, types, imports, exports, strings
- **Rename Symbols**: Let Claude rename functions based on analysis
- **Cross-References**: Find all uses of functions and data
- **Live Analysis**: Changes are reflected immediately in Binary Ninja

## 💬 Example Usage

Once set up, you can ask Claude things like:

- "What functions are in this binary?"
- "Decompile the main function and explain what it does"
- "Find all buffer overflow vulnerabilities"
- "Rename all functions with generic names to descriptive ones"
- "Trace where user input flows through the program"
- "What suspicious behavior does this malware exhibit?"

## 📚 Documentation

- **QUICKSTART.md** - Get started in 5 minutes
- **README.md** - Complete documentation with troubleshooting
- **EXAMPLES.md** - Real-world usage examples and workflows

## 🔧 Troubleshooting

### Plugin not loading?
- Check Binary Ninja's log console (View → Log Console)
- Verify file is in correct plugins directory
- Restart Binary Ninja

### Claude can't connect?
- Make sure you started the server (Plugins → Binary Ninja MCP → Start Server)
- Verify the path in claude_desktop_config.json is absolute
- Restart Claude Desktop after config changes

### Connection refused?
- Port 8080 might be in use by another application
- Check Binary Ninja's log console for server status

## 🎓 Learning Path

1. **Start Simple**: Open a basic binary and ask Claude "What does this binary do?"
2. **Explore Functions**: Ask Claude to decompile and explain key functions
3. **Hunt for Issues**: Ask Claude to find vulnerabilities or suspicious code
4. **Clean Up**: Let Claude rename functions to improve readability
5. **Go Deep**: Perform comprehensive security audits or malware analysis

## 🔗 Architecture

```
┌─────────────────┐          ┌──────────────────┐          ┌─────────────────┐
│  Claude Desktop │ ◄──MCP──►│   MCP Bridge     │ ◄──HTTP──►│  Binary Ninja   │
│                 │          │  (Python script) │          │    (Plugin)     │
└─────────────────┘          └──────────────────┘          └─────────────────┘
```

The MCP Bridge translates between Claude's Model Context Protocol and Binary Ninja's HTTP API.

## 📝 Credits

- Inspired by [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) by LaurieWired
- Built for [Binary Ninja](https://binary.ninja) by Vector 35
- Uses [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic

## 📄 License

Apache 2.0 - See LICENSE file

## 🆘 Getting Help

1. Check the README.md for detailed troubleshooting
2. Review Binary Ninja's log console for errors
3. Verify all paths are absolute (not relative)
4. Make sure both Binary Ninja and Claude Desktop are restarted after setup

---

**Ready to supercharge your reverse engineering workflow? Start with QUICKSTART.md!**

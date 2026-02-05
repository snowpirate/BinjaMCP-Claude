#!/bin/bash
# Binary Ninja MCP Installation Script

set -e

echo "======================================"
echo "Binary Ninja MCP Installation"
echo "======================================"
echo ""

# Detect OS
OS=""
BN_PLUGIN_DIR=""

if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    BN_PLUGIN_DIR="$HOME/Library/Application Support/Binary Ninja/plugins"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    BN_PLUGIN_DIR="$HOME/.binaryninja/plugins"
else
    echo "Unsupported OS: $OSTYPE"
    echo "Please install manually following the README.md"
    exit 1
fi

echo "Detected OS: $OS"
echo "Binary Ninja plugin directory: $BN_PLUGIN_DIR"
echo ""

# Check if Binary Ninja plugin directory exists
if [ ! -d "$BN_PLUGIN_DIR" ]; then
    echo "Warning: Binary Ninja plugin directory not found."
    echo "Creating directory: $BN_PLUGIN_DIR"
    mkdir -p "$BN_PLUGIN_DIR"
fi

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy plugin
echo "Installing Binary Ninja plugin..."
cp "$SCRIPT_DIR/binaryninja_mcp_plugin.py" "$BN_PLUGIN_DIR/"
echo "✓ Plugin installed to: $BN_PLUGIN_DIR/binaryninja_mcp_plugin.py"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
elif command -v pip &> /dev/null; then
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    echo "Error: pip not found. Please install Python and pip first."
    exit 1
fi
echo "✓ Python dependencies installed"
echo ""

# Get Claude Desktop config path
CLAUDE_CONFIG_DIR=""
CLAUDE_CONFIG_FILE=""

if [[ "$OS" == "macOS" ]]; then
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
elif [[ "$OS" == "Linux" ]]; then
    CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
    CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
fi

# Create Claude config directory if it doesn't exist
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    mkdir -p "$CLAUDE_CONFIG_DIR"
fi

# Get absolute path to bridge script
BRIDGE_PATH="$SCRIPT_DIR/bridge_mcp_binaryninja.py"

echo "======================================"
echo "Claude Desktop Configuration"
echo "======================================"
echo ""
echo "To complete the setup, add this to your Claude Desktop config:"
echo "File: $CLAUDE_CONFIG_FILE"
echo ""
echo '{'
echo '  "mcpServers": {'
echo '    "binaryninja": {'
echo '      "command": "python",'
echo '      "args": ['
echo "        \"$BRIDGE_PATH\","
echo '        "--binaryninja-server",'
echo '        "http://127.0.0.1:8080/"'
echo '      ]'
echo '    }'
echo '  }'
echo '}'
echo ""
echo "Would you like to automatically add this configuration? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    if [ -f "$CLAUDE_CONFIG_FILE" ]; then
        echo "Backing up existing config to ${CLAUDE_CONFIG_FILE}.backup"
        cp "$CLAUDE_CONFIG_FILE" "${CLAUDE_CONFIG_FILE}.backup"
        
        # Check if config already has mcpServers
        if grep -q "mcpServers" "$CLAUDE_CONFIG_FILE"; then
            echo "Config already has mcpServers section."
            echo "Please manually add the binaryninja entry following the README.md"
        else
            # Create new config with mcpServers
            cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "binaryninja": {
      "command": "python",
      "args": [
        "$BRIDGE_PATH",
        "--binaryninja-server",
        "http://127.0.0.1:8080/"
      ]
    }
  }
}
EOF
            echo "✓ Claude Desktop configuration updated"
        fi
    else
        # Create new config file
        cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "binaryninja": {
      "command": "python",
      "args": [
        "$BRIDGE_PATH",
        "--binaryninja-server",
        "http://127.0.0.1:8080/"
      ]
    }
  }
}
EOF
        echo "✓ Claude Desktop configuration created"
    fi
fi

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Restart Binary Ninja if it's running"
echo "2. Open a binary in Binary Ninja"
echo "3. Go to Plugins → Binary Ninja MCP → Start Server"
echo "4. Restart Claude Desktop"
echo "5. Start analyzing binaries with Claude!"
echo ""
echo "For troubleshooting, see README.md"

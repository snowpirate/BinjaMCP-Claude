# Binary Ninja MCP - Usage Examples

This document provides real-world examples of how to use Binary Ninja MCP with Claude.

## Table of Contents
1. [Basic Analysis](#basic-analysis)
2. [Function Analysis](#function-analysis)
3. [Finding Vulnerabilities](#finding-vulnerabilities)
4. [Automated Renaming](#automated-renaming)
5. [Cross-Reference Analysis](#cross-reference-analysis)
6. [Advanced Workflows](#advanced-workflows)

---

## Basic Analysis

### Example 1: Getting an Overview

**You:**
```
I've loaded a binary in Binary Ninja. Can you give me an overview of what this binary does?
```

**Claude will:**
1. Use `list_functions` to see all functions
2. Use `list_imports` to see what libraries are used
3. Use `list_strings` to find interesting strings
4. Use `decompile_function` on key functions like `main`
5. Provide a summary of the binary's purpose

### Example 2: Identifying the Entry Point

**You:**
```
What's the entry point of this binary and what does it do?
```

**Claude will:**
1. Look for `main`, `_start`, or `entry` functions
2. Decompile the entry point
3. Explain the initialization sequence
4. Identify key function calls

---

## Function Analysis

### Example 3: Deep Dive on a Specific Function

**You:**
```
Decompile the parse_config function and explain what it does in detail.
```

**Claude will:**
1. Use `decompile_function("parse_config")`
2. Analyze the HLIL code
3. Explain the function's logic
4. Identify any interesting behaviors or potential issues

### Example 4: Finding All Functions That Use a Specific Import

**You:**
```
Find all functions that use malloc or free. Check if they properly handle memory.
```

**Claude will:**
1. Use `get_cross_references("malloc")` and `get_cross_references("free")`
2. Decompile each function that uses these
3. Analyze memory allocation patterns
4. Flag potential memory leaks or double-frees

---

## Finding Vulnerabilities

### Example 5: Buffer Overflow Detection

**You:**
```
Look for potential buffer overflow vulnerabilities in this binary.
```

**Claude will:**
1. Search for dangerous functions (strcpy, sprintf, gets, etc.)
2. Find functions that use these via `get_cross_references`
3. Decompile and analyze each function
4. Identify missing bounds checks
5. Report potential vulnerabilities

### Example 6: Format String Vulnerabilities

**You:**
```
Check for format string vulnerabilities.
```

**Claude will:**
1. Look for printf-family functions
2. Use `get_cross_references` to find usages
3. Analyze if user input flows to format string parameters
4. Report findings with severity levels

---

## Automated Renaming

### Example 7: Rename Based on Analysis

**You:**
```
Analyze the binary and rename functions to descriptive names based on what they do.
```

**Claude will:**
1. Iterate through functions with generic names (sub_*, FUN_*, etc.)
2. Decompile each function
3. Determine its purpose
4. Use `rename_function` to give it a descriptive name
5. Use `update_analysis()` to refresh the analysis

**Example renaming:**
- `sub_401000` → `initialize_network_socket`
- `FUN_00402050` → `parse_http_header`
- `sub_403100` → `encrypt_user_data`

### Example 8: Rename with Pattern Recognition

**You:**
```
Find all functions that handle file operations and rename them appropriately.
```

**Claude will:**
1. Look for functions using file-related imports (fopen, fread, fwrite, etc.)
2. Analyze what each function does with files
3. Rename systematically:
   - `file_open_config`
   - `file_read_settings`
   - `file_write_logs`

---

## Cross-Reference Analysis

### Example 9: Understanding Program Flow

**You:**
```
Show me the call graph for the authenticate function. What calls it and what does it call?
```

**Claude will:**
1. Use `get_cross_references("authenticate")` to find callers
2. Decompile `authenticate` to see what it calls
3. Create a visual representation of the call flow
4. Explain the authentication process

### Example 10: Data Flow Analysis

**You:**
```
Trace where the 'password' string is used throughout the program.
```

**Claude will:**
1. Use `list_strings` to find the password string and its address
2. Use `get_cross_references` to find all references
3. Decompile each function that references it
4. Trace how the password is used and stored

---

## Advanced Workflows

### Example 11: Complete Vulnerability Assessment

**You:**
```
Perform a complete security audit of this binary. Look for:
- Buffer overflows
- Format string bugs
- Integer overflows
- Use-after-free
- Race conditions
- Insecure crypto usage
```

**Claude will:**
1. Systematically check for each vulnerability class
2. Use multiple tools in combination
3. Decompile suspicious functions
4. Generate a comprehensive security report

### Example 12: API Reconstruction

**You:**
```
This looks like a library. Can you reconstruct the public API by analyzing the exports?
```

**Claude will:**
1. Use `list_exports` to find exported functions
2. Decompile each exported function
3. Analyze parameters and return values
4. Generate API documentation in a readable format

### Example 13: Malware Analysis

**You:**
```
This is a suspicious executable. Analyze it for malicious behavior:
- Network connections
- File system access
- Registry modifications
- Process injection
- Anti-debugging techniques
```

**Claude will:**
1. Look for suspicious imports (WinAPI, network functions, etc.)
2. Find obfuscation or packing
3. Identify anti-analysis techniques
4. Trace network communication
5. Map file system interactions
6. Generate an indicators of compromise (IOCs) report

### Example 14: Comparing Two Functions

**You:**
```
Compare function_a and function_b. Are they similar? Could one be an obfuscated version of the other?
```

**Claude will:**
1. Decompile both functions
2. Compare their high-level structure
3. Identify common patterns
4. Flag differences
5. Determine if they're variants of the same functionality

### Example 15: Iterative Analysis and Refinement

**You:**
```
Let's do a multi-pass analysis:
1. First, identify all the important functions
2. Rename them based on what they do
3. Then re-analyze to find relationships between them
4. Finally, document the overall architecture
```

**Claude will:**
1. **Pass 1**: Analyze and categorize all functions
2. **Pass 2**: Rename functions systematically
3. **Pass 3**: Use updated names to understand call relationships
4. **Pass 4**: Generate architectural documentation with the cleaner names

---

## Tips for Best Results

### Be Specific
Instead of: "Analyze this binary"
Try: "Find all functions that perform network I/O and check for proper error handling"

### Use Multiple Steps
Break complex analysis into steps:
```
1. First, list all the functions
2. Now decompile the main function
3. Find all functions that main calls
4. Check those functions for vulnerabilities
```

### Provide Context
Give Claude information about what you're looking for:
```
This is a banking application. Check for:
- Proper input validation on transaction amounts
- Secure password handling
- Protection against SQL injection
```

### Iterate and Refine
Start broad, then drill down:
```
You: Give me an overview of the binary
You: That's interesting. Can you look deeper into the encryption function?
You: What algorithm is it using? Is it secure?
```

### Combine with Other Knowledge
Claude can combine Binary Ninja analysis with its general knowledge:
```
You: This function is using RC4 encryption. Is that a good choice?
```
Claude will analyze the implementation AND provide security context about RC4.

---

## Common Workflows

### Workflow: Complete Unknown Binary Analysis
1. Get overview (functions, imports, strings)
2. Identify entry point and main functions
3. Decompile key functions
4. Rename functions based on analysis
5. Look for suspicious behavior
6. Generate report

### Workflow: Targeted Vulnerability Hunt
1. Identify vulnerability type to search for
2. Find relevant imports/patterns
3. Decompile candidate functions
4. Analyze for specific vulnerability
5. Rate severity and exploitability

### Workflow: Clean Up Analysis Database
1. List all functions with generic names
2. Systematically decompile and analyze
3. Rename with descriptive names
4. Update analysis
5. Verify improvements

### Workflow: Understanding Protocol Implementation
1. Find network-related functions
2. Trace data flow from socket to processing
3. Identify message parsing logic
4. Document protocol structure
5. Check for implementation bugs

---

## Next Steps

- Review the [README.md](README.md) for complete documentation
- Try the [Quick Start Guide](QUICKSTART.md) to get set up
- Experiment with your own binaries
- Share your workflows and discoveries!

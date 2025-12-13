---
title: "AST Analysis Usage Guide"
type: guide
status: active
created: 2025-12-12
updated: 2025-12-12
tags: [guide, ast-analysis, code-analysis, tools]
---

# AST Analysis Usage Guide

## Overview

The AST Analysis tool provides code analysis capabilities using Python's Abstract Syntax Tree (AST) module. It can analyze code structure, generate test scaffolds, extract documentation, and check code quality.

## Available Commands

### 1. Analyze Code Structure

Analyzes Python files or directories to extract code structure information.

**Usage:**
```bash
python AgentQMS/interface/cli_tools/ast_analysis.py analyze [path]
```

**Examples:**
```bash
# Analyze current directory
python AgentQMS/interface/cli_tools/ast_analysis.py analyze

# Analyze specific directory
python AgentQMS/interface/cli_tools/ast_analysis.py analyze src/

# Analyze specific file
python AgentQMS/interface/cli_tools/ast_analysis.py analyze myfile.py

# Output as JSON
python AgentQMS/interface/cli_tools/ast_analysis.py analyze --json
```

**Output includes:**
- Classes and their methods
- Functions with signatures and complexity
- Import statements
- Total cyclomatic complexity
- Line counts

### 2. Generate Test Scaffolds

Generates pytest-style test scaffolds from Python code.

**Usage:**
```bash
python AgentQMS/interface/cli_tools/ast_analysis.py generate-tests <file> [--output <output_file>]
```

**Examples:**
```bash
# Generate test scaffold to stdout
python AgentQMS/interface/cli_tools/ast_analysis.py generate-tests mymodule.py

# Generate test scaffold to file
python AgentQMS/interface/cli_tools/ast_analysis.py generate-tests mymodule.py --output test_mymodule.py
```

**Features:**
- Generates test functions for all public functions
- Includes docstrings from original functions
- Creates test classes for classes
- Generates proper imports

### 3. Extract Documentation

Extracts documentation from Python code and generates Markdown.

**Usage:**
```bash
python AgentQMS/interface/cli_tools/ast_analysis.py extract-docs <file> [--output <output_file>]
```

**Examples:**
```bash
# Extract docs to stdout
python AgentQMS/interface/cli_tools/ast_analysis.py extract-docs mymodule.py

# Extract docs to file
python AgentQMS/interface/cli_tools/ast_analysis.py extract-docs mymodule.py --output docs.md
```

**Output includes:**
- Module-level docstrings
- Class documentation with methods
- Function signatures with type hints
- Function docstrings

### 4. Check Code Quality

Analyzes code quality metrics and detects code smells.

**Usage:**
```bash
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality [path] [--json]
```

**Examples:**
```bash
# Check current directory
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality

# Check specific directory
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality src/

# Output as JSON
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality --json
```

**Metrics provided:**
- Total files, classes, functions
- Total and average cyclomatic complexity
- Total lines of code
- Code smells (e.g., high complexity functions)
- Functions with complexity > 10

## Using from Dashboard

### Framework Auditor

1. Navigate to **Framework Auditor** in the dashboard
2. Switch to **Tool Runner** mode
3. Select an AST analysis tool:
   - **AST Code Analysis** - Analyze code structure
   - **Generate Test Scaffolds** - Generate tests
   - **Extract Documentation** - Extract docs
   - **Code Quality Check** - Check quality
4. Enter required arguments (file path or directory)
5. Click **Run Tool** to execute

### Quick Actions

The Framework Auditor also provides quick action buttons for common validation tasks. These use the standard AgentQMS tools.

## Integration with AgentQMS Workflow

### Before Code Review

```bash
# Check code quality before submitting
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality src/
```

### During Development

```bash
# Generate test scaffolds when creating new modules
python AgentQMS/interface/cli_tools/ast_analysis.py generate-tests mymodule.py --output tests/test_mymodule.py

# Extract documentation for new features
python AgentQMS/interface/cli_tools/ast_analysis.py extract-docs mymodule.py --output docs/mymodule.md
```

### Code Analysis

```bash
# Analyze project structure
python AgentQMS/interface/cli_tools/ast_analysis.py analyze . --json > analysis.json
```

## Best Practices

1. **Regular Quality Checks**: Run `check-quality` regularly to catch complexity issues early
2. **Test Generation**: Use `generate-tests` as a starting point, but always review and enhance generated tests
3. **Documentation**: Use `extract-docs` to maintain up-to-date documentation
4. **JSON Output**: Use `--json` flag for programmatic processing of results

## Limitations

- **Python Only**: Currently only supports Python code
- **Complexity Calculation**: Cyclomatic complexity is a basic calculation
- **No Type Inference**: Type hints are extracted but not inferred
- **Large Codebases**: May be slow on very large directories

## Troubleshooting

### Import Errors

If you encounter import errors, ensure:
- You're running from the project root
- PYTHONPATH includes the project root
- All dependencies are installed

### Syntax Errors

Files with syntax errors will be reported but won't stop analysis of other files.

### Performance

For large codebases:
- Use specific paths instead of analyzing entire project
- Consider using JSON output and processing programmatically
- Run analysis in smaller chunks

## Examples

### Example: Analyzing a Module

```bash
$ python AgentQMS/interface/cli_tools/ast_analysis.py analyze backend/routes/tools.py

============================================================
File: backend/routes/tools.py
Lines: 162
Classes: 1
Functions: 1
Total Complexity: 5

Classes:
  - ToolExecRequest (line 18)

Functions:
  - execute_tool() [complexity: 5]
```

### Example: Generating Tests

```bash
$ python AgentQMS/interface/cli_tools/ast_analysis.py generate-tests mymodule.py

# Test scaffold for mymodule.py
import pytest

from mymodule import *

def test_calculate():
    """Test calculate: Performs calculation."""
    # TODO: Implement test
    pass

def test_process_data():
    """Test process_data."""
    # TODO: Implement test
    pass
```

### Example: Quality Check

```bash
$ python AgentQMS/interface/cli_tools/ast_analysis.py check-quality src/

============================================================
Code Quality Report
============================================================

Summary:
  Files: 15
  Classes: 8
  Functions: 42
  Total Complexity: 156
  Total Lines: 2847
  Avg Complexity/Function: 3.71
  Avg Lines/File: 189.8

⚠️  Code Smells:
  - Found 2 functions with complexity > 10

⚠️  High Complexity Functions (>10):
  - process_complex_data in src/processor.py (complexity: 12)
  - handle_request in src/server.py (complexity: 15)
```

---

**Last Updated**: 2025-12-12


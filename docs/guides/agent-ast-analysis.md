---
title: "Agent AST Analysis Usage Guide"
type: guide
status: active
created: 2025-12-12
updated: 2025-12-12
tags: [guide, ast-analysis, agents, ai-tools]
---

# Agent AST Analysis Usage Guide

## Overview

This guide explains how AI agents should use the AST Analysis tool via the agent wrapper interface. The wrapper provides a simplified interface for agents to perform code analysis tasks.

## Agent Wrapper

The agent wrapper is located at:
```
AgentQMS/interface/cli_tools/ast_analysis.py
```

**⚠️ WARNING**: This tool is for AI agents only! Humans should use the main project tools directly.

## Available Commands

### 1. Analyze

Analyze code structure of a file or directory.

**Agent Usage:**
```bash
python AgentQMS/interface/cli_tools/ast_analysis.py analyze [path]
```

**Examples:**
```bash
# Analyze current directory
python AgentQMS/interface/cli_tools/ast_analysis.py analyze

# Analyze specific path
python AgentQMS/interface/cli_tools/ast_analysis.py analyze src/
python AgentQMS/interface/cli_tools/ast_analysis.py analyze backend/routes/tools.py
```

**When to Use:**
- Understanding code structure before making changes
- Analyzing dependencies and imports
- Getting overview of classes and functions
- Planning refactoring

### 2. Generate Tests

Generate test scaffolds from Python code.

**Agent Usage:**
```bash
python AgentQMS/interface/cli_tools/ast_analysis.py generate-tests <file>
```

**Examples:**
```bash
# Generate test scaffold
python AgentQMS/interface/cli_tools/ast_analysis.py generate-tests mymodule.py
```

**When to Use:**
- Creating test files for new modules
- Ensuring test coverage for existing code
- Following TDD practices
- Generating initial test structure

**Note:** Always review and enhance generated tests. They are scaffolds, not complete tests.

### 3. Extract Docs

Extract documentation from Python code.

**Agent Usage:**
```bash
python AgentQMS/interface/cli_tools/ast_analysis.py extract-docs <file>
```

**Examples:**
```bash
# Extract documentation
python AgentQMS/interface/cli_tools/ast_analysis.py extract-docs mymodule.py
```

**When to Use:**
- Creating or updating documentation
- Understanding module functionality
- Generating API documentation
- Maintaining docstring consistency

### 4. Check Quality

Check code quality metrics and detect issues.

**Agent Usage:**
```bash
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality [path]
```

**Examples:**
```bash
# Check current directory
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality

# Check specific path
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality src/
```

**When to Use:**
- Before submitting code changes
- Identifying high-complexity functions
- Detecting code smells
- Maintaining code quality standards

## Agent Workflow Integration

### Before Making Changes

1. **Analyze** the code you're about to modify:
   ```bash
   python AgentQMS/interface/cli_tools/ast_analysis.py analyze path/to/file.py
   ```

2. **Check Quality** to understand current state:
   ```bash
   python AgentQMS/interface/cli_tools/ast_analysis.py check-quality path/to/
   ```

### During Development

1. **Generate Tests** when creating new functionality:
   ```bash
   python AgentQMS/interface/cli_tools/ast_analysis.py generate-tests newmodule.py
   ```

2. **Extract Docs** to ensure documentation is up to date:
   ```bash
   python AgentQMS/interface/cli_tools/ast_analysis.py extract-docs newmodule.py
   ```

### Code Review Preparation

1. Run **Check Quality** on your changes:
   ```bash
   python AgentQMS/interface/cli_tools/ast_analysis.py check-quality changed/directory/
   ```

2. Address any high-complexity warnings before submitting

## Best Practices for Agents

### 1. Always Analyze Before Modifying

```bash
# Understand the code structure first
python AgentQMS/interface/cli_tools/ast_analysis.py analyze target_file.py
```

### 2. Check Quality Regularly

```bash
# Ensure code quality standards
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality .
```

### 3. Generate Tests for New Code

```bash
# Create test scaffolds
python AgentQMS/interface/cli_tools/ast_analysis.py generate-tests new_feature.py
# Then implement the actual tests
```

### 4. Extract Documentation

```bash
# Keep documentation current
python AgentQMS/interface/cli_tools/ast_analysis.py extract-docs updated_module.py
```

## Common Patterns

### Pattern 1: Understanding Existing Code

```bash
# Step 1: Analyze structure
python AgentQMS/interface/cli_tools/ast_analysis.py analyze existing_code.py

# Step 2: Extract documentation
python AgentQMS/interface/cli_tools/ast_analysis.py extract-docs existing_code.py

# Step 3: Check quality
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality existing_code.py
```

### Pattern 2: Adding New Features

```bash
# Step 1: Analyze related code
python AgentQMS/interface/cli_tools/ast_analysis.py analyze related_module.py

# Step 2: Implement new feature
# ... code changes ...

# Step 3: Generate tests
python AgentQMS/interface/cli_tools/ast_analysis.py generate-tests new_feature.py

# Step 4: Check quality
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality new_feature.py
```

### Pattern 3: Refactoring

```bash
# Step 1: Analyze current structure
python AgentQMS/interface/cli_tools/ast_analysis.py analyze module_to_refactor.py

# Step 2: Check quality (identify issues)
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality module_to_refactor.py

# Step 3: Refactor code
# ... refactoring ...

# Step 4: Verify quality improved
python AgentQMS/interface/cli_tools/ast_analysis.py check-quality module_to_refactor.py
```

## Error Handling

The tool handles errors gracefully:

- **Syntax Errors**: Reported but don't stop analysis
- **Missing Files**: Clear error messages
- **Import Errors**: Checked and reported

Always check the output for errors before proceeding.

## Integration with AgentQMS

### Artifact Creation

When creating artifacts that involve code changes:

1. Use `analyze` to understand current state
2. Use `check-quality` to document quality metrics
3. Include analysis results in artifact documentation

### Code Review

Before marking code as ready:

1. Run `check-quality` on changed files
2. Address any high-complexity warnings
3. Ensure tests are generated/updated

## Limitations

- **Python Only**: Only works with Python code
- **Basic Complexity**: Complexity calculation is simplified
- **No Execution**: Only analyzes structure, doesn't run code
- **Large Codebases**: May be slow on very large directories

## Troubleshooting

### Import Errors

If you see import errors:
- Ensure you're in the project root
- Check that AgentQMS is properly installed
- Verify PYTHONPATH is set correctly

### Command Not Found

If the command fails:
- Verify the file exists: `AgentQMS/interface/cli_tools/ast_analysis.py`
- Check file permissions
- Ensure Python 3 is available

### Empty Output

If you get no output:
- Check that the path exists
- Verify there are Python files in the path
- Check for syntax errors in target files

## Examples

### Example 1: Analyzing Before Refactoring

```bash
$ python AgentQMS/interface/cli_tools/ast_analysis.py analyze backend/routes/tools.py

============================================================
File: backend/routes/tools.py
Lines: 162
Classes: 1
Functions: 1
Total Complexity: 5
...
```

### Example 2: Quality Check Before Commit

```bash
$ python AgentQMS/interface/cli_tools/ast_analysis.py check-quality backend/

============================================================
Code Quality Report
============================================================

Summary:
  Files: 5
  Classes: 3
  Functions: 12
  Total Complexity: 45
  ...

⚠️  High Complexity Functions (>10):
  - execute_tool in backend/routes/tools.py (complexity: 12)
```

### Example 3: Generating Tests

```bash
$ python AgentQMS/interface/cli_tools/ast_analysis.py generate-tests mymodule.py

# Test scaffold for mymodule.py
import pytest

from mymodule import *

def test_my_function():
    """Test my_function: Does something useful."""
    # TODO: Implement test
    pass
```

---

**Last Updated**: 2025-12-12  
**For Agents**: Use this tool to understand and analyze code before making changes.


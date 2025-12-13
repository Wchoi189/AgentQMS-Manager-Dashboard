#!/usr/bin/env python3
"""
AST Analysis CLI Tool
Provides code analysis capabilities using Python's AST module.
"""

import ast
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class ASTAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing code structure."""
    
    def __init__(self):
        self.classes = []
        self.functions = []
        self.imports = []
        self.complexity = 0
        
    def visit_ClassDef(self, node):
        """Visit class definitions."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        
        self.classes.append({
            'name': node.name,
            'line': node.lineno,
            'methods': methods,
            'docstring': ast.get_docstring(node)
        })
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        args = [arg.arg for arg in node.args.args]
        complexity = self._calculate_complexity(node)
        
        self.functions.append({
            'name': node.name,
            'line': node.lineno,
            'args': args,
            'complexity': complexity,
            'docstring': ast.get_docstring(node),
            'returns': self._get_return_type(node)
        })
        self.complexity += complexity
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Visit import statements."""
        for alias in node.names:
            self.imports.append({
                'module': alias.name,
                'alias': alias.asname,
                'type': 'import'
            })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit from ... import statements."""
        for alias in node.names:
            self.imports.append({
                'module': node.module or '',
                'name': alias.name,
                'alias': alias.asname,
                'type': 'from_import'
            })
        self.generic_visit(node)
    
    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def _get_return_type(self, node) -> Optional[str]:
        """Extract return type annotation if present."""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return None


def analyze_file(file_path: str) -> Dict[str, Any]:
    """Analyze a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=file_path)
        analyzer = ASTAnalyzer()
        analyzer.visit(tree)
        
        return {
            'file': file_path,
            'classes': analyzer.classes,
            'functions': analyzer.functions,
            'imports': analyzer.imports,
            'total_complexity': analyzer.complexity,
            'line_count': len(content.splitlines())
        }
    except SyntaxError as e:
        return {
            'file': file_path,
            'error': f'Syntax error: {e.msg} at line {e.lineno}',
            'classes': [],
            'functions': [],
            'imports': [],
            'total_complexity': 0,
            'line_count': 0
        }
    except Exception as e:
        return {
            'file': file_path,
            'error': f'Error analyzing file: {str(e)}',
            'classes': [],
            'functions': [],
            'imports': [],
            'total_complexity': 0,
            'line_count': 0
        }


def analyze_directory(directory: str) -> List[Dict[str, Any]]:
    """Analyze all Python files in a directory."""
    results = []
    path = Path(directory)
    
    if path.is_file() and path.suffix == '.py':
        results.append(analyze_file(str(path)))
    elif path.is_dir():
        for py_file in path.rglob('*.py'):
            # Skip __pycache__ and virtual environments
            if '__pycache__' in str(py_file) or '.venv' in str(py_file):
                continue
            results.append(analyze_file(str(py_file)))
    else:
        print(f"Error: {directory} is not a valid Python file or directory")
        sys.exit(1)
    
    return results


def generate_test_scaffold(file_path: str) -> str:
    """Generate pytest test scaffold from a Python file."""
    analysis = analyze_file(file_path)
    
    if 'error' in analysis:
        return f"# Error analyzing file: {analysis['error']}\n"
    
    output = [f"# Test scaffold for {Path(file_path).name}"]
    output.append("import pytest\n")
    
    # Generate imports
    module_name = Path(file_path).stem
    output.append(f"from {module_name} import *\n")
    
    # Generate test functions
    for func in analysis['functions']:
        if func['name'].startswith('_') and not func['name'].startswith('__'):
            continue  # Skip private functions
        
        test_name = f"test_{func['name']}"
        output.append(f"\ndef {test_name}():")
        if func['docstring']:
            output.append(f'    """Test {func["name"]}: {func["docstring"][:50]}"""')
        else:
            output.append(f'    """Test {func["name"]}."""')
        output.append("    # TODO: Implement test")
        output.append("    pass\n")
    
    # Generate test classes
    for cls in analysis['classes']:
        output.append(f"\nclass Test{cls['name']}:")
        output.append(f'    """Test class for {cls["name"]}."""')
        output.append("    \n    def test_init(self):")
        output.append("        # TODO: Implement initialization test")
        output.append("        pass\n")
    
    return "\n".join(output)


def extract_documentation(file_path: str) -> str:
    """Extract documentation from a Python file."""
    analysis = analyze_file(file_path)
    
    if 'error' in analysis:
        return f"# Error: {analysis['error']}\n"
    
    output = [f"# Documentation for {Path(file_path).name}\n"]
    
    # Module-level docstring
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            module_doc = ast.get_docstring(tree)
            if module_doc:
                output.append(f"## Module Description\n\n{module_doc}\n")
    except:
        pass
    
    # Classes
    if analysis['classes']:
        output.append("## Classes\n")
        for cls in analysis['classes']:
            output.append(f"### {cls['name']}")
            if cls['docstring']:
                output.append(f"\n{cls['docstring']}\n")
            output.append(f"\n**Methods:** {', '.join(cls['methods'])}\n")
    
    # Functions
    if analysis['functions']:
        output.append("## Functions\n")
        for func in analysis['functions']:
            output.append(f"### {func['name']}")
            args_str = ", ".join(func['args'])
            output.append(f"\n**Signature:** `{func['name']}({args_str})`")
            if func['returns']:
                output.append(f"\n**Returns:** `{func['returns']}`")
            if func['docstring']:
                output.append(f"\n\n{func['docstring']}\n")
            output.append("")
    
    return "\n".join(output)


def check_quality(directory: str) -> Dict[str, Any]:
    """Check code quality metrics."""
    results = analyze_directory(directory)
    
    total_files = len(results)
    total_classes = sum(len(r.get('classes', [])) for r in results)
    total_functions = sum(len(r.get('functions', [])) for r in results)
    total_complexity = sum(r.get('total_complexity', 0) for r in results)
    total_lines = sum(r.get('line_count', 0) for r in results)
    
    # Code smells
    smells = []
    high_complexity_functions = []
    
    for result in results:
        for func in result.get('functions', []):
            if func.get('complexity', 0) > 10:
                high_complexity_functions.append({
                    'file': result['file'],
                    'function': func['name'],
                    'complexity': func['complexity']
                })
    
    if high_complexity_functions:
        smells.append(f"Found {len(high_complexity_functions)} functions with complexity > 10")
    
    # Calculate average metrics
    avg_complexity = total_complexity / total_functions if total_functions > 0 else 0
    avg_lines = total_lines / total_files if total_files > 0 else 0
    
    return {
        'summary': {
            'total_files': total_files,
            'total_classes': total_classes,
            'total_functions': total_functions,
            'total_complexity': total_complexity,
            'total_lines': total_lines,
            'avg_complexity_per_function': round(avg_complexity, 2),
            'avg_lines_per_file': round(avg_lines, 2)
        },
        'code_smells': smells,
        'high_complexity_functions': high_complexity_functions,
        'files': results
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='AST Analysis Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze code structure')
    analyze_parser.add_argument('path', nargs='?', default='.', help='File or directory to analyze')
    analyze_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Generate tests command
    test_parser = subparsers.add_parser('generate-tests', help='Generate test scaffolds')
    test_parser.add_argument('file', help='Python file to generate tests for')
    test_parser.add_argument('--output', help='Output file (default: stdout)')
    
    # Extract docs command
    docs_parser = subparsers.add_parser('extract-docs', help='Extract documentation')
    docs_parser.add_argument('file', help='Python file to extract docs from')
    docs_parser.add_argument('--output', help='Output file (default: stdout)')
    
    # Check quality command
    quality_parser = subparsers.add_parser('check-quality', help='Check code quality')
    quality_parser.add_argument('path', nargs='?', default='.', help='File or directory to check')
    quality_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'analyze':
        results = analyze_directory(args.path)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for result in results:
                print(f"\n{'='*60}")
                print(f"File: {result['file']}")
                if 'error' in result:
                    print(f"Error: {result['error']}")
                    continue
                print(f"Lines: {result['line_count']}")
                print(f"Classes: {len(result['classes'])}")
                print(f"Functions: {len(result['functions'])}")
                print(f"Total Complexity: {result['total_complexity']}")
                if result['classes']:
                    print("\nClasses:")
                    for cls in result['classes']:
                        print(f"  - {cls['name']} (line {cls['line']})")
                if result['functions']:
                    print("\nFunctions:")
                    for func in result['functions']:
                        args_str = ", ".join(func['args'])
                        print(f"  - {func['name']}({args_str}) [complexity: {func['complexity']}]")
    
    elif args.command == 'generate-tests':
        output = generate_test_scaffold(args.file)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Test scaffold written to {args.output}")
        else:
            print(output)
    
    elif args.command == 'extract-docs':
        output = extract_documentation(args.file)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Documentation written to {args.output}")
        else:
            print(output)
    
    elif args.command == 'check-quality':
        quality_report = check_quality(args.path)
        if args.json:
            print(json.dumps(quality_report, indent=2))
        else:
            print("\n" + "="*60)
            print("Code Quality Report")
            print("="*60)
            summary = quality_report['summary']
            print(f"\nSummary:")
            print(f"  Files: {summary['total_files']}")
            print(f"  Classes: {summary['total_classes']}")
            print(f"  Functions: {summary['total_functions']}")
            print(f"  Total Complexity: {summary['total_complexity']}")
            print(f"  Total Lines: {summary['total_lines']}")
            print(f"  Avg Complexity/Function: {summary['avg_complexity_per_function']}")
            print(f"  Avg Lines/File: {summary['avg_lines_per_file']}")
            
            if quality_report['code_smells']:
                print(f"\n⚠️  Code Smells:")
                for smell in quality_report['code_smells']:
                    print(f"  - {smell}")
            
            if quality_report['high_complexity_functions']:
                print(f"\n⚠️  High Complexity Functions (>10):")
                for func in quality_report['high_complexity_functions']:
                    print(f"  - {func['function']} in {func['file']} (complexity: {func['complexity']})")


if __name__ == '__main__':
    main()


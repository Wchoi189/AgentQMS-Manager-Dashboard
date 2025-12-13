#!/usr/bin/env python3
"""
Dead Link Checker
Scans markdown files for broken internal and external links.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path before importing AgentQMS modules
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from AgentQMS.agent_tools.utils.runtime import ensure_project_root_on_sys_path

ensure_project_root_on_sys_path()

# Import the link validator from documentation tools
try:
    from AgentQMS.agent_tools.documentation.validate_links import LinkValidator
except ImportError:
    try:
        # Try alternative import path
        from agent_tools.documentation.validate_links import LinkValidator
    except ImportError:
        # Fallback if import fails
        print("Warning: Could not import LinkValidator, using basic implementation")
        LinkValidator = None


def check_links(directory: str) -> tuple[bool, list[str]]:
    """Check links in markdown files.
    
    Args:
        directory: Directory to scan for markdown files
        
    Returns:
        Tuple of (has_errors, list_of_errors)
    """
    errors = []
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return True, [f"Directory not found: {directory}"]
    
    if not dir_path.is_dir():
        return True, [f"Path is not a directory: {directory}"]
    
    if LinkValidator:
        try:
            validator = LinkValidator(str(dir_path))
            validator.validate_all()
            
            if validator.errors:
                errors.extend(validator.errors)
            if validator.warnings:
                # Convert warnings to info messages
                for warning in validator.warnings:
                    errors.append(f"Warning: {warning}")
            
            return len(validator.errors) == 0, errors
        except Exception as e:
            return True, [f"Error during link validation: {str(e)}"]
    else:
        # Basic implementation
        md_files = list(dir_path.rglob('*.md'))
        if not md_files:
            return False, ["No markdown files found"]
        
        # Simple check - just report files found
        print(f"Found {len(md_files)} markdown files")
        print("Note: Full link validation requires LinkValidator module")
        return False, []


def main():
    parser = argparse.ArgumentParser(
        description='Check for broken links in markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--dir',
        default='.',
        help='Directory to scan for markdown files (default: current directory)'
    )
    
    args = parser.parse_args()
    
    has_errors, errors = check_links(args.dir)
    
    if not has_errors and not errors:
        print(f"✓ Link check completed: {args.dir}")
        sys.exit(0)
    elif errors:
        print(f"✗ Link check found issues: {args.dir}")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print(f"✓ No broken links found: {args.dir}")
        sys.exit(0)


if __name__ == '__main__':
    main()


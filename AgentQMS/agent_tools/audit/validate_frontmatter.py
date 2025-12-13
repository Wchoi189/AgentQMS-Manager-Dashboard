#!/usr/bin/env python3
"""
Frontmatter Validator
Validates YAML frontmatter in markdown files for required fields.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path before importing AgentQMS modules
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import frontmatter

from AgentQMS.agent_tools.utils.runtime import ensure_project_root_on_sys_path

ensure_project_root_on_sys_path()


def validate_frontmatter(file_path: str) -> tuple[bool, list[str]]:
    """Validate frontmatter in a markdown file.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    file = Path(file_path)
    
    if not file.exists():
        return False, [f"File not found: {file_path}"]
    
    if not file.suffix == '.md':
        return False, [f"File is not a markdown file: {file_path}"]
    
    try:
        with open(file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        metadata = post.metadata
        
        # Check required fields
        if not metadata.get('title'):
            errors.append("Missing required field: 'title'")
        
        if not metadata.get('type'):
            errors.append("Missing required field: 'type'")
        
        if not metadata.get('status'):
            errors.append("Missing required field: 'status'")
        
        # Check AgentQMS-specific fields
        if not metadata.get('branch_name'):
            errors.append("Missing AgentQMS field: 'branch_name'")
        
        # Check for date/timestamp
        has_date = metadata.get('date') or metadata.get('created') or metadata.get('updated')
        if not has_date:
            errors.append("Missing date field: 'date', 'created', or 'updated'")
        
        # Validate date format if present
        date_value = metadata.get('date') or metadata.get('created')
        if date_value:
            # Check if date follows format: YYYY-MM-DD HH:MM (TIMEZONE)
            import re
            date_pattern = r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+\([A-Z]+\)'
            if not re.match(date_pattern, str(date_value)):
                errors.append(f"Date format invalid: '{date_value}'. Expected: 'YYYY-MM-DD HH:MM (TIMEZONE)'")
        
        is_valid = len(errors) == 0
        return is_valid, errors
        
    except Exception as e:
        return False, [f"Error reading file: {str(e)}"]


def main():
    parser = argparse.ArgumentParser(
        description='Validate frontmatter in markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--file',
        required=True,
        help='Path to markdown file to validate'
    )
    
    args = parser.parse_args()
    
    is_valid, errors = validate_frontmatter(args.file)
    
    if is_valid:
        print(f"✓ Frontmatter is valid: {args.file}")
        sys.exit(0)
    else:
        print(f"✗ Frontmatter validation failed: {args.file}")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()


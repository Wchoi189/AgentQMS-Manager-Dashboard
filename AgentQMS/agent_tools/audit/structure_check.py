#!/usr/bin/env python3
"""
Structural Integrity Checker
Verifies that the folder structure matches the .agentqms/config.json rules.
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path before importing AgentQMS modules
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from AgentQMS.agent_tools.utils.runtime import ensure_project_root_on_sys_path

ensure_project_root_on_sys_path()


def check_structure(config_path: str = None) -> tuple[bool, list[str]]:
    """Check folder structure against configuration.
    
    Args:
        config_path: Path to .agentqms/config.json (optional)
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    warnings = []
    
    # Find project root
    current = Path.cwd()
    project_root = None
    
    # Look for .agentqms directory
    for parent in [current] + list(current.parents):
        agentqms_dir = parent / '.agentqms'
        if agentqms_dir.exists():
            project_root = parent
            break
    
    if not project_root:
        warnings.append("No .agentqms directory found - using default structure")
        # Check for basic AgentQMS structure
        agentqms_dir = current / 'AgentQMS'
        if not agentqms_dir.exists():
            errors.append("AgentQMS directory not found")
        else:
            # Check for expected subdirectories
            expected_dirs = ['agent_tools', 'knowledge', 'interface']
            for expected in expected_dirs:
                if not (agentqms_dir / expected).exists():
                    warnings.append(f"Expected directory not found: AgentQMS/{expected}")
        return len(errors) == 0, errors + warnings
    
    # Load config if provided
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = project_root / '.agentqms' / 'config.json'
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Check structure based on config
            if 'structure' in config:
                structure = config['structure']
                for key, expected_path in structure.items():
                    full_path = project_root / expected_path
                    if not full_path.exists():
                        errors.append(f"Required path not found: {expected_path}")
        except Exception as e:
            warnings.append(f"Could not parse config file: {str(e)}")
    else:
        warnings.append(f"Config file not found: {config_file}")
    
    # Basic structure checks
    agentqms_dir = project_root / 'AgentQMS'
    if agentqms_dir.exists():
        required_dirs = ['agent_tools']
        for req_dir in required_dirs:
            if not (agentqms_dir / req_dir).exists():
                errors.append(f"Required directory missing: AgentQMS/{req_dir}")
    else:
        errors.append("AgentQMS directory not found in project root")
    
    is_valid = len(errors) == 0
    return is_valid, errors + warnings


def main():
    parser = argparse.ArgumentParser(
        description='Check folder structure against AgentQMS configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--config',
        help='Path to .agentqms/config.json (default: auto-detect)'
    )
    
    args = parser.parse_args()
    
    is_valid, issues = check_structure(args.config)
    
    # Separate errors and warnings
    errors = [i for i in issues if not i.startswith('Warning:')]
    warnings = [i.replace('Warning: ', '') for i in issues if i.startswith('Warning:')]
    
    if warnings:
        for warning in warnings:
            print(f"⚠ {warning}")
    
    if is_valid:
        print("✓ Folder structure is valid")
        sys.exit(0)
    else:
        print("✗ Folder structure validation failed")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()


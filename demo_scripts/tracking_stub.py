#!/usr/bin/env python3
"""
Demo tracking stub that returns formatted status messages.
Matches the format expected by AgentQMS tracking query API.
"""
import sys
import argparse

def get_status(kind: str = "all") -> str:
    """Return status message for the given kind."""
    kind = kind.lower()
    
    if kind == "plan":
        return "demo-plan-001:in_progress open=3 | demo-plan-002:completed open=0"
    elif kind == "experiment":
        return "exp-ocr-tuning:completed | exp-prompt-optimization:in_progress"
    elif kind == "debug":
        return "debug-cors-issue:completed | debug-api-timeout:in_progress"
    elif kind == "refactor":
        return "refactor-toolkit-migration:completed | refactor-schema-update:in_progress"
    elif kind == "all":
        # Ultra-concise format matching AgentQMS query.py
        return "plans: demo-plan-001:in_progress open=3 | experiments: exp-ocr-tuning:completed | debug: debug-cors-issue:completed | refactors: refactor-toolkit-migration:completed"
    else:
        return f"Unknown kind: {kind}"


def main():
    parser = argparse.ArgumentParser(description="Demo tracking database stub")
    parser.add_argument(
        "--kind",
        default="all",
        help="Kind of status to return: plan, experiment, debug, refactor, or all"
    )
    args = parser.parse_args()
    
    status_text = get_status(args.kind)
    print(status_text)
    sys.exit(0)


if __name__ == "__main__":
    main()

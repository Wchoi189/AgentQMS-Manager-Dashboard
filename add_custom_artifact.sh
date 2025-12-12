#!/bin/bash
# Helper script to add custom artifacts to demo_data
# Usage: ./add_custom_artifact.sh <type> <title> <status> [tags...]
#
# Example:
#   ./add_custom_artifact.sh implementation_plan "My Plan" active "tag1" "tag2"

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 <type> <title> <status> [tags...]"
    echo ""
    echo "Types: implementation_plan, assessment, audit, bug_report, design"
    echo "Status: draft, active, completed, archived, resolved"
    echo ""
    echo "Example:"
    echo "  $0 implementation_plan \"My Feature Plan\" active \"feature\" \"enhancement\""
    exit 1
fi

TYPE=$1
TITLE=$2
STATUS=$3
shift 3
TAGS="$@"

# Validate type
case $TYPE in
    implementation_plan|assessment|audit|bug_report|design)
        ;;
    *)
        echo -e "${YELLOW}Error: Invalid type '$TYPE'${NC}"
        echo "Valid types: implementation_plan, assessment, audit, bug_report, design"
        exit 1
        ;;
esac

# Map type to directory
case $TYPE in
    implementation_plan)
        DIR="implementation_plans"
        ;;
    assessment)
        DIR="assessments"
        ;;
    audit)
        DIR="audits"
        ;;
    bug_report)
        DIR="bug_reports"
        ;;
    design)
        DIR="design_documents"
        ;;
esac

# Create directory if needed
mkdir -p "demo_data/artifacts/$DIR"

# Generate filename
TIMESTAMP=$(date +"%Y-%m-%d_%H%M")
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
FILENAME="${TIMESTAMP}_${TYPE}_${SLUG}.md"
FILEPATH="demo_data/artifacts/$DIR/$FILENAME"

# Format tags
TAG_LIST=""
if [ -n "$TAGS" ]; then
    TAG_LIST=$(echo "$TAGS" | sed "s/ /, /g")
    TAG_LIST="[$TAG_LIST]"
else
    TAG_LIST="[]"
fi

# Create artifact file
cat > "$FILEPATH" << EOF
---
title: "$TITLE"
type: $TYPE
status: $STATUS
created: $(date +"%Y-%m-%d %H:%M (KST)")
tags: $TAG_LIST
---

# $TITLE

## Description
Add your description here.

## Details
Add more details about this artifact.

## Notes
- Add notes here
- More notes

EOF

echo -e "${GREEN}✅ Created artifact:${NC}"
echo "   File: $FILEPATH"
echo "   Type: $TYPE"
echo "   Status: $STATUS"
echo "   Tags: $TAG_LIST"
echo ""
echo -e "${BLUE}Edit the file to add content:${NC}"
echo "   nano $FILEPATH"
echo "   # or"
echo "   code $FILEPATH"
echo ""
echo "The artifact will appear in the Librarian page after refreshing!"

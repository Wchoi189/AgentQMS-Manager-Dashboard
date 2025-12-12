---
title: "Artifact Management Guide"
status: draft
last_updated: 2025-12-12
tags: [artifacts, guide]
---

# Artifact Management Guide

This guide explains how to add, manage, and customize artifacts for the Librarian page.

---

## Current Artifact Count

After running the setup scripts, you'll have:
- **5 artifacts** (from `create_demo_data_simple.sh`)
- **18 artifacts** (after running `add_more_demo_artifacts.sh`)

**Breakdown by type**:
- Implementation Plans: 4
- Assessments: 3
- Audits: 3
- Bug Reports: 4
- Design Documents: 4

---

## Adding More Sample Artifacts

### Option 1: Use the Bulk Script (Recommended)

Adds 12 pre-made sample artifacts with variety:

```bash
./add_more_demo_artifacts.sh
```

This adds:
- 3 Implementation Plans (different statuses)
- 2 Assessments
- 2 Audits
- 3 Bug Reports
- 3 Design Documents

### Option 2: Add Custom Artifacts

Use the helper script to add your own artifacts:

```bash
# Syntax
./add_custom_artifact.sh <type> <title> <status> [tags...]

# Examples
./add_custom_artifact.sh implementation_plan "My Feature Plan" active "feature" "enhancement"
./add_custom_artifact.sh bug_report "Login Issue" resolved "bug" "authentication"
./add_custom_artifact.sh assessment "Performance Review" completed "performance"
```

**Valid Types**:
- `implementation_plan`
- `assessment`
- `audit`
- `bug_report`
- `design`

**Valid Statuses**:
- `draft`
- `active`
- `completed`
- `archived`
- `resolved`

### Option 3: Manual Creation

Create artifacts manually in the appropriate directory:

```bash
# Choose the right directory based on type
demo_data/artifacts/implementation_plans/
demo_data/artifacts/assessments/
demo_data/artifacts/audits/
demo_data/artifacts/bug_reports/
demo_data/artifacts/design_documents/
```

**File Naming Convention**:
```
YYYY-MM-DD_HHMM_<type>_<slug>.md
```

Example: `2025-12-12_1430_implementation_plan_my-feature.md`

**Required Frontmatter**:
```yaml
---
title: "Your Artifact Title"
type: implementation_plan  # or assessment, audit, bug_report, design
status: active  # draft, active, completed, archived, resolved
created: 2025-12-12 14:30 (KST)
tags: [tag1, tag2, tag3]
---
```

**Optional Frontmatter Fields**:
- `category`: Category name (e.g., "security", "performance")
- `priority`: Priority level (e.g., "high", "medium", "low")
- `phase`: Phase number (for implementation plans)
- `severity`: Severity level (for bug reports)
- `updated`: Update timestamp

---

## Artifact Structure Examples

### Implementation Plan
```markdown
---
title: "Implementation Plan: Feature X"
type: implementation_plan
status: active
created: 2025-12-12 14:30 (KST)
phase: 1
priority: high
tags: [feature, enhancement]
---

# Implementation Plan: Feature X

## Objective
Brief description of what we're building.

## Tasks
- [ ] Task 1
- [ ] Task 2
- [x] Completed task

## Timeline
- Week 1: Planning
- Week 2: Implementation

## Success Metrics
- Metric 1
- Metric 2
```

### Bug Report
```markdown
---
title: "BUG-005: Issue Description"
type: bug_report
status: active
created: 2025-12-12 14:30 (KST)
severity: high
tags: [bug, frontend]
---

# BUG-005: Issue Description

## Description
What the bug is.

## Steps to Reproduce
1. Step 1
2. Step 2
3. See error

## Root Cause
Why it happens.

## Fix
How to fix it.

## Status
🔧 In progress
```

### Assessment
```markdown
---
title: "Assessment: Topic Analysis"
type: assessment
status: completed
created: 2025-12-12 14:30 (KST)
category: evaluation
tags: [assessment, analysis]
---

# Assessment: Topic Analysis

## Summary
Brief summary of the assessment.

## Findings
- Finding 1
- Finding 2

## Recommendations
1. Recommendation 1
2. Recommendation 2
```

---

## Viewing Artifacts

After adding artifacts:

1. **Restart backend** (if running):
   ```bash
   # Stop and restart
   make stop-servers
   export DEMO_MODE=true
   ./start_dev.sh
   ```

2. **Or just refresh** the Librarian page in your browser

3. **Filter artifacts**:
   - By type: Implementation Plans, Assessments, Audits, Bug Reports
   - By status: Draft, Active, Completed, Archived
   - By search: Search in title, ID, or type

---

## Tips for Creating Good Artifacts

1. **Use Descriptive Titles**: Clear, concise titles help with search
2. **Add Relevant Tags**: Makes filtering easier
3. **Set Appropriate Status**: Helps track progress
4. **Include Dates**: Use consistent date format (KST)
5. **Follow Naming Convention**: Makes artifacts easier to find
6. **Add Rich Content**: More content = better testing of the UI

---

## Bulk Import from Your Own Artifacts

If you have existing artifacts you want to import:

1. **Copy files** to the appropriate directory:
   ```bash
   cp your-artifact.md demo_data/artifacts/implementation_plans/
   ```

2. **Ensure frontmatter** matches the expected format

3. **Rename if needed** to follow the naming convention

4. **Refresh** the Librarian page

---

## Troubleshooting

### Artifacts Not Showing Up

1. **Check file location**: Must be in correct subdirectory
2. **Check frontmatter**: Must have required fields
3. **Check file extension**: Must be `.md`
4. **Restart backend**: Changes require backend restart
5. **Check DEMO_MODE**: Must be set to `true`

### Frontmatter Errors

If artifacts don't parse correctly:

1. **Check YAML syntax**: Must be valid YAML
2. **Check required fields**: `title`, `type`, `status` are required
3. **Check date format**: Use `YYYY-MM-DD HH:MM (KST)`
4. **Check tags format**: Must be array `[tag1, tag2]`

### View Logs

```bash
# Backend logs show parsing errors
tail -f /tmp/backend.log

# Look for "Error parsing" messages
```

---

## Quick Reference

```bash
# Add 12 more sample artifacts
./add_more_demo_artifacts.sh

# Add custom artifact
./add_custom_artifact.sh implementation_plan "My Plan" active "tag1" "tag2"

# List all artifacts
find demo_data/artifacts -name "*.md"

# Count artifacts by type
find demo_data/artifacts/implementation_plans -name "*.md" | wc -l

# Edit an artifact
nano demo_data/artifacts/implementation_plans/2025-12-01_1000_plan-ocr-feature.md
```

---

**Happy artifact creating! 📚**

---
type: implementation_plan
title: DMS Phase 3 (Self-Healing & Automation)
status: draft
category: automation
tags: [backend, frontend, automation, git, compliance]
date: 2025-12-14 22:00 (KST)
---

# DMS Phase 3: Self-Healing & Automation

This plan outlines the "Self-Healing" capabilities for the Document Management System, allowing the system to automatically fix common compliance violations.

## Goal
Reduce user toil by automating reliable, deterministic fixes for compliance issues (e.g., missing dates, invalid status) and ensuring safety through Git integration.

## Proposed Changes

### Backend: Remediation Service

#### [NEW] [backend/services/compliance/remediator.py](file:///workspaces/AgentQMS-Manager-Dashboard/backend/services/compliance/remediator.py)
*   **Purpose**: Logic to apply fixes for specific `rule_ids`.
*   **Features**:
    *   `fix_violation(file_path, rule_id)`: Main entry point.
    *   `_fix_date(post)`: Sets `date` to current timestamp.
    *   `_fix_status(post, artifact_type)`: Sets `status` to a valid default (e.g., `draft` or `review_needed`).
    *   `_fix_tags(post)`: Adds empty `tags` list.
*   **Safety**: Validates the file exists and parses correctly before modifying.

#### [NEW] [backend/services/git/client.py](file:///workspaces/AgentQMS-Manager-Dashboard/backend/services/git/client.py)
*   **Purpose**: Abstract git operations to ensure changes are tracked.
*   **Features**:
    *   `commit_file(file_path, message)`: Stages and commits a single file.
    *   `get_file_history(file_path)`: (Optional for now) Returns commit log.

#### [MODIFY] [backend/routes/compliance.py](file:///workspaces/AgentQMS-Manager-Dashboard/backend/routes/compliance.py)
*   **New Endpoint**: `POST /compliance/fix`
    *   **Body**: `{ file_path: string, rule_id: string }`
    *   **Action**: Calls `Remediator`, then optionally `GitClient.commit_file`.

### Frontend: Quick Fix Actions

#### [MODIFY] [frontend/services/complianceService.ts](file:///workspaces/AgentQMS-Manager-Dashboard/frontend/services/complianceService.ts)
*   Add `fixViolation(path: string, rule_id: string)` method.

#### [MODIFY] [frontend/components/ViolationList.tsx](file:///workspaces/AgentQMS-Manager-Dashboard/frontend/components/ViolationList.tsx)
*   Add "Action" column.
*   Render "Fix" button for supported rule IDs (`missing_required_field`, `invalid_status`).
*   Show loading state during fix operation.

## Verification Plan

### Automated Tests
*   **Backend**: Unit tests for `Remediator` ensuring it modifies Frontmatter correctly without touching content.
*   **End-to-End**: Trigger a fix via API and verify the file on disk is updated.

### Manual Verification
1.  Open Compliance Dashboard.
2.  Find a file with "Missing Date".
3.  Click "Fix".
4.  Verify the violation disappears from the list.
5.  (Optional) Verify a git commit was created: `git log -1`.

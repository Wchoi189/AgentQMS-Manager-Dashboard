---
type: implementation_plan
title: DMS Phase 2 (Compliance Visualization)
status: draft
category: frontend
tags: [frontend, dashboard, compliance, dms]
date: 2025-12-14 21:00 (KST)
---

# DMS Phase 2: Compliance Visualization

This plan outlines the integration of the Compliance Engine into the AgentQMS Manager Dashboard.

## Goal
Provide a visual interface for users to see the "Health" of their documentation and identify specific violations that need fixing.

## Proposed Changes

### Frontend Components

#### [NEW] [frontend/components/ComplianceBadge.tsx](file:///workspaces/AgentQMS-Manager-Dashboard/frontend/components/ComplianceBadge.tsx)
- Visual component to display "Pass" (Green) / "Fail" (Red) status.
- Shows compliance score percentage.

#### [NEW] [frontend/components/ViolationList.tsx](file:///workspaces/AgentQMS-Manager-Dashboard/frontend/components/ViolationList.tsx)
- List view of `violations` from the API.
- Columns: File, Rule, Message, Severity.
- Action button (placeholder for Phase 3): "Fix".

#### [NEW] [frontend/services/complianceService.ts](file:///workspaces/AgentQMS-Manager-Dashboard/frontend/services/complianceService.ts)
- TypeScript service to call `GET /api/v1/compliance/validate`.
- Type definitions for `ValidationResult`.

### Frontend Pages

#### [MODIFY] [frontend/App.tsx](file:///workspaces/AgentQMS-Manager-Dashboard/frontend/App.tsx)
- Add new route: `/compliance`.
- Add navigation link in the Sidebar.

#### [NEW] [frontend/pages/ComplianceDashboard.tsx](file:///workspaces/AgentQMS-Manager-Dashboard/frontend/pages/ComplianceDashboard.tsx)
- Main view.
- **Header**: Overall System Health Score.
- **Body**: Tabbed view? Or just a list of artifacts with issues?
- *Initial Design*: Simple card layout showing "Top Violations" and "Compliance by Artifact Type".

## Verification Plan

### Manual Verification
1.  **Start Dev Servers**: `make dev`.
2.  **Navigate to Dashboard**: Click "Compliance" in sidebar.
3.  **Verify Data**: Ensure the "Health Score" matches the `curl` output (e.g., ~63%).
4.  **Verify Interact**: Click through to see violations for a specific file.

### Automated Tests
*   **Component Tests**: `npm test` should pass for new components.

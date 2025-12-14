---
type: implementation_plan
title: DMS Compliance Engine Implementation (Phase 1)
status: draft
category: backend
tags: [compliance, pydantic, automation]
date: 2025-12-14 20:00 (KST)
---

# DMS Compliance Engine Implementation (Phase 1)

This plan outlines the first phase of the Documentation Management System's "Compliance Engine". The goal is to replace the current demo stub with a real, rule-based validation system using Pydantic.

## User Review Required

> [!IMPORTANT]
> This change introduces `pydantic` as a primary validation engine for markdown frontmatter.
> This will deprecate the use of `demo_scripts/compliance_stub.py` for the API, but keep it for reference.

## Proposed Changes

### Backend Structure

We will create a new service module for compliance to isolate logic from routes.

#### [NEW] [backend/services/compliance/models.py](file:///workspaces/AgentQMS-Manager-Dashboard/backend/services/compliance/models.py)
- Define Pydantic models for `ArtifactMetadata` (common fields: type, status, date).
- Define `ValidationViolation` and `ValidationReport` models.

#### [NEW] [backend/services/compliance/rules.yaml](file:///workspaces/AgentQMS-Manager-Dashboard/backend/services/compliance/rules.yaml)
- Define the "Gold Standard" rules (e.g., required fields per artifact type).
- *Initial Scope*: Validate `type`, `status`, `date`, `title`.

#### [NEW] [backend/services/compliance/validator.py](file:///workspaces/AgentQMS-Manager-Dashboard/backend/services/compliance/validator.py)
- Implement `validate_file(path)` and `validate_directory(path)`.
- Use `frontmatter` to load files and `pydantic` to validate metadata.

#### [MODIFY] [backend/routes/compliance.py](file:///workspaces/AgentQMS-Manager-Dashboard/backend/routes/compliance.py)
- Import the new `validator` service.
- Update `/validate` endpoint to call `validator.validate_directory` instead of `subprocess.run(stub)`.
- *Note*: `DEMO_MODE` check will be updated to use the real validator if `DEMO_MODE=false` OR if explicitly requested.

## Verification Plan

### Automated Tests
*   **Unit Tests**: Create `backend/tests/test_compliance.py` (if test harness exists) or a standalone script `backend/test_compliance_local.py` to verify:
    *   Valid artifact returns 0 violations.
    *   Invalid artifact (missing title) returns 1 violation.
    *   Invalid directory returns aggregate stats.

### Manual Verification
1.  **Create Bad Artifact**:
    *   Create `demo_data/artifacts/implementation_plans/bad_plan.md` with missing `title`.
2.  **Run Validator Tool**:
    *   Curl or visit: `http://localhost:8000/api/v1/compliance/validate?target=demo_data/artifacts/implementation_plans/bad_plan.md`
    *   **Expect**: JSON response listing "Missing required field: title".
3.  **Run Dashboard Check**:
    *   Visit the Compliance Dashboard (if UI exists, otherwise check JSON output).

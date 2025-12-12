## AgentQMS Integration Plan (Physical Copy)

### Goals
- Make the imported `AgentQMS/` and `.agentqms/` usable in this project with a lightweight/pruned footprint.
- Reconfigure `.agentqms/` state for this repo and wire backend tool execution to the pruned AgentQMS where feasible.

### Steps
1) Inventory & pruning
- Identify required vs optional components in `AgentQMS/` (keep artifact generation/validation; drop unused agents/tools).
- Confirm required runtime/container dirs exist: `AgentQMS/`, `.agentqms/`, `docs/artifacts/`.

2) Reconfigure `.agentqms/`
- Review/update `.agentqms/settings.yaml` and `.agentqms/effective.yaml` (if present) for project name/paths/plugins.
- Check `.agentqms/state/architecture.yaml` and `plugins.yaml`; remove stale references to pruned components.

3) Align knowledge and rules
- Ensure `AgentQMS/knowledge/agent/system.md` rules match this repo (paths, naming, artifact types).
- Decide how to surface agent instructions in project docs/README.

4) Define minimal workflow
- Choose lightweight footprint: artifact creation + validation only; tracking optional.
- Keep demo mode as fallback; plan for “real mode” when AgentQMS present.

5) Wire backend execution
- Point backend tool routes to AgentQMS entrypoints when not in demo mode; keep stubs otherwise.
- Validate working directory/env for `AgentQMS/interface` commands.

6) Testing candidates
- Tool entrypoints: `AgentQMS/interface` Make targets (`make help`, `make validate`, `make compliance`, `make discover`).
- Rules: `AgentQMS/knowledge/agent/artifact_rules.yaml`.
- Tracking CLI (if kept): `AgentQMS/agent_tools/utilities/tracking/cli.py`.
- Remove or stub any pruned scripts still referenced.

7) Document stance & gaps
- Record current limitations (auditor incomplete, no real execution yet) and next steps to enable full audits/validations.

### Outputs
- Updated `.agentqms` config aligned to this repo.
- Backend ready to toggle between demo stubs and real AgentQMS commands (when available).
- Short integration note in docs/README summarizing footprint, requirements, and limits.

### Progress Log
- ✅ Step 1: Confirmed AgentQMS structure, validation script exists
- ✅ Step 1 (pruning): Removed `ocr_experiment.yaml` plugin (OCR-specific, not needed for dashboard)
- ✅ Step 2: Updated `.agentqms/state/architecture.yaml` and `plugins.yaml` with local repo paths
- ✅ Step 2 (plugins): Fixed `audit.yaml` validation error (removed `allowed_categories` field)
- ✅ Step 2 (plugins): Removed all old repo path references from `plugins.yaml`
- ✅ Step 3: Verified `system.md` already references `docs/artifacts/` correctly
- ✅ Step 5: Fixed backend routes project root paths (`../..` instead of `../../../..`)
- ✅ Step 5: Enhanced `tools.py` with fallback to direct script execution if make/uv fails
- ✅ Step 5: Fixed `server.py` workspace root path
- ✅ Step 5: Fixed `tracking.py` import path and added better error handling
- ✅ Step 6: Verified Makefile targets exist (`validate`, `compliance`, `boundary`, `discover`, `status`)
- ✅ Step 6: Confirmed `artifact_rules.yaml` and tracking CLI exist
- ✅ Step 7: Added integration note to README.md
- ✅ **NEW**: Added `/api/v1/stats` endpoint for real system statistics
- ✅ **NEW**: Added `/api/v1/compliance/metrics` endpoint for Strategy Dashboard metrics
- ✅ **NEW**: Wired Strategy Dashboard to fetch real compliance metrics
- ✅ **NEW**: Wired Context Explorer to load real artifacts
- ✅ **NEW**: Enhanced artifacts endpoint with better error handling and fallback search
- ✅ **NEW**: Made ARTIFACTS_ROOT dynamic (checks DEMO_MODE at request time)
- ✅ **NEW**: Fixed all remaining ARTIFACTS_ROOT references to use dynamic function
- ⏳ Step 3: Add agent instructions reference to project docs (optional enhancement)
- ⏳ Step 6: Test actual execution when DEMO_MODE=false (requires testing environment)
- ⚠️ **KNOWN ISSUE**: Artifacts API returns empty - backend needs DEMO_MODE=true set at startup (now checks at request time, but restart recommended)
- 📋 **SESSION HANDOVER**: See `docs/meta/session-handover-2025-12-12.md` for continuation prompt

# Agent Protocols

## 1. Context Health
*   **Monitor Step Count**: You are responsible for tracking your own context usage.
*   **Soft Limit (~120 steps)**: Conclude current logical task. Do not start new major features.
*   **Hard Limit (~150 steps)**: **STOP**. Initiate Session Handover.
    *   Do NOT attempt to "squeeze in" one more task.
    *   Misreporting completion due to context saturation is a critical failure.

## 2. Session Handover
*   **Trigger**: Reaching Hard Limit OR Phase Completion.
*   **Action**:
    1.  Create Handover Artifact: `demo_data/artifacts/handoffs/YYYY-MM-DD_handoff_session-[N].md`.
    2.  Notify User with **Continuation Prompt**.
*   **Continuation Prompt**: Must be self-contained code block.

## 3. Documentation
*   **Source of Truth**: `docs/meta/2025-12-14_roadmap_dms-agentqms.md`.
*   **Artifacts**: Always use `implementation_plan` before Execution.
*   **Validation**: Always verify changes before marking task complete.

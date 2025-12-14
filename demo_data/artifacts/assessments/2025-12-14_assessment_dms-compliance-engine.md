---
type: assessment
title: Assessment of DMS Compliance Engine & Self-Healing
status: review_needed
category: product_strategy
tags: [feature-evaluation, compliance-engine, self-healing]
date: 2025-12-14 19:15 (KST)
---

# Assessment: DMS Compliance Engine & Self-Healing

This document provides a technical deep-dive into the "Compliance Engine" phase of the Documentation Management System (DMS), focusing on implementation strategies for **validation** and **self-healing**.

## 1. Compliance Engine Architecture

**Goal**: Transform the current "demo stub" compliance check into a robust, rule-based validation system.

### Core Concepts

1.  **Rule Definitions**: Rules must be declarative and versionable.
    *   *Example*: "All artifacts of type `implementation_plan` must have a section starting with `## Verification Plan`."
    *   *Format*: YAML or JSON schema.
2.  **Validators**: Python classes that enforce rules.
    *   `SchemaValidator`: Checks Frontmatter fields (type, status, tags).
    *   `ContentValidator`: Checks markdown structure (headers, required sections).
    *   `ProjectValidator`: Checks directory structure and file naming conventions.
3.  **Reporting**: Granular JSON output detailing *which* rule failed, *where* (line number/section), and *severity*.

### Implementation Strategy (Phase 1)

Modify `backend/routes/compliance.py` to use a real validation logic instead of the `compliance_stub.py`.

*   **Logic Location**: `backend/services/compliance/` (new directory).
*   **Tech Stack**:
    *   `Pydantic`: For defining strict artifact schemas.
    *   `Python-Frontmatter`: Already in use, continue for metadata.
    *   `Mistune` or `Marko`: For AST-based markdown parsing (robust content validation).

## 2. Self-Healing Capabilities

**Goal**: Automatically fix compliance violations where deterministic or high-confidence solutions exist.

### Self-Healing Levels

| Level | Description | Mechanism | Example |
| :--- | :--- | :--- | :--- |
| **L1: Deterministic** | Simple syntax/format fixes. | Regex / String Ops | Fixing date format `2025/12/14` -> `2025-12-14`. Adding missing `status: draft`. |
| **L2: Structural** | Missing sections or boilerplate. | Template Injection | Appending a `## Verification Plan` template if missing. |
| **L3: Generative** | Missing *content* or logic. | LLM / Agent | Generating a summary based on file content. Writing a verification plan based on code changes. |

### Proposed "Healer" Architecture

1.  **The "Fixer" Interface**:
    ```python
    class ViolationFixer:
        def can_fix(self, violation: Violation) -> bool: ...
        def fix(self, violation: Violation, dry_run: bool = True) -> FixResult: ...
    ```
2.  **Agentic Integration**:
    *   Use the existing `backend/routes/tools.py` to expose a `heal_document` tool.
    *   The frontend can show a "Fix This" button next to violations.
    *   **L3 Heals** require a "human-in-the-loop" approval flow (Agent drafts -> User reviews -> Save).

## 3. Risks & Challenges

*   **False Positives**: Over-strict validators might flag valid documents. *Mitigation*: Allow "waivers" or `<!-- ignore-compliance -->` comments in markdown.
*   **Content Destruction**: Automated "healing" (especially L2/L3) could overwrite user work. *Mitigation*: STRICT version control (git) before any auto-fix.
*   **Performance**: Parsing hundreds of markdown files ASTs can be slow. *Mitigation*: Cache validation results; only re-validate modified files.

## 4. Next Steps (Implementation Plan)

1.  **Define the Schema**: Create `backend/compliance_rules.yaml` defining the "Gold Standard" for artifacts.
2.  **Build the Validator**: Implement `backend/services/compliance/validator.py` to check against the schema.
3.  **Update API**: Modify `GET /api/v1/compliance/validate` to run the real validator.
4.  **Prototype Self-Healing**: Implement one L1 fixer (e.g., "Fix Date Format").

## 5. Conclusion

Building a **Compliance Engine** is feasible and high-value. Starts with **strict Pydantic validation** (Phase 1) and evolve into **Generative Self-Healing** (Phase 2), with Git versioning being a hard prerequisite for any auto-healing.

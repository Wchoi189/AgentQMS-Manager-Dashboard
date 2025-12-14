---
type: roadmap
title: AgentQMS & DMS Roadmap (2025-2026)
status: active
category: product_strategy
tags: [roadmap, strategy, dms, compliance, ai-integration]
date: 2025-12-14 20:30 (KST)
last_updated: 2025-12-14
---

# AgentQMS & DMS Roadmap

This document outlines the strategic evolution of the content and compliance systems within AgentQMS.

## 🎯 Strategic Vision
To create a **Self-Healing, Self-Organizing Documentation Management System** that serves as the reliable "Source of Truth" for both human developers and AI Agents.

---

## 📅 Phased Roadmap

### ✅ Phase 0: Foundation (Current Status)
*   Basic `artifacts` CRUD API.
*   Dashboard for viewing `implementation_plans`, `assessments`, etc.
*   Basic Frontmatter parsing.

### 🚧 Phase 1: Compliance Engine (Immediate Focus)
**Goal**: Enforce strict data contracts on documentation.
*   **Action**: Replace demo stubs with `Pydantic` validation.
*   **Deliverable**: `/api/v1/compliance/validate` endpoint supporting strict checks.
*   **Artifacts**: `backend/services/compliance/` (Validator Service), `rules.yaml` (Gold Standard Schema).

### 📋 Phase 2: Compliance Visualization (Q1 2026)
**Goal**: Make compliance visible and actionable.
*   **Action**: Build Frontend Dashboard for Compliance.
*   **Features**:
    *   "Health Score" per artifact.
    *   Visual indicators for missing fields (e.g., "Verification Plan Missing").
    *   "Fix This" buttons for Phase 3 readiness.

### 🩹 Phase 3: Self-Healing & Automation (Q1-Q2 2026)
**Goal**: Reduce toil by automating simple fixes.
*   **L1 (Deterministic)**: Auto-fix date formats, status fields, and filenames.
*   **L2 (Structural)**: Inject missing boilerplate (templates) via "Scaffold Tool".
*   **Requirement**: Git integration to ensure all auto-fixes are version-controlled and reversible.

### 🧠 Phase 4: Context & Search (Q2 2026)
**Goal**: Make the DMS a queryable Knowledge Base.
*   **Action**: Implement Vector Search or Advanced Keyword Search over artifacts.
*   **Features**:
    *   "Find all plans related to Authentication".
    *   "Show me the architecture decision for X".

### 🤖 Phase 5: Generative Copilot (Q3 2026)
**Goal**: Active AI participation in management.
*   **Action**: Integrate LLMs (Gemini) with Phase 4 context.
*   **Capabilities**:
    *   **L3 Self-Healing**: "Write a verification plan for this code change."
    *   **Chat**: "What is the status of the DMS project?" (Queries the tracking DB).
    *   **Agentic Actions**: "Create a new plan for feature Y."

---

## ⚠️ Key Dependencies
1.  **Strict Data Contracts** (Phase 1) are required before **Automation** (Phase 3).
2.  **Git Integration** is required before **Self-Healing** to prevent data loss.
3.  **Context/Search** (Phase 4) is required before a **Useful Copilot** (Phase 5).

## 📊 Success Metrics
*   **Compliance Score**: % of artifacts meeting `rules.yaml`.
*   **Toil Reduction**: Time saved by auto-formatting and templating.
*   **Agent Reliability**: Success rate of AI tools interacting with artifacts (depends on strict schema).

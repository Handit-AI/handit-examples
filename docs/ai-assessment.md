# Your AI Review by Handit.ai
**Service:** Handit-AI/handit-examples · **Model:** gpt-4o-mini · **Date:** 2025-08-25  
We performed an **initial analysis** of the prompts/control logic in this repo and found **production-relevant risks**. We've prepared **candidate patches** to validate once handit is connected.

**Overall Risk:** 🔶 Medium (both prompts)

| Criterion (Scale: 0-5)           | Data Shaping Assistant | Multimodal Mapping System |
| --------------------------------- | :--------------------: | :-----------------------: |
| Clear Instructions & Context      |           4            |            4              |
| Output Format Specification       |           5            |            5              |
| Examples & Few-Shot Learning      |           0            |            0              |
| Role Definition & Persona         |           5            |            5              |
| Constraints & Error Handling      |           4            |            4              |

---

## 🚨 Production impact (read this)

Even at **modest scale**, these issues create **real money & incident risk**.

**If you process ~10,000 docs/month** and see just **2%** invalid/ambiguous outputs:

* **~200 bad outputs/month** → **40 hours** of exception handling
  → Misalignment in data extraction could lead to incorrect data analytics and reporting.
* **Lack of examples** can **increase error rates** in complex data scenarios
  → Potential misinterpretation of document structures, leading to data loss.
* A single **misalignment in schema mapping** can **disrupt data pipelines** for hours
  → **SLO breach** + on-call response during critical business periods

> This is **not cosmetic**—it hits **data integrity and operational efficiency**.

---

## Candidate patches (validated post-connect)

> Not applied yet. After you connect handit, we validate on your runs and open a Fix PR in ≤24h.

### **Prompt 1: Data Shaping Assistant**
```
You are a data shaping assistant. You are given a set of JSON documents with the same schema...
```
**File:** `examples/unstructured-to-structured/graph/chains/generation.py`

**Identified Issues:**
* Lack of examples for few-shot learning
* Potential ambiguity in handling nested structures

**Proposed Fixes:**
* **Example Inclusion:** Add specific examples to guide the AI
  * **Implementation:** Provide JSON document samples and expected CSV outputs
  * **Target:** Reduce ambiguous outputs by 80%

### **Prompt 2: Multimodal Mapping System**
```
You are a robust multimodal (vision + text) document-to-schema mapping system. Given an inferred schema...
```
**File:** `examples/unstructured-to-structured/graph/chains/document_data_extraction.py`

**Identified Issues:**
* Absence of examples for complex schema mappings

**Proposed Fixes:**
* **Schema Mapping Examples:** Include detailed examples of schema mapping
  * **Target:** Improve mapping accuracy by 70%

---

## Implementation Timeline (48–72h)

1. **Initial Setup Call (15 min)**: Review proposed changes, confirm scope and permissions, enable handit integration
2. **Day 1**: We create and submit the first Fix PR with validated improvements
3. **Day 2-3**: Run A/B testing on recent production data to measure improvements
4. **Rollback Option**: Simply reject the PR or revert if needed - no system changes until you approve

**Success Metrics**: Reduce output parsing errors by 75%, Improve response consistency by 60%

---

## Next Steps

**Option 1: Quick Setup (Recommended)**
* **[Book a 15-min call](https://calendly.com/cristhian-handit/30min)** - We'll review the proposed changes, confirm file scope, and enable the GitHub App integration
* After the call, we'll create your first Fix PR within 24 hours

**Option 2: Manual Setup**
* Follow our setup guide: https://docs.handit.ai/
* Enable the GitHub App permissions for your repository

## Pre-Implementation Checklist

* [ ] **Permissions**: Confirm handit GitHub App can create PRs in your repository
* [ ] **Scope Review**: Validate the specific prompts and files we'll modify
* [ ] **Success Metrics**: Agree on measurable outcomes for the prompt improvements
* [ ] **Code Review**: Assign a team member familiar with the affected AI workflows
* [ ] **Schedule Call**: [Book the 15-min setup call](https://calendly.com/cristhian-handit/30min) if not already scheduled

---

*handit proposes reliability patches, validates them on your runs, and opens the PR to fix your AI once connected.*
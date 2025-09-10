# Your AI Review by Handit.ai
**Service:** Multi-Currency Invoice & Document Data Extraction · **Model:** Optional · **Date:** 2025-09-10  
We performed an **initial analysis** of the prompts/control logic in this repo and found **production-relevant risks**. We've prepared **candidate patches** to validate once handit is connected.

**Overall Risk:** 🔶 Medium (both prompts)

| Criterion (Scale: 0-5)           | Multi-Currency Invoice | Document Data Extraction |
| --------------------------------- | :--------------------: | :----------------------: |
| Clear Instructions & Context      |           4            |            4             |
| Output Format Specification       |           5            |            5             |
| Examples & Few-Shot Learning      |           0            |            0             |
| Role Definition & Persona         |           5            |            5             |
| Constraints & Error Handling      |           3            |            4             |

---

## 🚨 Production impact (read this)

Even at **modest scale**, these issues create **real money & incident risk**.

**If you process ~10,000 docs/month** and see just **2%** invalid/ambiguous outputs:

* **~200 bad outputs/month** → **40 hours** of exception handling
  → Increased operational costs due to manual corrections and potential client dissatisfaction
* **Lack of examples** can lead to inconsistent extraction results
  → Reduced accuracy in data extraction impacting financial reporting
* A single **failure to handle document-specific nuances** can **disrupt automated workflows** for hours
  → **SLO breach** + on-call response during critical business periods

This is **not cosmetic**—it hits **financial document processing and client trust**.

---

## Candidate patches (validated post-connect)

> Not applied yet. After you connect handit, we validate on your runs and open a Fix PR in ≤24h.

### **Prompt 1: Multi-Currency Invoice Extraction**
```
You are an expert OCR and data extraction specialist with years of experience in processing financial documents. Your expertise includes:...
```
**File:** `examples/multi-currency-invoice/services/ExtractionService.js`

**Identified Issues:**
* Lack of examples for few-shot learning
* Limited constraints on error handling

**Proposed Fixes:**
* **Example Integration:** Add relevant examples to guide extraction
  * **Implementation:** Include sample documents with expected JSON outputs
  * **Target:** Improve extraction accuracy by 70%
* **Enhanced Error Handling:** Define specific error scenarios and responses
  * **Implementation:** Specify error handling for common document anomalies
  * **Target:** Reduce error-related disruptions by 50%

### **Prompt 2: Document Data Extraction**
```
You are a robust multimodal (vision + text) document-to-schema mapping system. Given an inferred schema and a document (image/pdf/text), analyze layout and visual structure first, then map fields strictly to the provided schema...
```
**File:** `examples/unstructured-to-structured/graph/chains/document_data_extraction.py`

**Identified Issues:**
* Absence of examples for schema mapping
* Potential ambiguity in handling multilingual variants

**Proposed Fixes:**
* **Schema Mapping Examples:** Provide examples for schema mapping
  * **Implementation:** Include sample mappings with explanations
  * **Target:** Enhance mapping precision by 60%
* **Multilingual Handling:** Clarify multilingual processing steps
  * **Target:** Improve multilingual accuracy by 40%

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
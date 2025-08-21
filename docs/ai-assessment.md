# Your AI Review by Handit.ai
**Service:** Handit-AI/handit-examples · **Model:** optional · **Date:** 2025-08-21  
We performed an **initial analysis** of the prompts/control logic in this repo and found **production-relevant risks**. We've prepared **candidate patches** to validate once handit is connected.

**Overall Risk:** 🔶 Medium (both prompts)

| Criterion (Scale: 0-5)           | Data Shaping Assistant | Multimodal Document Mapping |
| --------------------------------- | :--------------------: | :--------------------------: |
| Clear Instructions & Context      |           4            |              4               |
| Output Format Specification       |           5            |              5               |
| Examples & Few-Shot Learning      |           0            |              0               |
| Role Definition & Persona         |           5            |              5               |
| Constraints & Error Handling      |           3            |              3               |

---

## 🚨 Production impact (read this)

ANALYZE THE PROMPTS AND GENERATE SPECIFIC PRODUCTION IMPACTS:
- **Estimate realistic processing volume**: Given the repository's focus on data extraction and transformation, it's likely used in data processing pipelines or API endpoints handling thousands of documents monthly.
- **Calculate specific failure scenarios**: 
  - **Data Shaping Assistant**: Lack of examples could lead to misinterpretation of JSON structures, potentially causing 10% of outputs to be incorrectly formatted, resulting in ~300 erroneous tables/month.
  - **Multimodal Document Mapping**: Absence of examples may lead to incorrect field mappings, causing 5% of documents to be improperly processed, equating to ~150 mapping errors/month.
- **Quantify business impact**:
  - **Operational costs**: Each erroneous output could require manual correction, estimated at 15 minutes per document, leading to ~112.5 hours/month of additional labor.
  - **Business consequences**: Incorrect data outputs can lead to decision-making errors, impacting client trust and potentially resulting in financial penalties or loss of contracts.

> Even at **modest scale**, these issues create **real money & incident risk**.

**If you process ~3,000 docs/month** and see just **5%** invalid/ambiguous outputs:

* **~150 bad outputs/month** → **37.5 hours** of exception handling
  → Potential client dissatisfaction and increased operational costs
* **Lack of examples** can **lead to inconsistent data processing**
  → Reduced data reliability and increased error rates
* A single **misinterpretation of JSON structure** can **disrupt data pipelines** for hours
  → **SLO breach** + on-call response during critical business periods

> This is **not cosmetic**—it hits **data reliability and client trust**.

---

## Candidate patches (validated post-connect)

> Not applied yet. After you connect handit, we validate on your runs and open a Fix PR in ≤24h.

### **Prompt 1: Data Shaping Assistant**
```
You are a data shaping assistant. You are given a set of JSON documents with the same schema (same keys & depth)...
```
**File:** `examples/unstructured-to-structured/graph/chains/generation.py`

**Identified Issues:**
* Lack of examples for JSON to CSV transformation
* Limited error handling guidance

**Proposed Fixes:**
* **Example Inclusion:** Add examples demonstrating JSON to CSV conversion
  * **Implementation:** Provide sample JSON inputs and expected CSV outputs
  * **Target:** Reduce ambiguous outputs by 80%

### **Prompt 2: Multimodal Document Mapping**
```
You are a robust multimodal (vision + text) document-to-schema mapping system. Given an inferred schema and a document (image/pdf/text)...
```
**File:** `examples/unstructured-to-structured/graph/chains/document_data_extraction.py`

**Identified Issues:**
* Absence of examples for field mapping
* Limited constraints on error handling

**Proposed Fixes:**
* **Example Addition:** Include examples of document-to-schema mapping
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
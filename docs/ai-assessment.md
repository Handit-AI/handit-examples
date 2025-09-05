**Service:** Document Data Extraction · **Model:** gpt-4o-mini · **Date:** 2025-09-05  
We performed an **initial analysis** of the prompts/control logic in this repo and found **production-relevant risks**. We've prepared **candidate patches** to validate once handit is connected.

**Overall Risk:** 🔶 Medium (both prompts)

| Criterion                 | System Prompt | User Prompt |
| ------------------------- | :-----------: | :---------: |
| Context & Rationale (0–5) |       4       |      3      |
| Format / Output Contract  |       5       |      5      |
| Examples & Edge Cases     |       2       |      2      |
| Determinism & Guardrails  |       3       |      3      |
| Testability               |       3       |      3      |

---

## 🚨 Production impact (read this)

> Even at **modest scale**, these issues create **real money & incident risk**.

**If you process ~10,000 docs/month** and see just **2%** invalid/ambiguous outputs:

* **~200 bad docs/month** → **67 ops hours** of exception handling (≈20–40 min each)
  → Increased operational costs and potential delays in processing
* **Inconsistent data extraction** can **lead to incorrect business decisions**
  → Affects stakeholders relying on accurate data
* A single **schema mismatch** can **halt processing** for hours
  → **SLO breach** + on-call fire drill during critical periods
* **Incorrectly formatted outputs** inside JSON fields lead to **silent consumer errors**
  → Failures discovered **days later** in audit processes

> Bottom line: this is **not cosmetic**—it hits **data integrity and operational efficiency**.

---

## Candidate patches (validated post-connect)

> Not applied yet. After you connect handit, we validate on your runs and **open Fix PR #1 in ≤24h**.

**A) Enhanced Contextual Guidance**

* Improve context and rationale by embedding more detailed instructions and examples
* Implementation approach: Integrate few-shot examples and chain-of-thought reasoning
* **Target:** **Reduce ambiguous outputs by 50%**

**B) Edge Case Handling**

* Introduce specific edge case scenarios to test robustness
* Implementation details: Add test cases for multilingual and complex document layouts
* **Target:** Increase accuracy in edge cases by 30%

**C) Determinism and Guardrails**

* Strengthen determinism by specifying more guardrails and constraints
* **Target:** Ensure consistent outputs across similar inputs

---

## Rollout (48–72h)

1. **15-min Fix Review** (on the call): confirm flows & permissions so handit starts fixing your AI
2. **T+24h:** we **open Fix PR #1** with the validated patch
3. **T+48–72h:** quick A/B on recent runs; confirm lift; optionally ship **Fix PR #2**
4. **Rollback:** toggle `HANDIT_PATCH=off` (config) or revert PR

**Metrics we track:** Accuracy of data extraction, reduction in exception handling time, consistency of outputs

---

## How to proceed

* Book the 15-min call; we walk scopes & exact files we'll touch, then enable the App (My calendly is https://calendly.com/cristhian-handit/30min)
* Manual setup https://docs.handit.ai/
* We proceed to **Fix PR #1 within 24h** of enablement

## Reviewer checklist

* [ ] Confirm handit can open PRs via the GitHub App (or temporary permission)
* [ ] Select target flows (document processing flows)
* [ ] Agree success metrics (accuracy, consistency, operational efficiency)
* [ ] Add a reviewer who owns downstream consumers of these fields
* [ ] **[Book the 15-min Fix Review](https://calendly.com/cristhian-handit/30min)** if not scheduled

---

## Notes from analysis (context)

* **System Prompt:** Provides a robust framework for document-to-schema mapping but lacks examples and edge case handling.
* **User Prompt:** Reinforces schema adherence but could benefit from enhanced contextual guidance and determinism.

---

*handit proposes reliability patches, validates them on your runs, and opens the PR to fix your AI once connected.*
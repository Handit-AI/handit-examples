**Service:** Document Data Extraction · **Model:** gpt-4o-mini · **Date:** 2025-09-05  
We performed an **initial analysis** of the prompts/control logic in this repo and found **production-relevant risks**. We've prepared **candidate patches** to validate once handit is connected.

**Overall Risk:** 🔶 Medium (both prompts)

| Criterion                 | System Prompt | User Prompt |
| ------------------------- | :-----------: | :---------: |
| Context & Rationale (0–5) |       4       |      3      |
| Format / Output Contract  |       5       |      4      |
| Examples & Edge Cases     |       2       |      2      |
| Determinism & Guardrails  |       3       |      3      |
| Testability               |       4       |      3      |

---

## 🚨 Production impact (read this)

> Even at **modest scale**, these issues create **real money & incident risk**.

**If you process ~10,000 docs/month** and see just **2%** invalid/ambiguous outputs:

* **~200 bad docs/month** → **67 ops hours** of exception handling (≈20–40 min each)
  → Increased operational costs and potential delays in processing
* **Data quality issues** can lead to **incorrect data mapping**
  → Affecting decision-making processes and stakeholder trust
* A single **schema mismatch** can **disrupt automated workflows** for hours
  → **SLO breach** + on-call fire drill during critical periods
* **Incorrect field mappings** inside JSON fields lead to **silent consumer errors**
  → Failures discovered **days later** in audit processes

> Bottom line: this is **not cosmetic**—it hits **data integrity and operational efficiency**.

---

## Candidate patches (validated post-connect)

> Not applied yet. After you connect handit, we validate on your runs and **open Fix PR #1 in ≤24h**.

**A) Enhanced Schema Validation**

* Implement stricter schema validation checks before processing
* Ensure all fields are correctly mapped and validated against the schema
* **Target:** **Reduce invalid mappings by 50%**

**B) Example-Driven Prompting**

* Introduce few-shot examples to guide the AI in mapping complex fields
* Provide clear examples of edge cases and expected outputs
* **Target:** Improve accuracy in edge case handling by 30%

**C) Improved Confidence Scoring**

* Refine the confidence scoring mechanism to better reflect mapping accuracy
* Use historical data to calibrate confidence thresholds
* **Target:** Increase confidence score reliability by 20%

---

## Rollout (48–72h)

1. **15-min Fix Review** (on the call): confirm flows & permissions so handit starts fixing your AI
2. **T+24h:** we **open Fix PR #1** with the validated patch
3. **T+48–72h:** quick A/B on recent runs; confirm lift; optionally ship **Fix PR #2**
4. **Rollback:** toggle `HANDIT_PATCH=off` (config) or revert PR

**Metrics we track:** Mapping accuracy, error rate, processing time

---

## How to proceed

* Book the 15-min call; we walk scopes & exact files we'll touch, then enable the App (My calendly is https://calendly.com/cristhian-handit/30min)
* Manual setup https://docs.handit.ai/
* We proceed to **Fix PR #1 within 24h** of enablement

## Reviewer checklist

* [ ] Confirm handit can open PRs via the GitHub App (or temporary permission)
* [ ] Select target flows (document processing and mapping)
* [ ] Agree success metrics (accuracy, error rate)
* [ ] Add a reviewer who owns downstream consumers of these fields
* [ ] **[Book the 15-min Fix Review](https://calendly.com/cristhian-handit/30min)** if not scheduled

---

## Notes from analysis (context)

* **System Prompt:** The prompt effectively assigns a role and specifies output format, but lacks examples for edge cases.
* **User Prompt:** While it maintains format consistency, it could benefit from more explicit context and rationale.

---

*handit proposes reliability patches, validates them on your runs, and opens the PR to fix your AI once connected.*
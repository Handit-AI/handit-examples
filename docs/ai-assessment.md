# Your AI Review by Handit.ai
**Service:** Data Shaping & Mapping · **Model:** Optional · **Date:** 2025-08-20  
We performed an **initial analysis** of the prompts/control logic in this repo and found **production-relevant risks**. We've prepared **candidate patches** to validate once handit is connected.

**Overall Risk:** 🔶 Medium (both prompts)

| Criterion                 | Data Shaping Assistant | Multimodal Mapping System |
| ------------------------- | :--------------------: | :-----------------------: |
| Context & Rationale (0–5) |           4            |            4              |
| Format / Output Contract  |           5            |            5              |
| Examples & Edge Cases     |           3            |            3              |
| Determinism & Guardrails  |           4            |            4              |
| Testability               |           3            |            3              |

---

## 🚨 Production impact (read this)

> Even at **modest scale**, these issues create **real money & incident risk**.

**If you process ~10,000 docs/month** and see just **2%** invalid/ambiguous outputs:

* **~200 bad docs/month** → **67 ops hours** of exception handling (≈20–40 min each)
  → Increased operational costs and potential delays in data processing
* **Data quality issues** can **lead to incorrect business insights**
  → Misguided decision-making impacting strategic planning
* A single **schema mapping failure** can **halt data pipelines** for hours
  → **SLO breach** + on-call fire drill during critical periods
* **Incorrect data extraction** inside structured fields leads to **silent consumer errors**
  → Failures discovered **days later** in audit processes

> Bottom line: this is **not cosmetic**—it hits **data integrity and operational efficiency**.

---

## Candidate patches (validated post-connect)

> Not applied yet. After you connect handit, we validate on your runs and open a Fix PR in ≤24h.

**A) Enhanced Edge Case Handling**

* Introduce more comprehensive examples and edge case scenarios in prompts
* Implementation approach: Add few-shot examples to guide the model
* **Target:** **Reduce ambiguous outputs by 50%**

**B) Improved Contextual Instructions**

* Refine prompts to include more explicit context and rationale
* Implementation details: Embed additional background information and reasoning steps
* **Target:** Increase model alignment with desired outcomes

**C) Robust Testability Framework**

* Develop a framework for testing prompt outputs against expected results
* **Target:** Ensure consistent and reliable performance across varied inputs

---

## Rollout (48–72h)

1. **15-min Fix Review** (on the call): confirm flows & permissions so handit starts fixing your AI
2. **T+24h:** we **open Fix PR #1** with the validated patch
3. **T+48–72h:** quick A/B on recent runs; confirm lift.
4. **Rollback:** revert or do not accept the PR

**Metrics we track:** Output accuracy, error rate reduction, processing efficiency

---

## How to proceed

* Book the 15-min call; we walk scopes & exact files we'll touch, then enable the App (My calendly is https://calendly.com/cristhian-handit/30min)
* Manual setup https://docs.handit.ai/
* We proceed to **Fix PR #1 within 24h** of enablement

## Reviewer checklist

* [ ] Confirm handit can open PRs via the GitHub App (or temporary permission)
* [ ] Select target flows (Data Shaping, Multimodal Mapping)
* [ ] Agree success metrics (Output accuracy, error rate reduction)
* [ ] Add a reviewer who owns downstream consumers of these fields
* [ ] **[Book the 15-min Fix Review](https://calendly.com/cristhian-handit/30min)** if not scheduled

---

## Notes from analysis (context)

* **Data Shaping Assistant:** The prompt provides clear instructions and a structured output format, but lacks comprehensive examples for edge cases.
* **Multimodal Mapping System:** The prompt effectively uses schema contracts and visual cues but could benefit from more explicit reasoning steps and testability measures.

---

*handit proposes reliability patches, validates them on your runs, and opens the PR to fix your AI once connected.*
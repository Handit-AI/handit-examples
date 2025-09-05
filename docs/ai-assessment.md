**Service:** Document Data Extraction · **Model:** gpt-4o-mini · **Date:** 2025-09-05  
We performed an **initial analysis** of the prompts/control logic in this repo and found **production-relevant risks**. We've prepared **candidate patches** to validate once handit is connected.

**Overall Risk:** 🔶 Medium (both prompts)

| Criterion                 | System Prompt | User Prompt |
| ------------------------- | :-----------: | :---------: |
| Context & Rationale (0–5) |       4       |      3      |
| Format / Output Contract  |       5       |      5      |
| Examples & Edge Cases     |       2       |      2      |
| Determinism & Guardrails  |       4       |      3      |
| Testability               |       3       |      3      |

---

## 🚨 Production impact (read this)

> Even at **modest scale**, these issues create **real money & incident risk**.

**If you process ~10,000 docs/month** and see just **2%** invalid/ambiguous outputs:

* **~200 bad docs/month** → **67 ops hours** of exception handling (≈20 min each)
  → Increased operational costs and potential delays in processing
* **Inaccurate data extraction** can **lead to compliance issues**
  → Potential fines and reputational damage
* A single **schema mismatch** can **halt processing** for hours
  → **SLO breach** + on-call fire drill during critical periods
* **Incorrectly formatted outputs** inside JSON fields leads to **silent consumer errors**
  → failures discovered **days later** in audit processes

> Bottom line: this is **not cosmetic**—it hits **operational efficiency and compliance**.

---

## Candidate patches (validated post-connect)

> Not applied yet. After you connect handit, we validate on your runs and **open Fix PR #1 in ≤24h**.

**A) Enhanced Example Inclusion**

* Add few-shot examples to guide the model in handling edge cases
* Implementation approach: Integrate examples directly into prompts
* **Target:** **Reduce error rate by 30%**

**B) Contextual Reinforcement**

* Reinforce critical instructions throughout the prompt
* Implementation details: Repeat key instructions at the start and end of prompts
* **Target:** Improve consistency and accuracy by 20%

**C) Edge Case Handling**

* Develop specific sub-prompts for known edge cases
* **Target:** Increase robustness against uncommon document formats

---

## Rollout (48–72h)

1. **15-min Fix Review** (on the call): confirm flows & permissions so handit starts fixing your AI
2. **T+24h:** we **open Fix PR #1** with the validated patch
3. **T+48–72h:** quick A/B on recent runs; confirm lift; optionally ship **Fix PR #2**
4. **Rollback:** toggle `HANDIT_PATCH=off` (config) or revert PR

**Metrics we track:** Error rate reduction, processing time, compliance incidents

---

## How to proceed

* Book the 15-min call; we walk scopes & exact files we'll touch, then enable the App (My calendly is https://calendly.com/cristhian-handit/30min)
* Manual setup https://docs.handit.ai/
* We proceed to **Fix PR #1 within 24h** of enablement

## Reviewer checklist

* [ ] Confirm handit can open PRs via the GitHub App (or temporary permission)
* [ ] Select target flows (document processing flows)
* [ ] Agree success metrics (error rate, processing time)
* [ ] Add a reviewer who owns downstream consumers of these fields
* [ ] **[Book the 15-min Fix Review](https://calendly.com/cristhian-handit/30min)** if not scheduled

---

## Notes from analysis (context)

* **System Prompt:** Strong in format control but lacks examples for edge cases, which could improve robustness.
* **User Prompt:** Clear output contract but needs more context and rationale to guide the model effectively.

---

*handit proposes reliability patches, validates them on your runs, and opens the PR to fix your AI once connected.*
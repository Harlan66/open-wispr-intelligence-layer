# open-wispr-hybrid-review

A local-first, hybrid review pipeline for `open-wispr` transcripts.

This repo packages a practical method for improving voice-dictation quality **without** turning your correction loop into a fragile, fully-cloud workflow.

## What problem this solves

`open-wispr` can collect rich local transcript history, but a naive “auto-learn from edits” loop is dangerous:

- some edits are true local corrections
- some are rewrites
- some include pasted URLs or merged context
- some are style-only changes that should not pollute a glossary

This project uses a **three-stage pipeline**:

1. **Local transcript capture** via `open-wispr`
2. **Local nightly coarse review** for stability and contamination filtering
3. **Optional remote semantic review** for hard borderline cases

The design goal is:

> **stable by default, smarter where it matters, silent in daily use**

---

## Current method

### Stage 1 — local review (always on)

A local nightly script:

- reads `transcripts.jsonl`
- looks only at the last 24 hours
- classifies items conservatively into:
  - `accepted`
  - `local_correction`
  - `rewrite`
  - `style_edit`
  - `unclear`
- rejects obvious contamination patterns:
  - URL injection
  - pasted context
  - long semantic rewrites
  - ambiguous boundary cases
- writes:
  - `nightly-review-latest.md`
  - `review_queue.jsonl`
  - `remote-review-input.jsonl`

Why local first:

- no nightly dependency on remote model availability
- no chat spam
- cheap and predictable
- safer against accidental overfitting

### Stage 2 — remote semantic review (optional / recommended)

Instead of sending **all** transcript samples to an LLM, only send the small cleaned subset produced by the local stage.

This keeps the model focused on the difficult decisions:

- is this a real correction or a rewrite?
- is this technical-term normalization or semantic drift?
- is this safe enough to auto-promote?

This is the core of the **hybrid** approach.

### Stage 3 — recovery after outages

If a remote review task fails because of:

- transient upstream API outages
- temporary network failure
- scheduler/provider instability

this repo includes a local retry watcher that can re-trigger review when connectivity returns.

That means transient failures are treated as:

> **recoverable scheduling problems, not special-case disasters**

---

## Repository layout

```text
.
├── README.md
├── LICENSE
├── scripts/
│   ├── openwispr_nightly_review.py
│   └── network_recovery_retry.py
├── config/
│   └── network_recovery_retry.example.json
├── examples/
│   └── launchd/
│       ├── com.example.open-wispr-nightly-review.plist
│       └── com.example.network-recovery-retry.plist
└── docs/
    └── assets/
```

---

## Key properties

### Advantages

- **Local-first stability**
- **Silent operation**
- **Reduced cloud dependence**
- **Cleaner candidate pool for semantic review**
- **Better contamination control than naive auto-learning**
- **Recovery-friendly when remote review is temporarily unavailable**

### Trade-offs

- more moving parts than a pure local script
- more conservative than a fully automatic “learn everything” loop
- remote semantic review still needs careful writeback rules
- strong observability is necessary to avoid invisible failure modes

---

## Recommended deployment pattern

### Good default

- Local nightly coarse review runs every day
- Remote semantic review consumes only `remote-review-input.jsonl`
- Automatic writeback is limited to ultra-safe corrections
- Retry watcher re-runs remote review when network recovers

### Bad default

- Send all transcripts to a remote model every night
- Treat all edits as candidate corrections
- Auto-write style rewrites into the dictionary
- Fail permanently on transient provider outages

---

## Intended users

This is a good fit if you want:

- local dictation with technical vocabulary
- mixed Chinese/English usage
- silent nightly maintenance
- gradual quality improvement
- strong anti-contamination bias

---

## Logo

A generated logo can be placed in `docs/assets/` and referenced from this README once committed.

---

## License

MIT

#huanyuan

# open-wispr-intelligence-layer

A local-first intelligence layer that makes local speech transcription feel **smarter**, not just more private.

## What this project is actually about

This project is **not mainly about review workflows**.

Its real focus is:

> how to solve the problem that **pure local transcription is often not intelligent enough**

Local ASR / dictation systems such as `open-wispr` are great at:

- low latency
- privacy
- local control
- predictable cost

But they are often weak at:

- technical term normalization
- mixed Chinese / English correction
- distinguishing true corrections from rewrites
- learning safely from real edits without contaminating the dictionary
- recovering automatically when the semantic review layer is temporarily unavailable

This repo documents a practical architecture for fixing that gap.

---

## Core idea

The right goal is **not**:

- pure local rules only
- or fully cloud-dependent post-processing

The right goal is:

> **a stable, local-first transcription system with a lightweight intelligence layer on top**

In other words:

- keep the main transcription path local
- use local logic for bulk filtering and safety
- use a stronger agent only for a small number of hard decisions
- keep the system silent, automatic, and resilient

---

## The architecture

### 1. Local transcription stays primary

`open-wispr` continues to do the main dictation/transcription work locally.

This preserves:

- speed
- privacy
- low friction
- day-to-day reliability

### 2. Local intelligence preprocessing

A nightly local script reviews the last 24 hours of transcript/edit samples and does the cheap, deterministic work:

- parse transcript history
- classify samples conservatively
- reject obvious contamination
- prepare small, clean candidate sets
- write local artifacts for observability and recovery

This stage is designed to be:

- stable
- cheap
- silent
- anti-fragile

### 3. Remote semantic arbitration for hard cases

Pure local logic is not enough for the difficult cases.

Examples:

- technical-term normalization vs semantic rewrite
- context merge vs true correction
- mixed-language phrase cleanup
- borderline phrase-level edits

So instead of sending *all* transcripts to a model, this design sends only a **small, filtered candidate set** to an agent.

That means the agent is used for:

- semantic judgment
- ambiguity resolution
- safe promotion decisions

—not for bulk nightly processing.

### 4. Silent automatic improvement

The target user experience is:

- no manual babysitting
- no chat spam
- no constant operator intervention
- gradual quality improvement in the background

So the long-term goal is an **automatic, low-risk writeback path** for ultra-safe corrections, with strong filtering and recovery guards.

### 5. Automatic retry after transient failures

Provider outages, network instability, or scheduler hiccups should be treated as **recoverable infrastructure conditions**, not special disasters.

So this method includes a local retry watcher that can re-trigger semantic review once the network recovers.

---

## Why this matters

Many local transcription systems fail in one of two ways:

### Failure mode A: too dumb

Everything stays local, but the system never becomes meaningfully better at:

- your terminology
- your bilingual habits
- your app-specific writing style

### Failure mode B: too fragile

Everything gets shipped to a cloud model every night, and the system becomes:

- expensive
- brittle
- noisy
- dependent on upstream availability

This project tries to avoid both.

---

## Design principles

### Local-first
The primary path should still work even if the network is bad.

### Intelligence where it matters
Use stronger semantic reasoning only on difficult, high-value samples.

### Anti-contamination
Prefer missing a candidate over teaching the system the wrong thing.

### Silent operation
Nightly maintenance should not turn into a chat workflow.

### Recoverable by default
Transient provider failures should automatically retry later.

---

## Current reference implementation

The current implementation in this repository includes:

- a local nightly transcript review script
- a network-recovery retry watcher
- launchd examples for macOS deployment
- configuration examples for retry-managed remote review

Repository layout:

```text
.
├── README.md
├── LICENSE
├── config/
│   └── network_recovery_retry.example.json
├── examples/
│   └── launchd/
│       ├── com.example.open-wispr-nightly-review.plist
│       └── com.example.network-recovery-retry.plist
└── scripts/
    ├── openwispr_nightly_review.py
    └── network_recovery_retry.py
```

---

## What this repo is useful for

This repo is useful if you want to build a transcription system that is:

- local-first
- smarter than raw local ASR
- safer than naive auto-learning
- quieter than manual review workflows
- more stable than fully cloud-dependent nightly pipelines

---

## Short summary

This project is best understood as:

> **an intelligence layer for local transcription systems**

`open-wispr` is the immediate reference case, but the method generalizes to other local dictation / transcription tools.

---

## License

MIT

#huanyuan

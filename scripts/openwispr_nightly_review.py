#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

URL_RE = re.compile(r"https?://\S+")
WS_RE = re.compile(r"\s+")
PUNCT_RE = re.compile(r"[\s,，.。!！?？:：;；\"'“”‘’`~·…\-—_/\\()（）\[\]【】{}<>《》]+")


@dataclass
class Sample:
    ts: datetime
    raw: str
    observed: str
    edited: str
    app_name: str
    app_bundle: str
    accepted_without_edit: bool


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def normalize_ws(text: str) -> str:
    return WS_RE.sub(" ", text.strip())


def normalize_loose(text: str) -> str:
    text = normalize_ws(text).lower()
    return PUNCT_RE.sub("", text)


def is_style_only(raw: str, obs: str) -> bool:
    raw_n = normalize_loose(raw)
    obs_n = normalize_loose(obs)
    return bool(raw_n and obs_n and raw_n == obs_n and normalize_ws(raw) != normalize_ws(obs))


def has_structural_injection(obs: str) -> bool:
    return bool(URL_RE.search(obs) or "\n\n" in obs or obs.count("\n") >= 2)


def classify(sample: Sample) -> tuple[str, float, str]:
    raw = normalize_ws(sample.raw)
    obs = normalize_ws(sample.observed or sample.edited)

    if sample.accepted_without_edit:
        return "accepted", 1.0, "accepted_without_edit=true"
    if not raw or not obs:
        return "unclear", 0.2, "missing_text"
    if raw == obs:
        return "accepted", 0.95, "raw_equals_observed"
    if is_style_only(raw, obs):
        return "style_edit", 0.92, "punctuation_or_spacing_only"
    if has_structural_injection(obs):
        if raw and raw in obs and len(obs) > len(raw) * 1.2:
            return "rewrite", 0.9, "structural_injection_or_context_merge"
        return "unclear", 0.65, "structural_injection"

    ratio = SequenceMatcher(None, raw, obs).ratio()
    len_ratio = max(len(raw), len(obs)) / max(1, min(len(raw), len(obs)))

    if ratio >= 0.9 and len_ratio <= 1.2:
        return "local_correction", 0.9, f"high_similarity ratio={ratio:.3f}"
    if ratio >= 0.78 and len_ratio <= 1.35:
        return "style_edit", 0.72, f"medium_similarity ratio={ratio:.3f}"
    if ratio <= 0.6 or len_ratio >= 1.5:
        return "rewrite", 0.82, f"low_similarity ratio={ratio:.3f} len_ratio={len_ratio:.2f}"
    return "unclear", 0.5, f"borderline ratio={ratio:.3f} len_ratio={len_ratio:.2f}"


def load_samples(path: Path, cutoff: datetime) -> list[Sample]:
    if not path.exists():
        return []
    rows: list[Sample] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            ts = parse_ts(obj["ts"])
        except Exception:
            continue
        if ts < cutoff:
            continue
        rows.append(Sample(
            ts=ts,
            raw=str(obj.get("rawASR", "") or ""),
            observed=str(obj.get("observedValue", "") or ""),
            edited=str(obj.get("editedRegion", "") or ""),
            app_name=str(obj.get("appName", "") or ""),
            app_bundle=str(obj.get("appBundleId", "") or ""),
            accepted_without_edit=bool(obj.get("acceptedWithoutEdit", False)),
        ))
    return rows


def build_remote_candidates(classified: list[tuple[Sample, str, float, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for sample, cat, conf, reason in classified:
        if cat == "accepted":
            continue
        observed = normalize_ws(sample.observed or sample.edited)
        if not observed or has_structural_injection(observed):
            continue
        out.append({
            "ts": sample.ts.isoformat().replace("+00:00", "Z"),
            "raw": normalize_ws(sample.raw),
            "observed": observed,
            "localCategory": cat,
            "localConfidence": round(conf, 3),
            "localReason": reason,
            "appName": sample.app_name,
            "appBundleId": sample.app_bundle,
        })
    out.sort(key=lambda x: (x["localCategory"], -float(x["localConfidence"])))
    return out[:20]


def safe_queue_candidates(classified: list[tuple[Sample, str, float, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for sample, cat, conf, reason in classified:
        raw = normalize_ws(sample.raw)
        obs = normalize_ws(sample.observed or sample.edited)
        if cat != "local_correction":
            continue
        if conf < 0.9:
            continue
        if not raw or not obs or raw == obs:
            continue
        if has_structural_injection(obs):
            continue
        out.append({
            "ts": sample.ts.isoformat().replace("+00:00", "Z"),
            "raw": raw,
            "edited": obs,
            "category": cat,
            "confidence": round(conf, 3),
            "reason": reason,
            "appName": sample.app_name,
            "appBundleId": sample.app_bundle,
            "source": "nightly-open-wispr-review"
        })
    return out


def render_report(now_utc: datetime, cutoff: datetime, samples: list[Sample], classified: list[tuple[Sample, str, float, str]], queued: list[dict[str, Any]], remote_candidates: list[dict[str, Any]]) -> str:
    counts = Counter(cat for _, cat, _, _ in classified)
    apps = Counter(s.app_name or s.app_bundle or "unknown" for s, *_ in classified)
    lines: list[str] = []
    lines.append("# Nightly open-wispr transcript review")
    lines.append("")
    lines.append(f"- Generated at: {now_utc.astimezone().isoformat()}")
    lines.append(f"- Window: last 24h (cutoff {cutoff.isoformat().replace('+00:00', 'Z')})")
    lines.append(f"- Samples reviewed: {len(samples)}")
    lines.append("")
    lines.append("## Counts")
    for key in ["accepted", "local_correction", "rewrite", "style_edit", "unclear"]:
        lines.append(f"- {key}: {counts.get(key, 0)}")
    lines.append("")
    lines.append("## By App")
    for app, count in apps.most_common():
        lines.append(f"- {app}: {count}")
    lines.append("")
    lines.append("## Queue candidates")
    if queued:
        for item in queued:
            lines.append(f"- `{item['raw']}` → `{item['edited']}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Remote review candidates")
    if remote_candidates:
        for item in remote_candidates[:10]:
            lines.append(f"- [{item['localCategory']}] `{item['raw']}` → `{item['observed']}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("#huanyuan")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-dir", default=str(Path.home() / ".config" / "open-wispr"))
    parser.add_argument("--hours", type=int, default=24)
    args = parser.parse_args()

    config_dir = Path(args.config_dir).expanduser()
    config_dir.mkdir(parents=True, exist_ok=True)
    transcripts = config_dir / "transcripts.jsonl"
    latest_md = config_dir / "nightly-review-latest.md"
    queue_jsonl = config_dir / "review_queue.jsonl"
    remote_input_jsonl = config_dir / "remote-review-input.jsonl"

    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(hours=args.hours)
    samples = load_samples(transcripts, cutoff)
    classified = [(s, *classify(s)) for s in samples]
    queued = safe_queue_candidates(classified)
    remote_candidates = build_remote_candidates(classified)

    queue_jsonl.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in queued), encoding="utf-8")
    remote_input_jsonl.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in remote_candidates), encoding="utf-8")
    latest_md.write_text(render_report(now_utc, cutoff, samples, classified, queued, remote_candidates), encoding="utf-8")

    print(f"reviewed={len(samples)} queued={len(queued)} remote_candidates={len(remote_candidates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#huanyuan

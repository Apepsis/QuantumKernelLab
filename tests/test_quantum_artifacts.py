from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_quantum_protocol_is_honest_and_non_promoting() -> None:
    result = json.loads((ROOT / "public" / "data" / "quantum_kernel_lab.json").read_text(encoding="utf-8"))
    assert result["mode"] in {"protocol", "live"}
    assert result["governance"]["automaticPromotion"] is False
    assert result["governance"]["role"] == "shadow-challenger"
    if result["mode"] == "protocol":
        assert result["aggregateResults"] == []
        assert result["foldResults"] == []
        assert result["status"] == "awaiting-manual-run"


def test_quantum_history_points_to_a_snapshot() -> None:
    history = json.loads((ROOT / "public" / "data" / "quantum_kernel_history.json").read_text(encoding="utf-8"))
    assert history["snapshots"]
    assert history["currentFingerprint"] in {item["fingerprint"] for item in history["snapshots"]}

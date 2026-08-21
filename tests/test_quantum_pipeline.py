from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import rbf_kernel

import run_quantum_kernel_lab as lab


def test_pipeline_end_to_end_without_claiming_a_quantum_result(tmp_path, monkeypatch) -> None:
    """Exercise every downstream step with an explicitly classical surrogate.

    Qiskit itself is exercised by the manual workflow. This test isolates the
    data protocol, aggregation, bootstrap and governance from that dependency.
    Its output is never published as an experiment result.
    """

    config = json.loads((lab.ROOT / "quantum" / "config.json").read_text(encoding="utf-8"))
    config["sampling"].update({
        "maximumFitRows": 80,
        "maximumCalibrationRows": 40,
        "maximumTestRows": 48,
        "maximumFolds": 2,
        "firstTestYear": 2024,
    })
    rng = np.random.default_rng(config["seed"])
    rows: list[dict[str, object]] = []
    for ticker_index, ticker in enumerate(("AAA", "BBB", "CCC")):
        for index, date in enumerate(pd.bdate_range("2019-01-02", "2025-12-31")):
            base = np.sin(index / 23 + ticker_index) + rng.normal(0, 0.15)
            row: dict[str, object] = {"date": date.date().isoformat(), "ticker": ticker}
            for feature_index, name in enumerate(config["featureColumns"]):
                row[name] = float(base + np.cos(index / (11 + feature_index)) * 0.1 + feature_index * 0.002)
            for horizon in config["horizons"]:
                row[f"label_excess_positive_{horizon}"] = int(
                    np.sin((index + horizon) / (17 + ticker_index)) + rng.normal(0, 0.2) > 0
                )
            rows.append(row)

    feature_file = tmp_path / "feature_store.json"
    feature_file.write_text(json.dumps({"rows": rows}), encoding="utf-8")
    monkeypatch.setattr(lab, "FEATURE_FILE", feature_file)

    def classical_surrogate(fit_x, calibration_x, test_x, _config):
        return (
            rbf_kernel(fit_x, fit_x, gamma=0.4),
            rbf_kernel(calibration_x, fit_x, gamma=0.4),
            rbf_kernel(test_x, fit_x, gamma=0.4),
            {
                "software": "pytest-classical-surrogate",
                "backend": "not-a-quantum-result",
                "qubits": 4,
                "circuitDepth": 0,
                "circuitSize": 0,
                "elapsedSeconds": 0.0,
            },
        )

    monkeypatch.setattr(lab, "quantum_kernel_matrices", classical_surrogate)
    result = lab.execute(config)
    assert result["mode"] == "live"
    assert len(result["foldResults"]) == 6
    assert len(result["aggregateResults"]) == 9
    assert len(result["bootstrap"]) == 3
    assert result["governance"]["automaticPromotion"] is False


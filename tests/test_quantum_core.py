from __future__ import annotations

import numpy as np
import pandas as pd

from quantum_core import (
    TemporalAngleEncoder,
    append_history,
    binary_metrics,
    build_temporal_folds,
    temporal_balanced_sample,
)


def synthetic_frame() -> pd.DataFrame:
    dates = pd.bdate_range("2019-01-02", "2025-12-31")
    rows = []
    for ticker_index, ticker in enumerate(("AAA", "BBB")):
        for index, date in enumerate(dates):
            rows.append({
                "date": date,
                "ticker": ticker,
                "f1": np.sin(index / 17) + ticker_index,
                "f2": np.cos(index / 29),
                "label_excess_positive_20": int((index + ticker_index) % 3 == 0),
            })
    return pd.DataFrame(rows)


def test_temporal_folds_are_purged() -> None:
    folds = build_temporal_folds(synthetic_frame(), 20, 2023, 3)
    assert len(folds) == 3
    for fold in folds:
        assert fold.fit["date"].max() < fold.calibration["date"].min()
        assert fold.calibration["date"].max() < fold.test["date"].min()
        all_dates = sorted(synthetic_frame()["date"].drop_duplicates())
        fit_end = all_dates.index(fold.fit["date"].max())
        calibration_start = all_dates.index(fold.calibration["date"].min())
        calibration_end = all_dates.index(fold.calibration["date"].max())
        test_start = all_dates.index(fold.test["date"].min())
        assert calibration_start - fit_end > 20
        assert test_start - calibration_end > 20


def test_encoder_maps_to_angles_without_refitting() -> None:
    train = np.arange(200, dtype=float).reshape(100, 2)
    test = np.array([[-1000.0, 1000.0]])
    encoder = TemporalAngleEncoder(2, 7).fit(train)
    transformed = encoder.transform(test)
    assert transformed.shape == (1, 2)
    assert np.all(transformed >= 0)
    assert np.all(transformed <= np.pi)


def test_balanced_sample_is_deterministic() -> None:
    frame = synthetic_frame().rename(columns={"label_excess_positive_20": "label"})
    first = temporal_balanced_sample(frame, "label", 80)
    second = temporal_balanced_sample(frame, "label", 80)
    assert first[["date", "ticker", "label"]].equals(second[["date", "ticker", "label"]])
    assert set(first["label"]) == {0, 1}


def test_metrics_and_history_are_finite_and_immutable() -> None:
    metrics = binary_metrics(np.array([0, 1, 1, 0]), np.array([0.1, 0.7, 0.8, 0.2]))
    assert metrics["brierScore"] < 0.1
    result = {"generatedAt": "2026-01-01T00:00:00Z", "experimentId": "q1", "mode": "live", "value": 1}
    history = {"snapshots": []}
    first = append_history(history, result)
    second = append_history(history, {**result, "generatedAt": "2026-01-02T00:00:00Z"})
    assert first == second
    assert len(history["snapshots"]) == 1

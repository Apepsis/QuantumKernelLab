"""Leakage-resistant utilities for the Quantum Kernel Shadow Challenger.

This module deliberately contains no Qiskit import. The temporal protocol,
preprocessing, calibration, metrics and governance can therefore be tested in
the ordinary CI job without installing the heavier quantum dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class TemporalFold:
    test_year: int
    fit: pd.DataFrame
    calibration: pd.DataFrame
    test: pd.DataFrame
    purge_sessions: int


class TemporalAngleEncoder:
    """Fit-only-on-the-past StandardScaler + PCA + robust angle mapping."""

    def __init__(self, components: int, seed: int) -> None:
        self.components = components
        self.seed = seed
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=components, random_state=seed)
        self.lower_: np.ndarray | None = None
        self.upper_: np.ndarray | None = None

    def fit(self, values: np.ndarray) -> "TemporalAngleEncoder":
        projected = self.pca.fit_transform(self.scaler.fit_transform(values))
        self.lower_ = np.quantile(projected, 0.01, axis=0)
        self.upper_ = np.quantile(projected, 0.99, axis=0)
        too_close = np.isclose(self.upper_, self.lower_)
        self.upper_[too_close] = self.lower_[too_close] + 1.0
        return self

    def transform(self, values: np.ndarray) -> np.ndarray:
        if self.lower_ is None or self.upper_ is None:
            raise RuntimeError("TemporalAngleEncoder debe ajustarse antes de transformar")
        projected = self.pca.transform(self.scaler.transform(values))
        unit = np.clip((projected - self.lower_) / (self.upper_ - self.lower_), 0.0, 1.0)
        return unit * np.pi

    def manifest(self) -> dict[str, object]:
        if self.lower_ is None or self.upper_ is None:
            raise RuntimeError("Encoder no ajustado")
        return {
            "components": self.components,
            "explainedVarianceRatio": [round(float(value), 8) for value in self.pca.explained_variance_ratio_],
            "angleRange": [0.0, round(float(np.pi), 8)],
            "trainingQuantiles": {
                "lower": [round(float(value), 8) for value in self.lower_],
                "upper": [round(float(value), 8) for value in self.upper_],
            },
        }


def canonical_hash(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_temporal_folds(
    frame: pd.DataFrame,
    horizon: int,
    first_test_year: int,
    maximum_folds: int,
    minimum_fit_rows: int = 120,
    minimum_calibration_rows: int = 30,
    minimum_test_rows: int = 30,
) -> list[TemporalFold]:
    """Construct expanding yearly folds with a horizon-sized purge twice.

    The first purge separates fit from calibration; the second separates all
    model development data from the test year. Labels whose future window could
    touch the next partition are therefore excluded.
    """

    local = frame.copy()
    local["date"] = pd.to_datetime(local["date"], errors="raise")
    local = local.sort_values(["date", "ticker"]).reset_index(drop=True)
    years = [int(year) for year in sorted(local["date"].dt.year.unique()) if int(year) >= first_test_year]
    folds: list[TemporalFold] = []
    for year in years:
        test = local[local["date"].dt.year == year].copy()
        prior_dates = sorted(local.loc[local["date"].dt.year < year, "date"].drop_duplicates())
        if len(prior_dates) <= horizon * 3 or len(test) < minimum_test_rows:
            continue
        development_dates = prior_dates[:-horizon]
        calibration_start_index = max(horizon + 1, int(len(development_dates) * 0.80))
        calibration_dates = development_dates[calibration_start_index:]
        fit_dates = development_dates[: max(0, calibration_start_index - horizon)]
        if not fit_dates or not calibration_dates:
            continue
        fit = local[local["date"].isin(fit_dates)].copy()
        calibration = local[local["date"].isin(calibration_dates)].copy()
        if len(fit) < minimum_fit_rows or len(calibration) < minimum_calibration_rows:
            continue
        folds.append(TemporalFold(year, fit, calibration, test, horizon))
    return folds[-maximum_folds:]


def temporal_balanced_sample(frame: pd.DataFrame, label: str, maximum_rows: int) -> pd.DataFrame:
    """Select both classes deterministically while retaining temporal coverage."""

    if len(frame) <= maximum_rows:
        return frame.sort_values(["date", "ticker"]).reset_index(drop=True)
    pieces: list[pd.DataFrame] = []
    per_class = maximum_rows // 2
    for value in (0, 1):
        group = frame[frame[label] == value].sort_values(["date", "ticker"])
        count = min(per_class, len(group))
        if count:
            indices = np.linspace(0, len(group) - 1, num=count, dtype=int)
            pieces.append(group.iloc[np.unique(indices)])
    sampled = pd.concat(pieces, ignore_index=True) if pieces else frame.iloc[0:0].copy()
    if len(sampled) < maximum_rows:
        keys = set(zip(sampled["date"].astype(str), sampled["ticker"].astype(str)))
        remaining = frame[
            ~frame.apply(lambda row: (str(row["date"]), str(row["ticker"])) in keys, axis=1)
        ].sort_values(["date", "ticker"])
        sampled = pd.concat([sampled, remaining.head(maximum_rows - len(sampled))], ignore_index=True)
    return sampled.sort_values(["date", "ticker"]).reset_index(drop=True)


def fit_platt(decision_values: np.ndarray, labels: np.ndarray, seed: int) -> LogisticRegression | None:
    labels = np.asarray(labels, dtype=int)
    if len(np.unique(labels)) < 2:
        return None
    model = LogisticRegression(C=1.0, solver="lbfgs", random_state=seed)
    model.fit(np.asarray(decision_values, dtype=float).reshape(-1, 1), labels)
    return model


def apply_platt(model: LogisticRegression | None, decision_values: np.ndarray, prevalence: float) -> np.ndarray:
    if model is None:
        return np.full(len(decision_values), np.clip(prevalence, 1e-6, 1 - 1e-6))
    probabilities = model.predict_proba(np.asarray(decision_values, dtype=float).reshape(-1, 1))[:, 1]
    return np.clip(probabilities, 1e-6, 1 - 1e-6)


def expected_calibration_error(labels: np.ndarray, probabilities: np.ndarray, bins: int = 10) -> float:
    labels = np.asarray(labels, dtype=float)
    probabilities = np.asarray(probabilities, dtype=float)
    total = max(1, len(labels))
    error = 0.0
    boundaries = np.linspace(0.0, 1.0, bins + 1)
    for index in range(bins):
        lower, upper = boundaries[index], boundaries[index + 1]
        mask = (probabilities >= lower) & (probabilities < upper if index < bins - 1 else probabilities <= upper)
        if np.any(mask):
            error += float(np.sum(mask)) / total * abs(float(np.mean(probabilities[mask])) - float(np.mean(labels[mask])))
    return error


def binary_metrics(labels: np.ndarray, probabilities: np.ndarray) -> dict[str, float | int | None]:
    labels = np.asarray(labels, dtype=int)
    probabilities = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
    predictions = (probabilities >= 0.5).astype(int)
    auc = float(roc_auc_score(labels, probabilities)) if len(np.unique(labels)) == 2 else None
    return {
        "brierScore": round(float(brier_score_loss(labels, probabilities)), 8),
        "logLoss": round(float(log_loss(labels, probabilities, labels=[0, 1])), 8),
        "rocAuc": round(auc, 8) if auc is not None else None,
        "accuracy": round(float(accuracy_score(labels, predictions)), 8),
        "balancedAccuracy": round(float(balanced_accuracy_score(labels, predictions)), 8),
        "ece": round(float(expected_calibration_error(labels, probabilities)), 8),
        "sampleSize": int(len(labels)),
        "positiveRate": round(float(np.mean(labels)), 8),
    }


def paired_date_bootstrap(
    rows: Iterable[dict[str, object]],
    quantum_model: str,
    classical_model: str,
    seed: int,
    iterations: int = 1000,
) -> dict[str, float | int | str | None]:
    """Bootstrap dates, preserving the cross-section observed on each date."""

    frame = pd.DataFrame(list(rows))
    required = {"date", "label", quantum_model, classical_model}
    if frame.empty or not required.issubset(frame.columns):
        return {"iterations": 0, "deltaMean": None, "ciLow": None, "ciHigh": None, "probabilityQuantumBetter": None}
    by_date = []
    for _, group in frame.groupby("date", sort=True):
        labels = group["label"].to_numpy(float)
        q_loss = np.square(group[quantum_model].to_numpy(float) - labels)
        c_loss = np.square(group[classical_model].to_numpy(float) - labels)
        by_date.append(float(np.mean(q_loss - c_loss)))
    if len(by_date) < 2:
        return {"iterations": 0, "deltaMean": None, "ciLow": None, "ciHigh": None, "probabilityQuantumBetter": None}
    values = np.asarray(by_date, dtype=float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(iterations, len(values)), replace=True).mean(axis=1)
    return {
        "comparison": f"{quantum_model} minus {classical_model}",
        "iterations": iterations,
        "deltaMean": round(float(np.mean(values)), 8),
        "ciLow": round(float(np.quantile(draws, 0.025)), 8),
        "ciHigh": round(float(np.quantile(draws, 0.975)), 8),
        "probabilityQuantumBetter": round(float(np.mean(draws < 0)), 8),
    }


def artifact_fingerprint(payload: dict[str, object]) -> str:
    material = {key: value for key, value in payload.items() if key not in {"generatedAt", "runId", "fingerprint"}}
    return canonical_hash(material)


def append_history(history: dict[str, object], result: dict[str, object]) -> str:
    fingerprint = artifact_fingerprint(result)
    snapshots = history.setdefault("snapshots", [])
    if not isinstance(snapshots, list):
        raise ValueError("quantum_kernel_history.json contiene snapshots inválidos")
    if not any(isinstance(item, dict) and item.get("fingerprint") == fingerprint for item in snapshots):
        snapshots.append({
            "fingerprint": fingerprint,
            "archivedAt": result.get("generatedAt"),
            "experimentId": result.get("experimentId"),
            "result": result,
        })
    return fingerprint

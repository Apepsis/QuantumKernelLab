"""Execute the manual Quantum Kernel Shadow Challenger experiment.

The default backend is an exact statevector simulation. No claim of quantum
advantage is made: the goal is a controlled, auditable comparison under the
same point-in-time data and temporal folds used by the classical research lab.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import time
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from quantum_core import (
    TemporalAngleEncoder,
    append_history,
    apply_platt,
    binary_metrics,
    build_temporal_folds,
    canonical_hash,
    fit_platt,
    paired_date_bootstrap,
    temporal_balanced_sample,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "quantum" / "config.json"
FEATURE_FILE = ROOT / "research_work" / "feature_store.json"
OUTPUT_FILE = ROOT / "public" / "data" / "quantum_kernel_lab.json"
HISTORY_FILE = ROOT / "public" / "data" / "quantum_kernel_history.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unavailable"


def protocol_payload(config: dict[str, Any]) -> dict[str, Any]:
    generated_at = utc_now()
    return {
        "schemaVersion": 1,
        "generatedAt": generated_at,
        "mode": "protocol",
        "status": "awaiting-manual-run",
        "experimentId": config["experimentName"],
        "title": "Quantum Kernel Shadow Challenger",
        "hypothesis": "Un kernel cuántico de fidelidad puede reducir el Brier score fuera de muestra frente a regresión logística y SVM-RBF sin usar información futura.",
        "decisionTarget": "P(activo supera a SPY)",
        "horizons": config["horizons"],
        "design": {
            "validation": "expanding walk-forward por año",
            "purge": "igual al horizonte, entre fit/calibración y desarrollo/prueba",
            "preprocessing": "StandardScaler + PCA ajustados solo en fit; cuantiles de fit mapeados a [0, pi]",
            "qubits": config["qubits"],
            "featureMap": config["featureMap"],
            "sampling": config["sampling"],
            "baselines": ["logistic", "rbfSvm"],
            "quantumModels": ["quantumZZ"],
        },
        "features": config["featureColumns"],
        "aggregateResults": [],
        "foldResults": [],
        "bootstrap": [],
        "governance": {
            "role": "shadow-challenger",
            "promotionPolicy": config["promotionPolicy"],
            "eligibleForPromotion": False,
            "automaticPromotion": False,
            "decision": "No ejecutado. Ningún resultado cuántico modifica el modelo oficial.",
        },
        "reproducibility": {
            "seed": config["seed"],
            "configHash": canonical_hash(config),
            "gitCommit": git_commit(),
            "python": platform.python_version(),
            "backend": "FidelityStatevectorKernel exact simulation",
        },
        "limitations": [
            "El simulador de estados cuánticos se ejecuta en hardware clásico.",
            "Una mejora predictiva no demuestra ventaja computacional cuántica.",
            "El muestreo limitado es necesario porque una matriz kernel crece cuadráticamente.",
            "La selección de hiperparámetros posterior a observar test invalidaría el protocolo.",
            "El experimento no ejecuta operaciones ni produce asesoría financiera.",
        ],
        "sources": [
            {"title": "Supervised learning with quantum-enhanced feature spaces", "url": "https://arxiv.org/abs/1804.11326"},
            {"title": "Power of data in quantum machine learning", "url": "https://arxiv.org/abs/2011.01938"},
            {"title": "Qiskit Machine Learning - Quantum kernels", "url": "https://qiskit-community.github.io/qiskit-machine-learning/apidocs/qiskit_machine_learning.kernels.html"},
        ],
    }


def import_quantum_stack() -> tuple[Any, Any, str]:
    try:
        import qiskit
        import qiskit_machine_learning
        from qiskit.circuit.library import zz_feature_map
        from qiskit_machine_learning.kernels import FidelityStatevectorKernel
    except ImportError as exc:
        raise RuntimeError("Faltan las dependencias cuánticas. Instala requirements-quantum.txt") from exc
    version = f"qiskit={qiskit.__version__}; qiskit-machine-learning={qiskit_machine_learning.__version__}"
    return zz_feature_map, FidelityStatevectorKernel, version


def quantum_kernel_matrices(
    fit_x: np.ndarray,
    calibration_x: np.ndarray,
    test_x: np.ndarray,
    config: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    zz_feature_map, kernel_type, version = import_quantum_stack()
    feature_map = zz_feature_map(
        feature_dimension=config["qubits"],
        reps=config["featureMap"]["repetitions"],
        entanglement=config["featureMap"]["entanglement"],
    )
    kernel = kernel_type(feature_map=feature_map, shots=config["featureMap"]["shots"], enforce_psd=True)
    started = time.perf_counter()
    fit_kernel = np.asarray(kernel.evaluate(fit_x), dtype=float)
    calibration_kernel = np.asarray(kernel.evaluate(calibration_x, fit_x), dtype=float)
    test_kernel = np.asarray(kernel.evaluate(test_x, fit_x), dtype=float)
    return fit_kernel, calibration_kernel, test_kernel, {
        "software": version,
        "backend": "exact-statevector",
        "qubits": int(feature_map.num_qubits),
        "circuitDepth": int(feature_map.depth()),
        "circuitSize": int(feature_map.size()),
        "elapsedSeconds": round(time.perf_counter() - started, 6),
    }


def model_result(name: str, family: str, labels: np.ndarray, probabilities: np.ndarray, elapsed: float) -> dict[str, Any]:
    return {
        "name": name,
        "family": family,
        "metrics": binary_metrics(labels, probabilities),
        "runtimeSeconds": round(elapsed, 6),
    }


def aggregate(folds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fold in folds:
        for model in fold["models"]:
            rows.append({
                "horizonSessions": fold["horizonSessions"],
                "model": model["name"],
                **model["metrics"],
            })
    frame = pd.DataFrame(rows)
    output: list[dict[str, Any]] = []
    for (horizon, model), group in frame.groupby(["horizonSessions", "model"], sort=True):
        weights = group["sampleSize"].to_numpy(float)
        record: dict[str, Any] = {
            "horizonSessions": int(horizon),
            "model": str(model),
            "folds": int(len(group)),
            "sampleSize": int(group["sampleSize"].sum()),
        }
        for metric in ("brierScore", "logLoss", "rocAuc", "accuracy", "balancedAccuracy", "ece"):
            valid = group[metric].notna().to_numpy()
            record[metric] = round(float(np.average(group.loc[valid, metric], weights=weights[valid])), 8) if np.any(valid) else None
        output.append(record)
    return output


def governance(config: dict[str, Any], aggregate_rows: list[dict[str, Any]], bootstraps: list[dict[str, Any]]) -> dict[str, Any]:
    policy = config["promotionPolicy"]
    by_key = {(item["horizonSessions"], item["model"]): item for item in aggregate_rows}
    checks: list[dict[str, Any]] = []
    wins = 0
    for horizon in config["horizons"]:
        quantum = by_key.get((horizon, "quantumZZ"))
        baselines = [by_key.get((horizon, name)) for name in ("logistic", "rbfSvm")]
        baselines = [item for item in baselines if item]
        bootstrap = next((item for item in bootstraps if item.get("horizonSessions") == horizon), None)
        if not quantum or not baselines:
            checks.append({"horizonSessions": horizon, "passed": False, "reason": "resultado incompleto"})
            continue
        best = min(baselines, key=lambda item: item["brierScore"])
        improvement = best["brierScore"] - quantum["brierScore"]
        enough_folds = quantum["folds"] >= policy["minimumCompletedFolds"]
        brier_pass = improvement >= policy["minimumBrierImprovement"]
        ece_pass = quantum["ece"] <= best["ece"] + policy["maximumEceDegradation"]
        ci_pass = bool(bootstrap and bootstrap.get("ciHigh") is not None and bootstrap["ciHigh"] < 0)
        passed = enough_folds and brier_pass and ece_pass and (ci_pass or not policy["requireBootstrapUpperBoundBelowZero"])
        wins += int(passed)
        checks.append({
            "horizonSessions": horizon,
            "passed": passed,
            "bestClassical": best["model"],
            "brierImprovement": round(float(improvement), 8),
            "enoughFolds": enough_folds,
            "eceGate": ece_pass,
            "bootstrapGate": ci_pass,
        })
    eligible = wins >= policy["minimumHorizonsWon"]
    return {
        "role": "shadow-challenger",
        "promotionPolicy": policy,
        "checks": checks,
        "horizonsPassed": wins,
        "eligibleForPromotion": eligible,
        "automaticPromotion": False,
        "decision": (
            "Elegible para revisión humana, pero no promovido automáticamente."
            if eligible else
            "Permanece en shadow: no supera todas las puertas publicadas."
        ),
    }


def execute(config: dict[str, Any]) -> dict[str, Any]:
    if not FEATURE_FILE.exists():
        raise FileNotFoundError("Falta research_work/feature_store.json. Ejecuta scripts/build_feature_store.py primero.")
    feature_payload = json.loads(FEATURE_FILE.read_text(encoding="utf-8"))
    features = config["featureColumns"]
    frame = pd.DataFrame(feature_payload["rows"])
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    fold_results: list[dict[str, Any]] = []
    probability_rows: list[dict[str, Any]] = []

    for horizon in config["horizons"]:
        label = f"label_excess_positive_{horizon}"
        usable = frame.dropna(subset=features + [label]).copy()
        usable[label] = usable[label].astype(int)
        folds = build_temporal_folds(
            usable,
            horizon=horizon,
            first_test_year=config["sampling"]["firstTestYear"],
            maximum_folds=config["sampling"]["maximumFolds"],
        )
        for fold in folds:
            fit = temporal_balanced_sample(fold.fit, label, config["sampling"]["maximumFitRows"])
            calibration = temporal_balanced_sample(fold.calibration, label, config["sampling"]["maximumCalibrationRows"])
            test = temporal_balanced_sample(fold.test, label, config["sampling"]["maximumTestRows"])
            encoder = TemporalAngleEncoder(config["pcaComponents"], config["seed"]).fit(fit[features].to_numpy(float))
            fit_x = encoder.transform(fit[features].to_numpy(float))
            calibration_x = encoder.transform(calibration[features].to_numpy(float))
            test_x = encoder.transform(test[features].to_numpy(float))
            fit_y = fit[label].to_numpy(int)
            calibration_y = calibration[label].to_numpy(int)
            test_y = test[label].to_numpy(int)
            if len(np.unique(fit_y)) < 2 or len(np.unique(calibration_y)) < 2:
                raise RuntimeError(
                    f"Fold inválido para horizonte={horizon}, año={fold.test_year}: "
                    "fit y calibración deben contener ambas clases."
                )
            models: list[dict[str, Any]] = []

            started = time.perf_counter()
            logistic = LogisticRegression(C=1.0, max_iter=2000, random_state=config["seed"]).fit(fit_x, fit_y)
            logistic_prob = logistic.predict_proba(test_x)[:, 1]
            models.append(model_result("logistic", "classical-baseline", test_y, logistic_prob, time.perf_counter() - started))

            started = time.perf_counter()
            rbf = SVC(C=1.0, kernel="rbf", gamma="scale").fit(fit_x, fit_y)
            rbf_calibrator = fit_platt(rbf.decision_function(calibration_x), calibration_y, config["seed"])
            rbf_prob = apply_platt(rbf_calibrator, rbf.decision_function(test_x), float(np.mean(calibration_y)))
            models.append(model_result("rbfSvm", "classical-baseline", test_y, rbf_prob, time.perf_counter() - started))

            fit_kernel, calibration_kernel, test_kernel, quantum_manifest = quantum_kernel_matrices(fit_x, calibration_x, test_x, config)
            started = time.perf_counter()
            quantum_svc = SVC(C=1.0, kernel="precomputed").fit(fit_kernel, fit_y)
            quantum_calibrator = fit_platt(quantum_svc.decision_function(calibration_kernel), calibration_y, config["seed"])
            quantum_prob = apply_platt(quantum_calibrator, quantum_svc.decision_function(test_kernel), float(np.mean(calibration_y)))
            models.append(model_result("quantumZZ", "quantum-shadow", test_y, quantum_prob, time.perf_counter() - started + quantum_manifest["elapsedSeconds"]))

            fold_record = {
                "horizonSessions": horizon,
                "testYear": fold.test_year,
                "periods": {
                    "fit": [fit["date"].min().date().isoformat(), fit["date"].max().date().isoformat()],
                    "calibration": [calibration["date"].min().date().isoformat(), calibration["date"].max().date().isoformat()],
                    "test": [test["date"].min().date().isoformat(), test["date"].max().date().isoformat()],
                },
                "purgeSessions": fold.purge_sessions,
                "rows": {"fit": len(fit), "calibration": len(calibration), "test": len(test)},
                "encoder": encoder.manifest(),
                "quantumCircuit": quantum_manifest,
                "models": models,
            }
            fold_results.append(fold_record)
            for index, (_, row) in enumerate(test.reset_index(drop=True).iterrows()):
                probability_rows.append({
                    "horizonSessions": horizon,
                    "testYear": fold.test_year,
                    "date": row["date"].date().isoformat(),
                    "ticker": row["ticker"],
                    "label": int(test_y[index]),
                    "logistic": round(float(logistic_prob[index]), 8),
                    "rbfSvm": round(float(rbf_prob[index]), 8),
                    "quantumZZ": round(float(quantum_prob[index]), 8),
                })

    completed_horizons = {int(item["horizonSessions"]) for item in fold_results}
    missing_horizons = sorted(set(config["horizons"]) - completed_horizons)
    if missing_horizons:
        raise RuntimeError(
            "No existen folds válidos para los horizontes: "
            + ", ".join(str(value) for value in missing_horizons)
        )

    aggregate_rows = aggregate(fold_results)
    bootstraps: list[dict[str, Any]] = []
    for horizon in config["horizons"]:
        horizon_rows = [row for row in probability_rows if row["horizonSessions"] == horizon]
        baseline_metrics = [item for item in aggregate_rows if item["horizonSessions"] == horizon and item["model"] in {"logistic", "rbfSvm"}]
        if not baseline_metrics:
            continue
        best = min(baseline_metrics, key=lambda item: item["brierScore"])["model"]
        result = paired_date_bootstrap(horizon_rows, "quantumZZ", best, config["seed"] + horizon)
        result["horizonSessions"] = horizon
        result["bestClassical"] = best
        bootstraps.append(result)

    generated_at = utc_now()
    experiment_id = f"{config['experimentName']}-{generated_at[:10]}"
    result: dict[str, Any] = {
        **protocol_payload(config),
        "generatedAt": generated_at,
        "mode": "live",
        "status": "completed",
        "experimentId": experiment_id,
        "aggregateResults": aggregate_rows,
        "foldResults": fold_results,
        "bootstrap": bootstraps,
        "governance": governance(config, aggregate_rows, bootstraps),
        "reproducibility": {
            **protocol_payload(config)["reproducibility"],
            "dataHash": canonical_hash(feature_payload),
            "configHash": canonical_hash(config),
            "gitCommit": git_commit(),
        },
    }
    result["fingerprint"] = canonical_hash({key: value for key, value in result.items() if key not in {"generatedAt", "fingerprint"}})
    return result


def publish(result: dict[str, Any]) -> None:
    history: dict[str, Any] = {
        "schemaVersion": 1,
        "generatedAt": result["generatedAt"],
        "mode": result["mode"],
        "policy": "Cada resultado cuántico distinto se conserva por huella; ninguna medición anterior se reescribe.",
        "currentFingerprint": "",
        "snapshots": [],
    }
    if HISTORY_FILE.exists():
        loaded = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            history.update(loaded)
    fingerprint = append_history(history, result)
    history.update({"generatedAt": result["generatedAt"], "mode": result["mode"], "currentFingerprint": fingerprint})
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol-only", action="store_true", help="Publica únicamente el protocolo sin ejecutar Qiskit")
    args = parser.parse_args()
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    result = protocol_payload(config) if args.protocol_only else execute(config)
    publish(result)
    print(f"Quantum Kernel Lab: {result['status']}; {len(result['foldResults'])} folds; modo={result['mode']}.")


if __name__ == "__main__":
    main()

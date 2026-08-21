"""Fail closed when a published Quantum Kernel artifact is incomplete."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_FILE = ROOT / "public" / "data" / "quantum_kernel_lab.json"
HISTORY_FILE = ROOT / "public" / "data" / "quantum_kernel_history.json"


def main() -> None:
    result = json.loads(RESULT_FILE.read_text(encoding="utf-8"))
    history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    required = {"schemaVersion", "generatedAt", "mode", "status", "experimentId", "hypothesis", "design", "governance", "reproducibility", "limitations"}
    missing = sorted(required - set(result))
    if missing:
        raise ValueError(f"quantum_kernel_lab.json incompleto: {missing}")
    if result["mode"] not in {"protocol", "live"}:
        raise ValueError("Modo cuántico inválido")
    if result["mode"] == "live":
        if not result.get("foldResults") or not result.get("aggregateResults"):
            raise ValueError("Una ejecución live necesita folds y agregados")
        if result.get("status") != "completed":
            raise ValueError("Una ejecución live debe estar completada")
    snapshots = history.get("snapshots")
    if not isinstance(snapshots, list) or not snapshots:
        raise ValueError("El historial cuántico no contiene snapshots")
    fingerprints = [item.get("fingerprint") for item in snapshots if isinstance(item, dict)]
    if history.get("currentFingerprint") not in fingerprints:
        raise ValueError("La huella actual no aparece en el historial")
    if result["governance"].get("automaticPromotion") is not False:
        raise ValueError("La promoción automática debe permanecer desactivada")
    print(f"Artefactos cuánticos válidos: modo={result['mode']}; snapshots={len(snapshots)}")


if __name__ == "__main__":
    main()

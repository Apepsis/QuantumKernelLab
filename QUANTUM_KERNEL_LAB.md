# Quantum Kernel Lab

Este módulo añade a InvestmentResearchAI un experimento reproducible de *quantum machine learning* para estimar

> `P(activo supera a SPY en h sesiones)` para `h = 5, 20, 60`.

La versión cuántica es un **Shadow Challenger**. Nunca sustituye por sí sola al modelo oficial, no ejecuta operaciones y no altera predicciones históricas. El experimento compara, sobre exactamente las mismas observaciones:

1. Regresión logística.
2. SVM con kernel RBF.
3. SVC con un kernel de fidelidad generado mediante `ZZFeatureMap` y simulación exacta de cuatro qubits.

## Inicio rápido privado

```bash
python -m pip install -r requirements-quantum.txt
python scripts/build_feature_store.py
python scripts/run_quantum_kernel_lab.py
python scripts/validate_quantum_kernel_artifacts.py
pytest -q tests/test_quantum_core.py tests/test_quantum_artifacts.py
```

En GitHub se recomienda ejecutar manualmente **Actions -> Ejecutar Quantum Kernel Lab -> Run workflow** y mantener `publish_results = false`. Así el resultado queda como artefacto privado de la ejecución durante 30 días y no modifica la página pública.

## Archivos principales

- `quantum/config.json`: protocolo y puertas de promoción.
- `scripts/quantum_core.py`: purga temporal, transformación, métricas, bootstrap e historial.
- `scripts/run_quantum_kernel_lab.py`: comparación completa.
- `public/data/quantum_kernel_lab.json`: protocolo o última ejecución autorizada.
- `public/data/quantum_kernel_history.json`: historial append-only por huella.
- `app/components/QuantumKernelLab.tsx`: interfaz.
- `docs/quantum/`: protocolo, tarjetas, amenazas, manual y referencias.

Lee primero [RESEARCH_PROTOCOL.md](docs/quantum/RESEARCH_PROTOCOL.md) y después [GITHUB_MANUAL.md](docs/quantum/GITHUB_MANUAL.md).

## Declaración científica

Este proyecto evalúa si una representación cuántica aporta señal predictiva bajo un protocolo temporal controlado. Una mejora estadística en un simulador no constituye ventaja computacional cuántica ni garantiza rentabilidad futura.


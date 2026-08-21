# Artefactos de investigación

## Quantum Kernel Lab experimental

Esta edición incluye un laboratorio de *quantum machine learning* reproducible que compara regresión logística, SVM-RBF y un kernel de fidelidad cuántica bajo el mismo protocolo walk-forward. El modelo cuántico permanece como Shadow Challenger, se ejecuta manualmente y no se promueve ni opera automáticamente.

Empieza en [QUANTUM_KERNEL_LAB.md](QUANTUM_KERNEL_LAB.md). El protocolo completo está en [docs/quantum/RESEARCH_PROTOCOL.md](docs/quantum/RESEARCH_PROTOCOL.md).

El workflow `.github/workflows/update-market-data.yml` genera:

- `market.json`
- `backtest.json`
- `backtest_history.json` (mediciones walk-forward inmutables por huella)
- `risk_model.json`
- `event_studies.json`
- `live_predictions.json`
- `prediction_ledger.json`
- `model_registry.json`
- `model_monitoring.json`
- `alerts.json`
- `neural_lab.json`
- `neural_prediction_ledger.json`
- `quantum_kernel_lab.json`
- `quantum_kernel_history.json`
- `research_manifest.json`

El workflow `.github/workflows/refresh-fast-signals.yml` genera por separado:

- `fast_signals.json` (titulares, dirección y urgencia cada 20 minutos)

`build_journal.json` es documentación versionada del proceso. Mientras todavía
no existan resultados válidos, la interfaz muestra estructuras de demostración
claramente identificadas. No edites manualmente los artefactos generados y, en
especial, no borres `prediction_ledger.json`: es el historial pre-registrado.
Tampoco borres `neural_prediction_ledger.json`; sus probabilidades se publican
antes del resultado y deben permanecer inmutables.
No borres `backtest_history.json`: permite comparar la medición actual con las
ejecuciones matemáticamente distintas publicadas anteriormente.

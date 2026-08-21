# Inicio privado en 7 pasos

1. Conserva este ZIP fuera del repositorio hasta que quieras publicarlo.
2. Cuando estés listo, usa primero `QuantumKernelLab_GitHub_Overlay.zip` sobre una copia local de tu repositorio.
3. Ejecuta `npm ci`, `npm run typecheck` y `npm run build:pages`.
4. Haz commit y push.
5. En GitHub abre **Actions -> Ejecutar Quantum Kernel Lab**.
6. Ejecuta con `publish_results=false` y descarga el artifact privado.
7. Revisa las métricas con `docs/quantum/RESULTS_TEMPLATE.md`; publica en otra corrida solo si la evidencia es válida.

No necesitas una clave de IBM Quantum para Q1. Usa un simulador exacto. Las claves de Alpaca, Firebase o Cloudflare no están dentro de esta entrega.


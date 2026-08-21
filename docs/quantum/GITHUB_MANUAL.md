# Manual de GitHub - ejecución privada primero

## 1. Subir el código en el futuro

Cuando decidas publicarlo, copia el contenido del paquete sobre la raíz de tu repositorio y confirma que aparecen:

```text
.github/workflows/quantum-kernel-lab.yml
quantum/config.json
requirements-quantum.txt
scripts/quantum_core.py
scripts/run_quantum_kernel_lab.py
scripts/validate_quantum_kernel_artifacts.py
tests/test_quantum_core.py
tests/test_quantum_artifacts.py
app/components/QuantumKernelLab.tsx
docs/quantum/
```

Haz commit con un mensaje descriptivo, por ejemplo `quantum: add preregistered kernel shadow lab`.

## 2. Ejecutar sin publicar

1. Abre el repositorio en GitHub.
2. Entra en **Actions**.
3. Selecciona **Ejecutar Quantum Kernel Lab**.
4. Pulsa **Run workflow**.
5. Deja `publish_results` en `false`.
6. Espera que todas las etapas estén verdes.
7. Abre el run y descarga `quantum-kernel-results-<run-id>` en **Artifacts**.

Ese ZIP es privado para usuarios con acceso al repositorio y caduca a los 30 días. La web no cambia.

## 3. Revisar el resultado

Dentro del artefacto abre:

- `quantum_kernel_lab.json`: métricas, folds, bootstrap y gobernanza;
- `quantum_kernel_history.json`: fingerprint e historial.

Comprueba primero `mode=live`, `status=completed` y que existan resultados para los tres horizontes. Después usa `RESULTS_TEMPLATE.md`.

## 4. Publicar solamente tras revisión

Ejecuta otra vez el workflow con `publish_results=true`. El bot:

1. ejecuta el experimento desde cero;
2. valida artefactos y pruebas;
3. archiva el resultado como artifact;
4. hace commit solo si la huella cambió;
5. dispara el workflow de GitHub Pages.

Esto no promueve el modelo. Solamente hace visible la evidencia en la pestaña **Quantum Lab**.

## 5. Ejecutar localmente

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-quantum.txt
python scripts/build_feature_store.py
python scripts/run_quantum_kernel_lab.py
python scripts/validate_quantum_kernel_artifacts.py
pytest -q tests/test_quantum_core.py tests/test_quantum_artifacts.py
npm ci
npm run typecheck
npm run build:pages
```

## 6. Cambiar el experimento correctamente

No edites una corrida ya publicada. Duplica `quantum/config.json` conceptualmente creando un nuevo `experimentName`, documenta la motivación y vuelve al modo Shadow. Modificar qubits, feature map, variables, muestreo o puertas después de mirar test crea un experimento diferente.

## 7. Solución de problemas

- `Faltan las dependencias cuánticas`: instala `requirements-quantum.txt`.
- `Falta feature_store.json`: ejecuta `build_feature_store.py`.
- cero folds: amplía historia o reduce el primer año de prueba en una nueva revisión del protocolo.
- timeout: reduce filas en una nueva revisión; no elimines baselines.
- página sigue en modo protocolo: el último run fue privado o no se eligió publicar.


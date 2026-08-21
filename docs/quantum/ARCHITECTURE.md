# Arquitectura

```text
market.json / histórico
        |
        v
build_feature_store.py
        |
        +--> research_work/feature_store.json   [temporal, no se publica]
        |
        v
run_quantum_kernel_lab.py
        |
        +--> quantum_core.py                    [purga, PCA, métricas, bootstrap]
        +--> Qiskit FidelityStatevectorKernel   [matrices de fidelidad]
        |
        +--> public/data/quantum_kernel_lab.json
        +--> public/data/quantum_kernel_history.json
                    |
                    v
QuantumKernelLab.tsx -> GitHub Pages solamente si publish_results=true
```

## Fronteras de confianza

1. Las credenciales de mercado permanecen en GitHub Secrets o Cloudflare; el laboratorio no las escribe.
2. El feature store se reconstruye en el runner y no se sube como artefacto público.
3. Los resultados se suben como artefacto privado del workflow por defecto.
4. Publicar requiere una elección explícita al lanzar el workflow.
5. El código de interfaz nunca puede promover modelos ni operar.

## Artefactos

`quantum_kernel_lab.json` contiene el protocolo o una ejecución completa. `quantum_kernel_history.json` conserva una copia por fingerprint para impedir que una nueva corrida silenciosamente sustituya una evidencia distinta.


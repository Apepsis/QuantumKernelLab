# Model Card - Quantum Kernel Shadow Challenger

## Identidad

- Nombre: `quantumZZ`.
- Familia: SVC con kernel de fidelidad cuántica.
- Versión experimental: `quantum-kernel-shadow-v1`.
- Estado inicial: protocolo listo, ejecución manual pendiente.

## Uso previsto

Comparar representaciones no lineales bajo un protocolo temporal controlado. La salida es `P(activo supera a SPY)` a 5, 20 y 60 sesiones.

## Usos prohibidos

- ejecutar compras o ventas;
- sustituir automáticamente al Champion;
- presentar una probabilidad como certeza;
- reutilizar el año de prueba para ajustar parámetros;
- afirmar ventaja cuántica por superar un baseline una sola vez.

## Arquitectura

```text
15 variables -> StandardScaler -> PCA(4) -> ángulos [0,pi]
             -> ZZFeatureMap(4 qubits, reps=2, lineal)
             -> matriz de fidelidad -> SVC -> Platt -> probabilidad
```

## Controles

- semilla fija;
- doble purga igual al horizonte;
- matrices calculadas sobre exactamente las mismas filas;
- historial append-only;
- huella del config, datos y resultado;
- puertas de promoción publicadas antes de ejecutar.

## Riesgos conocidos

- muestra reducida por costo cuadrático;
- simulación clásica, no hardware real;
- desempeño sensible al feature map y al escalado angular;
- posibilidad de concentración del kernel;
- cambios de régimen financiero;
- calibración inestable con pocas observaciones.

## Interpretación

Una mejora de Brier con intervalo compatible con cero es evidencia insuficiente. Una mejora repetida y estadísticamente separada del baseline justifica revisión, no promoción automática.


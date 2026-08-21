# Cambios incluidos

## Investigación

- protocolo preregistrado con objetivos a 5, 20 y 60 sesiones;
- doble purga temporal y transformación ajustada solo con el pasado;
- regresión logística y SVM-RBF como baselines obligatorios;
- kernel de fidelidad `ZZFeatureMap` con cuatro qubits;
- calibración Platt, Brier, log-loss, ROC-AUC, ECE y balanced accuracy;
- bootstrap pareado por fecha y puertas de promoción;
- historial append-only por fingerprint.

## Software

- scripts Python separados entre núcleo clásico y dependencia cuántica;
- pruebas de leakage, transformación, muestreo e integridad;
- validador de JSON;
- workflow manual con artifact privado por defecto;
- pestaña visual Quantum Lab;
- tipos, fallback honesto y estilos responsive.

## Documentación

- protocolo, model card, data card, threat model;
- arquitectura, manual de GitHub, plantilla de resultados y bibliografía;
- manual PDF diseñado para lectura y presentación.

## No incluido deliberadamente

- resultados cuánticos inventados;
- promoción automática;
- órdenes de trading;
- secretos de API;
- ejecución automática costosa en cada commit.


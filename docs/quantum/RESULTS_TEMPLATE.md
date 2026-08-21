# Plantilla de interpretación

## Identidad de la corrida

- Experiment ID:
- Fecha UTC:
- Git commit:
- Config hash:
- Data hash:
- Qiskit / Qiskit Machine Learning:
- Backend:

## Integridad

- [ ] Los tres modelos usaron las mismas filas.
- [ ] Los tres horizontes completaron los folds previstos.
- [ ] Fit, calibración y test están separados por la doble purga.
- [ ] No se cambió el config después de observar test.
- [ ] El fingerprint quedó en el historial.

## Resultados por horizonte

| Horizonte | Mejor clásico Brier | Quantum Brier | Delta | IC 95% | ECE quantum | Conclusión |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| 5 | | | | | | |
| 20 | | | | | | |
| 60 | | | | | | |

## Conclusión permitida

Escribe una de estas formulaciones:

- **No concluyente:** el kernel cuántico no se separó de los baselines bajo el protocolo.
- **Prometedor:** mejoró la métrica primaria, pero faltan folds, estabilidad o un intervalo separado de cero.
- **Elegible para revisión:** pasó todas las puertas preregistradas; todavía no está promovido.

Nunca escribir “ventaja cuántica” a partir de esta simulación.

## Próxima decisión

- mantener sin cambios y esperar un nuevo fold;
- diseñar una revisión nueva y justificarla antes de ejecutarla;
- repetir en otro universo temporal independiente;
- probar hardware como experimento de robustez, no como reemplazo silencioso.


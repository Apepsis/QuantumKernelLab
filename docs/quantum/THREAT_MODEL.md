# Threat Model

| Amenaza | Consecuencia | Control implementado |
| --- | --- | --- |
| Look-ahead leakage | Backtest artificialmente alto | Walk-forward y doble purga igual al horizonte |
| Preprocesamiento global | Información futura en PCA o escalado | Ajuste exclusivo en fit |
| P-hacking | Selección del circuito que mejor vio test | Config versionado y nueva ID para cambios |
| Baseline desigual | Comparación inválida | Mismas filas, mismas variables y particiones |
| Corrida sobrescrita | Pérdida de evidencia negativa | Historial por huella SHA-256 |
| Resultado de muestra mostrado como real | Engaño en la interfaz | `mode=protocol`, arrays vacíos y etiqueta explícita |
| Promoción accidental | Modelo inestable pasa a producción | `automaticPromotion=false` en código y config |
| Secreto expuesto | Abuso de API | Ninguna credencial en JSON; GitHub Secrets y Cloudflare |
| Dependencia comprometida | Ejecución maliciosa | Versiones fijadas y workflow manual |
| Costo explosivo | Runner agotado | Límite de filas, cuatro qubits y timeout de 120 minutos |
| Drift de mercado | Métricas históricas irrelevantes | Reevaluación por folds nuevos, sin reescribir pasado |

## Respuesta a fallos

- Si una dependencia falla, el workflow termina sin publicar.
- Si faltan datos, no se rellenan resultados ficticios.
- Si el bootstrap no se puede calcular, la puerta estadística falla.
- Si un resultado parece extraordinario, se repite en una corrida archivada antes de cambiar el protocolo.


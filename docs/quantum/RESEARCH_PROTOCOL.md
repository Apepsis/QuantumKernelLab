# Protocolo preregistrado Q1

## Pregunta

¿Un kernel cuántico de fidelidad basado en `ZZFeatureMap` reduce el Brier score fuera de muestra al estimar la probabilidad de que una acción supere a SPY, frente a regresión logística y SVM-RBF, sin utilizar información futura?

## Estado

- Experimento: `quantum-kernel-shadow-v1`.
- Rol: `shadow-challenger`.
- Backend inicial: simulación exacta de estado.
- Publicación: manual y desactivada por defecto.
- Promoción: revisión humana obligatoria; jamás automática.
- Uso financiero: investigación; no ejecuta operaciones ni es asesoría.

## Objetivo y horizontes

Para cada activo y fecha `t`, la etiqueta para un horizonte `h` es:

```text
y(t,h) = 1 si retorno_activo(t,t+h) - retorno_SPY(t,t+h) > 0
         0 en caso contrario
```

Se evalúan 5, 20 y 60 sesiones. La predicción es una probabilidad calibrada, no una recomendación de compra.

## Variables

Se utilizan quince variables disponibles hasta la fecha de observación:

- retornos a 5, 20 y 60 sesiones;
- distancia a SMA 50 y SMA 200;
- RSI 14;
- volatilidad a 20 y 60 sesiones;
- drawdown a 252 sesiones;
- volumen normalizado a 20 sesiones;
- retornos de SPY a 20 y 60 sesiones;
- distancia de SPY a SMA 200;
- volatilidad de SPY a 60 sesiones;
- beta a 60 sesiones.

No se incluyen fundamentales con fechas corregidas retroactivamente ni noticias cuyo sello temporal no pueda auditarse.

## División temporal

La validación es *expanding walk-forward* por año. En cada fold:

1. El conjunto `fit` contiene solamente años anteriores.
2. Se eliminan `h` sesiones antes del conjunto de calibración.
3. `calibration` ajusta Platt sin tocar el año de prueba.
4. Se eliminan otras `h` sesiones antes de `test`.
5. El año de prueba se usa una sola vez para evaluación.

La doble purga evita que una etiqueta calculada con un retorno futuro cruce el límite de una partición.

## Preprocesamiento

`StandardScaler`, PCA y cuantiles de mapeo se ajustan solo en `fit`. Las cuatro componentes se recortan con cuantiles 1% y 99% de `fit` y se proyectan al intervalo `[0, pi]`. Ninguna transformación se vuelve a ajustar con calibración o prueba.

## Modelos

### Baseline 1: regresión logística

`C=1`, máximo 2000 iteraciones, semilla fija. Su salida probabilística es el baseline lineal interpretable.

### Baseline 2: SVM-RBF

`C=1`, `gamma=scale`. Sus márgenes se calibran con regresión logística de Platt en el conjunto independiente de calibración.

### Challenger: kernel cuántico ZZ

Las cuatro componentes alimentan cuatro qubits. `ZZFeatureMap`, dos repeticiones y entrelazado lineal construyen `|phi(x)>`. El kernel es

```text
K(x,z) = |<phi(x)|phi(z)>|^2
```

`FidelityStatevectorKernel` calcula la matriz exacta y un SVC de kernel precomputado aprende el separador. Sus márgenes también se calibran con Platt.

## Muestreo y costo

Una matriz kernel crece cuadráticamente. El protocolo limita por fold:

- 240 filas de fit;
- 96 filas de calibración;
- 120 filas de prueba;
- 3 folds por horizonte.

El muestreo es determinista, balancea clases cuando es posible y conserva cobertura temporal. La misma muestra se entrega a todos los modelos.

## Métricas primarias y secundarias

- Primaria: Brier score, menor es mejor.
- Secundarias: log-loss, ROC-AUC, ECE, accuracy y balanced accuracy.
- Incertidumbre: bootstrap pareado por fecha, 1000 iteraciones.

El remuestreo por fecha conserva la sección transversal observada el mismo día.

## Puertas de promoción

El resultado solamente queda **elegible para revisión** si:

1. completa al menos tres folds;
2. gana en Brier al menos 0.002;
3. no empeora ECE más de 0.01;
4. el límite superior del IC 95% del delta Brier queda bajo cero;
5. pasa en al menos dos de tres horizontes.

Incluso si pasa todas las puertas, `automaticPromotion` permanece en `false`.

## Reglas de integridad

- No cambiar hiperparámetros después de observar el test de esta revisión.
- Cualquier nuevo diseño crea un `experimentName` distinto.
- No reemplazar una corrida anterior; archivar por huella SHA-256.
- No describir un resultado de simulador como ventaja cuántica.
- Registrar resultados negativos y fallos de infraestructura.


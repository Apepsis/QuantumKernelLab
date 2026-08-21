# Data Card - Quantum Kernel Lab

## Origen

El laboratorio consume `research_work/feature_store.json`, generado por `scripts/build_feature_store.py` a partir de los datos históricos ya recopilados por el proyecto. No requiere claves cuánticas ni credenciales de IBM para la simulación exacta.

## Unidad de observación

Una fila corresponde a `(fecha, ticker)`. La fecha debe ser una sesión de mercado y cada variable debe haber sido observable en esa fecha.

## Cobertura mínima

El pipeline necesita años suficientes para construir fit, calibración, dos zonas purgadas y un año completo de prueba. Una corrida sin folds válidos debe fallar o mostrarse como incompleta, nunca como evidencia positiva.

## Calidad

Se eliminan filas con valores ausentes en las quince variables o en la etiqueta del horizonte. El artefacto final registra:

- hash del feature store;
- periodos de fit, calibración y test;
- número de filas por partición;
- varianza explicada por PCA;
- cuantiles usados para mapear ángulos;
- versión del software y circuito.

## Sesgos y limitaciones

- sesgo de supervivencia si el universo solo contiene empresas vigentes;
- ajustes corporativos incompletos;
- calidad y cobertura diferentes entre tickers;
- historia corta para regímenes extremos;
- selección previa del universo;
- timestamps corregidos retroactivamente.

## Datos que no deben entrar

- retorno futuro o etiqueta como variable;
- estadísticas normalizadas con toda la historia;
- datos macro revisados sin fecha de publicación original;
- noticias posteriores al cierre de la observación;
- resultados del test usados para elegir el circuito.


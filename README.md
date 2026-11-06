# analisis_costos_hospital

Proyecto para portafolio de análisis de costos que simula el control de costos de un hospital ya que trabajé en uno.
Compara costos reales contra presupuesto con filtros por departamento o categoría, calcula el costo por atención y detecta desviaciones.

## Los datos mostrados son SINTÉTICOS generados con python por lo que no encontrarás aquí información real del hospital donde trabajé.

## Qué demuestra
- Diseño de una base de datos relacional en MySQL
- Consultas SQL para análisis de costos (agregaciones, joins, desviaciones)
- Automatización de reportes con Python (pandas)
- Dashboard interactivo con Streamlit *(en desarrollo)*

## Tecnologías
Python · pandas · MySQL · Streamlit · Git

## Cómo ejecutarlo
1. Clona el repositorio e instala dependencias:
   pip install -r requirements.txt
2. Genera los datos:
   python generar_dataset.py
3. Ejecuta `sql/schema.sql` en MySQL e importa los CSV de `data/`.

## Conclusiones

- Mantenimiento en Hospitalización se desvió entre 25% y 55% del presupuesto de junio a diciembre de 2024, con tendencia creciente y un - sobrecosto acumulado cercano a $315,000.
- Se detectaron dos picos puntuales: material de curación en Quirófano (jul 2023) y medicamentos en Farmacia (mar 2024).
- El presupuesto no considera la estacionalidad invernal, lo que genera desviaciones del 20% en diciembre y enero en varios departamentos.
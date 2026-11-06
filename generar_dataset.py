"""Generador de dataset de costos hospitalarios"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)
OUT = Path("data")
OUT.mkdir(exist_ok=True)

# ------------------------------------------------------------------ catálogos
departamentos = pd.DataFrame(
    [
        (1, "Urgencias", "Clínico", 1800),
        (2, "Hospitalización", "Clínico", 900),
        (3, "Quirófano", "Clínico", 350),
        (4, "Laboratorio", "Apoyo", 4200),
        (5, "Imagenología", "Apoyo", 1500),
        (6, "Farmacia", "Apoyo", 5000),
        (7, "Consulta externa", "Clínico", 3000),
        (8, "Administración", "Administrativo", 0),
    ],
    columns=["departamento_id", "nombre", "tipo", "atenciones_base_mes"],
)

categorias = pd.DataFrame(
    [
        (1, "Personal"),
        (2, "Medicamentos"),
        (3, "Material de curación"),
        (4, "Mantenimiento"),
        (5, "Servicios generales"),
    ],
    columns=["categoria_id", "nombre"],
)

# Costo mensual base (MXN) por categoría para un departamento "promedio"
costo_base_categoria = {1: 450_000, 2: 220_000,
                        3: 90_000, 4: 60_000, 5: 45_000}

# Multiplicador de tamaño por departamento
escala_depto = {1: 1.4, 2: 1.8, 3: 1.6, 4: 0.9, 5: 0.8, 6: 1.1, 7: 1.0, 8: 0.6}

# Departamentos que casi no consumen cierta categoría
sin_consumo = {(8, 2), (8, 3), (4, 2), (5, 2)}

# ---------------------------------------------------------------- periodos
meses = pd.date_range("2023-01-01", "2024-12-01", freq="MS")

# Estacionalidad: más demanda en invierno (enfermedades respiratorias)
estacionalidad = {1: 1.15, 2: 1.08, 3: 1.0, 4: 0.97, 5: 0.95, 6: 0.97,
                  7: 1.0, 8: 1.0, 9: 1.02, 10: 1.05, 11: 1.08, 12: 1.15}

# ---------------------------------------------------------------- atenciones
filas_aten = []
for fecha in meses:
    for _, d in departamentos.iterrows():
        if d.atenciones_base_mes == 0:
            continue
        n = d.atenciones_base_mes * estacionalidad[fecha.month]
        n *= rng.normal(1.0, 0.05)
        filas_aten.append((fecha.date(), d.departamento_id, int(n)))
atenciones = pd.DataFrame(
    filas_aten, columns=["mes", "departamento_id", "num_atenciones"])

# ---------------------------------------------------------------- costos
inflacion_mensual = 0.004  # ~5% anual
filas_costos = []
for i, fecha in enumerate(meses):
    inflacion = (1 + inflacion_mensual) ** i
    for dep_id, escala in escala_depto.items():
        for cat_id, base in costo_base_categoria.items():
            if (dep_id, cat_id) in sin_consumo:
                continue
            # El presupuesto se fija con inflación, sin estacionalidad
            presupuesto = base * escala * inflacion
            # El costo real sí sigue la demanda, con ruido; personal casi no varía
            sensibilidad = 0.15 if cat_id == 1 else 1.0
            factor_demanda = 1 + \
                (estacionalidad[fecha.month] - 1) * sensibilidad
            real = presupuesto * factor_demanda * rng.normal(1.0, 0.04)
            filas_costos.append(
                [fecha.date(), dep_id, cat_id, real, presupuesto])

costos = pd.DataFrame(
    filas_costos,
    columns=["mes", "departamento_id", "categoria_id",
             "monto_real", "monto_presupuesto"],
)

# ---------------------------------------------------------------- anomalías
# Casos escondidos para que tu análisis tenga "hallazgos" que contar.


def inyectar(fecha_mes, dep, cat, factor):
    m = (costos.mes == pd.Timestamp(fecha_mes).date()) & (
        costos.departamento_id == dep) & (costos.categoria_id == cat)
    costos.loc[m, "monto_real"] *= factor


# pico de material de curación en Quirófano
inyectar("2023-07-01", 3, 3, 1.6)
inyectar("2024-03-01", 6, 2, 1.45)   # sobreprecio de medicamentos en Farmacia
for mes in pd.date_range("2024-06-01", "2024-12-01", freq="MS"):
    # mantenimiento de Hospitalización se dispara 7 meses
    inyectar(mes, 2, 4, 1.35)

costos["monto_real"] = costos["monto_real"].round(2)
costos["monto_presupuesto"] = costos["monto_presupuesto"].round(2)
costos.insert(0, "costo_id", range(1, len(costos) + 1))

# ---------------------------------------------------------------- exportar
departamentos.drop(columns="atenciones_base_mes").to_csv(
    OUT / "departamentos.csv", index=False)
categorias.to_csv(OUT / "categorias_costo.csv", index=False)
atenciones.to_csv(OUT / "atenciones.csv", index=False)
costos.to_csv(OUT / "costos.csv", index=False)

schema = """\
CREATE DATABASE IF NOT EXISTS costos_hospital;
USE costos_hospital;
 
CREATE TABLE departamentos (
    departamento_id INT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    tipo VARCHAR(30) NOT NULL
);
 
CREATE TABLE categorias_costo (
    categoria_id INT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL
);
 
CREATE TABLE atenciones (
    mes DATE NOT NULL,
    departamento_id INT NOT NULL,
    num_atenciones INT NOT NULL,
    PRIMARY KEY (mes, departamento_id),
    FOREIGN KEY (departamento_id) REFERENCES departamentos(departamento_id)
);
 
CREATE TABLE costos (
    costo_id INT PRIMARY KEY,
    mes DATE NOT NULL,
    departamento_id INT NOT NULL,
    categoria_id INT NOT NULL,
    monto_real DECIMAL(14,2) NOT NULL,
    monto_presupuesto DECIMAL(14,2) NOT NULL,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(departamento_id),
    FOREIGN KEY (categoria_id) REFERENCES categorias_costo(categoria_id)
);
"""
(OUT / "schema.sql").write_text(schema, encoding="utf-8")

print(f"departamentos: {len(departamentos)} filas")
print(f"categorias_costo: {len(categorias)} filas")
print(f"atenciones: {len(atenciones)} filas")
print(f"costos: {len(costos)} filas")
print(f"Archivos guardados en {OUT.resolve()}")

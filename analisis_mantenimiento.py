"""
Conecta a MySQL, trae la desviación mensual contra presupuesto de
Mantenimiento en Hospitalización y la grafica.

Requiere un archivo .env con: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
"""
import os
from pathlib import Path
from urllib.parse import quote_plus

import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ------------------------------------------------------------ conexión
load_dotenv()
usuario = os.getenv("DB_USER")
password = quote_plus(os.getenv("DB_PASSWORD", ""))  # protege caracteres especiales
host = os.getenv("DB_HOST", "127.0.0.1")
puerto = os.getenv("DB_PORT", "3306")
base = os.getenv("DB_NAME", "costos_hospital")

engine = create_engine(f"mysql+pymysql://{usuario}:{password}@{host}:{puerto}/{base}")

# ------------------------------------------------------------ consulta
QUERY = text("""
    SELECT
        c.mes,
        c.monto_presupuesto,
        c.monto_real,
        ROUND((c.monto_real - c.monto_presupuesto) / c.monto_presupuesto * 100, 2) AS desviacion_pct
    FROM costos AS c
    JOIN departamentos AS d ON d.departamento_id = c.departamento_id
    JOIN categorias_costo AS cc ON cc.categoria_id = c.categoria_id
    WHERE d.nombre = 'Hospitalización'
      AND cc.nombre = 'Mantenimiento'
    ORDER BY c.mes
""")

df = pd.read_sql(QUERY, engine)
df["mes"] = pd.to_datetime(df["mes"])
df["desviacion_pct"] = df["desviacion_pct"].astype(float)
print(df)

# ------------------------------------------------------------ gráfica
UMBRAL = 20
colores = ["#d62728" if v > UMBRAL else "#9aa5b1" for v in df["desviacion_pct"]]

fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(df["mes"].dt.strftime("%b %Y"), df["desviacion_pct"], color=colores)
ax.axhline(0, color="black", linewidth=0.8)
ax.axhline(UMBRAL, color="#d62728", linestyle="--", linewidth=1, label=f"Umbral {UMBRAL}%")
ax.set_title("Mantenimiento en Hospitalización: desviación vs. presupuesto")
ax.set_ylabel("Desviación (%)")
ax.legend()
plt.xticks(rotation=60, ha="right")
plt.tight_layout()

Path("images").mkdir(exist_ok=True)
plt.savefig("images/mantenimiento_hospitalizacion.png", dpi=150)
plt.show()

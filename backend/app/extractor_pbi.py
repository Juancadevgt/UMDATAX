import httpx
import pandas as pd
from datetime import datetime
import os


POWER_AUTOMATE_URL = "https://defaultbbd2639526d1499fa8a1ea5f2f9165.69.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/b90f312ce5964b72b6bf17b56d595068/triggers/manual/paths/invoke?api-version=1"


async def extraer_datos_pbi(url: str, reporte_nombre: str = "reporte"):
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            print(f"Llamando Power Automate...")
            resp = await client.post(
                POWER_AUTOMATE_URL,
                json={"reporte": reporte_nombre},
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text[:500]}")

            if resp.status_code != 200:
                return None

            data = resp.json()
            filas = _extraer_filas(data)
            print(f"Filas: {len(filas)}")

            if not filas:
                return None

            df = pd.DataFrame(filas)
            return _guardar_excel_pbi(df, reporte_nombre)

    except Exception as e:
        print(f"Error: {e}")
        return None


def _extraer_filas(dato: dict) -> list:
    filas = []
    try:
        # Power Automate devuelve los datos en "Results" o "value"
        resultados = dato.get("Results", dato.get("results", dato.get("value", [])))
        
        if isinstance(resultados, list):
            for fila in resultados:
                if isinstance(fila, dict):
                    filas.append(fila)
        elif isinstance(resultados, dict):
            tablas = resultados.get("Tables", resultados.get("tables", []))
            for tabla in tablas:
                rows = tabla.get("Rows", tabla.get("rows", []))
                cols = tabla.get("Columns", tabla.get("columns", []))
                col_names = [c.get("Name", f"col{i}") for i, c in enumerate(cols)]
                for row in rows:
                    if isinstance(row, list):
                        fila = {col_names[i]: v for i, v in enumerate(row) if i < len(col_names)}
                    else:
                        fila = row
                    filas.append(fila)

        print(f"Estructura dato: {list(dato.keys())}")
    except Exception as e:
        print(f"Error filas: {e}")
    return filas


def _guardar_excel_pbi(df: pd.DataFrame, nombre: str) -> str:
    carpeta = "/tmp/procesados_umdatax"
    os.makedirs(carpeta, exist_ok=True)
    nombre_limpio = nombre.replace(" ", "_").upper()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"PBI_{nombre_limpio}_{timestamp}.xlsx"
    ruta = os.path.join(carpeta, nombre_archivo)
    df.to_excel(ruta, index=False)
    return ruta
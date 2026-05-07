import httpx
import pandas as pd
from datetime import datetime
import os


async def extraer_datos_pbi(url: str, reporte_nombre: str = "reporte"):
    # El ResourceKey real del reporte (capturado del browser)
    resource_key = "13ca6812-f215-4bd6-90c7-85a8acfd6a2c"

    api_url = "https://wabi-paas-1-scus-api.analysis.windows.net/public/reports/querydata?synchronous=true"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://app.fabric.microsoft.com",
        "Referer": "https://app.fabric.microsoft.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/147.0.0.0 Safari/537.36",
        "X-PowerBI-ResourceKey": resource_key,
    }

    payload = {
        "version": "1.0.0",
        "queries": [{
            "Query": {
                "Commands": [{
                    "SemanticQueryDataShapeCommand": {
                        "Query": {
                            "Version": 2,
                            "From": [
                                {"Name": "w", "Entity": "wms_pallet_position", "Type": 0},
                                {"Name": "c", "Entity": "wms_movimientos_inventario", "Type": 0},
                                {"Name": "p", "Entity": "PRODUCTO", "Type": 0},
                                {"Name": "m", "Entity": "MEDIDAS", "Type": 0}
                            ],
                            "Select": [
                                {"Column": {"Expression": {"SourceRef": {"Source": "w"}}, "Property": "TipoUbicacion"}, "Name": "wms_pallet_position.TipoUbicacion"},
                                {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "Producto"}, "Name": "wms_movimientos_inventario.Producto"},
                                {"Column": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": "GLOSA"}, "Name": "PRODUCTO.GLOSA"},
                                {"Column": {"Expression": {"SourceRef": {"Source": "w"}}, "Property": "CodigoCompuesto"}, "Name": "wms_pallet_position.CodigoCompuesto"},
                                {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "SALDO ACTUAL"}, "Name": "MEDIDAS.SALDO ACTUAL"},
                                {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "FECHA ULTIMO MOVIMIENTO"}, "Name": "MEDIDAS.FECHA ULTIMO MOVIMIENTO"}
                            ]
                        },
                        "Binding": {
                            "Primary": {"Groupings": [{"Projections": [0,1,2,3,4,5], "Subtotal": 1}]},
                            "DataReduction": {"DataVolume": 3, "Primary": {"Window": {"Count": 500}}},
                            "Version": 1
                        },
                        "ExecutionMetricsKind": 1
                    }
                }]
            },
            "QueryId": "",
            "ApplicationContext": {"DatasetId": "", "Sources": [{"ReportId": "", "VisualId": ""}]}
        }],
        "cancelQueries": [],
        "modelId": 6068825
    }

    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            print(f"Llamando API con ResourceKey: {resource_key}")
            resp = await client.post(api_url, json=payload, headers=headers)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text[:300]}")

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
        for result in dato.get("results", []):
            ds = result.get("result", {}).get("data", {}).get("dsr", {}).get("DS", [])
            for tabla in ds:
                for ph in tabla.get("PH", []):
                    for dm in ph.get("DM0", []):
                        fila = {k: v for k, v in dm.items() if k != "R"}
                        if fila:
                            filas.append(fila)
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
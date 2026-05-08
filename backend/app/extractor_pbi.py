import httpx
import pandas as pd
from datetime import datetime
import os


async def extraer_datos_pbi(url: str, reporte_nombre: str = "reporte"):
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
            resp = await client.post(api_url, json=payload, headers=headers)
            print(f"Status: {resp.status_code}")

            if resp.status_code != 200:
                return None

            data = resp.json()
            filas = _extraer_filas(data)
            print(f"Filas extraidas: {len(filas)}")

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
            data = result.get("result", {}).get("data", {})
            dsr = data.get("dsr", {})
            descriptor = data.get("descriptor", {})

            # Nombres reales de columnas desde descriptor
            col_names = []
            for sel in descriptor.get("Select", []):
                col_names.append(sel.get("Name", sel.get("Value", f"col{len(col_names)}")))

            print(f"Columnas: {col_names}")

            for ds in dsr.get("DS", []):
                value_dicts = ds.get("ValueDicts", {})

                for ph in ds.get("PH", []):
                    # DM1 tiene los datos reales (DM0 es el subtotal)
                    dm_list = ph.get("DM1", ph.get("DM0", []))

                    # Schema de la primera fila
                    schema = []
                    prev_valores = {}

                    for dm in dm_list:
                        # Actualizar schema si existe
                        if "S" in dm:
                            schema = dm["S"]

                        valores = dm.get("C", [])
                        r_flags = dm.get("R", 0)

                        # Construir fila aplicando R flags (bits que indican valores repetidos)
                        fila_actual = dict(prev_valores)

                        col_idx = 0
                        val_idx = 0

                        for s_idx, s in enumerate(schema):
                            col_key = s.get("N", f"col{s_idx}")

                            # Verificar si este campo se repite del anterior (R flag)
                            if r_flags & (1 << s_idx):
                                # Mantener valor anterior
                                pass
                            else:
                                if val_idx < len(valores):
                                    val = valores[val_idx]
                                    # Resolver diccionario si aplica
                                    dn = s.get("DN", "")
                                    if dn and dn in value_dicts and isinstance(val, int):
                                        val = value_dicts[dn][val]
                                    fila_actual[col_key] = val
                                    val_idx += 1

                        # Mapear claves internas a nombres reales
                        fila_final = {}
                        key_map = {s.get("N"): col_names[i] if i < len(col_names) else s.get("N")
                                   for i, s in enumerate(schema)}

                        for k, v in fila_actual.items():
                            nombre_col = key_map.get(k, k)
                            fila_final[nombre_col] = v

                        if fila_final:
                            filas.append(fila_final)
                            prev_valores = fila_actual

    except Exception as e:
        import traceback
        print(f"Error filas: {e}")
        print(traceback.format_exc())
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
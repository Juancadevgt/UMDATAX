import httpx
import pandas as pd
from datetime import datetime
import os
import re


async def extraer_datos_pbi(url: str, reporte_nombre: str = "reporte"):
    # Extraer el token r= de la URL
    match = re.search(r'[?&]r=([^&]+)', url)
    if not match:
        return None
    
    token = match.group(1)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Origin": "https://app.fabric.microsoft.com",
        "Referer": url,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Obtener metadata del reporte
        meta_url = f"https://app.fabric.microsoft.com/view?r={token}"
        resp = await client.get(meta_url, headers=headers)
        
        # 2. Buscar el embed URL real en el HTML
        embed_match = re.search(r'"embedUrl":"([^"]+)"', resp.text)
        config_match = re.search(r'"reportId":"([^"]+)"', resp.text)
        
        if not embed_match:
            return None
            
        embed_url = embed_match.group(1).replace("\\u0026", "&")
        
        # 3. Obtener los datos del reporte via API interna
        api_url = f"https://wabi-west-europe-b-primary-redirect.analysis.windows.net/public/reports/querydata"
        
        payload = {
            "version": "1.0.0",
            "queries": [{
                "Query": {
                    "Commands": [{
                        "SemanticQueryDataShapeCommand": {
                            "Query": {
                                "Version": 2,
                                "From": [{"Name": "t", "Entity": "Table", "Type": 0}],
                                "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": "*"}, "Name": "t.*"}]
                            }
                        }
                    }]
                }
            }]
        }

        try:
            data_resp = await client.post(api_url, json=payload, headers={
                **headers,
                "Content-Type": "application/json",
                "X-PowerBI-ResourceKey": token
            })
            
            if data_resp.status_code == 200:
                data = data_resp.json()
                filas = _extraer_filas(data)
                if filas:
                    df = pd.DataFrame(filas)
                    return _guardar_excel_pbi(df, reporte_nombre)
        except Exception as e:
            print(f"Error API: {e}")
    
    return None


def _extraer_filas(dato: dict) -> list:
    filas = []
    try:
        if "results" in dato:
            for result in dato["results"]:
                tablas = result.get("result", {}).get("data", {}).get("dsr", {}).get("DS", [])
                for tabla in tablas:
                    for ph in tabla.get("PH", []):
                        for dm in ph.get("DM0", []):
                            fila = {k: v for k, v in dm.items() if k != "R"}
                            if fila:
                                filas.append(fila)
        elif "tables" in dato:
            for tabla in dato["tables"]:
                filas.extend(tabla.get("rows", []))
    except Exception:
        pass
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
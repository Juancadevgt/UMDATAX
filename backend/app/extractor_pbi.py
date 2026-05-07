import asyncio
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
import os


async def extraer_datos_pbi(url: str, reporte_nombre: str = "reporte") -> str:
    datos_capturados = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        async def capturar_respuesta(response):
            try:
                if any(k in response.url for k in ["querydata", "executeQueries", "models", "datasetExecuteQueries"]):
                    content_type = response.headers.get("content-type", "")
                    if "json" in content_type:
                        body = await response.json()
                        datos_capturados.append(body)
            except Exception:
                pass

        page.on("response", capturar_respuesta)

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Error navegando: {e}")
        finally:
            await browser.close()

    filas = []
    for dato in datos_capturados:
        filas.extend(_extraer_filas(dato))

    if not filas:
        return None

    df = pd.DataFrame(filas)
    return _guardar_excel_pbi(df, reporte_nombre)


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


def extraer_pbi_sync(url: str, reporte_nombre: str = "reporte") -> str:
    return asyncio.run(extraer_datos_pbi(url, reporte_nombre))
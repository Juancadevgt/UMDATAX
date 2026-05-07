import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
import os


async def extraer_datos_pbi(url: str, reporte_nombre: str = "reporte"):
    datos_capturados = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/147.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Interceptar ANTES de navegar
        async def capturar_respuesta(response):
            try:
                if "querydata" in response.url and response.status == 200:
                    print(f"Capturando: {response.url}")
                    text = await response.text()
                    print(f"Respuesta (primeros 200 chars): {text[:200]}")
                    import json
                    body = json.loads(text)
                    datos_capturados.append(body)
            except Exception as e:
                print(f"Error capturando respuesta: {e}")

        page.on("response", capturar_respuesta)

        try:
            print(f"Navegando a: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print("DOM cargado, esperando datos...")
            await page.wait_for_timeout(15000)
            print(f"Datos capturados: {len(datos_capturados)}")
        except Exception as e:
            print(f"Error navegando: {e}")
        finally:
            await browser.close()

    filas = []
    for dato in datos_capturados:
        filas.extend(_extraer_filas(dato))

    print(f"Total filas: {len(filas)}")

    if not filas:
        return None

    df = pd.DataFrame(filas)
    return _guardar_excel_pbi(df, reporte_nombre)


def _extraer_filas(dato: dict) -> list:
    filas = []
    try:
        resultados = dato.get("results", [])
        for result in resultados:
            ds = result.get("result", {}).get("data", {}).get("dsr", {}).get("DS", [])
            for tabla in ds:
                for ph in tabla.get("PH", []):
                    for dm in ph.get("DM0", []):
                        fila = {k: v for k, v in dm.items() if k != "R"}
                        if fila:
                            filas.append(fila)
    except Exception as e:
        print(f"Error extrayendo filas: {e}")
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
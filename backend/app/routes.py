from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
import os

# 🔥 IMPORT CORRECTO
from ..extractor import (
    procesar_zip,
    procesar_xml_individual,
    guardar_excel
)

router = APIRouter()

@router.post("/procesar/")
async def procesar_archivo(
    file: UploadFile = File(...),
    tipo: str = Form(...),
    campos: str = Form(...)
):
    # -------------------------
    # 1. Guardar archivo temporal
    # -------------------------
    ruta_temp = f"temp_{file.filename}"

    with open(ruta_temp, "wb") as f:
        f.write(await file.read())

    # -------------------------
    # 2. Convertir campos a lista
    # -------------------------
    campos_lista = campos.split(",")

    # -------------------------
    # 3. Detectar tipo automáticamente
    # -------------------------
    if file.filename.lower().endswith(".zip"):
        datos, errores = procesar_zip(ruta_temp, campos_lista)
    else:
        datos, errores = procesar_xml_individual(ruta_temp, campos_lista)

    # -------------------------
    # 4. Generar Excel
    # -------------------------
    salida = guardar_excel(datos)

    # -------------------------
    # 5. Eliminar archivo temporal
    # -------------------------
    if os.path.exists(ruta_temp):
        os.remove(ruta_temp)

    # -------------------------
    # 6. Devolver archivo para descarga
    # -------------------------
    return FileResponse(
        path=salida,
        filename=os.path.basename(salida),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import traceback

from .extractor_pbi import extraer_datos_pbi

router_pbi = APIRouter()


class ReporteRequest(BaseModel):
    url: str
    nombre: str = "reporte"


@router_pbi.post("/exportar-pbi/")
async def exportar_reporte_pbi(data: ReporteRequest):
    if not data.url.startswith("https://app.fabric.microsoft.com"):
        raise HTTPException(status_code=400, detail="URL de reporte inválida")

    try:
        ruta_excel = await extraer_datos_pbi(data.url, data.nombre)
    except Exception as e:
        error_detalle = traceback.format_exc()
        print("ERROR COMPLETO:", error_detalle)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    if not ruta_excel or not os.path.exists(ruta_excel):
        raise HTTPException(
            status_code=404,
            detail="No se extrajeron datos. El reporte puede requerir login."
        )

    return FileResponse(
        path=ruta_excel,
        filename=os.path.basename(ruta_excel),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
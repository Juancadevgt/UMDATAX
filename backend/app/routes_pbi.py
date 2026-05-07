from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from .extractor_pbi import extraer_pbi_sync

router_pbi = APIRouter()


class ReporteRequest(BaseModel):
    url: str
    nombre: str = "reporte"


@router_pbi.post("/exportar-pbi/")
async def exportar_reporte_pbi(data: ReporteRequest):
    if not data.url.startswith("https://app.fabric.microsoft.com"):
        raise HTTPException(status_code=400, detail="URL de reporte inválida")

    try:
        ruta_excel = extraer_pbi_sync(data.url, data.nombre)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al extraer datos: {str(e)}")

    if not ruta_excel or not os.path.exists(ruta_excel):
        raise HTTPException(
            status_code=404,
            detail="No se pudieron extraer datos. Verifica que el reporte sea público."
        )

    return FileResponse(
        path=ruta_excel,
        filename=os.path.basename(ruta_excel),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
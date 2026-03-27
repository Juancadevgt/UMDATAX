import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import os
from datetime import datetime


def obtener_texto(nodo, etiqueta):
    if nodo is None:
        return None
    elemento = nodo.find("{*}" + etiqueta)
    return elemento.text if elemento is not None else None


def extraer_campos(root, campos_seleccionados):
    resultado = {}

    emisor = root.find(".//{*}Emisor")
    direccion = root.find(".//{*}DireccionEmisor")
    frases = root.findall(".//{*}Frase")

    for campo in campos_seleccionados:

        if campo in ["AfiliacionIVA", "CodigoEstablecimiento", "CorreoEmisor",
                     "NITEmisor", "NombreComercial", "NombreEmisor"]:
            resultado[campo] = emisor.get(campo) if emisor is not None else None

        elif campo == "Frases":
            lista = [
                f"{f.get('CodigoEscenario')}-{f.get('TipoFrase')}"
                for f in frases
            ]
            resultado[campo] = ", ".join(lista)

        else:
            resultado[campo] = obtener_texto(direccion, campo)

    return resultado


def procesar_xml(file, nombre_archivo, campos):
    try:
        tree = ET.parse(file)
        root = tree.getroot()

        registro = extraer_campos(root, campos)
        registro["archivo"] = nombre_archivo

        return registro
    except:
        return None


def procesar_zip(ruta, campos):
    datos, errores = [], []

    with zipfile.ZipFile(ruta, 'r') as zip_ref:
        for archivo in zip_ref.namelist():
            if archivo.lower().endswith(".xml"):
                try:
                    with zip_ref.open(archivo) as f:
                        reg = procesar_xml(f, archivo, campos)
                        if reg:
                            datos.append(reg)
                        else:
                            errores.append(archivo)
                except:
                    errores.append(archivo)

    return datos, errores


def procesar_xml_individual(ruta, campos):
    datos, errores = [], []

    try:
        with open(ruta, 'rb') as f:
            reg = procesar_xml(f, os.path.basename(ruta), campos)
            if reg:
                datos.append(reg)
            else:
                errores.append(ruta)
    except:
        errores.append(ruta)

    return datos, errores


import os
from datetime import datetime
import pandas as pd

def guardar_excel(datos):
    carpeta = "C:\\PROCESADOS_UMDATAX"

    # Crear carpeta si no existe
    os.makedirs(carpeta, exist_ok=True)

    # Nombre único
    nombre_archivo = f"procesado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    ruta_completa = os.path.join(carpeta, nombre_archivo)

    # Guardar Excel
    df = pd.DataFrame(datos)
    df.to_excel(ruta_completa, index=False)
    
    

    return ruta_completa


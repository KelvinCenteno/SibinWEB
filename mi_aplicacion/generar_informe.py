from docx import Document
from docx.shared import Inches, Pt
from docx2pdf import convert
import os
import tempfile
from datetime import datetime
import pythoncom

def reemplazar_texto(parrafo, marcador, texto, tamaño_fuente=None):
    if marcador in parrafo.text:
        nuevo_texto = parrafo.text.replace(marcador, texto)
        parrafo.clear()
        run = parrafo.add_run(nuevo_texto)
        if tamaño_fuente:
            run.font.size = Pt(tamaño_fuente)

def completar_plantilla(ruta_plantilla, ruta_salida, datos, ruta_qr):

    pythoncom.CoInitialize()
    
    try:
        doc = Document(ruta_plantilla)
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        hora_actual = datetime.now().strftime("%H:%M:%S")

        for parrafo in doc.paragraphs:
            for clave, valor in datos.items():
                reemplazar_texto(parrafo, clave, valor)
            reemplazar_texto(parrafo, "{{Fecha}}", fecha_actual, tamaño_fuente=8)
            reemplazar_texto(parrafo, "{{Hora}}", hora_actual, tamaño_fuente=8)

        for tabla in doc.tables:
            for fila in tabla.rows:
                for celda in fila.cells:
                    for parrafo in celda.paragraphs:
                        for clave, valor in datos.items():
                            reemplazar_texto(parrafo, clave, valor)
                        reemplazar_texto(parrafo, "{{Fecha}}", fecha_actual, tamaño_fuente=8)
                        reemplazar_texto(parrafo, "{{Hora}}", hora_actual, tamaño_fuente=8)

        for parrafo in doc.paragraphs:
            if "{{QRCode}}" in parrafo.text:
                parrafo.text = parrafo.text.replace("{{QRCode}}", "")
                parrafo.add_run().add_picture(ruta_qr, width=Inches(1.0))

        for tabla in doc.tables:
            for fila in tabla.rows:
                for celda in fila.cells:
                    for parrafo in celda.paragraphs:
                        if "{{QRCode}}" in parrafo.text:
                            parrafo.text = parrafo.text.replace("{{QRCode}}", "")
                            parrafo.add_run().add_picture(ruta_qr, width=Inches(1.0))

        for parrafo in doc.paragraphs:
            if "{{QRCode2}}" in parrafo.text:
                parrafo.text = parrafo.text.replace("{{QRCode2}}", "")
                parrafo.add_run().add_picture(ruta_qr, width=Inches(0.6))

        for tabla in doc.tables:
            for fila in tabla.rows:
                for celda in fila.cells:
                    for parrafo in celda.paragraphs:
                        if "{{QRCode2}}" in parrafo.text:
                            parrafo.text = parrafo.text.replace("{{QRCode2}}", "")
                            parrafo.add_run().add_picture(ruta_qr, width=Inches(0.6))

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
            temp_docx_path = temp_docx.name
        doc.save(temp_docx_path)

        convert(temp_docx_path, ruta_salida)

        os.remove(temp_docx_path)
    
    finally:
        pythoncom.CoUninitialize()

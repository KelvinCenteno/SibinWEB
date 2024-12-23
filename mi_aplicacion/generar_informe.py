from docx import Document
from docx.shared import Inches
from docx2pdf import convert
import os
import tempfile
from datetime import datetime

def reemplazar_texto(parrafo, marcador, texto):
    if marcador in parrafo.text:
        parrafo.text = parrafo.text.replace(marcador, texto)

def completar_plantilla(ruta_plantilla, ruta_salida, datos, ruta_qr):
    # Abre el documento de plantilla
    doc = Document(ruta_plantilla)
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    hora_actual = datetime.now().strftime("%H:%M:%S")

    # Reemplaza los marcadores con los datos proporcionados y con la fecha y hora actual
    for parrafo in doc.paragraphs:
        for clave, valor in datos.items():
            reemplazar_texto(parrafo, clave, valor)
        reemplazar_texto(parrafo, "{{Fecha}}", fecha_actual)
        reemplazar_texto(parrafo, "{{Hora}}", hora_actual)

    # Reemplazar marcadores en las tablas
    for tabla in doc.tables:
        for fila in tabla.rows:
            for celda in fila.cells:
                for parrafo in celda.paragraphs:
                    for clave, valor in datos.items():
                        reemplazar_texto(parrafo, clave, valor)
                    reemplazar_texto(parrafo, "{{Fecha}}", fecha_actual)
                    reemplazar_texto(parrafo, "{{Hora}}", hora_actual)

    # Inserta la imagen del código QR
    for parrafo in doc.paragraphs:
        if "{{QRCode}}" in parrafo.text:
            parrafo.text = parrafo.text.replace("{{QRCode}}", "")
            parrafo.add_run().add_picture(ruta_qr, width=Inches(1.0))

    # Reemplazar marcadores de imagen en las tablas
    for tabla in doc.tables:
        for fila in tabla.rows:
            for celda in fila.cells:
                for parrafo in celda.paragraphs:
                    if "{{QRCode}}" in parrafo.text:
                        parrafo.text = parrafo.text.replace("{{QRCode}}", "")
                        parrafo.add_run().add_picture(ruta_qr, width=Inches(1.0))

    # Guardar el documento completado temporalmente como Word
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
        temp_docx_path = temp_docx.name
    doc.save(temp_docx_path)

    # Convertir el documento Word a PDF
    convert(temp_docx_path, ruta_salida)

    # Eliminar el archivo temporal de Word
    os.remove(temp_docx_path)

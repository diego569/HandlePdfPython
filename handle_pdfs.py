import os
import shutil
import fitz
import io

def merge_pdfs(input_folder, output_path):
    pdf_output = fitz.open()
    pdf_count = 0  # Contador de archivos PDF encontrados

    for raiz, _, archivos in os.walk(input_folder):
        for nombre_archivo in archivos:
            if nombre_archivo.lower().endswith('.pdf'):
                pdf_count += 1
                ruta_archivo = os.path.join(raiz, nombre_archivo)
                pdf = fitz.open(ruta_archivo)
                pdf_output.insert_pdf(pdf)
                pdf.close()

    if pdf_count == 0:
        raise FileNotFoundError("No files found")
    
    pdf_output.save(output_path)
    pdf_output.close()

def merge2_pdfs(input_folder):
    pdf_output = fitz.open()
    pdf_count = 0
    for raiz, _, archivos in os.walk(input_folder):
        for nombre_archivo in archivos:
            if nombre_archivo.lower().endswith('.pdf'):
                pdf_count += 1
                ruta_archivo = os.path.join(raiz, nombre_archivo)
                pdf = fitz.open(ruta_archivo)
                pdf_output.insert_pdf(pdf)
                pdf.close()

    output_stream = io.BytesIO()

    if pdf_count == 0:
        raise FileNotFoundError("No files found")
    
    pdf_output.save(output_stream)
    pdf_output.close()
    output_stream.seek(0)

    return output_stream
# def mergue_pdfs(input_file, output_file):
#     pdf_salida = fitz.open()
#     for raiz, _, archivos in os.walk(input_file):
#         for nombre_archivo in archivos:
#             if nombre_archivo.lower().endswith('.pdf'):
#                 ruta_archivo = os.path.join(raiz, nombre_archivo)
#                 pdf = fitz.open(ruta_archivo)
#                 pdf_salida.insert_pdf(pdf)
#                 pdf.close()
#     pdf_salida.save(output_file)
#     pdf_salida.close()


def transfer_only_pdfs(input_file, output_file):
    for raiz, directorios, archivos in os.walk(input_file):
        for nombre_archivo in archivos:
            if nombre_archivo.lower().endswith('.pdf'):
                ruta_archivo_entrada = os.path.join(raiz, nombre_archivo)
                
                # Determinar la ruta de salida correspondiente
                ruta_relativa = os.path.relpath(raiz, input_file)
                ruta_directorio_salida = os.path.join(output_file, ruta_relativa)
                
                # Crear el directorio de salida si no existe
                if not os.path.exists(ruta_directorio_salida):
                    os.makedirs(ruta_directorio_salida)
                
                # Copiar el archivo PDF a la carpeta de salida manteniendo la estructura de carpetas
                ruta_archivo_salida = os.path.join(ruta_directorio_salida, nombre_archivo)
                shutil.copy2(ruta_archivo_entrada, ruta_archivo_salida)

# carpeta_entrada = 'E:/server project/quisvar_proyect_bk/uploads/reviews'
# carpeta_salida = 'E:/New folder/Dhyrium stuff/DOCS/PDFs Filtrados'
# copiar_pdfs(carpeta_entrada, carpeta_salida)
# print("Se copiaron los PDFs exitosamente")
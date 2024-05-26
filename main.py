import os
import uuid
import time
import io
import zipfile
from flask_cors import CORS
from flask import Flask, jsonify, request, send_file, url_for
from products import products
from handle_pdfs import transfer_only_pdfs, merge_pdfs, merge2_pdfs,compress_pdfs

##from string import Template

app = Flask(__name__)
CORS(app, expose_headers=["File-Name"])


@app.route("/")
def index():
    return "Flask is running!"


@app.route("/pdf")
def pdf():
    return jsonify({"message": "Gaaaaaaaa"})


@app.route("/users", methods=["POST"])
def users():
    print(request.get_json())
    return jsonify({"message": "Gaaaaaaaa"})


@app.route("/products")
def get_products():
    return jsonify({"status": True, "products": products})


@app.route("/products/<id>")
def get_products_by_id(id):
    print(id)
    product_finder = [product for product in products if product["id"] == id]
    if len(product_finder) > 0:
        return jsonify({"status": True, "product": product_finder[0]})
    else:
        return jsonify({"status": False, "messsage": "Producto no encontrado"})


@app.route("/products", methods=["POST"])
def create_product():

    product = request.get_json()
    print(product)
    products.append(product)
    return jsonify({"status": True})


@app.route("/products/<id>", methods=["PUT"])
def edit_products_by_id(id):
    print(id)
    product = request.get_json()
    print(product)
    product_finder = [product for product in products if product["id"] == id]
    if len(product_finder) > 0:
        product_finder[0]["name"] = product["name"]
        product_finder[0]["price"] = product["price"]
        product_finder[0]["quantity"] = product["quantity"]
        return jsonify({"status": True, "product": product_finder[0]})
    else:
        return jsonify({"status": False, "messsage": "Producto no encontrado"})


@app.route("/pdf/merge")
def merge_pdf():
    params = request.args
    input_folder = params.get("input_folder")
    print(input_folder)

    if not input_folder or not os.path.isdir(input_folder):
        return jsonify({"message": "Invalid or missing input folder"}), 400
    unique_id = uuid.uuid4()
    output_filename = f"{unique_id}.pdf"
    print(output_filename)
    output_path = os.path.join(os.getcwd(), output_filename)

    # Llama a la función para fusionar los PDFs y guardarlos en output_path
    try:
        merge_pdfs(input_folder, output_path)
    except FileNotFoundError as err:
        return jsonify({"message": str(err)}), 400
    # Construye la URL de descarga
    server_host = request.host_url  # Obtiene el host del servidor
    download_url = f"{server_host}download/{output_filename}"

    response = {"message": "PDFs merged successfully", "download_url": download_url}

    return jsonify(response)


@app.route("/pdf/merge2")
def merge2_pdf():
    params = request.args
    input_folder = params.get("input_folder")

    if not input_folder or not os.path.isdir(input_folder):
        return jsonify({"message": "Invalid or missing input folder"}), 400

    try:
        compressed_pdf_stream = compress_pdfs(input_folder)
    except FileNotFoundError as err:
        return jsonify({"message": str(err)}), 400


    return send_file(

        compressed_pdf_stream,
        download_name="merged.pdf",
        as_attachment=True,
        etag=False,
        max_age=0,
        mimetype="application/pdf",  # Esto asegura que el archivo no se almacene en la caché del cliente
    )
    # output_route = body['output_route']
    # mergue_pdfs(input_route,output_route)
    # print(body)
    # return send_file(output_route, as_attachment=True)
    # return jsonify({"status": True,"messsage":"El archivo se comprimio perfectamente"})


# @app.route('/download/<filename>', methods=['GET'])
# def download_file(filename):
#     # Asegúrate de que el archivo existe antes de enviarlo
#     file_path = os.path.join(os.getcwd(), filename)
#     if not os.path.isfile(file_path):
#         return jsonify({"message": "File not found"}), 404
#     return send_file(file_path, as_attachment=True)
@app.route("/pdf/compress")
def compress_pdf():
    params = request.args
    input_folder = params.get("input_folder")

    if not input_folder or not os.path.isdir(input_folder):
        return jsonify({"message": "Invalid or missing input folder"}), 400

    try:
        merged_pdf_stream = merge2_pdfs(input_folder)
    except FileNotFoundError as err:
        return jsonify({"message": str(err)}), 400


    return send_file(

        merged_pdf_stream,
        download_name="merged.pdf",
        as_attachment=True,
        etag=False,
        max_age=0,
        mimetype="application/pdf",  # Esto asegura que el archivo no se almacene en la caché del cliente
    )

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    # Asegúrate de que el archivo existe antes de enviarlo
    file_path = os.path.join(os.getcwd(), filename)
    if not os.path.isfile(file_path):
        return jsonify({"message": "File not found"}), 404

    try:
        # Envía el archivo
        response = send_file(file_path, as_attachment=True)
        response.direct_passthrough = False

        @response.call_on_close
        def remove_file():
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error al eliminar el archivo: {e}")

        return response

    except Exception as e:
        return jsonify({"message": f"Error al procesar el archivo: {e}"}), 500

@app.route('/descargar_carpeta')
def descargar_carpeta():
    params = request.args
    type = params.get("type") #1. pdf, 2. all, 3. nopdf
    input_folder = params.get("input_folder")
    print(type=='pdf')
    print('Esta es la ur muajaja',input_folder)
    # Ruta completa de la input_folder
    ruta_input_folder = os.path.abspath(input_folder)

    # Crear un objeto de BytesIO para almacenar el archivo ZIP en memoria
    memoria_zip = io.BytesIO()

    # Crear un archivo ZIP en memoria
    with zipfile.ZipFile(memoria_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Recorrer los archivos de la input_folder
        for root, dirs, files in os.walk(ruta_input_folder):
            for archivo in files:
                
                # Filtrar solo archivos PDF
                if (type=='pdf'):
                    if (archivo.endswith('.pdf')):
                        # Ruta completa del archivo
                        ruta_archivo = os.path.join(root, archivo)
                        # Agregar el archivo al archivo ZIP con su ruta relativa
                        zipf.write(ruta_archivo, os.path.relpath(ruta_archivo, ruta_input_folder))
                elif (type == 'nopdf'):
                    if not(archivo.endswith('.pdf')):
                        # Ruta completa del archivo
                        ruta_archivo = os.path.join(root, archivo)
                        # Agregar el archivo al archivo ZIP con su ruta relativa
                        zipf.write(ruta_archivo, os.path.relpath(ruta_archivo, ruta_input_folder))
                else:
                    ruta_archivo = os.path.join(root, archivo)
                    # Agregar el archivo al archivo ZIP con su ruta relativa
                    zipf.write(ruta_archivo, os.path.relpath(ruta_archivo, ruta_input_folder))


    # Ir al inicio del archivo ZIP en memoria
    memoria_zip.seek(0)

    # Devolver el archivo ZIP en memoria como respuesta al cliente
    return send_file(memoria_zip, download_name='input_folder_pdf.zip', as_attachment=True)

if __name__ == "__main__":
    context = ("cert.pem", "key.pem")  # certificate and key files
    app.run(host="0.0.0.0", port=5000, debug=True)

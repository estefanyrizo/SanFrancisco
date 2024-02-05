
import os
from flask import redirect, request, session
from functools import wraps
from flask.helpers import flash
from base64 import b64encode
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import docraptor

ik = ImageKit(private_key='private_pbBN7H3s6r1YGqTsxPQqdelGb38=',
                public_key='public_rKkJyqI11fEPBRHq/2QD3PyJJwo=',
                url_endpoint='https://ik.imagekit.io/JefferssonVMT')

doc_api = docraptor.DocApi()
doc_api.api_client.configuration.username = '23md2lJdruKB9SQuJ2Pj'

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin") == 1:
            return """<h3 class="p-5" style="
            color: red;
            margin: 2%;
            font-size: 6vh;
            width: fit-content;
            ">No tienes permiso para acceder a este recurso</h3>""", 403
        return f(*args, **kwargs)
    return decorated_function


def validarString(dato):
    if not dato or not dato.isalpha() or dato.isspace():
        return False

    return True


def validarDouble(dato):
    if not dato or not dato.replace(".", "").isdigit() or float(dato) < 1:
        return False

    return True


def subirImagen(imagen, folderimg):

    imagen = b64encode(request.files["foto"].stream.read())
    # Al codificarla, se agrega una letra y una comilla al inicio del texto, tambien una comilla al fina
    # str(imagen)[2:len(imagen)] omito los primeros 2 caracteres y el ultimo

    imagen = str(imagen)[2:len(imagen)]

    # return f'<img src="data:image/png;base64,{imagen}">'
    # print(imagen)

    res = ik.upload(file=imagen, file_name=request.form.get(
        "codigo"), options=UploadFileRequestOptions(folder=f"Ganado/{folderimg}"))
    # El options es opcional de ponerlo y tiene varios parametros configurables, util como para custom_metadata = {"marca": "Gucci", "color":"rojo"}
    # print(res.url)
    # El url listo para guardar en la base de datos y mostrarlo en el html desde el link

    # print(res.response_metadata.raw)
    return res.url


def subirArchivo(archivo, nombre, folder):
    archivo = b64encode(request.files["file"].stream.read())
    # Al codificarla, se agrega una letra y una comilla al inicio del texto, tambien una comilla al fina
    # str(imagen)[2:len(imagen)] omito los primeros 2 caracteres y el ultimo

    archivo = str(archivo)[2:len(archivo)]

    # return f'<img src="data:image/png;base64,{imagen}">'
    # print(imagen)

    res = ik.upload(file=archivo, file_name=nombre, options= UploadFileRequestOptions(folder=folder))
    # El options es opcional de ponerlo y tiene varios parametros configurables, util como para custom_metadata = {"marca": "Gucci", "color":"rojo"}
    # print(res.url)
    # El url listo para guardar en la base de datos y mostrarlo en el html desde el link

    # print(res.response_metadata.raw)
    return res.url

def crearpdf(hmtlcode):

    """ options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8"
    }
    config = pdfkit.configuration()

    pdf = pdfkit.from_string(hmtlcode)
    return pdf """

    response = doc_api.create_doc({
        "test": True,                                                   # test documents are free but watermarked
        "document_content": hmtlcode,    # supply content directly
        # "document_url": "http://docraptor.com/examples/invoice.html", # or use a url
        "name": "reporte.pdf",                                 # help you find a document later
        "document_type": "pdf",                                         # pdf or xls or xlsx
        # "javascript": True,                                           # enable JavaScript processing
        # "prince_options": {
        #   "media": "screen",                                          # use screen styles instead of print styles
        #   "baseurl": "http://hello.com",                              # pretend URL when using document_content
        # },
    })

    return response
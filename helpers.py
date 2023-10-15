
import os
from flask import redirect, request, session
from functools import wraps
from flask.helpers import flash
from base64 import b64encode
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions


IK_PUBLIC = os.environ.get("IK_PUBLIC")
IK_PRIVATE = os.environ.get("IK_PRIVATE")
IK_URL = os.environ.get("IK_URL")

ik = ImageKit(private_key = IK_PRIVATE, public_key = IK_PUBLIC, url_endpoint = IK_URL)


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


def validarString(dato):
    if not dato or not dato.isalpha() or dato.isspace():
        return False
    
    return True


def validarDouble(dato):
    if not dato or not dato.replace(".","").isdigit() or float(dato) < 1:
        return False
    
    return True

def subirImagen(imagen):
    
    imagen = b64encode(request.files["foto"].stream.read())
    # Al codificarla, se agrega una letra y una comilla al inicio del texto, tambien una comilla al fina
    # str(imagen)[2:len(imagen)] omito los primeros 2 caracteres y el ultimo

    imagen = str(imagen)[2:len(imagen)]

    # return f'<img src="data:image/png;base64,{imagen}">'
    # print(imagen)

    res = ik.upload(file=imagen, file_name=request.form.get("codigo"), options = UploadFileRequestOptions(folder="Ganado"))
    # El options es opcional de ponerlo y tiene varios parametros configurables, util como para custom_metadata = {"marca": "Gucci", "color":"rojo"}
    #print(res.url)
    # El url listo para guardar en la base de datos y mostrarlo en el html desde el link

    #print(res.response_metadata.raw)
    return res.url
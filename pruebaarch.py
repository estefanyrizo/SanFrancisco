
import os
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from base64 import b64encode
from flask import request
from dotenv import load_dotenv

load_dotenv()

IK_PUBLIC = os.environ.get("IK_PUBLIC")
IK_PRIVATE = os.environ.get("IK_PRIVATE")
IK_URL = os.environ.get("IK_URL")

ik = ImageKit(private_key=IK_PRIVATE,
              public_key=IK_PUBLIC, url_endpoint=IK_URL)





def subirArchivo(archivo, nombre, folder):

    archivo = b64encode(archivo.stream.read())
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

with open("helpers.py", "rb") as file:
    a = file.read()
    subirArchivo(a, "hola", "Ventas")
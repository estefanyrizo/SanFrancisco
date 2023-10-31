from datetime import date, datetime
import os
import requests
from dotenv import load_dotenv
from flask import Flask, json, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, flash, redirect, render_template, request, session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, subirImagen, validarDouble, validarString
from flask import jsonify
from sqlalchemy.sql import text
import helpers
from flask_paginate import Pagination, get_page_parameter
import locale

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = 'super secret key'

Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"),pool_pre_ping=True)
db = scoped_session(sessionmaker(bind=engine))

locale.setlocale(locale.LC_TIME, 'es_ES')


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        cont = 0
        hash = None
        id = 0
        isAdmin = False

        if not request.form.get("username"):
            flash("Debe ingresar un usuario", "error")
            return render_template("login.html")

        elif not request.form.get("password"):
            flash("Debe ingresar una contraseña", "error")
            return render_template("login.html")

        for dato in db.execute(text("select count(usuario), id, usuario, hash, isAdmin from usuario WHERE usuario = :username group by id, usuario, hash, isAdmin"),
                               {"username": request.form.get("username")}):
            cont = dato[0]
            id = dato[1]
            hash = dato[3]
            isAdmin = dato[4]

        if cont != 1 or not check_password_hash(hash, request.form.get("password")):
            flash("Nombre o contraseña incorrectos", "error")
            return render_template("login.html")

        session["user_id"] = id
        session["admin"] = isAdmin

        return redirect("/")

    else:
        return render_template("login.html")
    

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

@app.route("/tablero", methods=["GET", "POST"])
def tablero():
    return render_template("tablero.html")

@app.route("/ingresarnovillo", methods=["GET", "POST"])
def ingresarGanado():

    razas = db.execute(text("select * from raza"))
    origen = db.execute(text("select * from origenganado"))

    if request.method == "POST":
        
        nombre = request.form.get("nombre") #string
        raza = request.form.get("raza") #int
        fechaNacimiento = request.form.get("fechaNacimiento") #date
        codigo = request.form.get("codigo") #string
        color = request.form.get("color") #string
        tamaño = request.form.get("tamaño") #real
        peso = request.form.get("peso") #real
        procedencia = request.form.get("procedencia") # int
        foto = request.files["foto"] # file para subir y obtener el url como string
        comentario = request.form.get("comentario") #string nullable
        
        print(request.form.to_dict())

        if not validarString(nombre):
            flash("Debe ingresar un nombre valido", "error")
            return render_template("ingresarNovillo.html")
        
        if not raza.isdigit() or not raza or int(raza) < 1 or int(raza) > 10:
            flash("Debe ingresar una raza valida", "error")
            return render_template("ingresarNovillo.html")
        
        if not fechaNacimiento or int(fechaNacimiento.split("-")[0]) != datetime.now().year:
            flash("Debe ingresar una fecha valida", "error")
            return render_template("ingresarNovillo.html")
        
        #fecha = fechaNacimiento.split("-") # año(0)-mes(1)-dia(2)
        #print(date(int(fecha[0]), int(fecha[1]), int(fecha[2])))

        if not codigo or codigo.isspace() or db.execute(text(f"select * from ganado where codigochapa = '{codigo}'")).fetchone():
            flash("Ha ingresado un codigo invalido o existente", "error")
            return render_template("ingresarNovillo.html")
        
        if not validarString(color):
            flash("Debe ingresar el color del animal", "error")
            return render_template("ingresarNovillo.html")
        
        if not validarDouble(tamaño):
            flash("Debe ingresar un tamaño valido", "error")
            return render_template("ingresarNovillo.html")

        if not validarDouble(peso):
            flash("Debe ingresar un peso valido", "error")
            return render_template("ingresarNovillo.html")
        
        if not procedencia or int(procedencia) < 1 or int(procedencia) > 2:
            flash("Debe ingresar un origen valido", "error")
            return render_template("ingresarNovillo.html")
        
        if not foto:
            flash("Debe ingresar una foto del animal", "error")
            return render_template("ingresarNovillo.html")

        flash("Informacion registrada con exito", "exito")
        
        raza = int(raza)
        fechaNacimiento = str(fechaNacimiento)
        tamaño = float(tamaño)
        peso = float(peso)
        procedencia = int(procedencia)
        foto = subirImagen(request.files["foto"])
        if comentario :        
            query = text("""INSERT INTO ganado(nombre, fechaNacimiento, peso, tamanio, color, codigoChapa, foto, comentario, estadoGanadoId, razaId, origenGanadoId)
                        VALUES(:nombre, :fechaNacimiento, :peso, :tamaño, :color, :codigoChapa, :foto, :comentario, :estadoGanadoId, :razaId, :origenGanadoId)
                        """)
            
            try:
                db.execute(query, {"nombre":nombre, "fechaNacimiento":fechaNacimiento, "peso":peso, "tamaño":tamaño, "color":color, "codigoChapa":codigo, "foto":foto, "comentario":comentario, "estadoGanadoId":1, "razaId":raza, "origenGanadoId":procedencia})
                db.commit()
            except:
                flash("Ha ocurrido un error", "error")
                return render_template("ingresarNovillo.html", razas=razas, origen=origen)
            
        if not comentario :        
            query = text("""INSERT INTO ganado(nombre, fechaNacimiento, peso, tamanio, color, codigoChapa, foto, estadoGanadoId, razaId, origenGanadoId)
                        VALUES(:nombre, :fechaNacimiento, :peso, :tamaño, :color, :codigoChapa, :foto, :estadoGanadoId, :razaId, :origenGanadoId)
                        """)
            
            try:
                db.execute(query, {"nombre":nombre, "fechaNacimiento":fechaNacimiento, "peso":peso, "tamaño":tamaño, "color":color, "codigoChapa":codigo, "foto":foto, "estadoGanadoId":1, "razaId":raza, "origenGanadoId":procedencia})
                db.commit()
            except:
                flash("Ha ocurrido un error", "error")
                return render_template("ingresarNovillo.html", razas=razas, origen=origen)
        
        return render_template("ingresarNovillo.html", razas=razas, origen=origen)

    else:
        return render_template("ingresarNovillo.html", razas=razas, origen=origen)
    

@app.route("/imagen", methods=["POST"])
def imagen():
    
    if request.files["file"]:
        return {"status":"200"}
    else:
        return {"status":"415"}

@app.route("/micuenta", methods=["GET", "POST"])
def miCuenta():
    return render_template("miCuenta.html")

@app.route("/ganado", methods=["GET"])
def ganado():
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    limit=10
    offset = page*limit - limit
    total = db.execute(text(f"SELECT * FROM ganado INNER JOIN raza ON ganado.razaid = raza.id WHERE estadoganadoid = 1")).rowcount
    ganado = db.execute(text(f"SELECT * FROM ganado INNER JOIN raza ON ganado.razaid = raza.id WHERE estadoganadoid = 1 LIMIT {limit} OFFSET {offset}"))
    page = request.args.get(get_page_parameter(), type=int, default=1)
    print(ganado.rowcount)
    
    pagination = Pagination(page=page, per_page=limit, total=total, search=False, record_name='ganado')

    return render_template("ganado.html", ganado = ganado, pagination = pagination)


@app.template_filter("datetimeformat")
def datetimeformat(value, format='B'):
    return value.strftime(format)


@app.route("/buscarganado", methods=["GET"])
def buscarganado():
    busqueda = request.args.get("q")

    if busqueda:
        ganado = db.execute(text(f"""SELECT * FROM ganado INNER JOIN raza ON ganado.razaid = raza.id
                                 WHERE estadoganadoid = 1 AND LOWER(nombre) LIKE '%{busqueda.lower()}%'
                                 OR LOWER(nombreraza) LIKE '%{busqueda.lower()}%'
                                 OR LOWER(codigochapa) LIKE '%{busqueda.lower()}%'
                                 """))
        
        if ganado.rowcount > 0:
            return render_template('ganadoresultados.html', ganado = ganado)
        else:
            return '''<div class="container-fluid text-center">
                        <h3>Ningun resultado para los parametros de busqueda</h3>
                    </div>'''
    
    else:
        ganado = db.execute(text(f"SELECT * FROM ganado INNER JOIN raza ON ganado.razaid = raza.id WHERE estadoganadoid = 1"))
        
        if ganado.rowcount > 0:
            return render_template('ganadoresultados.html', ganado = ganado)
        else:
            return '''<div class="container-fluid text-center">
                        <h3>Ningun resultado para los parametros de busqueda</h3>
                    </div>'''



@app.route("/infonovillo/<id>/edit", methods=["GET", "POST"])
def infonovillo(id):
    return render_template("novillo.html")
@app.route("/entidadComercial", methods=["GET", "POST"])
def entidadComercial():
    return render_template("entidadComercial.html")
@app.route("/alimento", methods=["GET", "POST"])
def alimento():
    return render_template("alimento.html")
@app.route("/alimentoGanado", methods=["GET", "POST"])
def alimentoGanado():
    return render_template("alimentoGanado.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")
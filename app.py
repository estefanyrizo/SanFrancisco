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
from helpers import admin_required, login_required, subirImagen, validarDouble, validarString
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
    return render_template("tablero.html")


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


@app.route("/ingresarnovillo", methods=["GET", "POST"])
@login_required
def ingresarGanado():

    razas = db.execute(text("select * from raza ORDER BY nombreraza"))
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
        
        if not raza.isdigit() or not raza or int(raza) < 1 or int(raza) > 11:
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
        foto = subirImagen(request.files["foto"], codigo)
        isasignado = True

        if procedencia == 2:
            isasignado = False

        if comentario :        
            query = text("""INSERT INTO ganado(nombre, fechaNacimiento, peso, tamanio, color, codigoChapa, foto, comentario, estadoGanadoId, razaId, origenGanadoId, isasignado)
                        VALUES(:nombre, :fechaNacimiento, :peso, :tamaño, :color, :codigoChapa, :foto, :comentario, :estadoGanadoId, :razaId, :origenGanadoId, :isasignado)
                        """)
            
            try:
                db.execute(query, {"nombre":nombre, "fechaNacimiento":fechaNacimiento, "peso":peso, "tamaño":tamaño, "color":color, "codigoChapa":codigo, "foto":foto, "comentario":comentario, "estadoGanadoId":1, "razaId":raza, "origenGanadoId":procedencia, "isasignado":isasignado})
                db.commit()
            except:
                flash("Ha ocurrido un error", "error")
                return render_template("ingresarNovillo.html", razas=razas, origen=origen)
            
        if not comentario :        
            query = text("""INSERT INTO ganado(nombre, fechaNacimiento, peso, tamanio, color, codigoChapa, foto, estadoGanadoId, razaId, origenGanadoId, isasignado)
                        VALUES(:nombre, :fechaNacimiento, :peso, :tamaño, :color, :codigoChapa, :foto, :estadoGanadoId, :razaId, :origenGanadoId, :isasignado)
                        """)
            
            try:
                db.execute(query, {"nombre":nombre, "fechaNacimiento":fechaNacimiento, "peso":peso, "tamaño":tamaño, "color":color, "codigoChapa":codigo, "foto":foto, "estadoGanadoId":1, "razaId":raza, "origenGanadoId":procedencia, "isasignado":isasignado})
                db.commit()
            except:
                flash("Ha ocurrido un error", "error")
                return render_template("ingresarNovillo.html", razas=razas, origen=origen)
        
        flash("Informacion registrada con exito", "exito")
        return render_template("ingresarNovillo.html", razas=razas, origen=origen)

    else:
        return render_template("ingresarNovillo.html", razas=razas, origen=origen)
    

@app.route("/imagen", methods=["POST"])
@login_required
def imagen():
    
    if request.files["file"]:
        return {"status":"200"}
    else:
        return {"status":"415"}


@app.route("/micuenta", methods=["GET", "POST"])
@login_required
def miCuenta():
    if request.method == "GET":
        usuario = db.execute(f"SELECT * FROM usuario WHERE id = {session['user_id']}")
        return render_template("miCuenta.html", usuario = usuario)
    if request.method == "POST":
        flash("Los cambios se guardaran", "consultar")
        return redirect("/micuenta")


@app.route("/ganado", methods=["GET"])
@login_required
def ganado():
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    limit=10
    offset = page*limit - limit
    total = db.execute(text(f"SELECT * FROM ganado INNER JOIN raza ON ganado.razaid = raza.id WHERE estadoganadoid = 1")).rowcount
    ganado = db.execute(text(f"SELECT * FROM ganado INNER JOIN raza ON ganado.razaid = raza.id WHERE estadoganadoid = 1 ORDER BY ganado.id DESC LIMIT {limit} OFFSET {offset}"))
    page = request.args.get(get_page_parameter(), type=int, default=1)
    
    pagination = Pagination(page=page, per_page=limit, total=total, search=False, record_name='ganado')

    return render_template("ganado.html", ganado = ganado, pagination = pagination)


@app.template_filter("datetimeformat")
def datetimeformat(value, format='B'):
    return value.strftime(format)


@app.route("/buscarganado", methods=["GET"])
@login_required
def buscarganado():
    busqueda = request.args.get("q")

    if busqueda:
        ganado = db.execute(text(f"""SELECT * FROM ganado INNER JOIN raza ON ganado.razaid = raza.id
                                 WHERE LOWER(nombre) LIKE '%{busqueda.lower()}%'
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
@login_required
@admin_required
def infonovillo(id):

    #imagen_actual = None

    if request.method == "GET":
        novillo = db.execute(f"SELECT * FROM ganado INNER JOIN raza ON ganado.razaid = raza.id WHERE ganado.id = {id}")
        #imagen_actual = db.execute(f"SELECT foto FROM ganado WHERE ganado.id = {id}").fetchone().foto

        razas = db.execute(text("SELECT * FROM raza ORDER BY nombreraza"))
        origen = db.execute(text("select * from origenganado"))
        return render_template("novillo.html", novillo = novillo, razas = razas, origen = origen)
    
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

        if not validarString(nombre):
            flash("Debe ingresar un nombre valido", "error")
            return redirect(f"/infonovillo/{id}/edit")
        
        if not raza.isdigit() or not raza or int(raza) < 1 or int(raza) > 11:
            flash("Debe ingresar una raza valida", "error")
            return redirect(f"/infonovillo/{id}/edit")
        
        if not fechaNacimiento or int(fechaNacimiento.split("-")[0]) != datetime.now().year:
            flash("Debe ingresar una fecha valida", "error")
            return redirect(f"/infonovillo/{id}/edit")
        
        if not codigo or codigo.isspace():
            flash("Ha ingresado un codigo invalido o existente", "error")
            return redirect(f"/infonovillo/{id}/edit")
        
        if not validarString(color):
            flash("Debe ingresar el color del animal", "error")
            return redirect(f"/infonovillo/{id}/edit")
        
        if not validarDouble(tamaño):
            flash("Debe ingresar un tamaño valido", "error")
            return redirect(f"/infonovillo/{id}/edit")
        if not validarDouble(peso):
            flash("Debe ingresar un peso valido", "error")
            return redirect(f"/infonovillo/{id}/edit")
        
        if not procedencia or int(procedencia) < 1 or int(procedencia) > 2:
            flash("Debe ingresar un origen valido", "error")
            return redirect(f"/infonovillo/{id}/edit")
        
        raza = int(raza)
        fechaNacimiento = str(fechaNacimiento)
        tamaño = float(tamaño)
        peso = float(peso)
        procedencia = int(procedencia)

        if foto:
            foto = subirImagen(request.files["foto"], codigo)

        if comentario :

            if foto:        
                try:
                    db.execute(text(f"""UPDATE ganado SET nombre = '{nombre}',
                            razaid = {raza},
                            fechanacimiento = '{fechaNacimiento}',
                            codigochapa = '{codigo}',
                            color = '{color}',
                            tamanio = {tamaño},
                            peso = {peso},
                            origenganadoid = {procedencia},
                            foto = '{foto}',
                            comentario = '{comentario}'
                            WHERE id = {id}"""))
                    
                    db.commit()
                
                except:
                    flash("Ha ocurrido un error", "error")
                    return redirect(f"/infonovillo/{id}/edit")
            
            else:
                try:
                    db.execute(text(f"""UPDATE ganado SET nombre = '{nombre}',
                            razaid = {raza},
                            fechanacimiento = '{fechaNacimiento}',
                            codigochapa = '{codigo}',
                            color = '{color}',
                            tamanio = {tamaño},
                            peso = {peso},
                            origenganadoid = {procedencia},
                            comentario = '{comentario}'
                            WHERE id = {id}"""))
                    
                    db.commit()
                
                except:
                    flash("Ha ocurrido un error", "error")
                    return redirect(f"/infonovillo/{id}/edit")

            
        if not comentario :        
            if foto:        
                try:
                    db.execute(text(f"""UPDATE ganado SET nombre = '{nombre}',
                            razaid = {raza},
                            fechanacimiento = '{fechaNacimiento}',
                            codigochapa = '{codigo}',
                            color = '{color}',
                            tamanio = {tamaño},
                            peso = {peso},
                            origenganadoid = {procedencia},
                            foto = '{foto}'
                            WHERE id = {id}"""))
                    
                    db.commit()
                
                except:
                    flash("Ha ocurrido un error", "error")
                    return redirect(f"/infonovillo/{id}/edit")
            
            else:
                try:
                    db.execute(text(f"""UPDATE ganado SET nombre = '{nombre}',
                            razaid = {raza},
                            fechanacimiento = '{fechaNacimiento}',
                            codigochapa = '{codigo}',
                            color = '{color}',
                            tamanio = {tamaño},
                            peso = {peso},
                            origenganadoid = {procedencia}
                            WHERE id = {id}"""))
                    
                    db.commit()

                except:
                    flash("Ha ocurrido un error", "error")
                    return redirect(f"/infonovillo/{id}/edit")
                
        
        flash("Informacion actualizada con exito", "exito")
        return redirect("/ganado")


@app.route("/infonovillo/<id>/muerto", methods=["GET"])
@login_required
def func_name(id):
    db.execute(text(f"UPDATE ganado SET estadoganadoid = 3 WHERE id = {id}"))
    db.commit()

    flash("Se ha actualizado el estado del bovino", "exito")
    return redirect(f"/infonovillo/{id}/edit")



@app.route('/infonovillo/<id>/borrar', methods=["POST"])
def borrar_novillo(id):
    try:
        db.execute(text(f"DELETE FROM ganado WHERE id = {id}"))
        db.commit()
    except:
        flash("Ocurrió un error inesperado", "error")
        return redirect("/ganado")
    
    flash("Registro eliminado exitosamente", "exito")
    return redirect("/ganado")


@app.route("/entidadesComerciales", methods=["GET", "POST"])
@login_required
def entidadComercial():
    return render_template("entidadComercial.html")


@app.route("/empleados", methods=["GET", "POST"])
@login_required
@admin_required
def empleados():

    if request.method == "GET":
        emps = db.execute(text("SELECT * FROM usuario WHERE id > 1 ORDER BY nombre"))
        conteo = db.execute(text("SELECT COUNT(id) AS cant from usuario")).fetchone()
        return render_template("empleados.html", empleados = emps, conteo = conteo)
    
    else:
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        password = request.form.get("password")

        if not nombre or nombre.isspace():
            flash("Nombre invalido", "error")
            return redirect("/empleados")
        
        if not apellido or apellido.isspace():
            flash("Nombre invalido", "error")
            return redirect("/empleados")

        if not password or password.isspace():
            flash("Nombre invalido", "error")
            return redirect("/empleados")
        
        user = (nombre[0]+apellido).lower()

        if db.execute(text(f"SELECT * FROM usuario WHERE usuario = '{user}'")).fetchone():
            flash("Este empleado ya esta registrado", "error")
            return redirect("/empleados")

        db.execute(text(f"INSERT INTO usuario(nombre, apellido, usuario, hash) values ('{nombre}', '{apellido}', '{user}', '{generate_password_hash(password)}')"))
        db.commit()

        flash("Empleado registrado exitosamente", "exito")
        return redirect("/empleados")
    

@app.route('/usuario/cambiar+estado/<id>')
def desactivarempleado(id):

    if db.execute(text(f"select activo from usuario WHERE id = {id}")).fetchone().activo:
        db.execute(text(f"UPDATE usuario SET activo = false WHERE id = {id}"))
        db.commit()

    else:
        db.execute(text(f"UPDATE usuario SET activo = true WHERE id = {id}"))
        db.commit()

    flash("Se actualizó con exito el estado del empleado", "exito")
    return redirect("/empleados")


@app.route('/usuario/recuperar+contraseña/<id>', methods=["POST"])
def repass(id):

    id_user = request.form.get("id")
    passw = request.form.get("password")
    repassw = request.form.get("repassword")

    if not passw or passw.isspace() or not repassw or repassw.isspace():
        flash("Debes llenar todos los campos", "error")
        return redirect("/empleados")
    
    if not passw == repassw:
        flash("Las contraseñas no coinciden", "error")
        return redirect("/empleados")

    try:
        db.execute(text(f"UPDATE usuario SET hash = '{generate_password_hash(passw)}' WHERE id = {id}"))
        db.commit()
    except:
        flash("Ha ocurrido un error inesperado", "error")
        return redirect("/empleados")
    
    flash("La contraseña se actualizó exitosamente", "exito")
    return redirect("/empleados")


@app.route("/alimento", methods=["GET", "POST"])
@login_required
def alimento():
    return render_template("alimento.html")


@app.route("/medicina", methods=["GET", "POST"])
@login_required
def medicina():
    return render_template("medicina.html")


@app.route("/alimentoGanado", methods=["GET", "POST"])
@login_required
def alimentoGanado():
    return render_template("alimentoGanado.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")
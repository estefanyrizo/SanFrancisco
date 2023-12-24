from datetime import date, datetime
import os
import requests
from dotenv import load_dotenv
from flask import Flask, json, session, url_for
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

#locale.setlocale(locale.LC_TIME, 'es_ES')

load_dotenv()


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
        
        if not validarString(nombre):
            flash("Debe ingresar un nombre valido", "error")
            return redirect("/ingresarnovillo")
        
        if not raza.isdigit() or not raza or int(raza) < 1 or int(raza) > 11:
            flash("Debe ingresar una raza valida", "error")
            return redirect("/ingresarnovillo")
        
        if not fechaNacimiento or int(fechaNacimiento.split("-")[0]) != datetime.now().year:
            flash("Debe ingresar una fecha valida", "error")
            return redirect("/ingresarnovillo")
        
        #fecha = fechaNacimiento.split("-") # año(0)-mes(1)-dia(2)
        #print(date(int(fecha[0]), int(fecha[1]), int(fecha[2])))

        if not codigo or codigo.isspace() or db.execute(text(f"select * from ganado where codigochapa = '{codigo}'")).fetchone():
            flash("Ha ingresado un codigo invalido o existente", "error")
            return redirect("/ingresarnovillo")
        
        if not validarString(color):
            flash("Debe ingresar el color del animal", "error")
            return redirect("/ingresarnovillo")
        
        if not validarDouble(tamaño):
            flash("Debe ingresar un tamaño valido", "error")
            return redirect("/ingresarnovillo")

        if not validarDouble(peso):
            flash("Debe ingresar un peso valido", "error")
            return redirect("/ingresarnovillo")
        
        if not procedencia or int(procedencia) < 1 or int(procedencia) > 2:
            flash("Debe ingresar un origen valido", "error")
            return redirect("/ingresarnovillo")
        
        if not foto:
            flash("Debe ingresar una foto del animal", "error")
            return redirect("/ingresarnovillo")
        
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
                return redirect("/ingresarnovillo")
            
        if not comentario :        
            query = text("""INSERT INTO ganado(nombre, fechaNacimiento, peso, tamanio, color, codigoChapa, foto, estadoGanadoId, razaId, origenGanadoId, isasignado)
                        VALUES(:nombre, :fechaNacimiento, :peso, :tamaño, :color, :codigoChapa, :foto, :estadoGanadoId, :razaId, :origenGanadoId, :isasignado)
                        """)
            
            try:
                db.execute(query, {"nombre":nombre, "fechaNacimiento":fechaNacimiento, "peso":peso, "tamaño":tamaño, "color":color, "codigoChapa":codigo, "foto":foto, "estadoGanadoId":1, "razaId":raza, "origenGanadoId":procedencia, "isasignado":isasignado})
                db.commit()
            except:
                flash("Ha ocurrido un error", "error")
                return redirect("/ingresarnovillo")
        
        flash("Informacion registrada con exito", "exito")
        return redirect("/ingresarnovillo")

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
        
@app.route("/infonovillo/<id>/", methods=["GET", "POST"])
@login_required
def infonovillo(id):

    #imagen_actual = None

    if request.method == "GET":
        novillo = db.execute(f"SELECT * FROM ganado INNER JOIN raza ON ganado.razaid = raza.id WHERE ganado.id = {id}")
        #imagen_actual = db.execute(f"SELECT foto FROM ganado WHERE ganado.id = {id}").fetchone().foto

        razas = db.execute(text("SELECT * FROM raza ORDER BY nombreraza"))
        origen = db.execute(text("select * from origenganado"))
        return render_template("novilloinfo.html", novillo = novillo, razas = razas, origen = origen)
    

@app.route("/infonovillo/<id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def infonovilloedit(id):

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
@login_required
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

    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido") #posibilidad de null si es entidad juridica
        telefono = request.form.get("telefono") #posibilidad de null
        identificacion = request.form.get("identificacion")
        tipoentidadid = int(request.form.get("tipoEntidad"))

        if not tipoentidadid or tipoentidadid < 1 or tipoentidadid > 2:
            flash("Debe seleccionar el tipo de entidad comercial", "error")
            return redirect("/entidadesComerciales")
        
        if not nombre or nombre.isspace():
            flash("Debe especificar el nombre de entidad comercial", "error")
            return redirect("/entidadesComerciales")
        if tipoentidadid == 1:
            if not apellido or apellido.isspace():
                flash("Debe especificar el apellido de entidad comercial", "error")
                return redirect("/entidadesComerciales")
        if not identificacion or identificacion.isspace():
            flash("Debe especificar la cédula o RUC de la entidad comercial", "error")
            return redirect("/entidadesComerciales")
        
        
        if tipoentidadid == 1:
            if telefono:
                db.execute(text(f"""INSERT INTO entidadcomercial(nombre, apellido, telefono, identificacion, tipoentidadid)
                                VALUES('{nombre}', '{apellido}', {telefono}, '{identificacion}', {tipoentidadid})"""))
            else:
                db.execute(text(f"""INSERT INTO entidadcomercial(nombre, apellido, identificacion, tipoentidadid)
                                VALUES('{nombre}', '{apellido}', '{identificacion}', {tipoentidadid})"""))
            
        else:
            if telefono:
                db.execute(text(f"""INSERT INTO entidadcomercial(nombre, telefono, identificacion, tipoentidadid)
                                VALUES('{nombre}', '{telefono}', '{identificacion}', {tipoentidadid})"""))
            else:
                db.execute(text(f"""INSERT INTO entidadcomercial(nombre, identificacion, tipoentidadid)
                                VALUES('{nombre}', '{identificacion}', {tipoentidadid})"""))
            
        try:
            db.commit()
        except:
            flash("Ocurrió un error inesperado", "error")
            return render_template("entidadComercial.html")

        flash("La entidad comercial fue registrada exitosamente", "exito")
        return redirect("/entidadesComerciales")
    
    else:
        entidades = db.execute(text("SELECT * FROM entidadcomercial ORDER BY nombre"))
        tiposentidad = db.execute(text("SELECT * FROM tipoentidad"))
        return render_template("entidadComercial.html", entidades = entidades, tiposentidades = tiposentidad)
    

@app.route("/entidadesComerciales/<id>/editar", methods=["POST"])
@login_required
def editarentidad(id):

    nombre = request.form.get("nombre")
    apellido = request.form.get("apellido") #posibilidad de null si es entidad juridica
    telefono = request.form.get("telefono") #posibilidad de null
    identificacion = request.form.get("identificacion")
    tipoentidadid = int(request.form.get("tipoEntidad"))

    if not tipoentidadid or tipoentidadid < 1 or tipoentidadid > 2:
        flash("Debe seleccionar el tipo de entidad comercial", "error")
        return redirect("/entidadesComerciales")
    
    if not nombre or nombre.isspace():
        flash("Debe especificar el nombre de entidad comercial", "error")
        return redirect("/entidadesComerciales")
    if tipoentidadid == 1:
        if not apellido or apellido.isspace():
            flash("Debe especificar el apellido de entidad comercial", "error")
            return redirect("/entidadesComerciales")
    if not identificacion or identificacion.isspace():
        flash("Debe especificar la cédula o RUC de la entidad comercial", "error")
        return redirect("/entidadesComerciales")
    
    if tipoentidadid == 1:
            if telefono:
                db.execute(text(f"UPDATE entidadcomercial SET nombre = '{nombre}', apellido = '{apellido}', telefono = '{telefono}', identificacion = '{identificacion}', tipoentidadid = {tipoentidadid} WHERE id = {id}"))
                
            else:
                db.execute(text(f"UPDATE entidadcomercial SET nombre = '{nombre}', apellido = '{apellido}', telefono = null, identificacion = '{identificacion}', tipoentidadid = {tipoentidadid} WHERE id = {id}"))
                 
    else:
        if telefono:
            db.execute(text(f"UPDATE entidadcomercial SET nombre = '{nombre}', apellido = null, telefono = {telefono}, identificacion = '{identificacion}', tipoentidadid = {tipoentidadid} WHERE id = {id}"))
                 
        else:
            db.execute(text(f"UPDATE entidadcomercial SET nombre = '{nombre}', apellido = null, telefono = null, identificacion = '{identificacion}', tipoentidadid = {tipoentidadid} WHERE id = {id}"))
                 
        
    try:
        db.commit()
    except:
        flash("Ocurrió un error inesperado", "error")
        return redirect("/entidadesComerciales")
    
    flash("Se guardaron los cambios", "exito")
    return redirect("/entidadesComerciales")


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
@login_required
@admin_required
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
    tipomedicina = db.execute(text("SELECT * FROM presentacion ORDER BY tipomedicina"))
    medicinas = db.execute(text("""select dp.id id,
                                m.nombre nombre,
                                p.viaaplicacion viaaplicacion,
                                p.tipomedicina tipomedicina,
                                dp.contenido contenido,
                                dp.cantidad cantidad,
                                dp.precio precio,
                                p.unidadmedida unidadmedida
                                from detallepresentacion dp
                                inner join medicina m
                                on dp.medicinaid = m.id
                                inner join presentacion p
                                on dp.presentacionid = p.id"""))

    if request.method == "GET":
        return render_template("medicina.html", tipomedicina = [t for t in tipomedicina], medicinas = [m for m in medicinas])

    else:
        nombre = request.form.get("nombre")
        tipo = request.form.get("tipomedicina")
        contenido = request.form.get("contenido")
        cantidad = request.form.get("cantidad")
        precio = request.form.get("precio")

        if not nombre or nombre.isspace():
            flash("Debe ingresar un nombre valido", "error")
            return redirect("/medicina")
        if not tipo or int(tipo) > 19 or int(tipo) < 1:
            flash("Debe ingresar un tipo de medicina valido", "error")
            return redirect("/medicina")
        if not contenido or contenido.isspace() or float(contenido) < 0:
            flash("Debe ingresar el contenido de produto", "error")
            return redirect("/medicina")
        if not cantidad or int(cantidad) < 1:
            flash("Debe ingresar una cantidad valida", "error")
            return redirect("/medicina")
        if not precio or precio.isspace() or float(precio) < 0:
            flash("Debe ingresar un precio valido", "error")
            return redirect("/medicina")
        
        med = db.execute(text(f"SELECT * FROM medicina WHERE nombre = '{nombre}'")).fetchone()
        
        if med:
            try:
                cant = db.execute(f"SELECT * FROM detallepresentacion WHERE medicinaid = {med['id']}").fetchone()["cantidad"] + int(cantidad)
                db.execute(text(f"UPDATE detallepresentacion SET cantidad = {cant} WHERE medicinaid = {med['id']}"))
                db.commit()
            except:
                flash("Ocurrió un error inesperado", "error")
                return redirect("/medicina")
            
        else:
            try:
                idmedicina = db.execute(text(f"INSERT INTO medicina (nombre) VALUES('{nombre}') RETURNING id")).fetchone()[0]
                db.execute(text(f"""INSERT INTO detallepresentacion (contenido, cantidad, precio, presentacionid, medicinaid)
                                VALUES ({float(contenido)}, {int(cantidad)}, {float(precio)}, {tipo}, {idmedicina})"""))
                
                db.commit()
            except:
                flash("Ocurrió un error inesperado", "error")
                return redirect("/medicina")

        flash("La medicina se ha registrado exitosamente", "exito")
        return redirect("/medicina")


@app.route("/medicina/editar", methods=["POST"])
@login_required
def mededit():
        
        idmed = request.form.get("medid")
        nombre = request.form.get("nombre")
        tipo = request.form.get("tipomedicina")
        contenido = request.form.get("contenido")
        cantidad = request.form.get("cantidad")
        precio = request.form.get("precio")

        if not nombre or nombre.isspace():
            flash("Debe ingresar un nombre valido", "error")
            return redirect("/medicina")
        if not tipo or int(tipo) > 19 or int(tipo) < 1:
            flash("Debe ingresar un tipo de medicina valido", "error")
            return redirect("/medicina")
        if not contenido or contenido.isspace() or float(contenido) < 0:
            flash("Debe ingresar el contenido de produto", "error")
            return redirect("/medicina")
        if not cantidad or int(cantidad) < 1:
            flash("Debe ingresar una cantidad valida", "error")
            return redirect("/medicina")
        if not precio or precio.isspace() or float(precio) < 0:
            flash("Debe ingresar un precio valido", "error")
            return redirect("/medicina")
        
        medid = db.execute(text(f"SELECT medicinaid FROM detallepresentacion WHERE id = '{idmed}'")).fetchone()

        #try:
        db.execute(f"UPDATE medicina SET nombre = '{nombre}' WHERE id = {medid['medicinaid']}")
        db.execute(f"UPDATE detallepresentacion SET contenido = {contenido}, precio = {precio}, presentacionid = {tipo}, medicinaid = {medid['medicinaid']}, cantidad = {cantidad} WHERE id = {int(idmed)}")
        db.commit()
        #except:
            #flash("Ha ocurrido un error inesperado", "error")
            #return redirect("/medicina")
        
        flash("Se actualizó el registro exitosamente", "exito")
        return redirect("/medicina")


@app.route('/registrosmedicos', methods=["GET", "POST"])
@login_required
def registrosmedicos():
    if request.method == "GET":
        enfermedades = db.execute(text("SELECT * FROM enfermedad ORDER BY nombre"))
        medicinas =  db.execute(text("SELECT * FROM medicina ORDER BY nombre"))
        registros = db.execute(text("""SELECT r.id,
                                    g.codigochapa,
                                    e.nombre enfermedad,
                                    r.fecha,
                                    m.nombre medicina,
                                    r.dosis,
                                    r.diagnostico
                                    FROM registromedico  r
                                    INNER JOIN ganado g on r.ganadoid = g.id
                                    INNER JOIN enfermedad e on r.enfermedadid = e.id
                                    INNER JOIN medicina m on r.medicinaid = m.id
                                    ORDER BY fecha"""))

        return render_template("registrosmedicos.html", enfermedades = [e for e in enfermedades], medicinas = [m for m in medicinas], registros = [r for r in registros])
    else:
        chapa = request.form.get("chapa")
        enfermedad = int(request.form.get("enfermedad"))
        fecha = str(request.form.get("fecha"))
        medicina = int(request.form.get("medicina"))
        dosis = request.form.get("dosis")
        diagnostico = request.form.get("diagnostico")

        if not chapa or chapa.isspace():
            flash("Debe ingresar una cahpa valida", "error")
            return redirect("/registrosmedicos", "error")
        if not dosis or dosis.isspace():
            flash("Debe ingresar una dosis valida", "error")
            return redirect("/registrosmedicos")
        if not validarString(diagnostico):
            flash("Debe ingresar un diagnostico valido", "error")
            return redirect("/registrosmedicos")
        if not enfermedad or enfermedad < 1:
            flash("Debe ingresar una enfermedad valida", "error")
            return redirect("/registrosmedicos")
        if not medicina or medicina < 1:
            flash("Debe ingresar una medicina valida", "error")
            return redirect("/registrosmedicos")

        bovinoid = 0
        try:
            bovinoid =  db.execute(text(f"SELECT * FROM ganado WHERE codigochapa = '{chapa}'")).fetchone()["id"]
        except:
            flash("El bovino ingresado no existe", "error")
            return redirect("/registrosmedicos")
        
        try:
            db.execute(text(f"""INSERT INTO registromedico(dosis, fecha, diagnostico, medicinaid, enfermedadid, ganadoid)
                            VALUES('{dosis}', '{fecha}', '{diagnostico}', {medicina}, {enfermedad}, {bovinoid})"""))
            
            db.commit()

        except:
            flash("Ocurrio un error inesperado", "error")
            return redirect("/registrosmedicos")
        
        flash("Registro agregado exitosamente", "exito")
        return redirect("/registrosmedicos")
    

@app.route('/registrosmedicos/editar', methods=["POST"])
@login_required
def editarregistrosmedicos():
    
    idreg = int(request.form.get("idreg"))
    chapa = request.form.get("chapa")
    enfermedad = int(request.form.get("enfermedad"))
    fecha = str(request.form.get("fecha"))
    medicina = int(request.form.get("medicina"))
    dosis = request.form.get("dosis")
    diagnostico = request.form.get("diagnostico")

    if not chapa or chapa.isspace():
        flash("Debe ingresar una cahpa valida", "error")
        return redirect("/registrosmedicos", "error")
    if not dosis or dosis.isspace():
        flash("Debe ingresar una dosis valida", "error")
        return redirect("/registrosmedicos")
    if not validarString(diagnostico):
        flash("Debe ingresar un diagnostico valido", "error")
        return redirect("/registrosmedicos")
    if not enfermedad or enfermedad < 1:
        flash("Debe ingresar una enfermedad valida", "error")
        return redirect("/registrosmedicos")
    if not medicina or medicina < 1:
        flash("Debe ingresar una medicina valida", "error")
        return redirect("/registrosmedicos")

    bovinoid = 0
    try:
        bovinoid =  db.execute(text(f"SELECT * FROM ganado WHERE codigochapa = '{chapa}'")).fetchone()["id"]
    except:
        flash("El bovino ingresado no existe", "error")
        return redirect("/registrosmedicos")
    
    try:
        db.execute(text(f"""UPDATE registromedico SET 
                        dosis = '{dosis}', fecha = '{fecha}', diagnostico = '{diagnostico}', 
                        medicinaid = {medicina}, enfermedadid = {enfermedad}, ganadoid = {bovinoid}
                        WHERE id = {idreg}"""))
        
        db.commit()

    except:
        flash("Ocurrio un error inesperado", "error")
        return redirect("/registrosmedicos")
    
    flash("Registro editado exitosamente", "exito")
    return redirect("/registrosmedicos")


@app.route("/control_bovino", methods=["GET","POST"])
@login_required
def controlbovino():
    if request.method == "GET":
        ganado = db.execute(text("SELECT id, codigochapa, nombre FROM ganado"))
        registros = db.execute(text("""SELECT g.id ganadoid,
                                    rp.id idregistro,
                                    g.codigochapa codigochapa,
                                    rp.fecha fecha,
                                    rp.peso peso,
                                    rp.comentario comentario
                                    FROM public.registroproduccion rp
                                    inner join ganado g
                                    on rp.ganadoid = g.id
                                    inner join usuario u
                                    on rp.usuarioid = u.id
                                    order by fecha"""))
        
        return render_template("controlbovino.html", registros = [r for r in registros], ganado = [g for g in ganado])
    
    else:
        fecha = str(request.form.get("fecha"))
        ganadoid = int(request.form.get("bovino"))
        peso = float(request.form.get("peso"))
        comentario = request.form.get("comentario")

        if not fecha:
            flash("Debe ingresar la fecha de control", "error")
            return redirect("/control_bovino")
        if not ganadoid or ganadoid < 1:
            flash("Debe seleccionar el bovino", "error")
            return redirect("/control_bovino")
        if not peso or peso < 1:
            flash("Debe ingresar el peso del bovino", "error")
            return redirect("/control_bovino")
        
        if comentario:
            try:
                db.execute(text(f"""INSERT INTO registroproduccion(fecha, ganadoid, peso, comentario, usuarioid) 
                                VALUES('{fecha}', {ganadoid}, {peso}, '{comentario}', {session["user_id"]})"""))
                db.commit()
            except:
                flash("Ocurrió un error inesperado", "error")
                return redirect("/control_bovino")
        else:
            try:
                db.execute(text(f"""INSERT INTO registroproduccion(fecha, ganadoid, peso, usuarioid) 
                                VALUES('{fecha}', {ganadoid}, {peso}, {session["user_id"]})"""))
                db.commit()
            except:
                flash("Ocurrió un error inesperado", "error")
                return redirect("/control_bovino")
            
        flash("Registro creado exitosamente", "exito")
        return redirect("/control_bovino")

@app.route("/alimentoGanado", methods=["GET", "POST"])
@login_required
def alimentoGanado():
    return render_template("alimentoGanado.html")

@app.route("/compra", methods=["GET", "POST"])
@login_required
def compra():
    return render_template("/compra/pri.html")
@app.route("/compra/individual", methods=["GET", "POST"])
@login_required
def compraIndividual():
    if request.method == "GET":
        ganado = db.execute(text(f"SELECT codigochapa, nombre, nombreraza, tamanio, peso, ganado.id AS id, raza FROM ganado INNER JOIN raza ON ganado.razaid = raza.id WHERE estadoganadoid = 1 AND isasignado = false ORDER BY ganado.id"))
        return render_template("compra/individual.html", ganado = ganado)
    else:
        id = request.form.get("bovino")
        print(id)
        novillo = db.execute(f"SELECT * FROM ganado INNER JOIN raza ON ganado.razaid = raza.id WHERE ganado.id = {id}").fetchone()
        flash(f"Has seleccionado el bovino {novillo.nombre} con codigo {novillo.codigochapa}", "consultar")
        return redirect(url_for("compraIndividualFin", id=id))

@app.route("/compra/individual/fin", methods=["GET", "POST"])
@login_required
def compraIndividualFin():
    if request.method == "GET":
        id = request.args.get('id')
        novillo = db.execute(f"SELECT codigochapa, nombre, nombreraza, tamanio, ganado.id AS id, raza FROM ganado INNER JOIN raza ON ganado.razaid = raza.id WHERE ganado.id = {id}")
        entidad = db.execute(f"SELECT * FROM entidadcomercial")
        return render_template("compra/fin.html", ganado=novillo, proveedor=entidad)
    
    else:
        id = request.form.get("bovino")
        fecha = request.form.get("fechaCompra")
        proveedor = request.form.get("proveedor")
        costo = request.form.get("costo")
        if not fecha or not proveedor or not costo:
            flash("Debe ingresar todos los datos solicitados", "error")
            return redirect(url_for("compraIndividualFin", id=id))

        fecha = str(fecha)
        compra = db.execute(text(f"INSERT INTO compra(fecha, cantidad, montoTotal, usuarioid, entidadcomercialid) VALUES('{fecha}', 1, {costo}, {session['user_id']}, {proveedor}) RETURNING id")).fetchone()[0]
        print(compra)
        db.execute(text(f"INSERT INTO detallecompra(compraid, ganadoid) VALUES ({compra}, {23})"))
        db.execute(text(f"UPDATE ganado SET isasignado = true WHERE ganado.id = {id}"))
        db.commit()
        flash("Compra ingresada correctamente", "exito")
        return redirect("/")
    
@app.route("/compras")
@login_required
def compras():
    compras = db.execute("SELECT * FROM compra INNER JOIN entidadcomercial ON compra.entidadcomercialid = entidadcomercial.id")
    return render_template("compras.html", compras = compras)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")
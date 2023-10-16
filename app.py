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
from helpers import login_required, administrador
from flask import jsonify

app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
    #raise RuntimeError("DATABASE_URL is not set")


# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# Set up database
#engine = create_engine(os.getenv("DATABASE_URL"))
#db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["GET", "POST"])
#@login_required
def index():
    session["user_id"] = 1
    session["admin"] = True
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

@app.route("/tablero", methods=["GET", "POST"])
def tablero():
    return render_template("tablero.html")

@app.route("/ingresarnovillo", methods=["GET", "POST"])
def ingresarGanado():
    return render_template("ingresarNovillo.html")

@app.route("/micuenta", methods=["GET", "POST"])
def miCuenta():
    return render_template("miCuenta.html")

@app.route("/ganado", methods=["GET", "POST"])
def ganado():
    return render_template("ganado.html")
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
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = "supersecreto"

# Rutas de archivos
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

# 📌 Preguntas de la encuesta
preguntas = [
    {"texto": "Tengo fama de decir lo que pienso claramente y sin rodeos.", "estilo": "Pragmático"},
    {"texto": "Estoy seguro/a de lo que es bueno y malo, lo que está bien y lo que está mal.", "estilo": "Teórico"},
    {"texto": "Muchas veces actúo sin mirar las consecuencias.", "estilo": "Activo"},
    {"texto": "Normalmente trato de resolver los problemas metódicamente y paso a paso.", "estilo": "Teórico"},
    {"texto": "Creo que los formalismos coartan y limitan la actuación libre de las personas.", "estilo": "Activo"},
]

# 📌 Verificar si la base de datos existe y crearla si no
def verificar_base_datos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla de usuarios si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        contraseña TEXT NOT NULL,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        matematicas INTEGER,
        historia INTEGER,
        fisica INTEGER,
        quimica INTEGER,
        biologia INTEGER,
        ingles INTEGER,
        geografia INTEGER
    )
    """)

    # Crear tabla de respuestas, permitiendo actualizar respuestas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS respuestas (
        id_usuario INTEGER,
        pregunta TEXT NOT NULL,
        respuesta TEXT,
        PRIMARY KEY (id_usuario, pregunta),
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    )
    """)

    conn.commit()
    conn.close()

verificar_base_datos()

# 📌 Ruta principal (Muestra la bienvenida)
@app.route('/')
def home():
    return render_template("bienvenida.html")  

# 📌 Ruta de registro de estudiante
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        contraseña = request.form.get("contraseña").strip()
        nombre = request.form.get("nombre").strip().title()
        apellido = request.form.get("apellido").strip().title()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            conn.close()
            return render_template("registro.html", error="⚠️ Este email ya está registrado. Intenta iniciar sesión.")

        cursor.execute("INSERT INTO usuarios (email, contraseña, nombre, apellido) VALUES (?, ?, ?, ?)", 
                       (email, contraseña, nombre, apellido))
        conn.commit()
        conn.close()

        return redirect(url_for("login"))  # ✅ Redirige al login después del registro

    return render_template("registro.html")

# 📌 Ruta de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        contraseña = request.form["contraseña"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre, apellido FROM usuarios WHERE email = ? AND contraseña = ?", (email, contraseña))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session["usuario_id"] = usuario[0]
            session["nombre"] = usuario[1]
            session["apellido"] = usuario[2]
            session["email"] = email  
            return redirect(url_for("dashboard"))  # ✅ Redirige al Dashboard en vez de la encuesta
        else:
            return render_template("login.html", error="⚠️ Email o contraseña incorrectos")

    return render_template("login.html")

# 📌 Ruta del Dashboard
@app.route('/dashboard')
def dashboard():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    nombre = session["nombre"]
    apellido = session["apellido"]
    
    return render_template("dashboard.html", nombre=nombre, apellido=apellido)

@app.route("/ver_progreso")
def ver_progreso():
    if "usuario_id" not in session:
        return redirect(url_for("login"))  # Redirige a login si el usuario no ha iniciado sesión

    usuario_id = session["usuario_id"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT pregunta, respuesta FROM respuestas WHERE id_usuario = ?", (usuario_id,))
    respuestas = cursor.fetchall()
    
    conn.close()

    return render_template("progreso.html", respuestas=respuestas)

# 📌 Ruta de la encuesta
@app.route('/encuesta', methods=['GET', 'POST'])
def encuesta():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    usuario_id = session["usuario_id"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT pregunta, respuesta FROM respuestas WHERE id_usuario = ?", (usuario_id,))
    respuestas_previas = dict(cursor.fetchall())

    conn.close()

    return render_template("encuesta.html", preguntas=preguntas, respuestas_previas=respuestas_previas)

# 📌 Guardar respuestas parciales de la encuesta
@app.route('/guardar_respuestas', methods=['POST'])
def guardar_respuestas():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    usuario_id = session["usuario_id"]
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for i, pregunta in enumerate(preguntas):
        respuesta = request.form.get(f'pregunta{i}')
        if respuesta:  
            cursor.execute("""
                INSERT INTO respuestas (id_usuario, pregunta, respuesta)
                VALUES (?, ?, ?)
                ON CONFLICT(id_usuario, pregunta) 
                DO UPDATE SET respuesta = excluded.respuesta
            """, (usuario_id, pregunta["texto"], respuesta))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))  # ✅ Redirige al Dashboard después de guardar

# 📌 Ruta de resultados de la encuesta
@app.route('/resultado', methods=['POST'])
def resultado():
    if "usuario_id" not in session:
        return redirect(url_for("login"))  

    nombre = session["nombre"]
    apellido = session["apellido"]

    respuestas = {f'pregunta{i}': request.form.get(f'pregunta{i}') for i in range(len(preguntas))}
    
    if None in respuestas.values():
        return render_template("encuesta.html", preguntas=preguntas, error="⚠️ Debes responder todas las preguntas.")

    estilos = {"Activo": 0, "Reflexivo": 0, "Teórico": 0, "Pragmático": 0}

    for i in range(len(preguntas)):  
        respuesta = respuestas.get(f'pregunta{i}')
        if respuesta == '+':
            estilos[preguntas[i]['estilo']] += 1  

    estilo_predominante = max(estilos, key=estilos.get)

    return render_template('resultado.html', nombre=nombre, apellido=apellido, estilo=estilo_predominante)

# 📌 Ruta para cerrar sesión
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)
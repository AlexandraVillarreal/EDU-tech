import sqlite3

# Crear la conexión a la base de datos
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Crear la tabla de usuarios
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    contraseña TEXT NOT NULL
);
""")

# Crear la tabla de rendimiento
cursor.execute("""
CREATE TABLE IF NOT EXISTS rendimiento (
    id_rendimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    matematicas INTEGER,
    historia INTEGER,
    fisica INTEGER,
    quimica INTEGER,
    biologia INTEGER,
    ingles INTEGER,
    geografia INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
""")

# Crear la tabla de progreso de la encuesta
cursor.execute("""
CREATE TABLE IF NOT EXISTS progreso_encuesta (
    id_progreso INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    pregunta_actual INTEGER NOT NULL,
    respuestas TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
""")

# Crear la tabla de resultados de la encuesta
cursor.execute("""
CREATE TABLE IF NOT EXISTS resultados_encuesta (
    id_resultado INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    estilo_aprendizaje TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
""")

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()

print("✅ Base de datos creada exitosamente")

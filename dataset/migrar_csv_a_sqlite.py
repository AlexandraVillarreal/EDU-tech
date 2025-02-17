import pandas as pd
import sqlite3

# Conectar a SQLite
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Leer el CSV y limpiar los nombres de las columnas (eliminar espacios y convertir a minúsculas)
df = pd.read_csv("dataset/datos.csv")
df.columns = df.columns.str.strip().str.lower()  # Convierte todas las columnas a minúsculas

# Verifica los nombres de columnas antes de insertar
print("📌 Columnas en el CSV:", df.columns.tolist())

# Insertar usuarios en la base de datos
for _, row in df.iterrows():
    try:
        cursor.execute("""
        INSERT INTO usuarios (nombre, apellido, email, contraseña, matematicas, historia, fisica, quimica, biologia, ingles, geografia)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (row['nombre'], row['apellido'], row['email'], "contraseña123", row['matematicas'], 
              row['historia'], row['fisica'], row['quimica'], row['biologia'], row['ingles'], row['geografia']))
    except sqlite3.IntegrityError:
        print(f"⚠️ El usuario con email {row['email']} ya existe. Saltando inserción...")

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()

print("✅ Usuarios importados correctamente a SQLite.")

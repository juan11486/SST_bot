import sqlite3
import pandas as pd

DB_PATH = "turnos.db"
CSV_PATH = "Cronograma_2025.csv"

# 🔹 Función para crear la base de datos y la tabla de turnos
def crear_base_de_datos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turnos (
            N_turno INTEGER PRIMARY KEY,
            Nombre_Completo TEXT,
            Fecha_Inicio TEXT,
            Fecha_Fin TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# 🔹 Función para cargar el CSV en la base de datos
def cargar_csv_a_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Leer CSV con Pandas
    df = pd.read_csv(CSV_PATH, encoding="latin1")

    # Vaciar la tabla antes de insertar nuevos datos
    cursor.execute("DELETE FROM turnos")

    # Insertar datos en la tabla
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO turnos (N_turno, Nombre_Completo, Fecha_Inicio, Fecha_Fin)
            VALUES (?, ?, ?, ?)
        """, (row["N_turno"], row["Nombre_Completo"], row["Fecha_Inicio"], row["Fecha_Fin"]))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_base_de_datos()
    cargar_csv_a_db()
    print("📢 Base de datos actualizada con el cronograma")


import sqlite3
import os


class Almacenamiento:
    def __init__(self, ruta_db="data/tekni.db"):
        self.ruta_db = ruta_db

        carpeta = os.path.dirname(ruta_db)

        if carpeta:
            os.makedirs(carpeta, exist_ok=True)

        self.conexion = sqlite3.connect(
            self.ruta_db,
            check_same_thread=False
        )

        self.crear_tablas()

    def crear_tablas(self):
        cursor = self.conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clave TEXT NOT NULL,
                valor TEXT NOT NULL,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferencias (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recordatorios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT NOT NULL,
                fecha TEXT NOT NULL,
                completado INTEGER DEFAULT 0
            )
        """)

        self.conexion.commit()

    def cerrar(self):
        self.conexion.close()
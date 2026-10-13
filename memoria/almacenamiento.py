import os
import sqlite3
import threading
from pathlib import Path


class Almacenamiento:
    def __init__(self, ruta_db="data/tekni.db"):
        self.ruta_db = str(Path(ruta_db))
        carpeta = os.path.dirname(self.ruta_db)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        self.conexion = sqlite3.connect(self.ruta_db, check_same_thread=False)
        self.conexion.execute("PRAGMA journal_mode=WAL")
        self.lock = threading.RLock()
        self.crear_tablas()

    def crear_tablas(self):
        with self.lock, self.conexion:
            self.conexion.execute("CREATE TABLE IF NOT EXISTS memorias (id INTEGER PRIMARY KEY AUTOINCREMENT, clave TEXT NOT NULL, valor TEXT NOT NULL, fecha DATETIME DEFAULT CURRENT_TIMESTAMP)")
            self.conexion.execute("CREATE INDEX IF NOT EXISTS idx_memorias_clave ON memorias(clave)")
            self.conexion.execute("CREATE TABLE IF NOT EXISTS preferencias (clave TEXT PRIMARY KEY, valor TEXT NOT NULL)")
            self.conexion.execute("CREATE TABLE IF NOT EXISTS recordatorios (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT NOT NULL, fecha TEXT NOT NULL, completado INTEGER DEFAULT 0)")

    def cerrar(self):
        with self.lock:
            self.conexion.close()

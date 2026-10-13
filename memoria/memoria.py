from memoria.almacenamiento import Almacenamiento


class Memory:
    def __init__(self, ruta_db="data/tekni.db"):
        self.almacenamiento = Almacenamiento(ruta_db)

    def guardar_memoria(self, clave, valor):
        clave = str(clave).strip()
        valor = str(valor).strip()
        if not clave or not valor:
            raise ValueError("La clave y el valor no pueden estar vacíos.")
        with self.almacenamiento.lock, self.almacenamiento.conexion:
            self.almacenamiento.conexion.execute("INSERT INTO memorias (clave, valor) VALUES (?, ?)", (clave, valor))

    def obtener_memorias(self, clave):
        with self.almacenamiento.lock:
            filas = self.almacenamiento.conexion.execute("SELECT valor FROM memorias WHERE clave = ? ORDER BY id", (clave,)).fetchall()
        return [fila[0] for fila in filas]

    def borrar_memorias(self, clave):
        with self.almacenamiento.lock, self.almacenamiento.conexion:
            self.almacenamiento.conexion.execute("DELETE FROM memorias WHERE clave = ?", (clave,))

    def guardar_preferencia(self, clave, valor):
        with self.almacenamiento.lock, self.almacenamiento.conexion:
            self.almacenamiento.conexion.execute("INSERT OR REPLACE INTO preferencias (clave, valor) VALUES (?, ?)", (clave, valor))

    def obtener_preferencia(self, clave):
        with self.almacenamiento.lock:
            fila = self.almacenamiento.conexion.execute("SELECT valor FROM preferencias WHERE clave = ?", (clave,)).fetchone()
        return fila[0] if fila else None

    def cerrar(self):
        self.almacenamiento.cerrar()

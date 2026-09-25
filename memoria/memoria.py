from memoria.almacenamiento import Almacenamiento


class Memory:
    def __init__(self):
        self.almacenamiento = Almacenamiento()

    def guardar_memoria(self, clave, valor):
        cursor = self.almacenamiento.conexion.cursor()
        cursor.execute("""INSERT INTO memories (clave, valor)
            VALUES (?, ?) """,(clave, valor))
        self.almacenamiento.conexion.commit()

    def obtener_memorias(self, clave):
        cursor = self.almacenamiento.conexion.cursor()
        cursor.execute("""SELECT valor FROM memories
            WHERE clave = ? """,(clave,))
        resultados = cursor.fetchall()
        return [fila[0] for fila in resultados]

    def borrar_memorias(self, clave):
        cursor = self.almacenamiento.conexion.cursor()
        cursor.execute(
            """
            DELETE FROM memories
            WHERE clave = ?
            """,
            (clave,)
        )
        self.almacenamiento.conexion.commit()

    def guardar_preferencia(self, clave, valor):
        cursor = self.almacenamiento.conexion.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO preferences (clave, valor)
            VALUES (?, ?)
            """,
            (clave, valor)
        )

        self.almacenamiento.conexion.commit()

    def obtener_preferencia(self, clave):
        cursor = self.almacenamiento.conexion.cursor()
        cursor.execute(
            """
            SELECT valor
            FROM preferences
            WHERE clave = ?
            """,
            (clave,)
        )

        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]
        return None

    def cerrar(self):
        self.almacenamiento.cerrar()
from typing import Optional
from dao.conexion import ConexionBD
from model.estudiante import Estudiante


class EstudianteDAO:
    """
    Data Access Object (DAO) para la entidad Estudiante.
    Implementa operaciones CRUD aplicando consultas parametrizadas (?)
    para garantizar la protección contra inyecciones SQL (SQL Injection).
    """

    @staticmethod
    def insertar(estudiante: Estudiante) -> bool:
        """
        Inserta un nuevo estudiante en la base de datos de forma segura.
        Retorna True si la inserción fue exitosa, False si el RUT ya existe o hubo error.
        """
        if not isinstance(estudiante, Estudiante):
            return False
        if not estudiante.validar_rut():
            print("[EstudianteDAO] RUT inválido: no se acepta un estudiante con dígito verificador incorrecto.")
            return False

        if EstudianteDAO.obtener_por_rut(estudiante.rut):
            print("[EstudianteDAO] El RUT ya existe en la base de datos.")
            return False

        sql = """
        INSERT INTO estudiante (
            rut, primer_nombre, segundo_nombre, primer_apellido,
            segundo_apellido, email, direccion, tiene_deuda_pendiente
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        valores = (
            estudiante.rut,
            estudiante.primer_nombre,
            estudiante.segundo_nombre,
            estudiante.primer_apellido,
            estudiante.segundo_apellido,
            estudiante.email,
            estudiante.direccion,
            1 if estudiante.tiene_deuda_pendiente else 0
        )
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, valores)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as error:
            print(f"[EstudianteDAO] Error al insertar estudiante: {error}")
            return False

    @staticmethod
    def obtener_por_rut(rut: str) -> Optional[Estudiante]:
        """
        Busca un estudiante por su RUT mediante consulta parametrizada.
        Reconstruye y retorna una instancia del modelo de dominio Estudiante.
        """
        sql = """
        SELECT rut, primer_nombre, segundo_nombre, primer_apellido,
               segundo_apellido, email, direccion, tiene_deuda_pendiente
        FROM estudiante
        WHERE rut = ?;
        """
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (rut.strip().upper(),))
                fila = cursor.fetchone()

                if fila:
                    return Estudiante(
                        rut=fila["rut"],
                        primer_nombre=fila["primer_nombre"],
                        segundo_nombre=fila["segundo_nombre"],
                        primer_apellido=fila["primer_apellido"],
                        segundo_apellido=fila["segundo_apellido"],
                        email=fila["email"],
                        direccion=fila["direccion"],
                        tiene_deuda_pendiente=bool(fila["tiene_deuda_pendiente"])
                    )
                return None
        except Exception as error:
            print(f"[EstudianteDAO] Error al buscar estudiante por RUT: {error}")
            return None

    @staticmethod
    def listar_todos() -> list[Estudiante]:
        """
        Retorna la lista completa de todos los estudiantes registrados en la institución.
        """
        sql = """
        SELECT rut, primer_nombre, segundo_nombre, primer_apellido,
               segundo_apellido, email, direccion, tiene_deuda_pendiente
        FROM estudiante
        ORDER BY primer_apellido ASC, primer_nombre ASC;
        """
        estudiantes: list[Estudiante] = []
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                for fila in cursor.fetchall():
                    estudiantes.append(
                        Estudiante(
                            rut=fila["rut"],
                            primer_nombre=fila["primer_nombre"],
                            segundo_nombre=fila["segundo_nombre"],
                            primer_apellido=fila["primer_apellido"],
                            segundo_apellido=fila["segundo_apellido"],
                            email=fila["email"],
                            direccion=fila["direccion"],
                            tiene_deuda_pendiente=bool(fila["tiene_deuda_pendiente"])
                        )
                    )
        except Exception as error:
            print(f"[EstudianteDAO] Error al listar estudiantes: {error}")

        return estudiantes

    @staticmethod
    def actualizar(estudiante: Estudiante) -> bool:
        """
        Actualiza los datos personales y estado financiero de un estudiante existente.
        """
        sql = """
        UPDATE estudiante
        SET primer_nombre = ?,
            segundo_nombre = ?,
            primer_apellido = ?,
            segundo_apellido = ?,
            email = ?,
            direccion = ?,
            tiene_deuda_pendiente = ?
        WHERE rut = ?;
        """
        valores = (
            estudiante.primer_nombre,
            estudiante.segundo_nombre,
            estudiante.primer_apellido,
            estudiante.segundo_apellido,
            estudiante.email,
            estudiante.direccion,
            1 if estudiante.tiene_deuda_pendiente else 0,
            estudiante.rut
        )
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, valores)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as error:
            print(f"[EstudianteDAO] Error al actualizar estudiante: {error}")
            return False

    @staticmethod
    def actualizar_estado_deuda(rut: str, tiene_deuda: bool) -> bool:
        """
        Actualiza únicamente el estado de morosidad/deuda de un estudiante.
        """
        sql = "UPDATE estudiante SET tiene_deuda_pendiente = ? WHERE rut = ?;"
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (1 if tiene_deuda else 0, rut.strip().upper()))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as error:
            print(f"[EstudianteDAO] Error al actualizar deuda: {error}")
            return False

    @staticmethod
    def eliminar(rut: str) -> bool:
        """
        Elimina un estudiante de la base de datos por su RUT.
        """
        sql = "DELETE FROM estudiante WHERE rut = ?;"
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (rut.strip().upper(),))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as error:
            print(f"[EstudianteDAO] Error al eliminar estudiante: {error}")
            return False

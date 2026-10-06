from typing import Optional
from dao.conexion import ConexionBD
from model.asignatura import Asignatura
from model.electivo import Electivo


class AsignaturaDAO:
    """
    Data Access Object (DAO) para Asignatura y Electivo.
    Administra la persistencia del catálogo curricular y el control de cupos.
    """

    @staticmethod
    def insertar(asignatura: Asignatura) -> Optional[int]:
        """
        Registra una nueva asignatura o electivo en la base de datos.
        Retorna el id_asignatura generado por autoincremento.
        """
        sql = """
        INSERT INTO asignatura (nombre, tipo, cupo_maximo, cupo_disponible)
        VALUES (?, ?, ?, ?);
        """
        es_electivo = isinstance(asignatura, Electivo)
        tipo = "Electivo" if es_electivo else "Regular"
        cupo_max = asignatura.cupo_maximo if es_electivo else 0
        cupo_disp = asignatura.cupo_disponible if es_electivo else 0

        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (asignatura.nombre, tipo, cupo_max, cupo_disp))
                conn.commit()
                return cursor.lastrowid
        except Exception as error:
            print(f"[AsignaturaDAO] Error al insertar asignatura: {error}")
            return None

    @staticmethod
    def _mapear_fila(fila) -> Optional[Asignatura]:
        """Convierte una fila de la BD a Asignatura o Electivo."""
        if not fila:
            return None

        if fila["tipo"] == "Electivo":
            obj = Electivo(nombre=fila["nombre"], cupo_maximo=fila["cupo_maximo"])
            obj._Electivo__cupo_disponible = fila["cupo_disponible"]
            return obj
        else:
            return Asignatura(nombre=fila["nombre"])

    @classmethod
    def obtener_por_id(cls, id_asignatura: int) -> Optional[Asignatura]:
        """Busca una asignatura por su ID numérico."""
        sql = "SELECT * FROM asignatura WHERE id_asignatura = ?;"
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (id_asignatura,))
                return cls._mapear_fila(cursor.fetchone())
        except Exception as error:
            print(f"[AsignaturaDAO] Error al buscar asignatura por ID: {error}")
            return None

    @classmethod
    def obtener_por_nombre(cls, nombre: str) -> Optional[Asignatura]:
        """Busca una asignatura por su nombre."""
        sql = "SELECT * FROM asignatura WHERE UPPER(nombre) = ?;"
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (nombre.strip().upper(),))
                return cls._mapear_fila(cursor.fetchone())
        except Exception as error:
            print(f"[AsignaturaDAO] Error al buscar asignatura por nombre: {error}")
            return None

    @classmethod
    def listar_todas(cls) -> list[Asignatura]:
        """Retorna todas las asignaturas y electivos registrados."""
        sql = "SELECT * FROM asignatura ORDER BY nombre ASC;"
        asignaturas: list[Asignatura] = []
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                for fila in cursor.fetchall():
                    obj = cls._mapear_fila(fila)
                    if obj:
                        asignaturas.append(obj)
        except Exception as error:
            print(f"[AsignaturaDAO] Error al listar asignaturas: {error}")

        return asignaturas

    @staticmethod
    def actualizar_cupo(id_asignatura: int, nuevo_cupo: int) -> bool:
        """Actualiza el cupo disponible de un electivo."""
        sql = "UPDATE asignatura SET cupo_disponible = ? WHERE id_asignatura = ?;"
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (nuevo_cupo, id_asignatura))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as error:
            print(f"[AsignaturaDAO] Error al actualizar cupo: {error}")
            return False

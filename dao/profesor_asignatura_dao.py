from dao.conexion import ConexionBD


class ProfesorAsignaturaDAO:
    """Gestiona qué asignaturas puede calificar cada profesor."""

    @staticmethod
    def asignar(id_trabajador: str, id_asignatura: int) -> bool:
        sql = """
        INSERT OR IGNORE INTO profesor_asignatura (id_trabajador, id_asignatura)
        VALUES (?, ?);
        """
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.execute(sql, (id_trabajador.strip().upper(), id_asignatura))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as error:
            print(f"[ProfesorAsignaturaDAO] No se pudo asignar la asignatura: {error}")
            return False

    @staticmethod
    def tiene_asignacion(id_trabajador: str, id_asignatura: int) -> bool:
        sql = """
        SELECT 1 FROM profesor_asignatura
        WHERE id_trabajador = ? AND id_asignatura = ?;
        """
        with ConexionBD.obtener_conexion() as conn:
            return conn.execute(sql, (id_trabajador.strip().upper(), id_asignatura)).fetchone() is not None
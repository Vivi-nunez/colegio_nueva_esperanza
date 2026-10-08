from typing import Optional

from dao.conexion import ConexionBD


class EvaluacionDAO:
    """Persiste evaluaciones asociadas a estudiante, asignatura y profesor."""

    @staticmethod
    def insertar(
        id_evaluacion: str,
        rut_estudiante: str,
        id_asignatura: int,
        id_profesor: str,
        tipo_evaluacion: str,
        fecha: str,
        periodo_academico: str,
        ponderacion: float,
        nota: float,
        observacion: str = "",
    ) -> bool:
        sql = """
        INSERT INTO evaluacion_registrada (
            id_evaluacion, rut_estudiante, id_asignatura, id_profesor,
            tipo_evaluacion, fecha, periodo_academico, ponderacion, nota, observacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            with ConexionBD.obtener_conexion() as conn:
                conn.execute(
                    sql,
                    (
                        id_evaluacion.strip().upper(),
                        rut_estudiante.strip().upper(),
                        id_asignatura,
                        id_profesor.strip().upper(),
                        tipo_evaluacion,
                        fecha,
                        periodo_academico,
                        ponderacion,
                        nota,
                        observacion.strip(),
                    ),
                )
                conn.commit()
                return True
        except Exception as error:
            print(f"[EvaluacionDAO] No se pudo guardar la evaluación: {error}")
            return False

    @staticmethod
    def listar_por_estudiante_asignatura(
        rut_estudiante: str, id_asignatura: int, periodo_academico: str
    ) -> list[dict]:
        sql = """
        SELECT id_registro, id_evaluacion, tipo_evaluacion, fecha,
               periodo_academico, ponderacion, nota, observacion, id_profesor
        FROM evaluacion_registrada
        WHERE rut_estudiante = ? AND id_asignatura = ? AND periodo_academico = ?
        ORDER BY fecha, id_registro;
        """
        with ConexionBD.obtener_conexion() as conn:
            rows = conn.execute(
                sql, (rut_estudiante.strip().upper(), id_asignatura, periodo_academico)
            ).fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def calcular_promedio_ponderado(
        rut_estudiante: str, id_asignatura: int, periodo_academico: str
    ) -> Optional[float]:
        sql = """
        SELECT SUM(nota * ponderacion) / SUM(ponderacion) AS promedio
        FROM evaluacion_registrada
        WHERE rut_estudiante = ? AND id_asignatura = ? AND periodo_academico = ?;
        """
        with ConexionBD.obtener_conexion() as conn:
            row = conn.execute(
                sql, (rut_estudiante.strip().upper(), id_asignatura, periodo_academico)
            ).fetchone()
            return round(row["promedio"], 1) if row["promedio"] is not None else None
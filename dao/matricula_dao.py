from typing import Optional
from dao.conexion import ConexionBD
from dao.cobro_mensual_dao import CobroMensualDAO
from dao.estudiante_dao import EstudianteDAO
from model.matricula import Matricula
from model.detalle_matricula import DetalleMatricula
from model.asignatura import Asignatura
from model.electivo import Electivo


class MatriculaDAO:
    """
    Data Access Object (DAO) para la transacción de Matrícula y DetalleMatricula.
    Implementa transacciones atómicas seguras (commit/rollback automático)
    y validación previa de deuda del estudiante con consultas parametrizadas.
    """

    @staticmethod
    def insertar(matricula: Matricula, lista_asignaturas: list[tuple[int, Asignatura]] = None) -> bool:
        """
        Registra el contrato formal de matrícula y sus asignaturas inscritas de manera transaccional.
        Verifica previamente en base de datos que el alumno no mantenga deudas pendientes.
        """
        if not matricula.estudiante:
            print("[MatriculaDAO] Error: No se puede matricular sin un estudiante asignado.")
            return False

        # Verificación de integridad financiera
        estudiante_db = EstudianteDAO.obtener_por_rut(matricula.estudiante.rut)
        anio_matricula = int(matricula.fecha[:4])
        deuda_anio_anterior = CobroMensualDAO.tiene_deuda_del_anio_anterior(
            matricula.estudiante.rut, anio_matricula
        )
        if not estudiante_db or estudiante_db.tiene_deuda_pendiente or deuda_anio_anterior:
            print(f"[MatriculaDAO] Rechazada: El estudiante {matricula.estudiante.rut} tiene deuda o no existe.")
            return False

        sql_matricula = """
        INSERT INTO matricula (id_matricula, rut_estudiante, fecha, arancel_uf, semestre)
        VALUES (?, ?, ?, ?, ?);
        """
        sql_detalle = """
        INSERT INTO detalle_matricula (id_matricula, id_asignatura, estado)
        VALUES (?, ?, ?);
        """
        sql_descontar_cupo = """
        UPDATE asignatura
        SET cupo_disponible = cupo_disponible - 1
        WHERE id_asignatura = ? AND tipo = 'Electivo' AND cupo_disponible > 0;
        """

        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()

                # 1. Inserta la cabecera de la matrícula
                cursor.execute(sql_matricula, (
                    matricula.id_matricula,
                    matricula.estudiante.rut,
                    matricula.fecha,
                    matricula.arancel_uf,
                    matricula.semestre
                ))

                # 2. Inserta los detalles de asignaturas asociadas
                if lista_asignaturas:
                    for id_asig, obj_asig in lista_asignaturas:
                        if isinstance(obj_asig, Electivo):
                            # Descuenta cupo en base de datos asegurando atomicidad
                            cursor.execute(sql_descontar_cupo, (id_asig,))
                            if cursor.rowcount == 0:
                                raise ValueError(f"Cupo agotado para el electivo '{obj_asig.nombre}'.")

                        cursor.execute(sql_detalle, (matricula.id_matricula, id_asig, "Inscrita"))

                conn.commit()
                print(f"[MatriculaDAO] Matrícula N°{matricula.id_matricula} registrada exitosamente.")
                return True

        except Exception as error:
            print(f"[MatriculaDAO] Error en la transacción de matrícula: {error}")
            return False

    @staticmethod
    def obtener_por_id(id_matricula: int) -> Optional[Matricula]:
        """
        Obtiene una matrícula por su ID con el estudiante asociado y sus materias inscritas.
        """
        sql_mat = "SELECT * FROM matricula WHERE id_matricula = ?;"
        sql_det = """
        SELECT d.id_detalle, d.estado, a.id_asignatura, a.nombre, a.tipo
        FROM detalle_matricula d
        JOIN asignatura a ON d.id_asignatura = a.id_asignatura
        WHERE d.id_matricula = ?;
        """
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql_mat, (id_matricula,))
                fila_mat = cursor.fetchone()

                if not fila_mat:
                    return None

                estudiante = EstudianteDAO.obtener_por_rut(fila_mat["rut_estudiante"])
                mat = Matricula(
                    id_matricula=fila_mat["id_matricula"],
                    fecha=fila_mat["fecha"],
                    arancel_uf=fila_mat["arancel_uf"],
                    semestre=fila_mat["semestre"],
                    estudiante=estudiante
                )

                # Carga los detalles
                cursor.execute(sql_det, (id_matricula,))
                for f in cursor.fetchall():
                    asig = Asignatura(nombre=f["nombre"])
                    detalle = DetalleMatricula(asignatura=asig, estado=f["estado"])
                    mat._Matricula__detalles.append(detalle)

                return mat
        except Exception as error:
            print(f"[MatriculaDAO] Error al obtener matrícula: {error}")
            return None

    @staticmethod
    def listar_todas() -> list[Matricula]:
        """Retorna todas las matrículas registradas."""
        sql = "SELECT id_matricula FROM matricula ORDER BY id_matricula DESC;"
        matriculas: list[Matricula] = []
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                for fila in cursor.fetchall():
                    mat = MatriculaDAO.obtener_por_id(fila["id_matricula"])
                    if mat:
                        matriculas.append(mat)
        except Exception as error:
            print(f"[MatriculaDAO] Error al listar matrículas: {error}")

        return matriculas

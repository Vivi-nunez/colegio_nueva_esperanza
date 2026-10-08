from dao import conexion as conexion_module
from dao.asignatura_dao import AsignaturaDAO
from dao.conexion import ConexionBD
from dao.profesor_asignatura_dao import ProfesorAsignaturaDAO
from dao.trabajador_dao import TrabajadorDAO
from model.profesor import Profesor

import main


def test_seed_creates_an_idempotent_scoped_professor_per_subject(monkeypatch, tmp_path):
    monkeypatch.setattr(conexion_module, "RUTA_BASE_DATOS", tmp_path / "pruebas.db")
    ConexionBD.inicializar_base_datos()

    main.inicializar_datos_semilla()
    asignaturas = AsignaturaDAO.listar_todas()

    for asignatura in asignaturas:
        id_asignatura = AsignaturaDAO.obtener_id_por_nombre(asignatura.nombre)
        assert id_asignatura is not None

        id_profesor = f"DOC-ASIG-{id_asignatura:03d}"
        profesor = TrabajadorDAO.obtener_por_id(id_profesor)
        assert isinstance(profesor, Profesor)
        assert profesor.autentificar("profe123")
        assert profesor.validar_rut()
        assert profesor.especialidad == asignatura.nombre.title()
        assert ProfesorAsignaturaDAO.tiene_asignacion(id_profesor, id_asignatura)
        assert set(main.obtener_opciones_por_rol(profesor)) == {"0", "7", "8", "9", "13"}
        with ConexionBD.obtener_conexion() as conn:
            asignaciones = conn.execute(
                "SELECT COUNT(*) FROM profesor_asignatura WHERE id_trabajador = ?;",
                (id_profesor,),
            ).fetchone()[0]
        assert asignaciones == 1

    with ConexionBD.obtener_conexion() as conn:
        cantidad_inicial = conn.execute(
            "SELECT COUNT(*) FROM profesor_asignatura;"
        ).fetchone()[0]

    main.inicializar_datos_semilla()

    with ConexionBD.obtener_conexion() as conn:
        cantidad_final = conn.execute(
            "SELECT COUNT(*) FROM profesor_asignatura;"
        ).fetchone()[0]

    assert cantidad_final == cantidad_inicial == len(asignaturas)

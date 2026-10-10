import sqlite3
from types import SimpleNamespace

import pytest

from dao import conexion as conexion_module
from dao.asignatura_dao import AsignaturaDAO
from dao.cobro_mensual_dao import CobroMensualDAO
from dao.evaluacion_dao import EvaluacionDAO
from dao.conexion import ConexionBD
from dao.estudiante_dao import EstudianteDAO
from dao.matricula_dao import MatriculaDAO
from dao.profesor_asignatura_dao import ProfesorAsignaturaDAO
from dao.trabajador_dao import TrabajadorDAO
from model.asignatura import Asignatura
from model.estudiante import Estudiante
from model.electivo import Electivo
from model.matricula import Matricula
from model.profesor import Profesor
from model.administrativo import Administrativo
from model.excepciones import DeudaPendienteError, CupoAgotadoError

import main
from model.calificacion import Calificacion
from model.indicador_uf import IndicadorUF


def _usar_base_temporal(monkeypatch, tmp_path):
    monkeypatch.setattr(conexion_module, "RUTA_BASE_DATOS", tmp_path / "pruebas.db")
    ConexionBD.inicializar_base_datos()


def _estudiante(rut="12.345.678-5", nombre="Ana", tiene_deuda=False):
    return Estudiante(
        rut=rut,
        primer_nombre=nombre,
        segundo_nombre="",
        primer_apellido="Prueba",
        segundo_apellido="",
        email=f"{nombre.lower()}@test.cl",
        direccion="Santiago",
        tiene_deuda_pendiente=tiene_deuda,
    )


def _administrativo():
    return Administrativo(
        rut="11.111.111-1",
        primer_nombre="Rosa",
        segundo_nombre="",
        primer_apellido="Soto",
        segundo_apellido="",
        email="rosa@test.cl",
        direccion="Santiago",
        id_trabajador="ADM01",
        clave="admin123",
        cargo="Inspectoría",
    )


def _matricula(id_matricula, estudiante):
    return Matricula(
        id_matricula=id_matricula,
        fecha="2026-10-07",
        arancel_uf=3.0,
        semestre="2026-2",
        estudiante=estudiante,
    )


def test_estudiante_dao_rejects_invalid_rut():
    ConexionBD.inicializar_base_datos()
    estudiante = Estudiante(
        rut="11.111.111-0",
        primer_nombre="Ana",
        segundo_nombre="",
        primer_apellido="Pérez",
        segundo_apellido="",
        email="ana@test.cl",
        direccion="Santiago",
        tiene_deuda_pendiente=False,
    )

    assert estudiante.validar_rut() is False
    assert EstudianteDAO.insertar(estudiante) is False


def test_rut_validation_is_prioritized_over_email_validation():
    with pytest.raises(ValueError, match="RUT"):
        main.validar_datos_persona("11.111.111-A", "correo_invalido")


def test_role_menu_restricts_professor_access():
    profesor = Profesor(
        rut="12.222.222-2",
        primer_nombre="Carlos",
        segundo_nombre="",
        primer_apellido="Mendoza",
        segundo_apellido="",
        email="carlos@test.cl",
        direccion="Santiago",
        id_trabajador="DOC01",
        clave="profe123",
        especialidad="Matemáticas",
    )
    administrativo = Administrativo(
        rut="11.111.111-1",
        primer_nombre="Rosa",
        segundo_nombre="",
        primer_apellido="Soto",
        segundo_apellido="",
        email="rosa@test.cl",
        direccion="Santiago",
        id_trabajador="ADM01",
        clave="admin123",
        cargo="Secretaría",
    )

    opciones_profesor = main.obtener_opciones_por_rol(profesor)
    opciones_admin = main.obtener_opciones_por_rol(administrativo)

    assert "1" not in opciones_profesor
    assert "9" in opciones_profesor
    assert "13" in opciones_profesor
    assert "1" in opciones_admin
    assert "10" not in opciones_profesor
    assert "10" in opciones_admin


def test_student_deletion_requires_confirmation(monkeypatch, capsys):
    estudiante = Estudiante(
        rut="12.345.678-5",
        primer_nombre="Ana",
        segundo_nombre="",
        primer_apellido="Pérez",
        segundo_apellido="",
        email="ana@test.cl",
        direccion="Santiago",
    )
    eliminados = []
    respuestas = iter([estudiante.rut, "s"])
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))
    monkeypatch.setattr(EstudianteDAO, "obtener_por_rut", lambda _: estudiante)
    monkeypatch.setattr(EstudianteDAO, "eliminar", lambda rut: eliminados.append(rut) or True)

    main.eliminar_estudiante(_administrativo())

    assert eliminados == [estudiante.rut]
    assert "eliminado correctamente" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("tipo", "datos", "aporte_esperado"),
    [
        ("1", ["85", "100"], "2.44"),
        ("2", ["BUENO"], "1.50"),
        ("3", ["14 min"], "3.50"),
    ],
)
def test_docente_muestra_aporte_ponderado(monkeypatch, tmp_path, capsys, tipo, datos, aporte_esperado):
    _usar_base_temporal(monkeypatch, tmp_path)
    profesor = Profesor(
        rut="12.345.678-5",
        primer_nombre="Carlos",
        segundo_nombre="",
        primer_apellido="Mendoza",
        segundo_apellido="",
        email="carlos@test.cl",
        direccion="Santiago",
        id_trabajador="DOC01",
        clave="profe123",
        especialidad="Matemáticas",
    )
    estudiante = _estudiante("22.222.222-2", "Luis")
    assert TrabajadorDAO.insertar(profesor)
    assert EstudianteDAO.insertar(estudiante)
    id_asignatura = AsignaturaDAO.insertar(Asignatura("Matemáticas"))
    assert ProfesorAsignaturaDAO.asignar(profesor.id_trabajador, id_asignatura)

    ponderacion = {"1": "40", "2": "30", "3": "50"}[tipo]
    respuestas = iter([estudiante.rut, "Matemáticas", tipo, "2026-1", ponderacion, *datos, ""])
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))

    main.registrar_evaluacion_y_nota_docente(profesor)

    output = capsys.readouterr().out
    assert f"[APORTE PONDERADO]: {aporte_esperado} puntos" in output
    assert "[PROMEDIO ACUMULADO 2026-1]" in output
    assert len(EvaluacionDAO.listar_por_estudiante_asignatura(estudiante.rut, id_asignatura, "2026-1")) == 1


@pytest.mark.parametrize("nota", [0.5, 8.5])
def test_calificacion_rejects_notes_outside_school_scale(nota):
    with pytest.raises(ValueError, match="escala de 1.0 a 7.0"):
        Calificacion(nota)


def test_uf_fallback_is_reported_in_console(monkeypatch, capsys):
    import model.indicador_uf as indicador_uf

    def fail_request(*args, **kwargs):
        raise ConnectionError("sin internet")

    monkeypatch.setattr(indicador_uf.requests, "get", fail_request)
    monkeypatch.setattr("builtins.input", lambda _: "1")

    main.consultar_uf_y_calcular_arancel()

    output = capsys.readouterr().out
    assert "[AVISO] No se pudo consultar la API" in output
    assert "[OK] Valor diario de la UF obtenido" not in output
    assert not IndicadorUF().obtenido_desde_api


def test_student_persists_after_reopening_database(monkeypatch, tmp_path):
    _usar_base_temporal(monkeypatch, tmp_path)
    estudiante = _estudiante()

    assert EstudianteDAO.insertar(estudiante)
    assert EstudianteDAO.obtener_por_rut(estudiante.rut).email == estudiante.email


def test_enrollment_stores_three_subject_details(monkeypatch, tmp_path):
    _usar_base_temporal(monkeypatch, tmp_path)
    estudiante = _estudiante()
    assert EstudianteDAO.insertar(estudiante)
    asignaturas = [Asignatura("Lenguaje"), Asignatura("Matemáticas"), Electivo("Teatro", 2)]
    asignaturas_con_id = [
        (AsignaturaDAO.insertar(asignatura), asignatura)
        for asignatura in asignaturas
    ]
    matricula = _matricula(1001, estudiante)

    assert MatriculaDAO.insertar(matricula, asignaturas_con_id)
    recuperada = MatriculaDAO.obtener_por_id(1001)

    assert recuperada is not None
    assert {detalle.asignatura.nombre for detalle in recuperada.detalles} == {
        "Lenguaje",
        "Matemáticas",
        "Teatro",
    }


def test_student_with_debt_cannot_be_enrolled(monkeypatch, tmp_path):
    _usar_base_temporal(monkeypatch, tmp_path)
    estudiante = _estudiante(tiene_deuda=True)
    assert EstudianteDAO.insertar(estudiante)

    with pytest.raises(DeudaPendienteError, match="deuda pendiente"):
        MatriculaDAO.insertar(_matricula(1002, estudiante))
    assert MatriculaDAO.obtener_por_id(1002) is None


def test_full_elective_rejects_enrollment_and_rolls_back(monkeypatch, tmp_path):
    _usar_base_temporal(monkeypatch, tmp_path)
    primer_estudiante = _estudiante()
    segundo_estudiante = _estudiante("22.222.222-2", "Luis")
    assert EstudianteDAO.insertar(primer_estudiante)
    assert EstudianteDAO.insertar(segundo_estudiante)
    electivo = Electivo("Teatro", 1)
    id_electivo = AsignaturaDAO.insertar(electivo)

    assert MatriculaDAO.insertar(_matricula(1003, primer_estudiante), [(id_electivo, electivo)])
    with pytest.raises(CupoAgotadoError, match="Cupo agotado"):
        MatriculaDAO.insertar(_matricula(1004, segundo_estudiante), [(id_electivo, electivo)])
    assert MatriculaDAO.obtener_por_id(1004) is None
    assert AsignaturaDAO.obtener_por_id(id_electivo).cupo_disponible == 0


def test_student_grade_records_accumulate_into_weighted_average(monkeypatch, tmp_path):
    _usar_base_temporal(monkeypatch, tmp_path)
    estudiante = _estudiante()
    profesor = Profesor(
        rut="11.111.111-1",
        primer_nombre="Carlos",
        segundo_nombre="",
        primer_apellido="Docente",
        segundo_apellido="",
        email="carlos@test.cl",
        direccion="Santiago",
        id_trabajador="DOC02",
        clave="profe123",
        especialidad="Matemáticas",
    )
    assert EstudianteDAO.insertar(estudiante)
    assert TrabajadorDAO.insertar(profesor)
    id_asignatura = AsignaturaDAO.insertar(Asignatura("Matemáticas"))
    assert EvaluacionDAO.insertar("EV-1", estudiante.rut, id_asignatura, "DOC02", "Prueba", "2026-03-01", "2026-1", 40, 5.0)
    assert EvaluacionDAO.insertar("EV-2", estudiante.rut, id_asignatura, "DOC02", "Trabajo", "2026-04-01", "2026-1", 60, 7.0)
    assert EvaluacionDAO.insertar("EV-3", estudiante.rut, id_asignatura, "DOC02", "Prueba", "2026-08-01", "2026-2", 100, 2.0)

    assert EvaluacionDAO.calcular_promedio_ponderado(estudiante.rut, id_asignatura, "2026-1") == 6.2
    assert len(EvaluacionDAO.listar_por_estudiante_asignatura(estudiante.rut, id_asignatura, "2026-1")) == 2


def test_monthly_charges_record_partial_and_full_payment(monkeypatch, tmp_path):
    _usar_base_temporal(monkeypatch, tmp_path)
    estudiante = _estudiante()
    assert EstudianteDAO.insertar(estudiante)
    id_cobro = CobroMensualDAO.emitir(estudiante.rut, "2026-03", 4.0, 40000)

    assert id_cobro is not None
    assert not CobroMensualDAO.emitir(estudiante.rut, "2026-03", 4.0, 41000)
    assert CobroMensualDAO.registrar_pago(id_cobro, 50000, "Abono inicial")
    parcial = CobroMensualDAO.listar_por_estudiante(estudiante.rut)[0]
    assert (parcial["total_pesos"], parcial["pagado"], parcial["saldo"], parcial["estado"]) == (
        160000,
        50000,
        110000,
        "Abono parcial",
    )
    assert not CobroMensualDAO.registrar_pago(id_cobro, 110001)
    assert CobroMensualDAO.registrar_pago(id_cobro, 110000, "Saldo final")
    pagado = CobroMensualDAO.listar_por_estudiante(estudiante.rut)[0]
    assert (pagado["pagado"], pagado["saldo"], pagado["estado"]) == (160000, 0, "Pagado")


def test_monthly_billing_console_emits_charge_and_records_payment(monkeypatch, tmp_path, capsys):
    _usar_base_temporal(monkeypatch, tmp_path)
    estudiante = _estudiante()
    assert EstudianteDAO.insertar(estudiante)
    monkeypatch.setattr(
        main,
        "IndicadorUF",
        lambda: SimpleNamespace(obtenido_desde_api=True, valor_diario=40000.0),
    )
    respuestas = iter(
        ["1", estudiante.rut, "2026-03", "4", "2", "1", "50000", "Abono inicial", "3", estudiante.rut, "0"]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))

    main.gestionar_cobros_mensuales(_administrativo())

    output = capsys.readouterr().out
    cobro = CobroMensualDAO.listar_por_estudiante(estudiante.rut)[0]
    assert "Cobro N°1 emitido por $160,000 CLP" in output
    assert "Abono parcial" in output
    assert (cobro["pagado"], cobro["saldo"], cobro["estado"]) == (50000, 110000, "Abono parcial")


def test_admin_can_assign_subject_to_teacher(monkeypatch, tmp_path, capsys):
    _usar_base_temporal(monkeypatch, tmp_path)
    profesor = Profesor(
        rut="12.345.678-5",
        primer_nombre="Carlos",
        segundo_nombre="",
        primer_apellido="Docente",
        segundo_apellido="",
        email="carlos@test.cl",
        direccion="Santiago",
        id_trabajador="DOC03",
        clave="profe123",
    )
    assert TrabajadorDAO.insertar(profesor)
    id_asignatura = AsignaturaDAO.insertar(Asignatura("Historia"))
    respuestas = iter([profesor.id_trabajador, "Historia"])
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))

    main.asignar_asignatura_a_profesor(_administrativo())

    assert ProfesorAsignaturaDAO.tiene_asignacion(profesor.id_trabajador, id_asignatura)
    assert "asignada a Carlos Docente" in capsys.readouterr().out


def test_professor_cannot_grade_unassigned_subject(monkeypatch, tmp_path, capsys):
    _usar_base_temporal(monkeypatch, tmp_path)
    profesor = Profesor(
        rut="12.345.678-5",
        primer_nombre="Carlos",
        segundo_nombre="",
        primer_apellido="Docente",
        segundo_apellido="",
        email="carlos@test.cl",
        direccion="Santiago",
        id_trabajador="DOC04",
        clave="profe123",
    )
    estudiante = _estudiante("22.222.222-2", "Luis")
    assert TrabajadorDAO.insertar(profesor)
    assert EstudianteDAO.insertar(estudiante)
    id_asignatura = AsignaturaDAO.insertar(Asignatura("Historia"))
    respuestas = iter([estudiante.rut, "Historia"])
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))

    main.registrar_evaluacion_y_nota_docente(profesor)

    assert "PERMISO DENEGADO" in capsys.readouterr().out
    assert EvaluacionDAO.listar_por_estudiante_asignatura(estudiante.rut, id_asignatura, "2026-1") == []


def test_unpaid_previous_year_monthly_charge_blocks_enrollment(monkeypatch, tmp_path):
    _usar_base_temporal(monkeypatch, tmp_path)
    estudiante = _estudiante()
    assert EstudianteDAO.insertar(estudiante)
    assert CobroMensualDAO.emitir(estudiante.rut, "2025-12", 3.0, 40000)

    with pytest.raises(DeudaPendienteError, match="deuda pendiente"):
        MatriculaDAO.insertar(_matricula(1005, estudiante))
    assert MatriculaDAO.obtener_por_id(1005) is None


def test_unexpected_database_error_is_not_misclassified(monkeypatch, tmp_path):
    _usar_base_temporal(monkeypatch, tmp_path)
    estudiante = _estudiante()
    assert EstudianteDAO.insertar(estudiante)

    def _fallar_conexion():
        raise sqlite3.DatabaseError("Base de datos caida")

    monkeypatch.setattr("dao.matricula_dao.ConexionBD.obtener_conexion", _fallar_conexion)

    with pytest.raises(sqlite3.DatabaseError, match="Base de datos caida"):
        MatriculaDAO.insertar(_matricula(1006, estudiante))


def test_invalid_rut_is_rejected_before_enrollment_lookup(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "12.345.678-9")
    monkeypatch.setattr(
        EstudianteDAO,
        "obtener_por_rut",
        lambda _: pytest.fail("No debe consultar la base con un RUT inválido"),
    )

    main.registrar_matricula_estudiante(_administrativo())

    assert "RUT inválido" in capsys.readouterr().out


def test_professor_cannot_invoke_enrollment_handler(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: pytest.fail("No debe pedir datos"))
    profesor = Profesor(
        rut="12.345.678-5",
        primer_nombre="Carlos",
        segundo_nombre="",
        primer_apellido="Docente",
        segundo_apellido="",
        email="carlos@test.cl",
        direccion="Santiago",
        id_trabajador="DOC01",
        clave="profe123",
    )

    main.registrar_matricula_estudiante(profesor)

    assert "PERMISO DENEGADO" in capsys.readouterr().out


def test_administrative_user_cannot_invoke_grade_handler(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: pytest.fail("No debe pedir datos"))

    main.registrar_evaluacion_y_nota_docente(_administrativo())

    assert "PERMISO DENEGADO" in capsys.readouterr().out

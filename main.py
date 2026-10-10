import sys
import re
from datetime import date
from model import (
    Estudiante,
    Trabajador,
    Administrativo,
    Profesor,
    Asignatura,
    Electivo,
    Arancel,
    IndicadorUF,
    Matricula,
    Calificacion,
    Prueba,
    Trabajo,
    PresentacionOral,
)
from model.excepciones import DeudaPendienteError, CupoAgotadoError
from dao import (
    ConexionBD,
    EstudianteDAO,
    TrabajadorDAO,
    AsignaturaDAO,
    MatriculaDAO,
    EvaluacionDAO,
    ProfesorAsignaturaDAO,
    CobroMensualDAO,
)

def inicializar_datos_semilla() -> None:
    """
    Inserta datos iniciales de prueba si la base de datos está vacía.
    Permite probar el sistema de inmediato con usuarios y materias predeterminadas.
    """
    # 1. Crear usuarios por defecto si no existen
    if not TrabajadorDAO.obtener_por_id("ADM01"):
        admin = Administrativo(
            rut="11.111.111-1",
            primer_nombre="Rosa",
            segundo_nombre="Maria",
            primer_apellido="Soto",
            segundo_apellido="Perez",
            email="rosa.soto@colegio.cl",
            direccion="Av. Concha y Toro 1234, Puente Alto",
            id_trabajador="ADM01",
            clave="admin123",
            cargo="Secretaría Académica y Cobranzas"
        )
        TrabajadorDAO.insertar(admin)

    if not TrabajadorDAO.obtener_por_id("DOC01"):
        profe = Profesor(
            rut="12.222.222-2",
            primer_nombre="Carlos",
            segundo_nombre="Eduardo",
            primer_apellido="Mendoza",
            segundo_apellido="Silva",
            email="carlos.mendoza@colegio.cl",
            direccion="Calle Balmaceda 456, Santiago",
            id_trabajador="DOC01",
            clave="profe123",
            especialidad="Educación General Básica"
        )
        TrabajadorDAO.insertar(profe)

    # 2. Asignaturas regulares del colegio (currículum escolar chileno)
    asignaturas_escolares = [
        "Lenguaje y Comunicación",
        "Matemáticas",
        "Ciencias Naturales"
    ]
    for nom in asignaturas_escolares:
        if not AsignaturaDAO.obtener_por_nombre(nom):
            AsignaturaDAO.insertar(Asignatura(nom))

    # 3. Talleres electivos adaptados a colegio regular de niños en Chile
    electivos_escolares = [
        ("Taller de Teatro Escolar", 15),
        ("Taller de Robótica Infantil", 12),
        ("Taller de Música y Coro", 15)
    ]
    for nom, cupo in electivos_escolares:
        if not AsignaturaDAO.obtener_por_nombre(nom):
            AsignaturaDAO.insertar(Electivo(nom, cupo_maximo=cupo))

    # 4. Crear un profesor de prueba por asignatura con permisos acotados a esa materia.
    for asignatura in AsignaturaDAO.listar_todas():
        id_asignatura = AsignaturaDAO.obtener_id_por_nombre(asignatura.nombre)
        if id_asignatura is None:
            raise RuntimeError(
                f"No se pudo obtener el ID de la asignatura '{asignatura.nombre}'."
            )

        id_profesor = f"DOC-ASIG-{id_asignatura:03d}"
        profesor = TrabajadorDAO.obtener_por_id(id_profesor)
        if profesor is None:
            cuerpo_rut = str(20_000_000 + id_asignatura)
            suma = 0
            multiplicador = 2
            for digito in reversed(cuerpo_rut):
                suma += int(digito) * multiplicador
                multiplicador = 2 if multiplicador == 7 else multiplicador + 1

            resto = 11 - (suma % 11)
            digito_verificador = (
                "0" if resto == 11 else "K" if resto == 10 else str(resto)
            )
            profesor = Profesor(
                rut=f"{cuerpo_rut}-{digito_verificador}",
                primer_nombre="Docente",
                segundo_nombre="",
                primer_apellido="Asignatura",
                segundo_apellido=str(id_asignatura),
                email=f"docente.asignatura.{id_asignatura}@colegio.cl",
                direccion="Colegio Nueva Esperanza",
                id_trabajador=id_profesor,
                clave="profe123",
                especialidad=asignatura.nombre,
            )
            if not TrabajadorDAO.insertar(profesor):
                raise RuntimeError(
                    f"No se pudo crear el profesor para '{asignatura.nombre}'."
                )
        elif not isinstance(profesor, Profesor):
            raise RuntimeError(
                f"El ID {id_profesor} ya existe y no corresponde a un profesor."
            )

        if not ProfesorAsignaturaDAO.tiene_asignacion(id_profesor, id_asignatura):
            if not ProfesorAsignaturaDAO.asignar(id_profesor, id_asignatura):
                raise RuntimeError(
                    f"No se pudo asignar '{asignatura.nombre}' al profesor {id_profesor}."
                )


def _rut_es_valido(rut: str) -> bool:
    """Valida el RUT chileno sin depender de la creación del objeto."""
    if not isinstance(rut, str):
        return False

    rut_limpio = rut.strip().upper().replace(".", "")
    if not rut_limpio:
        return False

    if "-" in rut_limpio:
        cuerpo, dv = rut_limpio.rsplit("-", 1)
    else:
        if len(rut_limpio) < 2:
            return False
        cuerpo = rut_limpio[:-1]
        dv = rut_limpio[-1]

    if len(cuerpo) < 2 or len(cuerpo) > 8 or not cuerpo.isdigit():
        return False
    if not dv.isdigit() and dv.upper() != "K":
        return False

    suma = 0
    multiplicador = 2
    for caracter in reversed(cuerpo):
        suma += int(caracter) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = 11 - (suma % 11)
    if resto == 11:
        dv_esperado = "0"
    elif resto == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(resto)

    return dv.upper() == dv_esperado


def _rut_canonico(rut: str) -> str | None:
    if not _rut_es_valido(rut):
        return None
    limpio = rut.strip().upper().replace(".", "").replace("-", "")
    cuerpo, dv = limpio[:-1], limpio[-1]
    cuerpo_formateado = re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1.", cuerpo)
    return f"{cuerpo_formateado}-{dv}"


def _email_es_valido(email: str) -> bool:
    """Valida el formato básico del email."""
    if not isinstance(email, str):
        return False
    email = email.strip().lower()
    return "@" in email and "." in email and email.count("@") == 1 and len(email.split("@", 1)[0]) > 0


def validar_datos_persona(rut: str, email: str) -> bool:
    """Revisa primero el RUT y luego el email para evitar que el error de correo oculte un RUT inválido."""
    if not _rut_es_valido(rut):
        raise ValueError("El RUT ingresado no cumple con el algoritmo Módulo 11.")
    if not _email_es_valido(email):
        raise ValueError("El correo electrónico debe ser válido (contener '@' y '.').")
    return True


def menu_autenticacion() -> Trabajador | None:
    """
    Gestiona el inicio de sesión del personal institucional mediante SHA-256.
    """
    print("\n" + "=" * 55)
    print("        INICIO DE SESIÓN - COLEGIO NUEVA ESPERANZA")
    print("=" * 55)
    print("Credenciales de demostración inicial:")
    print("  • Administrativo -> ID: ADM01  | Clave: admin123")
    print("  • Profesor       -> ID: DOC01  | Clave: profe123")
    print("  • Profesores por asignatura (clave: profe123):")
    for asignatura in AsignaturaDAO.listar_todas():
        id_asignatura = AsignaturaDAO.obtener_id_por_nombre(asignatura.nombre)
        if id_asignatura is not None:
            print(f"      {asignatura.nombre}: DOC-ASIG-{id_asignatura:03d}")
    print("-" * 55)

    id_trab = input("Ingrese su ID de Trabajador: ").strip().upper()
    clave = input("Ingrese su contraseña: ").strip()

    usuario = TrabajadorDAO.autenticar(id_trab, clave)
    if usuario:
        print(f"\n[OK] Autenticación exitosa. Bienvenido(a) {usuario.obtener_nombre_completo()}.")
        print(f"     Rol activo: {usuario.obtener_rol()}")
        return usuario
    else:
        print("\n[ERROR] ID de trabajador o contraseña incorrectos.")
        return None


def registrar_nuevo_estudiante(usuario: Trabajador) -> None:
    """Flujo para ingresar un nuevo estudiante con validación de RUT por módulo 11."""
    if not isinstance(usuario, Administrativo):
        print("[PERMISO DENEGADO] Solo el perfil administrativo puede registrar estudiantes.")
        return
    print("\n--- REGISTRO DE NUEVO ESTUDIANTE ---")
    try:
        rut = input("RUT (ej: 11.111.111-1): ").strip()
        primer_nombre = input("Primer Nombre: ").strip()
        segundo_nombre = input("Segundo Nombre (opcional): ").strip()
        primer_apellido = input("Primer Apellido: ").strip()
        segundo_apellido = input("Segundo Apellido (opcional): ").strip()
        email = input("Correo electrónico: ").strip()
        direccion = input("Dirección de residencia: ").strip()
        deuda_resp = input("¿Posee deuda pendiente previa? (s/n): ").strip().lower()
        tiene_deuda = deuda_resp in ["s", "si", "sí", "true", "1"]

        try:
            validar_datos_persona(rut, email)
        except ValueError as ve:
            print(f"\n[ERROR DE VALIDACIÓN]: {ve}")
            print("Registro cancelado. Debe corregir los datos antes de guardar.")
            return

        # Instancia el modelo de dominio (dispara validaciones de setters)
        estudiante = Estudiante(
            rut=rut,
            primer_nombre=primer_nombre,
            segundo_nombre=segundo_nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            email=email,
            direccion=direccion,
            tiene_deuda_pendiente=tiene_deuda
        )

        # Validación formal de RUT chileno Módulo 11
        if not estudiante.validar_rut():
            print("\n[ERROR] El RUT ingresado no cumple con el algoritmo Módulo 11.")
            print("Registro cancelado. Debe ingresar un RUT válido para continuar.")
            return

        if EstudianteDAO.insertar(estudiante):
            print(f"\n[ÉXITO] Estudiante {estudiante.obtener_nombre_completo()} registrado correctamente en SQLite.")
        else:
            print("\n[ERROR] No se pudo guardar el estudiante (posible RUT duplicado o dato inválido).")

    except ValueError as ve:
        print(f"\n[ERROR DE VALIDACIÓN POO]: {ve}")


def listar_estudiantes() -> None:
    """Muestra todos los estudiantes con su estado de deuda."""
    print("\n--- LISTADO DE ESTUDIANTES REGISTRADOS ---")
    estudiantes = EstudianteDAO.listar_todos()
    if not estudiantes:
        print("No hay estudiantes registrados en el sistema.")
        return

    for idx, e in enumerate(estudiantes, start=1):
        estado_deuda = "CON DEUDA (Bloqueado)" if e.tiene_deuda_pendiente else "AL DÍA (Habilitado)"
        print(f"{idx}. {e.obtener_nombre_completo()} | RUT: {e.rut} | Estado: {estado_deuda} | Email: {e.email}")


def consultar_estudiante_por_rut() -> None:
    """Busca y muestra la ficha de un estudiante."""
    rut = input("\nIngrese RUT del estudiante a consultar: ").strip()
    estudiante = EstudianteDAO.obtener_por_rut(rut)
    if estudiante:
        print("\n" + "-" * 50)
        print(f"FICHA DEL ESTUDIANTE: {estudiante.obtener_nombre_completo()}")
        print(f"  • RUT:            {estudiante.rut} (Válido M11: {estudiante.validar_rut()})")
        print(f"  • Email:          {estudiante.email}")
        print(f"  • Dirección:      {estudiante.direccion}")
        print(f"  • Estado Deuda:   {'CON DEUDA PENDIENTE' if estudiante.tiene_deuda_pendiente else 'AL DÍA'}")
        print(f"  • Apto Matrícula: {'SÍ' if estudiante.validar_deuda() else 'NO (Morosidad activa)'}")
        print("-" * 50)
    else:
        print(f"\nNo se encontró ningún estudiante con el RUT {rut}.")


def eliminar_estudiante(usuario: Trabajador) -> None:
    """Elimina un estudiante solo después de verificarlo y confirmar la acción."""
    if not isinstance(usuario, Administrativo):
        print("[PERMISO DENEGADO] Solo el perfil administrativo puede eliminar estudiantes.")
        return
    rut = input("\nIngrese el RUT del estudiante que desea eliminar: ").strip()
    estudiante = EstudianteDAO.obtener_por_rut(rut)
    if not estudiante:
        print(f"No se encontró ningún estudiante con el RUT {rut}.")
        return

    confirmacion = input(
        f"Confirma eliminar a {estudiante.obtener_nombre_completo()}? (s/n): "
    ).strip().lower()
    if confirmacion not in ["s", "si", "sí"]:
        print("Eliminación cancelada.")
        return

    if EstudianteDAO.eliminar(rut):
        print(f"Estudiante {estudiante.obtener_nombre_completo()} eliminado correctamente.")
    else:
        print("No se pudo eliminar. Verifique si el estudiante tiene matrículas asociadas.")


def modificar_deuda_estudiante(usuario: Trabajador) -> None:
    """Permite cambiar el estado de morosidad de un alumno."""
    if not isinstance(usuario, Administrativo):
        print("[PERMISO DENEGADO] Solo el perfil administrativo puede modificar deudas.")
        return
    rut = input("\nIngrese RUT del estudiante para modificar su deuda: ").strip()
    est = EstudianteDAO.obtener_por_rut(rut)
    if not est:
        print(f"Estudiante con RUT {rut} no encontrado.")
        return

    print(f"Estado actual: {'CON DEUDA' if est.tiene_deuda_pendiente else 'AL DÍA'}")
    opcion = input("Nuevo estado: [1] Marcar AL DÍA | [2] Marcar CON DEUDA: ").strip()
    nuevo_estado = opcion == "2"

    if EstudianteDAO.actualizar_estado_deuda(rut, nuevo_estado):
        print(f"\n[ÉXITO] Estado de deuda actualizado para {est.obtener_nombre_completo()}.")
    else:
        print("\n[ERROR] No se pudo actualizar el estado.")


def consultar_uf_y_calcular_arancel() -> None:
    """Consulta la API de la UF en vivo y cotiza un arancel."""
    print("\n--- COTIZADOR DE ARANCEL CON VALOR UF EN VIVO ---")
    print("Consultando API de mindicador.cl mediante requests...")

    indicador = IndicadorUF()
    valor_uf = indicador.valor_diario
    if indicador.obtenido_desde_api:
        print(f"[OK] Valor diario de la UF obtenido: ${valor_uf:,.2f} CLP")
    else:
        print(f"[AVISO] No se pudo consultar la API. Se usará el valor de respaldo: ${valor_uf:,.2f} CLP.")

    try:
        arancel_uf_input = input("Ingrese el arancel a pactar en UF (ej: 4.5): ").strip()
        cantidad_uf = float(arancel_uf_input.replace(",", "."))
        arancel = Arancel(cantidad_uf)
        total_pesos = arancel.calcular_monto_pesos(indicador)

        print("-" * 50)
        print(f"Cálculo del Contrato:")
        print(f"  • Arancel base:       {arancel.cantidad_uf:.2f} UF")
        print(f"  • Valor UF aplicado:  ${valor_uf:,.2f} CLP")
        print(f"  • Total en pesos:     ${total_pesos:,.0f} CLP")
        print("-" * 50)
    except ValueError as ve:
        print(f"[ERROR]: {ve}")


def registrar_matricula_estudiante(usuario: Trabajador) -> None:
    """
    Registra una matrícula formal verificando la condición crítica:
    No mantener deudas pendientes y respetar cupos de electivos.
    """
    if not isinstance(usuario, Administrativo):
        print("[PERMISO DENEGADO] Solo el perfil administrativo puede matricular estudiantes.")
        return
    print("\n--- GESTIÓN Y FORMALIZACIÓN DE MATRÍCULA ---")
    rut_ingresado = input("Ingrese el RUT del estudiante a matricular: ").strip()
    rut = _rut_canonico(rut_ingresado)
    if not rut:
        print("[ERROR] RUT inválido. Verifique el formato y dígito verificador.")
        return
    estudiante = EstudianteDAO.obtener_por_rut(rut)

    if not estudiante:
        print(f"[ERROR] El estudiante con RUT {rut} no se encuentra registrado en el sistema.")
        return

    print(f"Estudiante seleccionado: {estudiante.obtener_nombre_completo()}")

    # Validación crítica de la rúbrica. El control principal se realiza en MatriculaDAO,
    # pero aquí se deja un mensaje de usuario claro antes de continuar con la inscripción.
    if estudiante.tiene_deuda_pendiente:
        print("\n" + "!" * 60)
        print(" [MATRÍCULA RECHAZADA - BLOQUEO ADMINISTRATIVO]")
        print(f" El estudiante {estudiante.obtener_nombre_completo()} presenta DEUDA PENDIENTE.")
        print(" De acuerdo a las políticas institucionales, no es posible autorizar")
        print(" la matrícula hasta regularizar la situación financiera en cobranzas.")
        print("!" * 60)
        return

    print("[OK] Verificación financiera aprobada: Estudiante sin deudas pendientes.")

    try:
        id_matricula = int(input("Ingrese N° de Folio / ID de Matrícula (ej: 1001): ").strip())
        semestre = input("Semestre académico (ej: 2026-1): ").strip().upper()
        arancel_uf = float(input("Arancel acordado en UF (ej: 4.5): ").strip().replace(",", "."))

        # Crear instancia de Matrícula
        fecha_actual = date.today().strftime("%Y-%m-%d")
        matricula = Matricula(
            id_matricula=id_matricula,
            fecha=fecha_actual,
            arancel_uf=arancel_uf,
            semestre=semestre,
            estudiante=estudiante
        )

        # Selección de asignaturas y electivos
        asignaturas_disponibles = AsignaturaDAO.listar_todas()
        asignaturas_seleccionadas = []

        if asignaturas_disponibles:
            print("\nAsignaturas disponibles para inscripción:")
            for a in asignaturas_disponibles:
                info_extra = f" (Cupos: {a.cupo_disponible}/{a.cupo_maximo})" if isinstance(a, Electivo) else ""
                print(f"  [{a.nombre}]{info_extra}")

            print("\nSeleccione asignaturas escribiendo su nombre exacto (o Enter para finalizar):")
            while True:
                nombre_asig = input("Nombre de asignatura a inscribir (Enter para terminar): ").strip()
                if not nombre_asig:
                    break

                asig_obj = AsignaturaDAO.obtener_por_nombre(nombre_asig)
                if not asig_obj:
                    print("Asignatura no encontrada.")
                    continue

                if isinstance(asig_obj, Electivo) and not asig_obj.verificar_cupo():
                    print(f"[RECHAZADA] Cupo agotado para el electivo '{asig_obj.nombre}'.")
                    continue

                # Obtener el ID para la relación en base de datos
                with ConexionBD.obtener_conexion() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT id_asignatura FROM asignatura WHERE UPPER(nombre) = ?;", (nombre_asig.upper(),))
                    fila = cur.fetchone()
                    id_asig = fila["id_asignatura"] if fila else 1

                asignaturas_seleccionadas.append((id_asig, asig_obj))
                print(f"  -> Asignatura '{asig_obj.nombre}' agregada a la matrícula.")

        try:
            if MatriculaDAO.insertar(matricula, asignaturas_seleccionadas):
                print(f"\n[CONTRATO EMITIDO] Matrícula N°{matricula.id_matricula} formalizada exitosamente.")
                indicador_uf = IndicadorUF()
                uf_actual = indicador_uf.valor_diario
                arancel_calc = Arancel(matricula.arancel_uf)
                total_pesos = arancel_calc.calcular_monto_pesos(indicador_uf)
                if not indicador_uf.obtenido_desde_api:
                    print("[AVISO] Se calculó el arancel con el valor UF de respaldo; confirme el monto antes de cobrar.")
                print(f"  • Estudiante: {estudiante.obtener_nombre_completo()}")
                print(f"  • Arancel:    {matricula.arancel_uf:.2f} UF (~ ${total_pesos:,.0f} CLP)")
                print(f"  • Materias:   {len(asignaturas_seleccionadas)} inscritas.")
            else:
                print("[ERROR] No se pudo registrar la matrícula en la base de datos.")
        except DeudaPendienteError as error:
            print(f"\n[MATRÍCULA RECHAZADA] {error}")
        except CupoAgotadoError as error:
            print(f"\n[ELECTIVO SIN CUPOS] {error}")

    except ValueError as ve:
        print(f"[ERROR]: {ve}")


def listar_matriculas() -> None:
    """Lista todas las matrículas registradas."""
    print("\n--- MATRÍCULAS REGISTRADAS EN EL SISTEMA ---")
    matriculas = MatriculaDAO.listar_todas()
    if not matriculas:
        print("No hay matrículas registradas.")
        return

    for m in matriculas:
        print("-" * 55)
        print(m)
        if m.detalles:
            print("  Asignaturas inscritas:")
            for d in m.detalles:
                print(f"    • {d.asignatura.nombre} [{d.estado}]")


def gestionar_asignaturas() -> None:
    """Muestra catálogo de asignaturas y permite agregar nuevas."""
    print("\n--- CATÁLOGO DE ASIGNATURAS Y ELECTIVOS ---")
    asignaturas = AsignaturaDAO.listar_todas()
    for a in asignaturas:
        print(f"  • {a}")

    agregar = input("\n¿Desea registrar una nueva materia? (s/n): ").strip().lower()
    if agregar in ["s", "si", "sí"]:
        nombre = input("Nombre de la materia: ").strip()
        tipo = input("¿Es materia Regular o Electivo con cupos? (r/e): ").strip().lower()
        if tipo in ["e", "electivo"]:
            try:
                cupo = int(input("Cupo máximo de estudiantes: ").strip())
                nuevo_elec = Electivo(nombre=nombre, cupo_maximo=cupo)
                AsignaturaDAO.insertar(nuevo_elec)
                print(f"[OK] Electivo '{nombre}' registrado con {cupo} cupos.")
            except ValueError as ve:
                print(f"[ERROR]: {ve}")
        else:
            nueva_asig = Asignatura(nombre=nombre)
            AsignaturaDAO.insertar(nueva_asig)
            print(f"[OK] Asignatura regular '{nombre}' registrada.")


def asignar_asignatura_a_profesor(usuario: Trabajador) -> None:
    if not isinstance(usuario, Administrativo):
        print("[PERMISO DENEGADO] Solo el perfil administrativo puede asignar materias.")
        return
    id_profesor = input("ID del profesor: ").strip().upper()
    profesor = TrabajadorDAO.obtener_por_id(id_profesor)
    if not isinstance(profesor, Profesor):
        print("[ERROR] No se encontró un profesor con ese ID.")
        return

    nombre_asignatura = input("Nombre exacto de la asignatura: ").strip()
    id_asignatura = AsignaturaDAO.obtener_id_por_nombre(nombre_asignatura)
    if id_asignatura is None:
        print("[ERROR] No se encontró esa asignatura.")
        return

    if ProfesorAsignaturaDAO.asignar(id_profesor, id_asignatura):
        print(f"[OK] {nombre_asignatura} asignada a {profesor.obtener_nombre_completo()}.")
    else:
        print("La asignatura ya estaba asignada o no se pudo guardar la relación.")


def gestionar_cobros_mensuales(usuario: Trabajador) -> None:
    if not isinstance(usuario, Administrativo):
        print("[PERMISO DENEGADO] Solo el perfil administrativo puede gestionar cobros.")
        return

    while True:
        print("\n--- COBROS MENSUALES ---")
        print("[1] Emitir cobro mensual en UF")
        print("[2] Registrar pago o abono")
        print("[3] Consultar historial y saldo")
        print("[0] Volver")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            return
        if opcion == "1":
            rut = _rut_canonico(input("RUT del estudiante: ").strip())
            if not rut:
                print("[ERROR] RUT inválido. Verifique el formato y dígito verificador.")
                continue
            if not EstudianteDAO.obtener_por_rut(rut):
                print("[ERROR] No existe un estudiante registrado con ese RUT.")
                continue
            periodo = input("Período del cobro (AAAA-MM): ").strip()
            try:
                arancel_uf = float(input("Arancel mensual en UF: ").strip().replace(",", "."))
                indicador = IndicadorUF()
                if not indicador.obtenido_desde_api:
                    print(f"[AVISO] UF de respaldo: ${indicador.valor_diario:,.2f} CLP.")
                    confirmar = input("¿Emitir el cobro con este valor aproximado? (s/n): ").strip().lower()
                    if confirmar not in ["s", "si", "sí"]:
                        continue
                id_cobro = CobroMensualDAO.emitir(rut, periodo, arancel_uf, indicador.valor_diario)
                if id_cobro:
                    total = round(arancel_uf * indicador.valor_diario)
                    print(f"[OK] Cobro N°{id_cobro} emitido por ${total:,.0f} CLP. Estado: Pendiente.")
                else:
                    print("[ERROR] No se pudo emitir; puede existir ya un cobro para ese mes.")
            except ValueError as error:
                print(f"[ERROR] {error}")
        elif opcion == "2":
            try:
                id_cobro = int(input("Número de cobro: ").strip())
                monto = int(input("Monto pagado en pesos (ej: 35.000): ").strip().replace(".", ""))
                observacion = input("Observación o referencia (opcional): ").strip()
                if CobroMensualDAO.registrar_pago(id_cobro, monto, observacion):
                    print("[OK] Pago registrado. Consulte el historial para ver el saldo actualizado.")
                else:
                    print("[ERROR] Pago rechazado; revise el cobro, el saldo y el monto ingresado.")
            except ValueError:
                print("[ERROR] Ingrese un número de cobro y un monto entero válidos.")
        elif opcion == "3":
            rut = _rut_canonico(input("RUT del estudiante: ").strip())
            if not rut:
                print("[ERROR] RUT inválido. Verifique el formato y dígito verificador.")
                continue
            cobros = CobroMensualDAO.listar_por_estudiante(rut)
            if not cobros:
                print("No hay cobros registrados para ese estudiante.")
                continue
            for cobro in cobros:
                print(
                    f"Cobro {cobro['id_cobro']} | {cobro['periodo']} | "
                    f"Total ${cobro['total_pesos']:,.0f} | Pagado ${cobro['pagado']:,.0f} | "
                    f"Saldo ${cobro['saldo']:,.0f} | {cobro['estado']}"
                )
        else:
            print("Opción inválida.")


def listar_notas_de_asignaturas_profesor(usuario: Trabajador) -> None:
    """Lista las calificaciones registradas por el profesor en sus asignaturas."""
    print("\n--- MIS ASIGNATURAS Y CALIFICACIONES REGISTRADAS ---")
    if not isinstance(usuario, Profesor):
        print("[PERMISO DENEGADO] Solo un profesor puede listar calificaciones.")
        return

    print(f"Profesor activo: {usuario.obtener_nombre_completo()} ({usuario.especialidad})")
    with ConexionBD.obtener_conexion() as conn:
        asignaturas = conn.execute(
            """
            SELECT a.id_asignatura, a.nombre
            FROM profesor_asignatura pa
            JOIN asignatura a ON a.id_asignatura = pa.id_asignatura
            WHERE pa.id_trabajador = ?
            ORDER BY a.nombre ASC;
            """,
            (usuario.id_trabajador,),
        ).fetchall()

        if not asignaturas:
            print("No tienes asignaturas asignadas para calificar.")
            return

        hay_calificaciones = False
        for asignatura in asignaturas:
            filas = conn.execute(
                """
                SELECT e.rut_estudiante, e.periodo_academico, e.nota, e.observacion,
                       est.primer_nombre, est.segundo_nombre, est.primer_apellido, est.segundo_apellido
                FROM evaluacion_registrada e
                LEFT JOIN estudiante est ON est.rut = e.rut_estudiante
                WHERE e.id_profesor = ? AND e.id_asignatura = ?
                ORDER BY e.periodo_academico DESC, est.primer_apellido ASC, est.primer_nombre ASC;
                """,
                (usuario.id_trabajador, asignatura["id_asignatura"]),
            ).fetchall()

            if not filas:
                continue

            hay_calificaciones = True
            print(f"\nAsignatura: {asignatura['nombre']}")
            print(f"{'RUT':<12} {'ESTUDIANTE':<28} {'PERIODO':<10} {'NOTA':>6} {'OBSERVACIÓN'}")
            for fila in filas:
                nombre = " ".join(
                    parte for parte in (
                        fila["primer_nombre"],
                        fila["segundo_nombre"],
                        fila["primer_apellido"],
                        fila["segundo_apellido"],
                    ) if parte and parte.strip()
                )
                observacion = fila["observacion"].strip() if fila["observacion"] else "-"
                print(
                    f"{fila['rut_estudiante']:<12} {nombre:<28} "
                    f"{fila['periodo_academico']:<10} {fila['nota']:>6.1f} {observacion}"
                )

        if not hay_calificaciones:
            print("Todavía no hay calificaciones registradas en tus asignaturas.")


def registrar_evaluacion_y_nota_docente(usuario: Trabajador) -> None:
    """Permite al profesor registrar calificaciones y calcular nota final."""
    print("\n--- MÓDULO DOCENTE: INGRESO DE NOTAS Y EVALUACIONES ---")
    if not isinstance(usuario, Profesor):
        print("[PERMISO DENEGADO] Solo un profesor puede registrar evaluaciones.")
        return
    print(f"Profesor activo: {usuario.obtener_nombre_completo()} ({usuario.especialidad})")

    try:
        rut = _rut_canonico(input("RUT del estudiante: ").strip())
        if not rut:
            print("[ERROR] RUT inválido. Verifique el formato y dígito verificador.")
            return
        estudiante = EstudianteDAO.obtener_por_rut(rut)
        if not estudiante:
            print("[ERROR] No existe un estudiante registrado con ese RUT.")
            return

        nombre_materia = input("Asignatura a calificar: ").strip()
        id_asignatura = AsignaturaDAO.obtener_id_por_nombre(nombre_materia)
        asignatura = AsignaturaDAO.obtener_por_nombre(nombre_materia)
        if id_asignatura is None or asignatura is None:
            print("[ERROR] La asignatura no está registrada.")
            return
        if not ProfesorAsignaturaDAO.tiene_asignacion(usuario.id_trabajador, id_asignatura):
            print("[PERMISO DENEGADO] No tiene asignada esa asignatura.")
            return

        print("\nSeleccione el tipo de evaluación a registrar:")
        print("  [1] Prueba escrita (Puntaje)")
        print("  [2] Trabajo de investigación (Rúbrica)")
        print("  [3] Presentación oral (Tiempo de disertación)")
        tipo_ev = input("Opción: ").strip()

        periodo_academico = input("Semestre académico (AAAA-1 o AAAA-2): ").strip()
        if not re.fullmatch(r"\d{4}-[12]", periodo_academico):
            print("[ERROR] El semestre debe tener formato AAAA-1 o AAAA-2.")
            return

        fecha_hoy = date.today().strftime("%Y-%m-%d")
        id_ev = f"EV-{date.today().strftime('%m%d')}"
        ponderacion = float(input("Ponderación de la evaluación (ej: 40 para 40%): ").strip())

        if tipo_ev == "1":
            puntaje = float(input("Puntaje obtenido por el estudiante (ej: 85): ").strip())
            max_puntaje = float(input("Puntaje máximo de la prueba (ej: 100): ").strip())
            ev = Prueba(id_evaluacion=id_ev, fecha=fecha_hoy, ponderacion=ponderacion, puntaje=puntaje, puntaje_maximo=max_puntaje)
            tipo_nombre = "Prueba"
        elif tipo_ev == "2":
            print("Niveles de rúbrica: SOBRESALIENTE (7.0) | MUY BUENO (6.0) | BUENO (5.0) | SUFICIENTE (4.0)")
            rubrica = input("Nivel de logro en rúbrica: ").strip()
            ev = Trabajo(id_evaluacion=id_ev, fecha=fecha_hoy, ponderacion=ponderacion, rubrica=rubrica)
            tipo_nombre = "Trabajo"
        elif tipo_ev == "3":
            tiempo = input("Duración de la presentación (ej: '14 min'): ").strip()
            ev = PresentacionOral(id_evaluacion=id_ev, fecha=fecha_hoy, ponderacion=ponderacion, tiempo_presentacion=tiempo)
            tipo_nombre = "Presentación oral"
        else:
            print("Opción inválida.")
            return

        asignatura.agregar_evaluacion(ev)
        nota_obtenida = ev.calcular_nota()
        print(f"\n[CALIFICACIÓN GENERADA]: Nota calculada: {nota_obtenida:.1f}")
        aporte_ponderado = nota_obtenida * ponderacion / 100
        print(f"[APORTE PONDERADO]: {aporte_ponderado:.2f} puntos para la nota final ({ponderacion:.1f}%).")

        obs = input("Ingrese observación pedagógica (opcional): ").strip()
        calif = Calificacion(nota=nota_obtenida, observacion=obs)
        if not EvaluacionDAO.insertar(
            id_evaluacion=id_ev,
            rut_estudiante=estudiante.rut,
            id_asignatura=id_asignatura,
            id_profesor=usuario.id_trabajador,
            tipo_evaluacion=tipo_nombre,
            fecha=fecha_hoy,
            periodo_academico=periodo_academico,
            ponderacion=ponderacion,
            nota=nota_obtenida,
            observacion=obs,
        ):
            print("[ERROR] La evaluación no quedó guardada; no se actualizará el promedio.")
            return
        print(f"[REGISTRO GUARDADO]: {calif} | Estudiante: {estudiante.obtener_nombre_completo()}")
        evaluaciones = EvaluacionDAO.listar_por_estudiante_asignatura(
            estudiante.rut, id_asignatura, periodo_academico
        )
        promedio = EvaluacionDAO.calcular_promedio_ponderado(
            estudiante.rut, id_asignatura, periodo_academico
        )
        print(
            f"[PROMEDIO ACUMULADO {periodo_academico}]: "
            f"{promedio:.1f} ({len(evaluaciones)} evaluaciones)"
        )

        usuario.ingresar_nota(nota_obtenida)
        if obs:
            usuario.ingresar_observacion(obs)

    except ValueError as ve:
        print(f"[ERROR]: {ve}")


def ejecutar_demostracion_completa() -> None:
    """
    Ejecuta una demostración automática integral que prueba en cadena:
    Modelos POO, Validación de RUT Módulo 11, API de la UF, DAO SQLite y Reglas de Negocio.
    """
    print("\n" + "=" * 60)
    print("      DEMOSTRACIÓN INTEGRAL AUTOMÁTICA DEL SISTEMA")
    print("=" * 60)

    # 1. API UF
    print("\n[PASO 1] Consultando API en vivo de la Unidad de Fomento (UF):")
    ind_uf = IndicadorUF()
    uf_valor = ind_uf.valor_diario
    if ind_uf.obtenido_desde_api:
        print(f"  -> Valor UF obtenido en vivo: ${uf_valor:,.2f} CLP")
    else:
        print(f"  -> [AVISO] API no disponible; se usa el valor de respaldo ${uf_valor:,.2f} CLP.")

    # 2. Creación y persistencia de estudiantes
    print("\n[PASO 2] Creando estudiantes con validación de RUT Módulo 11:")
    e_al_dia = Estudiante(
        rut="11.111.111-1",
        primer_nombre="Viviana",
        segundo_nombre="Andrea",
        primer_apellido="Nuñez",
        segundo_apellido="Vera",
        email="viviana.nunez@alumnos.inacap.cl",
        direccion="Santiago, Chile",
        tiene_deuda_pendiente=False
    )
    e_moroso = Estudiante(
        rut="22.222.222-2",
        primer_nombre="Ignacio",
        segundo_nombre="Andres",
        primer_apellido="Silva",
        segundo_apellido="Rojas",
        email="ignacio.silva@colegio.cl",
        direccion="Puente Alto, Chile",
        tiene_deuda_pendiente=True
    )
    print(f"  -> Alumno 1: {e_al_dia.obtener_nombre_completo()} (RUT Válido M11: {e_al_dia.validar_rut()})")
    print(f"  -> Alumno 2: {e_moroso.obtener_nombre_completo()} (Deuda: {e_moroso.tiene_deuda_pendiente})")
    if not EstudianteDAO.obtener_por_rut(e_al_dia.rut):
        EstudianteDAO.insertar(e_al_dia)
    else:
        EstudianteDAO.actualizar_estado_deuda(e_al_dia.rut, False)

    if not EstudianteDAO.obtener_por_rut(e_moroso.rut):
        EstudianteDAO.insertar(e_moroso)
    else:
        EstudianteDAO.actualizar_estado_deuda(e_moroso.rut, True)

    # 3. Prueba de Matrícula (Verificación de deuda)
    print("\n[PASO 3] Probando regla crítica de matrícula:")
    with ConexionBD.obtener_conexion() as conn:
        conn.execute("DELETE FROM matricula WHERE id_matricula IN (9901, 9902);")
        conn.commit()

    mat_moroso = Matricula(id_matricula=9901, fecha="2026-03-01", arancel_uf=4.0, semestre="2026-1", estudiante=e_moroso)
    print("  -> Intentando matricular estudiante moroso (debe ser bloqueado):")
    try:
        MatriculaDAO.insertar(mat_moroso)
    except DeudaPendienteError as error:
        print(f"    [BLOQUEADO] {error}")

    mat_valida = Matricula(id_matricula=9902, fecha="2026-03-01", arancel_uf=4.0, semestre="2026-1", estudiante=e_al_dia)
    print("  -> Intentando matricular estudiante al día:")
    asig_lenguaje = AsignaturaDAO.obtener_por_nombre("Lenguaje y Comunicación")
    elec_teatro = AsignaturaDAO.obtener_por_nombre("Taller de Teatro Escolar")

    # Restablece cupos para la demostración y busca los IDs dinámicos
    with ConexionBD.obtener_conexion() as conn:
        conn.execute("UPDATE asignatura SET cupo_disponible = cupo_maximo WHERE tipo = 'Electivo';")
        conn.commit()
        cur = conn.cursor()
        cur.execute("SELECT id_asignatura FROM asignatura WHERE nombre = ?;", (asig_lenguaje.nombre,))
        id_asig = cur.fetchone()["id_asignatura"]
        cur.execute("SELECT id_asignatura FROM asignatura WHERE nombre = ?;", (elec_teatro.nombre,))
        id_elec = cur.fetchone()["id_asignatura"]

    elec_teatro._Electivo__cupo_disponible = elec_teatro.cupo_maximo
    try:
        MatriculaDAO.insertar(mat_valida, [(id_asig, asig_lenguaje), (id_elec, elec_teatro)])
    except (DeudaPendienteError, CupoAgotadoError) as error:
        print(f"    [BLOQUEADO] {error}")

    # 4. Cálculo de arancel en pesos
    arancel = Arancel(mat_valida.arancel_uf)
    total_clp = arancel.calcular_monto_pesos(ind_uf)
    print(f"\n[PASO 4] Cálculo de arancel indexado a la UF:")
    print(f"  -> {mat_valida.arancel_uf} UF al valor diario (${uf_valor:,.2f}) = ${total_clp:,.0f} CLP")

    # 5. Evaluaciones académicas polimórficas
    print("\n[PASO 5] Polimorfismo de Evaluaciones:")
    pr = Prueba("EV-1", "2026-04-15", 40.0, 90.0, 100.0)
    tr = Trabajo("EV-2", "2026-05-20", 30.0, "SOBRESALIENTE")
    po = PresentacionOral("EV-3", "2026-06-10", 30.0, "15 min", 15)
    asig = Asignatura("Ciencias Naturales")
    asig.agregar_evaluacion(pr)
    asig.agregar_evaluacion(tr)
    asig.agregar_evaluacion(po)
    print(f"  -> Nota final ponderada calculada: {asig.calcular_nota_final():.1f}")

    print("\n" + "=" * 60)
    print("  ¡DEMOSTRACIÓN INTEGRAL FINALIZADA CON ÉXITO AL 100%!")
    print("=" * 60)


def obtener_opciones_por_rol(usuario: Trabajador) -> dict[str, str]:
    """Devuelve las opciones visibles para cada perfil y centraliza el control de permisos."""
    if isinstance(usuario, Administrativo):
        return {
            "1": "Registrar nuevo estudiante",
            "2": "Listar estudiantes",
            "3": "Consultar estudiante por RUT",
            "4": "Modificar deuda",
            "5": "Formalizar matrícula",
            "6": "Consultar matrículas",
            "7": "Cotizar arancel",
            "8": "Catálogo de asignaturas",
            "10": "Eliminar estudiante",
            "11": "Gestionar cobros mensuales",
            "12": "Asignar asignaturas a profesores",
            "0": "Cerrar sesión",
        }
    if isinstance(usuario, Profesor):
        return {
            "7": "Cotizar arancel",
            "8": "Catálogo de asignaturas",
            "9": "Módulo docente: evaluación y nota",
            "13": "Listar notas de mis asignaturas",
            "0": "Cerrar sesión",
        }
    return {
        "0": "Cerrar sesión",
        "7": "Cotizar arancel",
    }


def menu_principal() -> None:
    """Bucle principal de la interfaz por consola."""
    # Inicializa base de datos y datos de prueba
    ConexionBD.inicializar_base_datos()
    inicializar_datos_semilla()

    usuario_activo: Trabajador | None = None

    while True:
        if not usuario_activo:
            print("\n" + "=" * 55)
            print("        SISTEMA COLEGIO NUEVA ESPERANZA")
            print("      Programación Orientada a Objeto Seguro")
            print("=" * 55)
            print("  [1] Iniciar Sesión (Autenticación SHA-256)")
            print("  [2] Consultar Valor UF del Día (API requests)")
            print("  [3] Ejecutar Demostración Integral Completa")
            print("  [0] Salir")
            print("=" * 55)

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                usuario_activo = menu_autenticacion()
            elif opcion == "2":
                consultar_uf_y_calcular_arancel()
            elif opcion == "3":
                ejecutar_demostracion_completa()
            elif opcion == "0":
                print("\nGracias por utilizar el Sistema Colegio Nueva Esperanza. ¡Hasta luego!")
                sys.exit(0)
            else:
                print("Opción inválida, intente nuevamente.")

        else:
            opciones_permitidas = obtener_opciones_por_rol(usuario_activo)
            print("\n" + "=" * 55)
            print(f"  PANEL DE CONTROL: {usuario_activo.obtener_nombre_completo()}")
            print(f"  Rol: {usuario_activo.obtener_rol()} | ID: {usuario_activo.id_trabajador}")
            print("=" * 55)

            if isinstance(usuario_activo, Administrativo):
                print("--- GESTIÓN DE ESTUDIANTES (CRUD) ---")
                print("  [1] Registrar nuevo estudiante (Validación Módulo 11)")
                print("  [2] Listar todos los estudiantes y estado financiero")
                print("  [3] Consultar estudiante por RUT")
                print("  [4] Modificar estado de deuda (Cobranzas)")
                print("\n--- GESTIÓN DE MATRÍCULAS Y ARANCELES ---")
                print("  [5] Formalizar matrícula (Verifica deudas y cupos)")
                print("  [6] Consultar matrículas registradas")
                print("  [7] Cotizar arancel con valor UF en vivo (API)")
                print("\n--- GESTIÓN ACADÉMICA Y DOCENCIA ---")
                print("  [8] Catálogo de asignaturas y electivos (Cupos)")
                print("  [10] Eliminar estudiante")
                print("  [11] Gestionar cobros mensuales")
                print("  [12] Asignar asignaturas a profesores")
            elif isinstance(usuario_activo, Profesor):
                print("\n--- GESTIÓN ACADÉMICA Y DOCENCIA ---")
                print("  [7] Cotizar arancel con valor UF en vivo (API)")
                print("  [8] Catálogo de asignaturas y electivos (Cupos)")
                print("  [9] Módulo docente: Ingresar evaluación y nota")
                print("  [13] Listar notas de mis asignaturas")
            else:
                print("\n--- OPERACIONES GENERALES ---")
                print("  [7] Cotizar arancel con valor UF en vivo (API)")

            print("\n--- SESIÓN ---")
            print("  [0] Cerrar Sesión")
            print("=" * 55)

            opcion = input("Seleccione una opción: ").strip()
            if opcion not in opciones_permitidas:
                print("[PERMISO DENEGADO] Esta opción no está disponible para tu perfil.")
                continue

            if opcion == "1":
                registrar_nuevo_estudiante(usuario_activo)
            elif opcion == "2":
                listar_estudiantes()
            elif opcion == "3":
                consultar_estudiante_por_rut()
            elif opcion == "4":
                modificar_deuda_estudiante(usuario_activo)
            elif opcion == "5":
                registrar_matricula_estudiante(usuario_activo)
            elif opcion == "6":
                listar_matriculas()
            elif opcion == "7":
                consultar_uf_y_calcular_arancel()
            elif opcion == "8":
                gestionar_asignaturas()
            elif opcion == "9":
                registrar_evaluacion_y_nota_docente(usuario_activo)
            elif opcion == "10":
                eliminar_estudiante(usuario_activo)
            elif opcion == "11":
                gestionar_cobros_mensuales(usuario_activo)
            elif opcion == "12":
                asignar_asignatura_a_profesor(usuario_activo)
            elif opcion == "13":
                listar_notas_de_asignaturas_profesor(usuario_activo)
            elif opcion == "0":
                print(f"\nSesión de {usuario_activo.obtener_nombre_completo()} cerrada.")
                usuario_activo = None
            else:
                print("Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    menu_principal()

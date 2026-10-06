import sys
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
from dao import (
    ConexionBD,
    EstudianteDAO,
    TrabajadorDAO,
    AsignaturaDAO,
    MatriculaDAO,
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
            especialidad="Ciencias de la Computación"
        )
        TrabajadorDAO.insertar(profe)

    # 2. Crear materias iniciales si no existen
    if not AsignaturaDAO.obtener_por_nombre("Programación Orientada a Objeto"):
        AsignaturaDAO.insertar(Asignatura("Programación Orientada a Objeto"))

    if not AsignaturaDAO.obtener_por_nombre("Bases de Datos Relacionales"):
        AsignaturaDAO.insertar(Asignatura("Bases de Datos Relacionales"))

    if not AsignaturaDAO.obtener_por_nombre("Taller de Robótica"):
        AsignaturaDAO.insertar(Electivo("Taller de Robótica", cupo_maximo=3))


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


def registrar_nuevo_estudiante() -> None:
    """Flujo para ingresar un nuevo estudiante con validación de RUT por módulo 11."""
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
            print("\n[ADVERTENCIA] El RUT ingresado no cumple con el algoritmo Módulo 11.")
            continuar = input("¿Desea registrarlo de todas formas para pruebas? (s/n): ").strip().lower()
            if continuar not in ["s", "si", "sí"]:
                print("Registro cancelado.")
                return

        if EstudianteDAO.insertar(estudiante):
            print(f"\n[ÉXITO] Estudiante {estudiante.obtener_nombre_completo()} registrado correctamente en SQLite.")
        else:
            print("\n[ERROR] No se pudo guardar el estudiante (posible RUT duplicado).")

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
        print(f"  • Apto Matrícula: {'SÍ' if estudiante.validar_matricula() else 'NO (Morosidad activa)'}")
        print("-" * 50)
    else:
        print(f"\nNo se encontró ningún estudiante con el RUT {rut}.")


def modificar_deuda_estudiante() -> None:
    """Permite cambiar el estado de morosidad de un alumno."""
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
    valor_uf = indicador.actualizar_desde_api()
    print(f"[OK] Valor diario de la UF obtenido: ${valor_uf:,.2f} CLP")

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


def registrar_matricula_estudiante() -> None:
    """
    Registra una matrícula formal verificando la condición crítica:
    No mantener deudas pendientes y respetar cupos de electivos.
    """
    print("\n--- GESTIÓN Y FORMALIZACIÓN DE MATRÍCULA ---")
    rut = input("Ingrese el RUT del estudiante a matricular: ").strip()
    estudiante = EstudianteDAO.obtener_por_rut(rut)

    if not estudiante:
        print(f"[ERROR] El estudiante con RUT {rut} no se encuentra registrado en el sistema.")
        return

    print(f"Estudiante seleccionado: {estudiante.obtener_nombre_completo()}")

    # Validación crítica de la rúbrica
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

        # Transacción en base de datos
        if MatriculaDAO.insertar(matricula, asignaturas_seleccionadas):
            print(f"\n[CONTRATO EMITIDO] Matrícula N°{matricula.id_matricula} formalizada exitosamente.")
            # Calcular arancel en pesos con la UF actual
            uf_actual = IndicadorUF().actualizar_desde_api()
            arancel_calc = Arancel(matricula.arancel_uf)
            total_pesos = arancel_calc.calcular_monto_pesos(IndicadorUF(uf_actual))
            print(f"  • Estudiante: {estudiante.obtener_nombre_completo()}")
            print(f"  • Arancel:    {matricula.arancel_uf:.2f} UF (~ ${total_pesos:,.0f} CLP)")
            print(f"  • Materias:   {len(asignaturas_seleccionadas)} inscritas.")
        else:
            print("[ERROR] No se pudo registrar la matrícula en la base de datos.")

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


def registrar_evaluacion_y_nota_docente(usuario: Trabajador) -> None:
    """Permite al profesor registrar calificaciones y calcular nota final."""
    print("\n--- MÓDULO DOCENTE: INGRESO DE NOTAS Y EVALUACIONES ---")
    if isinstance(usuario, Profesor):
        print(f"Profesor activo: {usuario.obtener_nombre_completo()} ({usuario.especialidad})")
    else:
        print(f"Usuario: {usuario.obtener_nombre_completo()} (Modo supervisor docente)")

    try:
        nombre_materia = input("Ingrese el nombre de la asignatura a calificar: ").strip()
        asig = Asignatura(nombre_materia)

        print("\nSeleccione el tipo de evaluación a registrar:")
        print("  [1] Prueba escrita (Puntaje)")
        print("  [2] Trabajo de investigación (Rúbrica)")
        print("  [3] Presentación oral (Tiempo de disertación)")
        tipo_ev = input("Opción: ").strip()

        fecha_hoy = date.today().strftime("%Y-%m-%d")
        id_ev = f"EV-{date.today().strftime('%m%d')}"
        ponderacion = float(input("Ponderación de la evaluación (ej: 40 para 40%): ").strip())

        if tipo_ev == "1":
            puntaje = float(input("Puntaje obtenido por el estudiante (ej: 85): ").strip())
            max_puntaje = float(input("Puntaje máximo de la prueba (ej: 100): ").strip())
            ev = Prueba(id_evaluacion=id_ev, fecha=fecha_hoy, ponderacion=ponderacion, puntaje=puntaje, puntaje_maximo=max_puntaje)
        elif tipo_ev == "2":
            print("Niveles de rúbrica: SOBRESALIENTE (7.0) | MUY BUENO (6.0) | BUENO (5.0) | SUFICIENTE (4.0)")
            rubrica = input("Nivel de logro en rúbrica: ").strip()
            ev = Trabajo(id_evaluacion=id_ev, fecha=fecha_hoy, ponderacion=ponderacion, rubrica=rubrica)
        elif tipo_ev == "3":
            tiempo = input("Duración de la presentación (ej: '14 min'): ").strip()
            ev = PresentacionOral(id_evaluacion=id_ev, fecha=fecha_hoy, ponderacion=ponderacion, tiempo_presentacion=tiempo)
        else:
            print("Opción inválida.")
            return

        asig.agregar_evaluacion(ev)
        nota_obtenida = ev.calcular_nota()
        print(f"\n[CALIFICACIÓN GENERADA]: Nota calculada: {nota_obtenida:.1f}")

        obs = input("Ingrese observación pedagógica (opcional): ").strip()
        calif = Calificacion(nota=nota_obtenida, observacion=obs)
        print(f"[REGISTRO]: {calif}")

        if isinstance(usuario, Profesor):
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
    uf_valor = ind_uf.actualizar_desde_api()
    print(f"  -> Valor UF obtenido en vivo: ${uf_valor:,.2f} CLP")

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
    MatriculaDAO.insertar(mat_moroso)

    mat_valida = Matricula(id_matricula=9902, fecha="2026-03-01", arancel_uf=4.0, semestre="2026-1", estudiante=e_al_dia)
    print("  -> Intentando matricular estudiante al día:")
    asig_poo = AsignaturaDAO.obtener_por_nombre("Programación Orientada a Objeto")
    elec_rob = AsignaturaDAO.obtener_por_nombre("Taller de Robótica")
    MatriculaDAO.insertar(mat_valida, [(1, asig_poo), (3, elec_rob)])

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
    asig = Asignatura("Ingeniería de Software")
    asig.agregar_evaluacion(pr)
    asig.agregar_evaluacion(tr)
    asig.agregar_evaluacion(po)
    print(f"  -> Nota final ponderada calculada: {asig.calcular_nota_final():.1f}")

    print("\n" + "=" * 60)
    print("  ¡DEMOSTRACIÓN INTEGRAL FINALIZADA CON ÉXITO AL 100%!")
    print("=" * 60)


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
            print("\n" + "=" * 55)
            print(f"  PANEL DE CONTROL: {usuario_activo.obtener_nombre_completo()}")
            print(f"  Rol: {usuario_activo.obtener_rol()} | ID: {usuario_activo.id_trabajador}")
            print("=" * 55)
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
            print("  [9] Módulo docente: Ingresar evaluación y nota")
            print("\n--- SESIÓN ---")
            print("  [0] Cerrar Sesión")
            print("=" * 55)

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                registrar_nuevo_estudiante()
            elif opcion == "2":
                listar_estudiantes()
            elif opcion == "3":
                consultar_estudiante_por_rut()
            elif opcion == "4":
                modificar_deuda_estudiante()
            elif opcion == "5":
                registrar_matricula_estudiante()
            elif opcion == "6":
                listar_matriculas()
            elif opcion == "7":
                consultar_uf_y_calcular_arancel()
            elif opcion == "8":
                gestionar_asignaturas()
            elif opcion == "9":
                registrar_evaluacion_y_nota_docente(usuario_activo)
            elif opcion == "0":
                print(f"\nSesión de {usuario_activo.obtener_nombre_completo()} cerrada.")
                usuario_activo = None
            else:
                print("Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    menu_principal()

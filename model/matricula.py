try:
    from model.detalle_matricula import DetalleMatricula
except ModuleNotFoundError:
    from detalle_matricula import DetalleMatricula


class Matricula:
    """
    Clase principal de transacción administrativa que representa el contrato formal
    de matrícula de un estudiante en un año académico o semestre determinado.
    """

    def __init__(
        self,
        id_matricula: int,
        fecha: str,
        arancel_uf: float,
        semestre: str,
        estudiante=None
    ) -> None:
        """Constructor que inicializa la transacción de matrícula."""
        self.id_matricula = id_matricula
        self.fecha = fecha
        self.arancel_uf = arancel_uf
        self.semestre = semestre
        self.estudiante = estudiante
        self.__detalles: list[DetalleMatricula] = []

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def id_matricula(self) -> int:
        """Getter para el ID numérico de matrícula."""
        return self.__id_matricula

    @id_matricula.setter
    def id_matricula(self, valor: int) -> None:
        """Setter con validación de ID positivo."""
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("El ID de matrícula debe ser un entero positivo.")
        self.__id_matricula = valor

    @property
    def fecha(self) -> str:
        """Getter para la fecha del contrato de matrícula."""
        return self.__fecha

    @fecha.setter
    def fecha(self, valor: str) -> None:
        """Setter para la fecha."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("La fecha de matrícula debe ser un texto válido (ej: YYYY-MM-DD).")
        self.__fecha = valor.strip()

    @property
    def arancel_uf(self) -> float:
        """Getter para el arancel fijado en UF."""
        return self.__arancel_uf

    @arancel_uf.setter
    def arancel_uf(self, valor: float) -> None:
        """Setter con validación."""
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ValueError("El arancel en UF debe ser mayor a cero.")
        self.__arancel_uf = float(valor)

    @property
    def semestre(self) -> str:
        """Getter para el período o semestre escolar."""
        return self.__semestre

    @semestre.setter
    def semestre(self, valor: str) -> None:
        """Setter para el semestre."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El semestre no puede estar vacío (ej: '2026-1').")
        self.__semestre = valor.strip().upper()

    @property
    def detalles(self) -> list[DetalleMatricula]:
        """Getter para los detalles de asignaturas inscritas."""
        return list(self.__detalles)

    # ---------------------------------------------------------
    # Métodos específicos del diagrama UML
    # ---------------------------------------------------------

    def matricular_estudiante(self, estudiante=None) -> bool:
        """
        Método del UML: Formaliza la matrícula verificando que el estudiante
        no posea deudas pendientes (validar_deuda() == False) y que su RUT sea válido.
        """
        alumno = estudiante if estudiante is not None else self.estudiante

        if alumno is None:
            print("Error: No se ha asignado un estudiante para matricular.")
            return False

        # Verifica si el estudiante tiene deuda
        if hasattr(alumno, "validar_deuda") and not alumno.validar_deuda():
            print(f"Matrícula RECHAZADA para {alumno.obtener_nombre_completo()}: Registra deuda pendiente.")
            return False

        self.estudiante = alumno
        print(f"Matrícula N°{self.__id_matricula} APROBADA con éxito para el estudiante {alumno.obtener_nombre_completo()}.")
        return True

    def inscribir_asignatura(self, asignatura) -> bool:
        """Método complementario para agregar un detalle de asignatura a la matrícula."""
        detalle = DetalleMatricula(asignatura=asignatura)
        if detalle.agregar_asignatura(asignatura):
            self.__detalles.append(detalle)
            return True
        return False

    def __str__(self) -> str:
        """Representación en texto de la matrícula."""
        nombre_est = self.estudiante.obtener_nombre_completo() if self.estudiante else "Sin alumno asignado"
        return f"Matrícula N°{self.__id_matricula} | Semestre: {self.__semestre} | Alumno: {nombre_est} | Arancel: {self.__arancel_uf} UF"

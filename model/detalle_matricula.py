class DetalleMatricula:
    """
    Clase de detalle transaccional que vincula la matrícula con cada una de las
    asignaturas específicas inscritas por el alumno.
    """

    def __init__(self, asignatura, estado: str = "Inscrita") -> None:
        """Constructor que inicializa el detalle con la asignatura y su estado."""
        self.asignatura = asignatura
        self.estado = estado

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def estado(self) -> str:
        """Getter para el estado de la asignatura en la matrícula."""
        return self.__estado

    @estado.setter
    def estado(self, valor: str) -> None:
        """Setter con validación."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El estado del detalle de matrícula no puede estar vacío.")
        self.__estado = valor.strip().capitalize()

    # ---------------------------------------------------------
    # Métodos específicos del diagrama UML
    # ---------------------------------------------------------

    def agregar_asignatura(self, asignatura) -> bool:
        """
        Método del UML: Vincula una nueva asignatura al detalle si cumple las condiciones.
        Si la asignatura es un Electivo, reserva el cupo.
        """
        if asignatura is None:
            return False

        # Si es un electivo, valida y descuenta cupo
        if hasattr(asignatura, "reserva_cupo"):
            if not asignatura.reserva_cupo():
                return False

        self.asignatura = asignatura
        self.__estado = "Inscrita"
        return True

    def __str__(self) -> str:
        """Representación en texto del detalle."""
        nombre_asig = getattr(self.asignatura, "nombre", "Sin asignar")
        return f"Detalle Matrícula: Asignatura '{nombre_asig}' | Estado: {self.__estado}"

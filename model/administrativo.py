try:
    from model.trabajador import Trabajador
except ModuleNotFoundError:
    from trabajador import Trabajador


class Administrativo(Trabajador):
    """
    Subtipo de Trabajador orientado al rol de gestión y cobranza institucional (secretaría, inspectoría).
    Posee las atribuciones exclusivas para realizar matriculaciones y gestionar cobros.
    """

    def __init__(
        self,
        rut: str,
        primer_nombre: str,
        segundo_nombre: str,
        primer_apellido: str,
        segundo_apellido: str,
        email: str,
        direccion: str,
        id_trabajador: str,
        clave: str,
        cargo: str
    ) -> None:
        """Constructor de Administrativo. Invoca al constructor de Trabajador con super()."""
        super().__init__(
            rut=rut,
            primer_nombre=primer_nombre,
            segundo_nombre=segundo_nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            email=email,
            direccion=direccion,
            id_trabajador=id_trabajador,
            clave=clave
        )
        self.cargo = cargo

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def cargo(self) -> str:
        """Getter para el cargo administrativo."""
        return self.__cargo

    @cargo.setter
    def cargo(self, valor: str) -> None:
        """Setter para el cargo con validación de obligatoriedad."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El cargo no puede estar vacío y debe ser un texto válido.")
        self.__cargo = valor.strip().title()

    # ---------------------------------------------------------
    # Implementación de rol
    # ---------------------------------------------------------

    def obtener_rol(self) -> str:
        """Sobrescribe el rol con Administrativo."""
        return f"Administrativo ({self.__cargo})"

    # ---------------------------------------------------------
    # Métodos de negocio específicos del diagrama UML
    # ---------------------------------------------------------

    def matricular_estudiante(self, estudiante=None) -> bool:
        """
        Método del UML: Permite al administrativo registrar la matrícula de un estudiante,
        validando previamente que el estudiante no mantenga deudas pendientes.
        """
        if estudiante is not None and hasattr(estudiante, "validar_deuda"):
            if not estudiante.validar_deuda():
                print(f"[{self.obtener_nombre_completo()}] Matrícula RECHAZADA: El estudiante tiene deuda pendiente.")
                return False

        print(f"[{self.obtener_nombre_completo()}] Matrícula procesada y autorizada con éxito.")
        return True

    def cobrar_matricula(self, monto: float) -> bool:
        """
        Método del UML: Gestiona el cobro administrativo del arancel/matrícula.
        """
        if monto <= 0:
            print("El monto a cobrar debe ser mayor a cero.")
            return False
        print(f"[{self.obtener_nombre_completo()}] Cobro de ${monto:,.0f} registrado exitosamente.")
        return True

    def __str__(self) -> str:
        """Representación en texto del administrativo."""
        return f"Administrativo: {self.obtener_nombre_completo()} | Cargo: {self.__cargo} | ID: {self.id_trabajador}"

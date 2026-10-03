try:
    from model.persona import Persona
except ModuleNotFoundError:
    from persona import Persona


class Estudiante(Persona):
    """
    Clase que representa a un estudiante del colegio,
    heredando de la clase abstracta Persona según el diagrama UML.
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
        tiene_deuda_pendiente: bool = False
    ) -> None:
        """Constructor que inicializa los atributos heredados mediante super() y los propios."""
        super().__init__(
            rut=rut,
            primer_nombre=primer_nombre,
            segundo_nombre=segundo_nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            email=email,
            direccion=direccion
        )
        self.tiene_deuda_pendiente = tiene_deuda_pendiente

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def tiene_deuda_pendiente(self) -> bool:
        """Getter para el estado de deuda pendiente del estudiante."""
        return self.__tiene_deuda_pendiente

    @tiene_deuda_pendiente.setter
    def tiene_deuda_pendiente(self, valor: bool) -> None:
        """Setter para la deuda pendiente con validación de tipo booleano."""
        if not isinstance(valor, bool):
            raise ValueError("El estado de deuda pendiente debe ser un valor de tipo booleano (True/False).")
        self.__tiene_deuda_pendiente = valor

    # ---------------------------------------------------------
    # Implementación obligatoria del método abstracto de Persona
    # ---------------------------------------------------------

    def obtener_rol(self) -> str:
        """Implementación del método abstracto de la clase base Persona."""
        return "Estudiante"

    # ---------------------------------------------------------
    # Métodos específicos del diagrama UML
    # ---------------------------------------------------------

    def validar_deuda(self) -> bool:
        """
        Método del UML: Valida si el estudiante tiene deudas pendientes.
        Retorna False si tiene deuda (moroso) y True si está al día.
        """
        if self.__tiene_deuda_pendiente:
            return False
        return True

    def consultar_notas(self) -> None:
        """Método del UML: Permite consultar las notas del estudiante."""
        # Se conectará posteriormente con el modelo de calificaciones / base de datos
        print(f"Consultando notas para el estudiante {self.obtener_nombre_completo()}...")

    def __str__(self) -> str:
        """Representación en texto del estudiante."""
        estado = "Con Deuda Pendiente" if self.__tiene_deuda_pendiente else "Al Día (Sin Deuda)"
        return f"Estudiante: {self.obtener_nombre_completo()} | RUT: {self.rut} | Estado: {estado} | Email: {self.email}"

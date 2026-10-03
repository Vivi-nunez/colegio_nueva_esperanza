try:
    from model.trabajador import Trabajador
except ModuleNotFoundError:
    from trabajador import Trabajador


class Profesor(Trabajador):
    """
    Subtipo de Trabajador orientado al rol docente.
    Posee los métodos y permisos necesarios para registrar notas y observaciones
    académicas de los estudiantes en sus respectivas asignaturas.
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
        especialidad: str = "Docente General"
    ) -> None:
        """Constructor de Profesor. Invoca al constructor de Trabajador con super()."""
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
        self.especialidad = especialidad
        self.__observaciones_ingresadas: list[str] = []
        self.__notas_registradas: list[float] = []

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def especialidad(self) -> str:
        """Getter para la especialidad o área docente."""
        return self.__especialidad

    @especialidad.setter
    def especialidad(self, valor: str) -> None:
        """Setter para la especialidad."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("La especialidad no puede estar vacía.")
        self.__especialidad = valor.strip().title()

    # ---------------------------------------------------------
    # Implementación de rol
    # ---------------------------------------------------------

    def obtener_rol(self) -> str:
        """Sobrescribe el rol como Profesor."""
        return f"Profesor ({self.__especialidad})"

    # ---------------------------------------------------------
    # Métodos específicos del diagrama UML
    # ---------------------------------------------------------

    def ingresar_nota(self, nota: float) -> None:
        """
        Método del UML: Registra una calificación dentro de la escala escolar (1.0 a 7.0).
        """
        if not isinstance(nota, (int, float)):
            raise ValueError("La nota debe ser un valor numérico.")
        if nota < 1.0 or nota > 7.0:
            raise ValueError("La nota debe encontrarse entre 1.0 y 7.0.")

        self.__notas_registradas.append(float(nota))
        print(f"Profesor {self.obtener_nombre_completo()} registró nota: {nota:.1f}")

    def ingresar_observacion(self, texto: str) -> None:
        """
        Método del UML: Registra una anotación u observación pedagógica.
        """
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("La observación no puede estar vacía.")

        self.__observaciones_ingresadas.append(texto.strip())
        print(f"Profesor {self.obtener_nombre_completo()} registró observación: '{texto.strip()}'")

    def __str__(self) -> str:
        """Representación en texto del profesor."""
        return f"Profesor: {self.obtener_nombre_completo()} | Especialidad: {self.__especialidad} | ID: {self.id_trabajador}"

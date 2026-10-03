class Calificacion:
    """
    Clase que almacena el resultado numérico obtenido por un estudiante en una evaluación particular,
    junto a las observaciones u hoja de comentarios registrada por el docente.
    """

    def __init__(self, nota: float, observacion: str = "") -> None:
        """Constructor que inicializa y valida la nota y observación."""
        self.nota = nota
        self.observacion = observacion

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def nota(self) -> float:
        """Getter para la nota obtenida."""
        return self.__nota

    @nota.setter
    def nota(self, valor: float) -> None:
        """Setter para la nota con validación de escala chilena (1.0 a 7.0)."""
        if not isinstance(valor, (int, float)):
            raise ValueError("La calificación debe ser numérica.")
        if valor < 1.0 or valor > 7.0:
            raise ValueError("La nota debe estar en la escala de 1.0 a 7.0.")
        self.__nota = round(float(valor), 1)

    @property
    def observacion(self) -> str:
        """Getter para el comentario pedagógico."""
        return self.__observacion

    @observacion.setter
    def observacion(self, valor: str) -> None:
        """Setter para la observación."""
        if not isinstance(valor, str):
            raise ValueError("La observación debe ser un texto.")
        self.__observacion = valor.strip()

    # ---------------------------------------------------------
    # Métodos de negocio específicos del diagrama UML
    # ---------------------------------------------------------

    def validar_nota(self) -> bool:
        """
        Método del UML: Valida si la calificación se encuentra en el rango reglamentario.
        """
        return 1.0 <= self.__nota <= 7.0

    def es_aprobatoria(self) -> bool:
        """Retorna True si la nota es igual o superior a 4.0."""
        return self.__nota >= 4.0

    def __str__(self) -> str:
        """Representación en texto de la calificación."""
        obs = f" | Obs: {self.__observacion}" if self.__observacion else ""
        return f"Nota: {self.__nota:.1f}{obs}"

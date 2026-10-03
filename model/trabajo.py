try:
    from model.evaluacion import Evaluacion
except ModuleNotFoundError:
    from evaluacion import Evaluacion


class Trabajo(Evaluacion):
    """
    Subtipo de Evaluación orientado a investigaciones, proyectos o tareas prácticas,
    cuya calificación se determina mediante niveles de logro según una rúbrica específica.
    """

    NIVELES_RUBRICA: dict[str, float] = {
        "SOBRESALIENTE": 7.0,
        "MUY BUENO": 6.0,
        "BUENO": 5.0,
        "SUFICIENTE": 4.0,
        "INSUFICIENTE": 2.5,
        "DEFICIENTE": 1.0,
    }

    def __init__(
        self,
        id_evaluacion: str,
        fecha: str,
        ponderacion: float,
        rubrica: str
    ) -> None:
        """Constructor de Trabajo. Invoca al constructor de Evaluacion con super()."""
        super().__init__(id_evaluacion=id_evaluacion, fecha=fecha, ponderacion=ponderacion)
        self.rubrica = rubrica

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def rubrica(self) -> str:
        """Getter para el nivel o descripción de la rúbrica."""
        return self.__rubrica

    @rubrica.setter
    def rubrica(self, valor: str) -> None:
        """Setter con validación de obligatoriedad."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("La rúbrica no puede estar vacía.")
        self.__rubrica = valor.strip().upper()

    # ---------------------------------------------------------
    # Implementación del método abstracto de Evaluacion
    # ---------------------------------------------------------

    def calcular_nota(self) -> float:
        """
        Método del UML: Determina la nota a partir del nivel de logro establecido en la rúbrica.
        """
        for nivel, nota in self.NIVELES_RUBRICA.items():
            if nivel in self.__rubrica:
                return nota

        # Si no coincide exactamente con una clave, asigna nota aprobatoria base de 4.0
        return 4.0

    def __str__(self) -> str:
        """Representación en texto del trabajo."""
        return f"Trabajo [{self.id_evaluacion}] - Rúbrica: '{self.__rubrica}' -> Nota: {self.calcular_nota()}"

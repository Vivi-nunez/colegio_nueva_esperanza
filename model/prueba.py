try:
    from model.evaluacion import Evaluacion
except ModuleNotFoundError:
    from evaluacion import Evaluacion


class Prueba(Evaluacion):
    """
    Subtipo de Evaluación que representa exámenes escritos ordenados por puntaje
    obtenido sobre una escala de notas tradicional.
    """

    def __init__(
        self,
        id_evaluacion: str,
        fecha: str,
        ponderacion: float,
        puntaje: float,
        puntaje_maximo: float = 100.0
    ) -> None:
        """Constructor de Prueba. Invoca al constructor de Evaluacion con super()."""
        super().__init__(id_evaluacion=id_evaluacion, fecha=fecha, ponderacion=ponderacion)
        self.puntaje_maximo = puntaje_maximo
        self.puntaje = puntaje

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def puntaje(self) -> float:
        """Getter para el puntaje obtenido."""
        return self.__puntaje

    @puntaje.setter
    def puntaje(self, valor: float) -> None:
        """Setter con validación de rango no negativo."""
        if not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("El puntaje no puede ser negativo.")
        self.__puntaje = float(valor)

    @property
    def puntaje_maximo(self) -> float:
        """Getter para el puntaje total de la prueba."""
        return self.__puntaje_maximo

    @puntaje_maximo.setter
    def puntaje_maximo(self, valor: float) -> None:
        """Setter con validación de puntaje positivo."""
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ValueError("El puntaje máximo debe ser mayor a cero.")
        self.__puntaje_maximo = float(valor)

    # ---------------------------------------------------------
    # Implementación del método abstracto de Evaluacion
    # ---------------------------------------------------------

    def calcular_nota(self) -> float:
        """
        Método del UML: Calcula la nota escolar chilena (1.0 a 7.0)
        en base al porcentaje de logro del puntaje obtenido sobre el máximo.
        """
        if self.__puntaje_maximo <= 0:
            return 1.0

        porcentaje = min(self.__puntaje / self.__puntaje_maximo, 1.0)
        # Escala lineal estándar 1.0 a 7.0
        nota = 1.0 + (porcentaje * 6.0)
        return round(nota, 1)

    def __str__(self) -> str:
        """Representación en texto de la prueba."""
        return f"Prueba [{self.id_evaluacion}]: {self.__puntaje}/{self.__puntaje_maximo} pts -> Nota: {self.calcular_nota()}"

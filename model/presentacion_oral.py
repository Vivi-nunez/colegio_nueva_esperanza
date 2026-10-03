try:
    from model.evaluacion import Evaluacion
except ModuleNotFoundError:
    from evaluacion import Evaluacion


class PresentacionOral(Evaluacion):
    """
    Subtipo de Evaluación que mide disertaciones o exposiciones orales,
    calculando la nota en función del tiempo de presentación y el desempeño expuesto.
    """

    def __init__(
        self,
        id_evaluacion: str,
        fecha: str,
        ponderacion: float,
        tiempo_presentacion: str,
        tiempo_objetivo_minutos: int = 15
    ) -> None:
        """Constructor de PresentacionOral. Invoca al constructor de Evaluacion con super()."""
        super().__init__(id_evaluacion=id_evaluacion, fecha=fecha, ponderacion=ponderacion)
        self.tiempo_objetivo_minutos = tiempo_objetivo_minutos
        self.tiempo_presentacion = tiempo_presentacion

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def tiempo_presentacion(self) -> str:
        """Getter para el tiempo o duración registrada de la presentación."""
        return self.__tiempo_presentacion

    @tiempo_presentacion.setter
    def tiempo_presentacion(self, valor: str) -> None:
        """Setter para el tiempo de presentación."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El tiempo de presentación no puede estar vacío (ej: '15 min').")
        self.__tiempo_presentacion = valor.strip()

    @property
    def tiempo_objetivo_minutos(self) -> int:
        """Getter para el tiempo objetivo reglamentario."""
        return self.__tiempo_objetivo_minutos

    @tiempo_objetivo_minutos.setter
    def tiempo_objetivo_minutos(self, valor: int) -> None:
        """Setter para el tiempo objetivo."""
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("El tiempo objetivo debe ser un número entero positivo.")
        self.__tiempo_objetivo_minutos = valor

    # ---------------------------------------------------------
    # Implementación del método abstracto de Evaluacion
    # ---------------------------------------------------------

    def calcular_nota(self) -> float:
        """
        Método del UML: Evalúa el cumplimiento del tiempo establecido para la disertación.
        Si está dentro del rango óptimo (+/- 3 minutos), obtiene 7.0; de lo contrario se descuenta.
        """
        import re
        numeros = re.findall(r"\d+", self.__tiempo_presentacion)
        minutos_reales = int(numeros[0]) if numeros else self.__tiempo_objetivo_minutos

        diferencia = abs(minutos_reales - self.__tiempo_objetivo_minutos)
        if diferencia <= 2:
            return 7.0
        elif diferencia <= 5:
            return 5.5
        elif diferencia <= 8:
            return 4.0
        else:
            return 3.0

    def __str__(self) -> str:
        """Representación en texto de la presentación oral."""
        return f"Presentación Oral [{self.id_evaluacion}] - Duración: {self.__tiempo_presentacion} -> Nota: {self.calcular_nota()}"

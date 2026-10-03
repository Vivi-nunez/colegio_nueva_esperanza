from abc import ABC, abstractmethod


class Evaluacion(ABC):
    """
    Clase abstracta que define la estructura base para los instrumentos de medición académica.
    Almacena el identificador, la fecha y la ponderación (porcentaje) de la evaluación dentro del ramo.
    """

    def __init__(self, id_evaluacion: str, fecha: str, ponderacion: float) -> None:
        """Constructor base que inicializa los atributos comunes de una evaluación."""
        self.id_evaluacion = id_evaluacion
        self.fecha = fecha
        self.ponderacion = ponderacion

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def id_evaluacion(self) -> str:
        """Getter para el ID de evaluación."""
        return self.__id_evaluacion

    @id_evaluacion.setter
    def id_evaluacion(self, valor: str) -> None:
        """Setter con validación."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El ID de evaluación no puede estar vacío.")
        self.__id_evaluacion = valor.strip().upper()

    @property
    def fecha(self) -> str:
        """Getter para la fecha de la evaluación."""
        return self.__fecha

    @fecha.setter
    def fecha(self, valor: str) -> None:
        """Setter para la fecha."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("La fecha de evaluación debe ser un texto válido (ej: YYYY-MM-DD).")
        self.__fecha = valor.strip()

    @property
    def ponderacion(self) -> float:
        """Getter para la ponderación (en porcentaje 0 a 100 o decimal 0 a 1)."""
        return self.__ponderacion

    @ponderacion.setter
    def ponderacion(self, valor: float) -> None:
        """Setter con validación de porcentaje."""
        if not isinstance(valor, (int, float)) or valor <= 0 or valor > 100:
            raise ValueError("La ponderación debe ser un valor porcentual entre 1 y 100.")
        self.__ponderacion = float(valor)

    # ---------------------------------------------------------
    # Método abstracto específico del diagrama UML
    # ---------------------------------------------------------

    @abstractmethod
    def calcular_nota(self) -> float:
        """
        Método abstracto del UML: Cada subtipo de evaluación calcula la calificación
        según su propia escala y dinámica de medición (puntaje, rúbrica o tiempo).
        """
        pass

    def __str__(self) -> str:
        """Representación en texto de la evaluación."""
        return f"Evaluación [{self.__id_evaluacion}] - Ponderación: {self.__ponderacion}% - Fecha: {self.__fecha}"

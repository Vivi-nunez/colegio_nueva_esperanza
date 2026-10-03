try:
    from model.asignatura import Asignatura
except ModuleNotFoundError:
    from asignatura import Asignatura


class Electivo(Asignatura):
    """
    Subtipo especializado de Asignatura que representa cursos de libre elección.
    Mantiene el control de cupo máximo y disponible, bloqueando inscripciones al agotarse.
    """

    def __init__(self, nombre: str, cupo_maximo: int) -> None:
        """Constructor de Electivo. Invoca al constructor de Asignatura con super()."""
        super().__init__(nombre=nombre)
        self.cupo_maximo = cupo_maximo
        self.__cupo_disponible = cupo_maximo

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def cupo_maximo(self) -> int:
        """Getter para el cupo máximo autorizado."""
        return self.__cupo_maximo

    @cupo_maximo.setter
    def cupo_maximo(self, valor: int) -> None:
        """Setter con validación de entero positivo."""
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("El cupo máximo debe ser un número entero mayor a cero.")
        self.__cupo_maximo = valor

    @property
    def cupo_disponible(self) -> int:
        """Getter para los cupos que van quedando disponibles."""
        return self.__cupo_disponible

    # ---------------------------------------------------------
    # Métodos específicos del diagrama UML
    # ---------------------------------------------------------

    def verificar_cupo(self) -> bool:
        """
        Método del UML: Retorna True si existen cupos disponibles para inscripción, False si están agotados.
        """
        return self.__cupo_disponible > 0

    def reserva_cupo(self) -> bool:
        """
        Método del UML: Descuenta un cupo si hay disponibilidad. Retorna True si la reserva fue exitosa.
        """
        if self.verificar_cupo():
            self.__cupo_disponible -= 1
            print(f"Cupo reservado con éxito en electivo '{self.nombre}'. Quedan: {self.__cupo_disponible}")
            return True

        print(f"Inscripción rechazada: Cupos agotados para el electivo '{self.nombre}'.")
        return False

    def liberar_cupo(self) -> bool:
        """Método complementario para liberar un cupo en caso de anulación."""
        if self.__cupo_disponible < self.__cupo_maximo:
            self.__cupo_disponible += 1
            return True
        return False

    def __str__(self) -> str:
        """Representación en texto del electivo."""
        return f"Electivo: {self.nombre} | Cupos: {self.__cupo_disponible}/{self.__cupo_maximo}"

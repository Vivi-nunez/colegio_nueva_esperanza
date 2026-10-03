try:
    from model.indicador_uf import IndicadorUF
except ModuleNotFoundError:
    from indicador_uf import IndicadorUF


class Arancel:
    """
    Clase encargada de la lógica financiera y cobro del colegio.
    Convierte el arancel pactado en UF a pesos chilenos según el valor de la UF del día.
    """

    def __init__(self, cantidad_uf: float) -> None:
        """Constructor que inicializa el arancel en UF."""
        self.cantidad_uf = cantidad_uf

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def cantidad_uf(self) -> float:
        """Getter para la cantidad fijada en UF."""
        return self.__cantidad_uf

    @cantidad_uf.setter
    def cantidad_uf(self, valor: float) -> None:
        """Setter con validación de cantidad positiva."""
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ValueError("La cantidad de UF debe ser un número positivo.")
        self.__cantidad_uf = float(valor)

    # ---------------------------------------------------------
    # Métodos de negocio específicos del diagrama UML
    # ---------------------------------------------------------

    def calcular_monto_pesos(self, indicador: IndicadorUF) -> float:
        """
        Método del UML: Multiplica la cantidad de UF por el valor diario del indicador económico.
        """
        if not isinstance(indicador, IndicadorUF):
            raise TypeError("El indicador proporcionado debe ser una instancia de IndicadorUF.")

        monto_pesos = round(self.__cantidad_uf * indicador.valor_diario, 0)
        return float(monto_pesos)

    def __str__(self) -> str:
        """Representación en texto del arancel."""
        return f"Arancel: {self.__cantidad_uf:.2f} UF"

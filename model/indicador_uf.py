import requests


class IndicadorUF:
    """
    Clase que representa el indicador económico externo de la Unidad de Fomento (UF).
    Consume una API económica mediante 'requests' para obtener el valor diario actualizado.
    """

    def __init__(self, valor_diario: float = 0.0) -> None:
        """Constructor que inicializa el valor diario de la UF."""
        self.__valor_diario = 0.0
        if valor_diario > 0:
            self.valor_diario = valor_diario
        else:
            self.actualizar_desde_api()

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def valor_diario(self) -> float:
        """Getter para el valor diario de la UF en pesos chilenos."""
        return self.__valor_diario

    @valor_diario.setter
    def valor_diario(self, valor: float) -> None:
        """Setter con validación de valor positivo."""
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ValueError("El valor diario de la UF debe ser un número positivo.")
        self.__valor_diario = float(valor)

    # ---------------------------------------------------------
    # Métodos de negocio y consumo de API
    # ---------------------------------------------------------

    def actualizar_desde_api(self) -> float:
        """
        Consulta la API de mindicador.cl mediante requests para obtener la UF del día.
        En caso de fallo de conexión, asigna un valor referencial seguro.
        """
        url = "https://mindicador.cl/api/uf"
        try:
            respuesta = requests.get(url, timeout=5)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                # Extrae el primer valor de la serie histórica
                self.valor_diario = float(datos["serie"][0]["valor"])
                return self.__valor_diario
        except Exception:
            pass

        # Valor de respaldo seguro en caso de contingencia o sin internet
        if self.__valor_diario <= 0:
            self.valor_diario = 38500.0

        return self.__valor_diario

    def __str__(self) -> str:
        """Representación en texto del valor UF."""
        return f"Indicador UF Diario: ${self.__valor_diario:,.2f} CLP"

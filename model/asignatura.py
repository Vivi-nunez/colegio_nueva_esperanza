class Asignatura:
    """
    Representa las materias o cursos del plan académico (ej: Matemáticas, Lenguaje).
    Almacena las evaluaciones correspondientes y calcula el promedio final del semestre.
    """

    def __init__(self, nombre: str) -> None:
        """Constructor que inicializa la asignatura con su nombre y lista de evaluaciones."""
        self.nombre = nombre
        self.__evaluaciones: list = []

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def nombre(self) -> str:
        """Getter para el nombre de la asignatura."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Setter con validación de obligatoriedad."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre de la asignatura no puede estar vacío.")
        self.__nombre = valor.strip().title()

    @property
    def evaluaciones(self) -> list:
        """Getter para la lista de evaluaciones agregadas."""
        return list(self.__evaluaciones)

    # ---------------------------------------------------------
    # Métodos específicos del diagrama UML
    # ---------------------------------------------------------

    def agregar_evaluacion(self, evaluacion) -> None:
        """
        Método del UML: Agrega una evaluación (Prueba, Trabajo o Presentación Oral) a la asignatura.
        """
        if not hasattr(evaluacion, "calcular_nota") or not hasattr(evaluacion, "ponderacion"):
            raise TypeError("El objeto agregado debe ser una evaluación válida.")
        self.__evaluaciones.append(evaluacion)
        print(f"Evaluación agregada a {self.__nombre}: {evaluacion}")

    def calcular_nota_final(self) -> float:
        """
        Método del UML: Calcula la nota final ponderada del semestre.
        Suma (nota * ponderacion / 100) para cada evaluación registrada.
        """
        if not self.__evaluaciones:
            return 1.0

        suma_ponderada = 0.0
        ponderacion_total = 0.0

        for ev in self.__evaluaciones:
            nota = ev.calcular_nota()
            ponderacion = ev.ponderacion
            suma_ponderada += (nota * ponderacion)
            ponderacion_total += ponderacion

        if ponderacion_total <= 0:
            return 1.0

        nota_final = suma_ponderada / ponderacion_total
        return round(nota_final, 1)

    def __str__(self) -> str:
        """Representación en texto de la asignatura."""
        return f"Asignatura: {self.__nombre} ({len(self.__evaluaciones)} evaluaciones registradas)"

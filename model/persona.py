from abc import ABC, abstractmethod


# Definición de la clase abstracta Persona para el sistema del Colegio Nueva Esperanza
class Persona(ABC):
    """
    Clase abstracta de nivel superior que representa la entidad general
    de un individuo en la institución (Docentes, Estudiantes, Administrativos).
    No puede ser instanciada directamente.
    """

    def __init__(
        self,
        rut: str,
        primer_nombre: str,
        segundo_nombre: str,
        primer_apellido: str,
        segundo_apellido: str,
        email: str,
        direccion: str
    ) -> None:
        """Constructor que inicializa y valida los atributos de la persona."""
        self.rut = rut
        self.primer_nombre = primer_nombre
        self.segundo_nombre = segundo_nombre
        self.primer_apellido = primer_apellido
        self.segundo_apellido = segundo_apellido
        self.email = email
        self.direccion = direccion

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    # --- RUT ---
    @property
    def rut(self) -> str:
        """Getter para el RUT de la persona."""
        return self.__rut

    @rut.setter
    def rut(self, valor: str) -> None:
        """Setter para el RUT con validación básica de formato."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El RUT no puede estar vacío y debe ser una cadena de texto.")
        self.__rut = valor.strip().upper()

    # --- PRIMER NOMBRE ---
    @property
    def primer_nombre(self) -> str:
        """Getter para el primer nombre."""
        return self.__primer_nombre

    @primer_nombre.setter
    def primer_nombre(self, valor: str) -> None:
        """Setter para el primer nombre con validación de obligatoriedad."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El primer nombre es obligatorio y debe ser un texto válido.")
        self.__primer_nombre = valor.strip().capitalize()

    # --- SEGUNDO NOMBRE ---
    @property
    def segundo_nombre(self) -> str:
        """Getter para el segundo nombre."""
        return self.__segundo_nombre

    @segundo_nombre.setter
    def segundo_nombre(self, valor: str) -> None:
        """Setter para el segundo nombre (opcional o compuesto)."""
        if not isinstance(valor, str):
            raise ValueError("El segundo nombre debe ser una cadena de texto.")
        self.__segundo_nombre = valor.strip().capitalize()

    # --- PRIMER APELLIDO ---
    @property
    def primer_apellido(self) -> str:
        """Getter para el primer apellido."""
        return self.__primer_apellido

    @primer_apellido.setter
    def primer_apellido(self, valor: str) -> None:
        """Setter para el primer apellido con validación de obligatoriedad."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El primer apellido es obligatorio y debe ser un texto válido.")
        self.__primer_apellido = valor.strip().capitalize()

    # --- SEGUNDO APELLIDO ---
    @property
    def segundo_apellido(self) -> str:
        """Getter para el segundo apellido."""
        return self.__segundo_apellido

    @segundo_apellido.setter
    def segundo_apellido(self, valor: str) -> None:
        """Setter para el segundo apellido."""
        if not isinstance(valor, str):
            raise ValueError("El segundo apellido debe ser una cadena de texto.")
        self.__segundo_apellido = valor.strip().capitalize()

    # --- EMAIL ---
    @property
    def email(self) -> str:
        """Getter para el correo electrónico."""
        return self.__email

    @email.setter
    def email(self, valor: str) -> None:
        """Setter para el correo electrónico con validación de estructura."""
        if not isinstance(valor, str) or "@" not in valor or "." not in valor:
            raise ValueError("El correo electrónico debe ser válido (contener '@' y '.').")
        self.__email = valor.strip().lower()

    # --- DIRECCIÓN ---
    @property
    def direccion(self) -> str:
        """Getter para la dirección de la persona."""
        return self.__direccion

    @direccion.setter
    def direccion(self, valor: str) -> None:
        """Setter para la dirección con validación de obligatoriedad."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("La dirección es obligatoria y debe ser un texto válido.")
        self.__direccion = valor.strip()

    # ---------------------------------------------------------
    # Métodos abstractos (deben ser implementados por subclases)
    # ---------------------------------------------------------

    @abstractmethod
    def obtener_rol(self) -> str:
        """
        Método abstracto que obliga a cada clase derivada (Estudiante, Profesor, Administrativo)
        a definir y retornar su rol específico dentro del colegio.
        """
        pass

    # ---------------------------------------------------------
    # Métodos de negocio y auxiliares
    # ---------------------------------------------------------

    def validar_rut(self) -> bool:
        """Valida el RUT chileno de la persona utilizando el algoritmo de Módulo 11."""
        rut_limpio = self.__rut.replace(".", "").replace("-", "").strip().upper()

        if len(rut_limpio) < 2:
            return False

        cuerpo = rut_limpio[:-1]
        dv = rut_limpio[-1]

        if not cuerpo.isdigit():
            return False

        suma = 0
        multiplicador = 2

        # Recorrido inverso para ponderar cada dígito
        for caracter in reversed(cuerpo):
            suma += int(caracter) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1

        resto = 11 - (suma % 11)

        if resto == 11:
            dv_esperado = "0"
        elif resto == 10:
            dv_esperado = "K"
        else:
            dv_esperado = str(resto)

        return dv == dv_esperado

    def obtener_nombre_completo(self) -> str:
        """Retorna el nombre completo de la persona formateado."""
        partes = [
            self.__primer_nombre,
            self.__segundo_nombre,
            self.__primer_apellido,
            self.__segundo_apellido,
        ]
        return " ".join(p for p in partes if p)

    def __str__(self) -> str:
        """Representación legible en texto de la persona."""
        return f"[{self.obtener_rol()}] {self.obtener_nombre_completo()} (RUT: {self.__rut}, Email: {self.__email})"

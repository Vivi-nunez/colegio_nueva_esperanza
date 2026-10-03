import hashlib
try:
    from model.persona import Persona
except ModuleNotFoundError:
    from persona import Persona


class Trabajador(Persona):
    """
    Subtipo de Persona que agrupa al personal que labora en la institución.
    Mantiene el identificador interno del empleado y gestiona sus credenciales de acceso.
    """

    def __init__(
        self,
        rut: str,
        primer_nombre: str,
        segundo_nombre: str,
        primer_apellido: str,
        segundo_apellido: str,
        email: str,
        direccion: str,
        id_trabajador: str,
        clave: str
    ) -> None:
        """Constructor de Trabajador. Invoca al constructor de Persona con super()."""
        super().__init__(
            rut=rut,
            primer_nombre=primer_nombre,
            segundo_nombre=segundo_nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            email=email,
            direccion=direccion
        )
        self.id_trabajador = id_trabajador
        self.establecer_clave(clave)

    # ---------------------------------------------------------
    # Getters y Setters con validaciones (@property)
    # ---------------------------------------------------------

    @property
    def id_trabajador(self) -> str:
        """Getter para el ID de empleado."""
        return self.__id_trabajador

    @id_trabajador.setter
    def id_trabajador(self, valor: str) -> None:
        """Setter para el ID de empleado con validación."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El ID de trabajador no puede estar vacío y debe ser un texto.")
        self.__id_trabajador = valor.strip().upper()

    @property
    def clave_encrypted(self) -> str:
        """Getter para el hash seguro de la contraseña."""
        return self.__clave_encrypted

    # ---------------------------------------------------------
    # Métodos de seguridad y negocio
    # ---------------------------------------------------------

    def establecer_clave(self, clave_plana: str) -> None:
        """Hashea y almacena de forma segura la clave con algoritmo SHA-256."""
        if not isinstance(clave_plana, str) or len(clave_plana) < 4:
            raise ValueError("La clave debe tener al menos 4 caracteres.")
        self.__clave_encrypted = hashlib.sha256(clave_plana.encode("utf-8")).hexdigest()

    def autentificar(self, clave: str) -> bool:
        """
        Método del UML: Valida si la clave ingresada coincide con la contraseña almacenada.
        """
        if not isinstance(clave, str):
            return False
        hash_ingresado = hashlib.sha256(clave.encode("utf-8")).hexdigest()
        return hash_ingresado == self.__clave_encrypted

    def obtener_rol(self) -> str:
        """Implementación base de rol para trabajador."""
        return "Trabajador"

    def __str__(self) -> str:
        """Representación en texto del trabajador."""
        return f"Trabajador [{self.id_trabajador}]: {self.obtener_nombre_completo()} | Email: {self.email}"

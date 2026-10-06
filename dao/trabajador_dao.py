from typing import Optional
from dao.conexion import ConexionBD
from model.trabajador import Trabajador
from model.administrativo import Administrativo
from model.profesor import Profesor


class TrabajadorDAO:
    """
    Data Access Object (DAO) para las entidades Trabajador, Administrativo y Profesor.
    Maneja la persistencia y autenticación segura con consultas parametrizadas.
    """

    @staticmethod
    def insertar(trabajador: Trabajador) -> bool:
        """
        Inserta un nuevo trabajador (Administrativo o Profesor) en la base de datos.
        Guarda la contraseña ya cifrada con SHA-256.
        """
        sql = """
        INSERT INTO trabajador (
            id_trabajador, rut, primer_nombre, segundo_nombre,
            primer_apellido, segundo_apellido, email, direccion,
            clave_encrypted, tipo_trabajador, cargo_o_especialidad
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        if isinstance(trabajador, Administrativo):
            tipo = "Administrativo"
            detalle = trabajador.cargo
        elif isinstance(trabajador, Profesor):
            tipo = "Profesor"
            detalle = trabajador.especialidad
        else:
            tipo = "Trabajador"
            detalle = "General"

        valores = (
            trabajador.id_trabajador,
            trabajador.rut,
            trabajador.primer_nombre,
            trabajador.segundo_nombre,
            trabajador.primer_apellido,
            trabajador.segundo_apellido,
            trabajador.email,
            trabajador.direccion,
            trabajador.clave_encrypted,
            tipo,
            detalle
        )
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, valores)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as error:
            print(f"[TrabajadorDAO] Error al insertar trabajador: {error}")
            return False

    @staticmethod
    def _mapear_fila_a_objeto(fila) -> Optional[Trabajador]:
        """Convierte una fila de la base de datos al tipo de objeto correspondiente."""
        if not fila:
            return None

        tipo = fila["tipo_trabajador"]
        if tipo == "Administrativo":
            instancia = Administrativo(
                rut=fila["rut"],
                primer_nombre=fila["primer_nombre"],
                segundo_nombre=fila["segundo_nombre"],
                primer_apellido=fila["primer_apellido"],
                segundo_apellido=fila["segundo_apellido"],
                email=fila["email"],
                direccion=fila["direccion"],
                id_trabajador=fila["id_trabajador"],
                clave="temp", # Clave temporal que sobreescribiremos con el hash
                cargo=fila["cargo_o_especialidad"]
            )
        elif tipo == "Profesor":
            instancia = Profesor(
                rut=fila["rut"],
                primer_nombre=fila["primer_nombre"],
                segundo_nombre=fila["segundo_nombre"],
                primer_apellido=fila["primer_apellido"],
                segundo_apellido=fila["segundo_apellido"],
                email=fila["email"],
                direccion=fila["direccion"],
                id_trabajador=fila["id_trabajador"],
                clave="temp",
                especialidad=fila["cargo_o_especialidad"]
            )
        else:
            instancia = Trabajador(
                rut=fila["rut"],
                primer_nombre=fila["primer_nombre"],
                segundo_nombre=fila["segundo_nombre"],
                primer_apellido=fila["primer_apellido"],
                segundo_apellido=fila["segundo_apellido"],
                email=fila["email"],
                direccion=fila["direccion"],
                id_trabajador=fila["id_trabajador"],
                clave="temp"
            )

        # Asigna directamente el hash almacenado previamente
        instancia._Trabajador__clave_encrypted = fila["clave_encrypted"]
        return instancia

    @classmethod
    def obtener_por_id(cls, id_trabajador: str) -> Optional[Trabajador]:
        """
        Busca un trabajador por su ID mediante consulta parametrizada.
        """
        sql = """
        SELECT id_trabajador, rut, primer_nombre, segundo_nombre,
               primer_apellido, segundo_apellido, email, direccion,
               clave_encrypted, tipo_trabajador, cargo_o_especialidad
        FROM trabajador
        WHERE id_trabajador = ?;
        """
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (id_trabajador.strip().upper(),))
                fila = cursor.fetchone()
                return cls._mapear_fila_a_objeto(fila)
        except Exception as error:
            print(f"[TrabajadorDAO] Error al buscar trabajador por ID: {error}")
            return None

    @classmethod
    def autenticar(cls, id_trabajador: str, clave_plana: str) -> Optional[Trabajador]:
        """
        Método de seguridad: Valida las credenciales de acceso de un trabajador.
        Consulta parametrizada por ID y verificación criptográfica del hash.
        """
        trabajador = cls.obtener_por_id(id_trabajador)
        if trabajador and trabajador.autentificar(clave_plana):
            return trabajador
        return None

    @classmethod
    def listar_todos(cls) -> list[Trabajador]:
        """Retorna todos los trabajadores registrados en el colegio."""
        sql = """
        SELECT id_trabajador, rut, primer_nombre, segundo_nombre,
               primer_apellido, segundo_apellido, email, direccion,
               clave_encrypted, tipo_trabajador, cargo_o_especialidad
        FROM trabajador
        ORDER BY primer_apellido ASC, primer_nombre ASC;
        """
        trabajadores: list[Trabajador] = []
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                for fila in cursor.fetchall():
                    obj = cls._mapear_fila_a_objeto(fila)
                    if obj:
                        trabajadores.append(obj)
        except Exception as error:
            print(f"[TrabajadorDAO] Error al listar trabajadores: {error}")

        return trabajadores

    @staticmethod
    def eliminar(id_trabajador: str) -> bool:
        """Elimina un trabajador por su ID."""
        sql = "DELETE FROM trabajador WHERE id_trabajador = ?;"
        try:
            with ConexionBD.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (id_trabajador.strip().upper(),))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as error:
            print(f"[TrabajadorDAO] Error al eliminar trabajador: {error}")
            return False

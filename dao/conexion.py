import sqlite3
from pathlib import Path

# Ruta dinámica que asegura ubicar la base de datos siempre en la raíz del proyecto
RUTA_BASE_DATOS = Path(__file__).resolve().parent.parent / "colegio.db"


class ConexionBD:
    """
    Gestiona la conexión centralizada a la base de datos SQLite del Colegio Nueva Esperanza.
    Garantiza la activación de claves foráneas y la creación automática de tablas.
    """

    @staticmethod
    def obtener_conexion() -> sqlite3.Connection:
        """
        Retorna una nueva conexión activa con SQLite configurada con row_factory
        para acceder a las columnas por nombre y con claves foráneas habilitadas.
        """
        conexion = sqlite3.connect(RUTA_BASE_DATOS)
        # Permite acceder a los campos como diccionarios (fila['rut'])
        conexion.row_factory = sqlite3.Row
        # Activa integridad referencial en SQLite
        conexion.execute("PRAGMA foreign_keys = ON;")
        return conexion

    @classmethod
    def inicializar_base_datos(cls) -> None:
        """
        Crea automáticamente todas las tablas relacionales del sistema si no existen.
        Previene fallos en primer arranque y garantiza la integridad de los datos.
        """
        script_ddl = """
        -- 1. Tabla de Estudiantes (Hereda de Persona)
        CREATE TABLE IF NOT EXISTS estudiante (
            rut TEXT PRIMARY KEY,
            primer_nombre TEXT NOT NULL,
            segundo_nombre TEXT DEFAULT '',
            primer_apellido TEXT NOT NULL,
            segundo_apellido TEXT DEFAULT '',
            email TEXT NOT NULL,
            direccion TEXT NOT NULL,
            tiene_deuda_pendiente INTEGER NOT NULL DEFAULT 0
        );

        -- 2. Tabla de Trabajadores (Docentes y Administrativos)
        CREATE TABLE IF NOT EXISTS trabajador (
            id_trabajador TEXT PRIMARY KEY,
            rut TEXT NOT NULL,
            primer_nombre TEXT NOT NULL,
            segundo_nombre TEXT DEFAULT '',
            primer_apellido TEXT NOT NULL,
            segundo_apellido TEXT DEFAULT '',
            email TEXT NOT NULL,
            direccion TEXT NOT NULL,
            clave_encrypted TEXT NOT NULL,
            tipo_trabajador TEXT NOT NULL, -- 'Administrativo' o 'Profesor'
            cargo_o_especialidad TEXT NOT NULL
        );

        -- 3. Tabla de Asignaturas y Electivos
        CREATE TABLE IF NOT EXISTS asignatura (
            id_asignatura INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL DEFAULT 'Regular', -- 'Regular' o 'Electivo'
            cupo_maximo INTEGER DEFAULT 0,
            cupo_disponible INTEGER DEFAULT 0
        );

        -- 4. Tabla de Matrículas (Transacción principal)
        CREATE TABLE IF NOT EXISTS matricula (
            id_matricula INTEGER PRIMARY KEY,
            rut_estudiante TEXT NOT NULL,
            fecha TEXT NOT NULL,
            arancel_uf REAL NOT NULL,
            semestre TEXT NOT NULL,
            FOREIGN KEY (rut_estudiante) REFERENCES estudiante (rut) ON DELETE RESTRICT
        );

        -- 5. Tabla de Detalle de Matrícula (Materia inscrita en un contrato)
        CREATE TABLE IF NOT EXISTS detalle_matricula (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_matricula INTEGER NOT NULL,
            id_asignatura INTEGER NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Inscrita',
            FOREIGN KEY (id_matricula) REFERENCES matricula (id_matricula) ON DELETE CASCADE,
            FOREIGN KEY (id_asignatura) REFERENCES asignatura (id_asignatura) ON DELETE RESTRICT
        );

        -- 6. Tabla de Calificaciones
        CREATE TABLE IF NOT EXISTS calificacion (
            id_calificacion INTEGER PRIMARY KEY AUTOINCREMENT,
            rut_estudiante TEXT NOT NULL,
            id_asignatura INTEGER NOT NULL,
            nota REAL NOT NULL CHECK(nota >= 1.0 AND nota <= 7.0),
            observacion TEXT DEFAULT '',
            FOREIGN KEY (rut_estudiante) REFERENCES estudiante (rut) ON DELETE CASCADE,
            FOREIGN KEY (id_asignatura) REFERENCES asignatura (id_asignatura) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS profesor_asignatura (
            id_trabajador TEXT NOT NULL,
            id_asignatura INTEGER NOT NULL,
            PRIMARY KEY (id_trabajador, id_asignatura),
            FOREIGN KEY (id_trabajador) REFERENCES trabajador (id_trabajador) ON DELETE CASCADE,
            FOREIGN KEY (id_asignatura) REFERENCES asignatura (id_asignatura) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS evaluacion_registrada (
            id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
            id_evaluacion TEXT NOT NULL,
            rut_estudiante TEXT NOT NULL,
            id_asignatura INTEGER NOT NULL,
            id_profesor TEXT NOT NULL,
            tipo_evaluacion TEXT NOT NULL CHECK (tipo_evaluacion IN ('Prueba', 'Trabajo', 'Presentación oral')),
            fecha TEXT NOT NULL,
            periodo_academico TEXT NOT NULL DEFAULT '',
            ponderacion REAL NOT NULL CHECK (ponderacion > 0 AND ponderacion <= 100),
            nota REAL NOT NULL CHECK (nota >= 1.0 AND nota <= 7.0),
            observacion TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (rut_estudiante) REFERENCES estudiante (rut) ON DELETE CASCADE,
            FOREIGN KEY (id_asignatura) REFERENCES asignatura (id_asignatura) ON DELETE CASCADE,
            FOREIGN KEY (id_profesor) REFERENCES trabajador (id_trabajador) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS cobro_mensual (
            id_cobro INTEGER PRIMARY KEY AUTOINCREMENT,
            rut_estudiante TEXT NOT NULL,
            periodo TEXT NOT NULL,
            arancel_uf REAL NOT NULL CHECK (arancel_uf > 0),
            valor_uf REAL NOT NULL CHECK (valor_uf > 0),
            total_pesos INTEGER NOT NULL CHECK (total_pesos > 0),
            fecha_emision TEXT NOT NULL,
            UNIQUE (rut_estudiante, periodo),
            FOREIGN KEY (rut_estudiante) REFERENCES estudiante (rut) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS pago_mensual (
            id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cobro INTEGER NOT NULL,
            monto_pesos INTEGER NOT NULL CHECK (monto_pesos > 0),
            fecha_pago TEXT NOT NULL,
            observacion TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (id_cobro) REFERENCES cobro_mensual (id_cobro) ON DELETE RESTRICT
        );
        """
        with cls.obtener_conexion() as conexion:
            conexion.executescript(script_ddl)
            columnas_evaluacion = {
                fila["name"] for fila in conexion.execute("PRAGMA table_info(evaluacion_registrada);")
            }
            if "periodo_academico" not in columnas_evaluacion:
                conexion.execute(
                    "ALTER TABLE evaluacion_registrada ADD COLUMN periodo_academico TEXT NOT NULL DEFAULT '';"
                )
            conexion.commit()


# Inicialización automática de la estructura al importar el módulo
ConexionBD.inicializar_base_datos()

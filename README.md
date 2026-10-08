# Colegio Nueva Esperanza

Sistema integral de gestión académica, administrativa y financiera para el Colegio Nueva Esperanza, desarrollado en Python 3 aplicando los principios de la Programación Orientada a Objetos (POO) y buenas prácticas de seguridad de software (POO Seguro).

---

## 1. Arquitectura del Modelo de Dominio (`model/`)

### A. Jerarquía de Personas y Personal
- `Persona`: Clase base abstracta (`ABC`) con encapsulamiento estricto (`__`), getters/setters validados, validación de RUT chileno mediante algoritmo Módulo 11 y método abstracto `obtener_rol()`.
- `Estudiante`: Subtipo de `Persona`. Gestiona el estado de morosidad (`tiene_deuda_pendiente`), `validar_deuda()` y `consultar_notas()`.
- `Trabajador`: Subtipo de `Persona`. Almacena credenciales con contraseña cifrada mediante algoritmo criptográfico **SHA-256** y método `autentificar()`.
  - `Administrativo`: Subtipo de `Trabajador` para secretaría y cobranza (`matricular_estudiante()` y `cobrar_matricula()`).
  - `Profesor`: Subtipo de `Trabajador` para registro docente (`ingresar_nota()` en escala 1.0 a 7.0 e `ingresar_observacion()`).

### B. Instrumentos de Evaluación
- `Evaluacion`: Clase base abstracta con método abstracto `calcular_nota()`.
  - `Prueba`: Exámenes escritos ponderados según escala de puntaje sobre el máximo.
  - `Trabajo`: Investigaciones evaluadas por escala de logro en rúbrica pedagógica.
  - `PresentacionOral`: Disertaciones evaluadas por cumplimiento de tiempo reglamentario.

### C. Currículum y Cursos
- `Asignatura`: Administra evaluaciones y calcula el promedio final ponderado (`calcular_nota_final()`).
- `Electivo`: Subtipo de `Asignatura` con control y reserva de cupos disponibles (`verificar_cupo()`, `reserva_cupo()`).

### D. Transacciones y Finanzas
- `IndicadorUF`: Consume en vivo la API de `mindicador.cl/api/uf` mediante `requests` para obtener el valor diario de la UF.
- `Arancel`: Convierte aranceles fijados en UF a pesos chilenos según el valor de la UF del día.
- `Calificacion`: Almacena notas reglamentarias (escala 1.0 a 7.0) y comentarios pedagógicos.
- `Matricula` y `DetalleMatricula`: Contrato formal de matrícula que verifica condición de deuda del estudiante e inscribe asignaturas.

---

## 2. Capa de Persistencia y Acceso a Datos (`dao/`)

Diseñada para prevenir vulnerabilidades de inyección SQL (SQL Injection) mediante **consultas preparadas y parametrizadas (`?`)**:
- `conexion.py`: Manejador centralizado de SQLite (`colegio.db`), activación de claves foráneas (`PRAGMA foreign_keys = ON;`) y creación automática de tablas relacionales DDL.
- `estudiante_dao.py`: Operaciones CRUD completas para estudiantes y actualización de morosidad.
- `trabajador_dao.py`: Persistencia y autenticación criptográfica de administrativos y docentes.
- `asignatura_dao.py`: Catálogo curricular y control atómico de cupos de electivos.
- `matricula_dao.py`: Transacción atómica de matrícula validando integridad financiera en base de datos.

---

## 3. Aplicación Principal (`main.py`)

Interfaz de consola interactiva que unifica todas las capas:
- **Autenticación:** Inicio de sesión con SHA-256 para el personal institucional.
- **Validación crítica:** Bloqueo administrativo automático si el estudiante registra deuda.
- **API en vivo:** Consulta de la UF y cálculo de aranceles en tiempo real.
- **Modo Demostración:** Ejecución integral automatizada de pruebas de todas las reglas del negocio.

### Ejecución
```bash
python main.py
```

### Credenciales de demostración inicial:
- **Administrativo:** ID `ADM01` | Clave `admin123`
- **Profesor:** ID `DOC01` | Clave `profe123`
- **Profesores por asignatura:** ID `DOC-ASIG-<id de asignatura>` | Clave `profe123`. La relación entre cada materia y su ID se muestra en el inicio de sesión.

---

## Estructura del Repositorio
- `Colegio_3.drawio`: Diagrama de clases UML oficial del proyecto.
- `model/`: 16 módulos de dominio bajo POO.
- `dao/`: Capa de persistencia con SQLite y consultas parametrizadas.
- `main.py`: Punto de entrada con menú interactivo.
- `.gitignore`: Exclusión de bases de datos locales, cachés y temporales.

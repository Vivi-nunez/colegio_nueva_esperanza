# Colegio Nueva Esperanza

Sistema de gestión académica, administrativa y financiera para el Colegio Nueva Esperanza, desarrollado en Python 3 aplicando los principios de la Programación Orientada a Objetos (POO).

## Arquitectura del Modelo (`model/`)

### 1. Jerarquía de Personas y Personal
- `Persona`: Clase abstracta base (`ABC`) con atributos privados, propiedades, validación de RUT mediante algoritmo Módulo 11 y método abstracto `obtener_rol()`.
- `Estudiante`: Subtipo de `Persona`. Gestiona el estado de morosidad (`tiene_deuda_pendiente`), `validar_deuda()` y `consultar_notas()`.
- `Trabajador`: Subtipo de `Persona`. Administra credenciales con contraseña cifrada (SHA-256) y autenticación.
  - `Administrativo`: Subtipo de `Trabajador` para secretaría y cobranza (`matricular_estudiante()` y `cobrar_matricula()`).
  - `Profesor`: Subtipo de `Trabajador` para registro pedagógico (`ingresar_nota()` e `ingresar_observacion()`).

### 2. Evaluaciones Académicas
- `Evaluacion`: Clase abstracta con método abstracto `calcular_nota()`.
  - `Prueba`: Exámenes escritos ponderados por escala de puntaje.
  - `Trabajo`: Proyectos evaluados por escala de logro en rúbrica.
  - `PresentacionOral`: Disertaciones evaluadas por cumplimiento de tiempo.

### 3. Asignaturas y Cursos
- `Asignatura`: Administra evaluaciones y calcula promedio ponderado final (`calcular_nota_final()`).
- `Electivo`: Subtipo de `Asignatura` con control de cupos máximos y disponibles (`verificar_cupo()`, `reserva_cupo()`).

### 4. Transacciones y Finanzas
- `IndicadorUF`: Consume la API de `mindicador.cl/api/uf` mediante `requests` para obtener la UF del día.
- `Arancel`: Convierte aranceles fijados en UF a pesos chilenos según el valor diario.
- `Calificacion`: Almacena notas reglamentarias (escala 1.0 a 7.0) y observaciones.
- `Matricula` y `DetalleMatricula`: Contrato formal de matrícula que verifica estado de deuda y vincula asignaturas/electivos.

## Archivos del Repositorio
- `Colegio_3.drawio`: Diagrama de clases UML oficial del proyecto.
- `model/`: Paquete con las 16 clases del modelo de dominio.

class ReglaNegocioError(Exception):
    """Excepción base para errores de reglas de negocio del sistema escolar."""


class DeudaPendienteError(ReglaNegocioError):
    """Se lanza cuando un estudiante tiene deuda pendiente y no puede matricularse."""


class CupoAgotadoError(ReglaNegocioError):
    """Se lanza cuando un electivo ya no tiene cupos disponibles para la inscripción."""

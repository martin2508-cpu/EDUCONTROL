from modelos.calificacion import Calificacion


class RegistroAcademico:
    """Compone las tres calificaciones de un estudiante en una asignatura."""
    def __init__(self, estudiante, asignatura, notas):
        if len(notas) != 3:
            raise ValueError("Cada registro debe contener exactamente tres notas.")
        self.estudiante = estudiante
        self.asignatura = asignatura
        self.calificaciones = [Calificacion(nota) for nota in notas]

    @property
    def promedio(self):
        return round(sum(n.nota for n in self.calificaciones) / 3, 2)

    @property
    def estado(self):
        return "Aprobado" if self.promedio >= 3.0 else "Reprobado"

    def actualizar_notas(self, notas):
        if len(notas) != 3:
            raise ValueError("Debes ingresar exactamente tres notas.")
        nuevas = [Calificacion(nota) for nota in notas]
        self.calificaciones = nuevas

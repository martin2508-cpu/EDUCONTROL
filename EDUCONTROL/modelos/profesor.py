from modelos.persona import Persona


class Profesor(Persona):
    def __init__(self, identificacion, nombre, correo, especialidad):
        super().__init__(identificacion, nombre, correo)
        self.especialidad = str(especialidad).strip()
        if not self.especialidad:
            raise ValueError("La especialidad es obligatoria.")

    def mostrar_informacion(self):
        return f"Profesor: {self.nombre} | Especialidad: {self.especialidad}"

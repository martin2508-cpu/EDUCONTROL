from modelos.persona import Persona


class Estudiante(Persona):
    def __init__(self, identificacion, nombre, correo, codigo, programa):
        super().__init__(identificacion, nombre, correo)
        self.codigo = str(codigo).strip()
        self.programa = str(programa).strip()
        if not self.codigo or not self.programa:
            raise ValueError("El código y el programa académico son obligatorios.")

    def mostrar_informacion(self):
        return f"Estudiante: {self.nombre} | Código: {self.codigo} | Programa: {self.programa}"

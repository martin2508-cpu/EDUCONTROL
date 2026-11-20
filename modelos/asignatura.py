class Asignatura:
    def __init__(self, codigo, nombre, intensidad_horaria, profesor=None):
        self.codigo = str(codigo).strip()
        self.nombre = str(nombre).strip()
        if not self.codigo or not self.nombre:
            raise ValueError("El código y el nombre de la asignatura son obligatorios.")
        try:
            self.intensidad_horaria = int(intensidad_horaria)
        except (TypeError, ValueError):
            raise ValueError("La intensidad horaria debe ser un número entero.")
        if self.intensidad_horaria <= 0:
            raise ValueError("La intensidad horaria debe ser mayor que cero.")
        self.profesor = profesor

    def mostrar_informacion(self):
        docente = self.profesor.nombre if self.profesor else "Sin asignar"
        return f"{self.codigo} - {self.nombre} ({docente})"

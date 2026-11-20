class Calificacion:
    def __init__(self, nota):
        self.nota = nota

    @property
    def nota(self):
        return self._nota

    @nota.setter
    def nota(self, valor):
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            raise ValueError("La nota debe ser numérica.")
        if not 0 <= numero <= 5:
            raise ValueError("La nota debe estar entre 0.0 y 5.0.")
        self._nota = round(numero, 2)

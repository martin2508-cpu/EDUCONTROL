from abc import ABC, abstractmethod


class Persona(ABC):
    def __init__(self, identificacion, nombre, correo):
        self._identificacion = self._validar_texto(identificacion, "La identificación")
        self._nombre = self._validar_texto(nombre, "El nombre")
        self._correo = self._validar_texto(correo, "El correo")

    @staticmethod
    def _validar_texto(valor, campo):
        valor = str(valor).strip()
        if not valor:
            raise ValueError(f"{campo} es obligatorio.")
        return valor

    @property
    def identificacion(self):
        return self._identificacion

    @property
    def nombre(self):
        return self._nombre

    @property
    def correo(self):
        return self._correo

    @abstractmethod
    def mostrar_informacion(self):
        pass

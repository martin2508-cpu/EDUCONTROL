import unittest
from servicios.gestor_academico import GestorAcademico


class PruebasGestorAcademico(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorAcademico()
        self.estudiante = self.gestor.agregar_estudiante(
            "1001", "Ana Pérez", "ana@correo.com", "EST001", "Ingeniería en Sistemas")
        self.asignatura = self.gestor.agregar_asignatura("MAT01", "Matemáticas", 4)

    def test_registro_estudiante(self):
        self.assertEqual(len(self.gestor.estudiantes), 1)

    def test_identificacion_duplicada(self):
        with self.assertRaises(ValueError):
            self.gestor.agregar_estudiante("1001", "Otro", "otro@correo.com", "EST002", "Sistemas")

    def test_promedio(self):
        registro = self.gestor.guardar_calificaciones("1001", "MAT01", [4, 3, 5])
        self.assertEqual(registro.promedio, 4.0)
        self.assertEqual(registro.estado, "Aprobado")

    def test_nota_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            self.gestor.guardar_calificaciones("1001", "MAT01", [4, 6, 5])

    def test_reprobado(self):
        registro = self.gestor.guardar_calificaciones("1001", "MAT01", [2, 2.5, 3])
        self.assertEqual(registro.estado, "Reprobado")


if __name__ == "__main__":
    unittest.main()

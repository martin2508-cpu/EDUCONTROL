import unittest
from servicios.gestor_academico import GestorAcademico


class PruebasEstadisticas(unittest.TestCase):
    def setUp(self):
        self.g = GestorAcademico()
        self.g.cargar_datos_demo()

    def test_datos_demo_se_conservan(self):
        self.assertEqual((len(self.g.estudiantes), len(self.g.profesores),
                          len(self.g.asignaturas), len(self.g.registros)), (10, 4, 5, 16))

    def test_estadisticas_de_una_asignatura(self):
        datos = self.g.estadisticas_asignatura("MAT101")
        self.assertEqual(datos["inscritos"], 4)
        self.assertEqual(datos["aprobados"] + datos["reprobados"], 4)
        self.assertEqual(datos["mejor"].estudiante.identificacion, "1001")
        self.assertEqual(len(datos["promedio_por_nota"]), 3)

    def test_asignatura_sin_notas(self):
        self.g.agregar_asignatura("NUEVA", "Sin notas", 2)
        datos = self.g.estadisticas_asignatura("NUEVA")
        self.assertEqual(datos["inscritos"], 0)
        self.assertEqual(datos["porcentaje_aprobacion"], 0.0)
        self.assertIsNone(datos["mejor"])

    def test_distribucion_suma_todos_los_registros(self):
        rangos, conteos = self.g.distribucion_promedios()
        self.assertEqual(len(rangos), 5)
        self.assertEqual(sum(conteos), len(self.g.registros))
        self.assertEqual(sum(conteos[3:]), self.g.contar_aprobados())   # 3.0 o más = aprobado

    def test_promedio_por_asignatura_omite_las_vacias(self):
        self.g.agregar_asignatura("NUEVA", "Sin notas", 2)
        codigos = [a.codigo for a, _, _ in self.g.promedio_por_asignatura()]
        self.assertNotIn("NUEVA", codigos)
        self.assertEqual(len(codigos), 5)

    def test_estudiantes_por_programa(self):
        conteo = dict(self.g.estudiantes_por_programa())
        self.assertEqual(sum(conteo.values()), 10)
        self.assertEqual(conteo["Ingeniería en Sistemas"], 4)

    def test_estudiantes_en_riesgo(self):
        riesgo = self.g.estudiantes_en_riesgo()
        self.assertTrue(all(promedio < 3.0 for _, promedio, _ in riesgo))
        self.assertEqual([p for _, p, _ in riesgo], sorted(p for _, p, _ in riesgo))

    def test_mejores_estudiantes(self):
        mejores = self.g.mejores_estudiantes(3)
        self.assertEqual(len(mejores), 3)
        self.assertGreaterEqual(mejores[0][1], mejores[-1][1])

    def test_actualizar_asignatura_invalida_no_modifica_datos(self):
        asignatura = self.g.buscar_asignatura("MAT101")
        with self.assertRaises(ValueError):
            self.g.actualizar_asignatura("MAT101", "Nombre nuevo", "abc")
        self.assertEqual(asignatura.nombre, "Matemáticas básicas")
        self.assertEqual(asignatura.intensidad_horaria, 4)


if __name__ == "__main__":
    unittest.main()

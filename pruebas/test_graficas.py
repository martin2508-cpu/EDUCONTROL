import unittest

from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from interfaz import graficas, tema


def nueva_figura(ancho=400, alto=300):
    figura = Figure(figsize=(ancho / 100, alto / 100), dpi=100)
    FigureCanvasAgg(figura)
    return figura


def mover(figura, ax, x, y):
    px, py = ax.transData.transform((x, y))
    figura.canvas.callbacks.process("motion_notify_event",
                                    MouseEvent("motion_notify_event", figura.canvas, px, py))


class PruebasGraficas(unittest.TestCase):
    def test_dona_cambia_el_centro_al_pasar_el_cursor(self):
        figura = nueva_figura()
        graficas.dona(figura, ["Aprobados", "Reprobados"], [3, 1], [tema.OK, tema.ERROR],
                      "de aprobación", "75%")
        figura.canvas.draw()
        mover(figura, figura.axes[0], 0.9, 0.2)                 # sector de aprobados
        textos = [t.get_text() for t in figura.axes[0].texts]
        self.assertIn("Aprobados", textos)
        figura.canvas.callbacks.process("figure_leave_event",
                                        MouseEvent("figure_leave_event", figura.canvas, 0, 0))
        self.assertIn("de aprobación", [t.get_text() for t in figura.axes[0].texts])

    def test_barras_ejecutan_el_clic(self):
        figura = nueva_figura()
        clics = []
        graficas.barras(figura, ["A", "B"], [3.0, 4.0], [tema.AZUL, tema.VERDE], ["a", "b"],
                        maximo=5.6, al_clic=clics.append)
        figura.canvas.draw()
        ax = figura.axes[0]
        mover(figura, ax, 1, 1.0)
        px, py = ax.transData.transform((1, 1.0))
        figura.canvas.callbacks.process("button_press_event",
                                        MouseEvent("button_press_event", figura.canvas, px, py, button=1))
        self.assertEqual(clics, [1])

    def test_barras_devuelven_lo_necesario_para_animar(self):
        figura = nueva_figura()
        info = graficas.barras(figura, ["A"], [2.0], [tema.AZUL], ["a"])
        self.assertEqual(len(info["barras"]), 1)
        self.assertEqual(len(info["etiquetas"]), 1)

    def test_graficas_sin_datos_no_fallan(self):
        for dibujar in (lambda f: graficas.dona(f, [], [0, 0], ["#fff"] * 2, "x", "0"),
                        lambda f: graficas.barras(f, [], [], [], []),
                        lambda f: graficas.barras_horizontales(f, [], [], [], []),
                        lambda f: graficas.linea(f, ["a", "b", "c"], [0, 0, 0], tema.AZUL, [])):
            figura = nueva_figura()
            dibujar(figura)
            figura.canvas.draw()

    def test_abreviar(self):
        self.assertEqual(graficas.abreviar("Ingeniería en Sistemas"), "Ing. en Sistemas")


if __name__ == "__main__":
    unittest.main()

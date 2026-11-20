"""Gráficas del sistema dibujadas con Matplotlib.

Este módulo NO usa Tkinter: cada función recibe una ``Figure``, la dibuja y conecta
los eventos del ratón (tooltip al pasar el cursor y clic opcional). Gracias a eso se
pueden probar sin abrir ninguna ventana.

Las funciones que dibujan barras devuelven un diccionario con las barras y las
etiquetas para que ``TarjetaGrafica`` (en componentes.py) pueda animarlas.
"""
import math

import matplotlib
from matplotlib import font_manager
from matplotlib.ticker import MaxNLocator

from interfaz import tema

# Segoe UI existe en Windows; en otros sistemas se usa la fuente por defecto de Matplotlib.
_fuentes = {f.name for f in font_manager.fontManager.ttflist}
matplotlib.rcParams["font.family"] = "Segoe UI" if "Segoe UI" in _fuentes else "DejaVu Sans"


# ----------------------------------------------------------------------
# Utilidades internas
# ----------------------------------------------------------------------
def abreviar(texto):
    return texto.replace("Ingeniería", "Ing.")


def _preparar(fig):
    fig.clear()
    fig.set_facecolor(tema.TARJETA)


def _sin_datos(fig, texto="Aún no hay datos para mostrar"):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.text(0.5, 0.5, texto, ha="center", va="center", color=tema.TEXTO_SUAVE, fontsize=10)
    return {}


def _ejes(fig, rect, grilla="y"):
    ax = fig.add_axes(rect)
    ax.set_facecolor(tema.TARJETA)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(tema.BORDE)
    ax.tick_params(colors=tema.TEXTO_MEDIO, labelsize=9, length=0)
    if grilla:
        ax.grid(axis=grilla, color=tema.BORDE, alpha=0.6, linewidth=0.7)
    ax.set_axisbelow(True)
    return ax


def _etiqueta_referencia(ax, valor, n, texto="Mínimo"):
    """Rotula la línea punteada en el margen derecho (fuera de las barras)."""
    ax.text(1.015, valor, f"{texto}\n{valor:.1f}", transform=ax.get_yaxis_transform(),
            ha="left", va="center", color=tema.AMARILLO, fontsize=8, fontweight="bold",
            clip_on=False, linespacing=1.1)


def _conectar(fig, ax, elementos, textos, resaltar, restaurar, al_clic=None):
    """Conecta el tooltip, el resaltado al pasar el cursor y el clic opcional."""
    nota = ax.annotate(
        "", xy=(0, 0), xytext=(12, 12), textcoords="offset points", fontsize=8.5,
        color=tema.TEXTO, fontweight="bold", zorder=50, annotation_clip=False,
        bbox=dict(boxstyle="round,pad=0.5", fc=tema.FONDO, ec=tema.AZUL, lw=1))
    nota.set_visible(False)
    estado = {"actual": None}

    def actualizar(indice, evento=None):
        if indice != estado["actual"]:
            if estado["actual"] is not None:
                restaurar(estado["actual"])
            if indice is not None:
                resaltar(indice)
            estado["actual"] = indice
        if indice is None:
            if nota.get_visible():
                nota.set_visible(False)
            fig.canvas.draw_idle()
            return
        a_la_derecha = evento.x > fig.bbox.width * 0.6
        nota.xy = (evento.xdata, evento.ydata)
        nota.xyann = (-12 if a_la_derecha else 12, 12)
        nota.set_ha("right" if a_la_derecha else "left")
        nota.set_text(textos[indice])
        nota.set_visible(True)
        fig.canvas.draw_idle()

    def al_mover(evento):
        indice = None
        if evento.inaxes is ax:
            for i, elemento in enumerate(elementos):
                if elemento.contains(evento)[0]:
                    indice = i
                    break
        actualizar(indice, evento)

    def al_pulsar(evento):
        if al_clic and estado["actual"] is not None and evento.button == 1:
            al_clic(estado["actual"])

    fig.canvas.mpl_connect("motion_notify_event", al_mover)
    fig.canvas.mpl_connect("figure_leave_event", lambda evento: actualizar(None))
    fig.canvas.mpl_connect("button_press_event", al_pulsar)


# ----------------------------------------------------------------------
# Gráficas
# ----------------------------------------------------------------------
def dona(fig, etiquetas, valores, colores, titulo_centro, texto_centro,
         columnas=None, al_clic=None):
    """Gráfica circular tipo dona. Al pasar el cursor, el sector crece y el centro cambia."""
    _preparar(fig)
    total = sum(valores)
    if total == 0:
        return _sin_datos(fig)
    ncol = columnas or min(len(etiquetas), 3)
    filas = math.ceil(len(etiquetas) / ncol)
    base = 0.07 + 0.085 * filas          # espacio que ocupa la leyenda (crece con sus filas)
    ax = fig.add_axes([0.04, base, 0.92, 0.97 - base])
    cunas, _ = ax.pie(valores, colors=colores, startangle=90, counterclock=False,
                      wedgeprops=dict(width=0.32, edgecolor=tema.TARJETA, linewidth=2.5))
    ax.set(xlim=(-1.15, 1.15), ylim=(-1.15, 1.15))
    ax.set_aspect("equal")
    valor = ax.text(0, 0.07, texto_centro, ha="center", va="center", fontsize=21,
                    fontweight="bold", color=tema.TEXTO)
    nombre = ax.text(0, -0.23, titulo_centro, ha="center", va="center", fontsize=8,
                     color=tema.TEXTO_MEDIO)
    fig.legend(cunas, etiquetas, loc="lower center", frameon=False, fontsize=9,
               ncol=ncol, labelcolor=tema.TEXTO_MEDIO, handlelength=1, handleheight=1,
               columnspacing=1.4, borderaxespad=0.5)

    textos = [f"{etiquetas[i]}\n{valores[i]} · {valores[i] / total:.0%}"
              for i in range(len(valores))]

    def resaltar(i):
        cunas[i].set_radius(1.07)
        valor.set_text(f"{valores[i] / total:.0%}")
        nombre.set_text(etiquetas[i])

    def restaurar(i):
        cunas[i].set_radius(1.0)
        valor.set_text(texto_centro)
        nombre.set_text(titulo_centro)

    _conectar(fig, ax, cunas, textos, resaltar, restaurar, al_clic)
    return {}


def barras(fig, etiquetas, valores, colores, textos, maximo=None, marcas=None,
           referencia=None, formato="{:.2f}", al_clic=None):
    """Barras verticales con valor encima, línea de referencia opcional y tooltip."""
    _preparar(fig)
    if not valores:
        return _sin_datos(fig)
    ancho = 0.80 if referencia is not None else 0.87
    ax = _ejes(fig, [0.10, 0.17, ancho, 0.73])
    posiciones = list(range(len(valores)))
    rectangulos = list(ax.bar(posiciones, valores, color=colores, width=0.62, alpha=0.9))
    maximo = maximo or max(max(valores) * 1.3, 1)
    ax.set_ylim(0, maximo)
    ax.set_xlim(-0.6, len(valores) - 0.4)
    ax.set_xticks(posiciones)
    ax.set_xticklabels(etiquetas)
    if marcas is not None:
        ax.set_yticks(marcas)
    else:
        ax.yaxis.set_major_locator(MaxNLocator(integer=formato == "{:.0f}", nbins=5))
    if referencia is not None:
        ax.axhline(referencia, color=tema.AMARILLO, linestyle="--", linewidth=1.1, alpha=0.8)
        _etiqueta_referencia(ax, referencia, len(valores))
    numeros = [ax.text(i, v + maximo * 0.02, formato.format(v), ha="center", va="bottom",
                       color=tema.TEXTO, fontsize=9, fontweight="bold")
               for i, v in enumerate(valores)]

    def resaltar(i):
        rectangulos[i].set_alpha(1)
        rectangulos[i].set_edgecolor("white")
        rectangulos[i].set_linewidth(1.5)

    def restaurar(i):
        rectangulos[i].set_alpha(0.9)
        rectangulos[i].set_linewidth(0)

    _conectar(fig, ax, rectangulos, textos, resaltar, restaurar, al_clic)
    return {"barras": [(r, v, False) for r, v in zip(rectangulos, valores)],
            "etiquetas": numeros}


def barras_horizontales(fig, etiquetas, valores, colores, textos, maximo=5.0,
                        formato="{:.2f}", al_clic=None):
    """Ranking en barras horizontales (por ejemplo, los mejores estudiantes)."""
    _preparar(fig)
    if not valores:
        return _sin_datos(fig)
    ax = _ejes(fig, [0.37, 0.06, 0.60, 0.88], grilla=None)
    ax.spines["bottom"].set_visible(False)
    posiciones = list(range(len(valores)))
    rectangulos = list(ax.barh(posiciones, valores, color=colores, height=0.58, alpha=0.9))
    ax.set_xlim(0, maximo * 1.18)
    ax.set_ylim(len(valores) - 0.4, -0.6)
    ax.set_xticks([])
    ax.set_yticks(posiciones)
    ax.set_yticklabels(etiquetas, color=tema.TEXTO_MEDIO, fontsize=9)
    numeros = [ax.text(v + maximo * 0.02, i, formato.format(v), va="center", ha="left",
                       color=tema.TEXTO, fontsize=9, fontweight="bold")
               for i, v in enumerate(valores)]

    def resaltar(i):
        rectangulos[i].set_alpha(1)
        rectangulos[i].set_edgecolor("white")
        rectangulos[i].set_linewidth(1.5)

    def restaurar(i):
        rectangulos[i].set_alpha(0.9)
        rectangulos[i].set_linewidth(0)

    _conectar(fig, ax, rectangulos, textos, resaltar, restaurar, al_clic)
    return {"barras": [(r, v, True) for r, v in zip(rectangulos, valores)],
            "etiquetas": numeros}


def linea(fig, etiquetas, valores, color, textos, referencia=3.0):
    """Línea con área sombreada y puntos interactivos (evolución por corte)."""
    _preparar(fig)
    if not any(valores):
        return _sin_datos(fig)
    ancho = 0.70 if referencia is not None else 0.86
    ax = _ejes(fig, [0.10, 0.17, ancho, 0.73])
    xs = list(range(len(valores)))
    ax.fill_between(xs, valores, 0, color=color, alpha=0.14)
    ax.plot(xs, valores, color=color, linewidth=2.4, zorder=3)
    if referencia is not None:
        ax.axhline(referencia, color=tema.AMARILLO, linestyle="--", linewidth=1.1, alpha=0.8)
        _etiqueta_referencia(ax, referencia, len(valores))
    puntos = []
    for x, v in zip(xs, valores):
        punto, = ax.plot([x], [v], "o", color=color, markeredgecolor=tema.TARJETA,
                         markeredgewidth=2, markersize=9, zorder=4)
        punto.set_pickradius(12)
        puntos.append(punto)
        ax.text(x, v + 0.28, f"{v:.2f}", ha="center", va="bottom", color=tema.TEXTO,
                fontsize=9, fontweight="bold")
    ax.set_ylim(0, 5.6)
    ax.set_yticks(range(6))
    ax.set_xlim(-0.4, len(valores) - 0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels(etiquetas)

    def resaltar(i):
        puntos[i].set_markersize(13)

    def restaurar(i):
        puntos[i].set_markersize(9)

    _conectar(fig, ax, puntos, textos, resaltar, restaurar)
    return {}

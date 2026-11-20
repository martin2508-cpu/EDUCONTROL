"""Componentes visuales reutilizables: tarjetas, gráficas, tablas, botones y avisos."""
from datetime import datetime
from tkinter import ttk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from interfaz import tema, iconos

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_hoy():
    hoy = datetime.now()
    return f"{DIAS[hoy.weekday()].capitalize()}, {hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}"


# ----------------------------------------------------------------------
# Interacción
# ----------------------------------------------------------------------
def _dentro(widget, contenedor):
    if widget is None:
        return False
    ruta, base = str(widget), str(contenedor)
    return ruta == base or ruta.startswith(base + ".")


def resaltar_al_pasar(tarjeta, color_hover, color_normal=tema.BORDE):
    """Cambia el borde de la tarjeta cuando el cursor está encima."""
    def entrar(_evento):
        tarjeta.configure(border_color=color_hover)

    def salir(_evento):
        x, y = tarjeta.winfo_pointerxy()
        if not _dentro(tarjeta.winfo_containing(x, y), tarjeta):
            tarjeta.configure(border_color=color_normal)

    tarjeta.bind("<Enter>", entrar, add="+")
    tarjeta.bind("<Leave>", salir, add="+")


def hacer_clicable(widget, accion):
    """Hace que el widget y todo lo que contiene respondan al clic."""
    widget.bind("<Button-1>", lambda _evento: accion(), add="+")
    for hijo in widget.winfo_children():
        if not isinstance(hijo, (ctk.CTkButton, ctk.CTkEntry, ctk.CTkOptionMenu)):
            hacer_clicable(hijo, accion)


# ----------------------------------------------------------------------
# Botones, chips y avisos
# ----------------------------------------------------------------------
ESTILOS_BOTON = {
    "primario": (tema.ACENTO, tema.ACENTO_HOVER, "#FFFFFF"),
    "secundario": (tema.GRIS, tema.GRIS_HOVER, tema.TEXTO),
    "peligro": (tema.PELIGRO, tema.PELIGRO_HOVER, "#FFFFFF"),
    "exito": (tema.mezclar(tema.OK, tema.TARJETA, 0.25), tema.mezclar(tema.OK, tema.TARJETA, 0.4), tema.OK),
}


def boton(padre, texto, comando, estilo="primario", ancho=None, alto=36):
    fondo, hover, letra = ESTILOS_BOTON[estilo]
    opciones = {"width": ancho} if ancho else {}
    return ctk.CTkButton(padre, text=texto, command=comando, height=alto, corner_radius=tema.radio(9),
                         fg_color=fondo, hover_color=hover, text_color=letra,
                         font=tema.fuente(12, True), **opciones)


def insignia(padre, texto, color):
    """Pequeña etiqueta de color (chip)."""
    return ctk.CTkLabel(padre, text=f"  {texto}  ", height=24, corner_radius=tema.radio(8),
                        fg_color=tema.mezclar(color, tema.TARJETA, 0.2), bg_color=tema.TARJETA,
                        text_color=color, font=tema.fuente(11, True))


def mostrar_aviso(ventana, texto, exito=True):
    """Aviso flotante (toast) que desaparece solo; reemplaza a los cuadros de 'Aceptar'."""
    color = tema.OK if exito else tema.ERROR
    aviso = ctk.CTkLabel(ventana, text=f"  {'✓' if exito else '✕'}   {texto}   ", height=42,
                         corner_radius=tema.radio(12), fg_color=color, bg_color=tema.FONDO, text_color="#06210F",
                         font=tema.fuente(12, True))
    aviso.place(relx=1.0, rely=1.0, x=-28, y=-28, anchor="se")
    aviso.after(2600, aviso.destroy)


# ----------------------------------------------------------------------
# Tarjetas
# ----------------------------------------------------------------------
class TarjetaKPI(ctk.CTkFrame):
    """Indicador principal: título, ícono, valor grande y detalle (con barra opcional)."""

    def __init__(self, padre, titulo, valor, color, icono, detalle="", progreso=None,
                 fondo=tema.FONDO):
        # bg_color explícito: así las esquinas redondeadas siempre usan el color real del
        # fondo y no uno "adivinado" por CustomTkinter (causa de las esquinas oscuras).
        super().__init__(padre, fg_color=tema.TARJETA, bg_color=fondo, corner_radius=tema.radio(14),
                         border_width=1, border_color=tema.BORDE)
        cabecera = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        cabecera.pack(fill="x", padx=18, pady=(16, 0))
        ctk.CTkLabel(cabecera, text=titulo.upper(), text_color=tema.TEXTO_SUAVE,
                     font=tema.fuente(11, True)).pack(side="left")
        ctk.CTkLabel(cabecera, text="", width=40, height=40, fg_color=tema.TARJETA, bg_color=tema.TARJETA,
                     image=iconos.insignia(icono, color, tema.mezclar(color, tema.TARJETA, 0.2),
                                           lado=40, fondo_esquina=tema.TARJETA)).pack(side="right")
        ctk.CTkLabel(self, text=str(valor), text_color=color,
                     font=tema.fuente(32, True), anchor="w").pack(fill="x", padx=18, pady=(2, 0))
        if progreso is not None:
            barra = ctk.CTkProgressBar(self, height=8, corner_radius=tema.radio(4), fg_color=tema.BORDE,
                                   progress_color=color)
            barra.set(max(0, min(1, progreso)))
            barra.pack(fill="x", padx=18, pady=(4, 0))
        ctk.CTkLabel(self, text=detalle, text_color=tema.TEXTO_MEDIO, font=tema.fuente(11),
                     anchor="w").pack(fill="x", padx=18, pady=(5, 16))
        resaltar_al_pasar(self, color)


class TarjetaGrafica(ctk.CTkFrame):
    """Tarjeta con título que contiene una gráfica de Matplotlib embebida."""

    def __init__(self, padre, titulo, subtitulo="", alto=300, fondo=tema.FONDO):
        super().__init__(padre, fg_color=tema.TARJETA, bg_color=fondo, corner_radius=tema.radio(14),
                         border_width=1, border_color=tema.BORDE, height=alto)
        self.pack_propagate(False)
        ctk.CTkLabel(self, text=titulo, font=tema.fuente(14, True), text_color=tema.TEXTO,
                     anchor="w").pack(fill="x", padx=18, pady=(14, 0))
        if subtitulo:
            ctk.CTkLabel(self, text=subtitulo, font=tema.fuente(11), text_color=tema.TEXTO_MEDIO,
                         anchor="w").pack(fill="x", padx=18)
        self.figura = Figure(figsize=(3, 2.4), dpi=100, facecolor=tema.TARJETA)
        self.lienzo = FigureCanvasTkAgg(self.figura, master=self)
        widget = self.lienzo.get_tk_widget()
        widget.configure(bg=tema.TARJETA, highlightthickness=0, bd=0)
        widget.pack(fill="both", expand=True, padx=10, pady=(4, 16))

    def dibujar(self, constructor, **datos):
        """Ejecuta una función de graficas.py y, si hay barras, las anima al crecer."""
        info = constructor(self.figura, **datos) or {}
        barras = info.get("barras", [])
        for rectangulo, _final, horizontal in barras:
            (rectangulo.set_width if horizontal else rectangulo.set_height)(0)
        for texto in info.get("etiquetas", []):
            texto.set_visible(False)
        self.lienzo.draw()
        if barras:
            self._animar(info, 0)

    def _animar(self, info, paso, total=14):
        try:
            if not self.winfo_exists():
                return
            progreso = 1 - (1 - (paso + 1) / total) ** 3      # crece rápido y frena al final
            for rectangulo, final, horizontal in info["barras"]:
                (rectangulo.set_width if horizontal else rectangulo.set_height)(final * progreso)
            if paso + 1 >= total:
                for texto in info.get("etiquetas", []):
                    texto.set_visible(True)
            else:
                self.after(22, lambda: self._animar(info, paso + 1, total))
            self.lienzo.draw_idle()
        except Exception:      # la ventana pudo cerrarse durante la animación
            pass


# ----------------------------------------------------------------------
# Tablas
# ----------------------------------------------------------------------
def configurar_estilos_tabla():
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("Edu.Treeview", background=tema.TARJETA, foreground="#E8EEF8",
                     fieldbackground=tema.TARJETA, rowheight=34, borderwidth=0,
                     font=tema.fuente(10))
    estilo.layout("Edu.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    estilo.configure("Edu.Treeview.Heading", background="#24344D", foreground="#FFFFFF",
                     relief="flat", borderwidth=0, padding=(10, 9), font=tema.fuente(10, True))
    estilo.map("Edu.Treeview.Heading", background=[("active", "#2D4263")])
    estilo.map("Edu.Treeview", background=[("selected", tema.ACENTO)],
               foreground=[("selected", "#FFFFFF")])
    estilo.configure("Edu.Vertical.TScrollbar", background=tema.GRIS, troughcolor=tema.TARJETA,
                     bordercolor=tema.TARJETA, arrowcolor="#DCE6F5", relief="flat")


def crear_tabla(padre, columnas, anchos=None, altura=12, expandir=True):
    marco = ctk.CTkFrame(padre, fg_color=tema.TARJETA, bg_color=tema.FONDO, corner_radius=tema.radio(12),
                         border_width=1, border_color=tema.BORDE)
    marco.pack(fill="both", expand=expandir, pady=(8, 0))
    tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=altura,
                         style="Edu.Treeview", selectmode="browse")
    for i, columna in enumerate(columnas):
        tabla.heading(columna, text=columna)
        tabla.column(columna, width=(anchos[i] if anchos else 140), anchor="w")
    scroll = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview,
                           style="Edu.Vertical.TScrollbar")
    tabla.configure(yscrollcommand=scroll.set)
    tabla.tag_configure("par", background=tema.TARJETA)
    tabla.tag_configure("impar", background=tema.TARJETA_2)
    tabla.tag_configure("aprobado", foreground=tema.OK)
    tabla.tag_configure("reprobado", foreground=tema.ERROR)
    tabla.tag_configure("aviso", foreground=tema.AMARILLO)
    tabla.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
    scroll.pack(side="right", fill="y", padx=(0, 6), pady=8)
    return tabla


def llenar_tabla(tabla, filas, iids=None, etiqueta=None):
    """Reemplaza el contenido de la tabla. `iids` identifica cada fila de forma segura
    (así no dependemos de los textos mostrados) y `etiqueta` colorea según la fila."""
    tabla.delete(*tabla.get_children())
    for i, fila in enumerate(filas):
        tags = ["par" if i % 2 == 0 else "impar"]
        if etiqueta and etiqueta(fila):
            tags.append(etiqueta(fila))
        opciones = {"iid": iids[i]} if iids else {}
        tabla.insert("", "end", values=fila, tags=tags, **opciones)


def estado_general(promedio, cantidad):
    """Texto y etiqueta de color del estado global de un estudiante."""
    if cantidad == 0:
        return "Sin notas", "aviso"
    if promedio >= 3.0:
        return "Aprobando", "aprobado"
    return "En riesgo", "reprobado"


# Color de cada estado en las tablas (las etiquetas se definen en crear_tabla)
ETIQUETA_ESTADO = {"Aprobado": "aprobado", "Reprobado": "reprobado", "Aprobando": "aprobado",
                   "En riesgo": "reprobado", "Sin notas": "aviso"}

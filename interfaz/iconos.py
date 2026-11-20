"""Iconos vectoriales dibujados con Pillow.

Antes se usaban símbolos de texto (♙ ♧ ▤ ✎ ▥ ★) que dependían de la fuente instalada:
salían diminutos, de tamaños distintos y desalineados. Aquí cada icono se dibuja
a 8x y se reduce, así queda nítido y con el mismo tamaño en cualquier equipo.
También se dibujan las "insignias" (icono dentro de un cuadrado redondeado) con
esquinas realmente transparentes, para que no queden restos oscuros en los bordes.
"""
import math

import customtkinter as ctk
from PIL import Image, ImageDraw

from interfaz import tema

_ESCALA = 8          # supermuestreo para suavizar bordes
_BASE = 24           # los iconos se diseñan sobre una rejilla de 24 x 24
_cache = {}


def _rgb(color):
    return tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))


def _lienzo(lado=_BASE):
    tam = lado * _ESCALA
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def _p(*puntos):
    """Convierte coordenadas de la rejilla de 24 al lienzo ampliado."""
    return [(x * _ESCALA, y * _ESCALA) for x, y in puntos]


def _dibujar(nombre, d, c):
    s = _ESCALA
    if nombre == "inicio":
        d.polygon(_p((12, 3), (22, 12), (19.5, 12), (19.5, 20), (4.5, 20), (4.5, 12), (2, 12)), fill=c)
        d.rectangle([10 * s, 14 * s, 14 * s, 20 * s], fill=(0, 0, 0, 0))
    elif nombre == "estudiante":          # birrete
        d.polygon(_p((12, 4), (23, 9.5), (12, 15), (1, 9.5)), fill=c)
        d.polygon(_p((6, 13), (12, 16), (18, 13), (18, 17.5), (12, 20.5), (6, 17.5)), fill=c)
        d.rectangle([21.2 * s, 10 * s, 22.2 * s, 17 * s], fill=c)
    elif nombre == "profesor":            # persona
        d.ellipse([7.5 * s, 3 * s, 16.5 * s, 12 * s], fill=c)
        d.rounded_rectangle([3.5 * s, 14 * s, 20.5 * s, 21 * s], radius=4 * s, fill=c)
    elif nombre == "asignatura":          # libro abierto
        d.polygon(_p((2, 5), (11, 6.5), (11, 20), (2, 18.5)), fill=c)
        d.polygon(_p((22, 5), (13, 6.5), (13, 20), (22, 18.5)), fill=c)
    elif nombre == "calificacion":        # lápiz
        d.polygon(_p((16.5, 2.5), (21.5, 7.5), (8.5, 20.5), (3, 21), (3.5, 15.5)), fill=c)
        d.line(_p((4, 21.5), (21, 21.5)), fill=c, width=int(1.6 * s))
        d.polygon(_p((15.2, 3.8), (16.5, 2.5), (21.5, 7.5), (20.2, 8.8)), fill=(0, 0, 0, 0))
        d.line(_p((15.9, 3.2), (20.8, 8.1)), fill=(0, 0, 0, 0), width=int(1.0 * s))
    elif nombre == "reportes":            # barras
        d.rounded_rectangle([3 * s, 12 * s, 8 * s, 21 * s], radius=1.2 * s, fill=c)
        d.rounded_rectangle([9.5 * s, 4 * s, 14.5 * s, 21 * s], radius=1.2 * s, fill=c)
        d.rounded_rectangle([16 * s, 9 * s, 21 * s, 21 * s], radius=1.2 * s, fill=c)
    elif nombre == "estrella":
        puntos = []
        for i in range(10):
            radio = 10 if i % 2 == 0 else 4.4
            ang = -math.pi / 2 + i * math.pi / 5
            puntos.append((12 + radio * math.cos(ang), 12.8 + radio * math.sin(ang)))
        d.polygon(_p(*puntos), fill=c)
    elif nombre == "marca":               # letra E del logo, hecha con rectángulos
        d.rounded_rectangle([5 * s, 4 * s, 9.2 * s, 20 * s], radius=1 * s, fill=c)
        for y0, y1, x1 in ((4, 7.4, 19), (10.3, 13.7, 17), (16.6, 20, 19)):
            d.rounded_rectangle([5 * s, y0 * s, x1 * s, y1 * s], radius=1 * s, fill=c)


def icono(nombre, color, tam=20):
    """Devuelve un CTkImage cuadrado con el icono `nombre` del color indicado."""
    clave = ("i", nombre, color, tam)
    if clave not in _cache:
        img, d = _lienzo()
        _dibujar(nombre, d, _rgb(color) + (255,))
        img = img.resize((tam * 4, tam * 4), Image.LANCZOS)
        _cache[clave] = ctk.CTkImage(light_image=img, dark_image=img, size=(tam, tam))
    return _cache[clave]


def insignia(nombre, color, fondo_insignia, lado=38, icono_tam=0.56, radio=11,
             fondo_esquina=None):
    """Icono dentro de un cuadrado redondeado con esquinas transparentes."""
    clave = ("b", nombre, color, fondo_insignia, lado, fondo_esquina)
    if clave not in _cache:
        k = 4
        grande = lado * k
        esquina = _rgb(fondo_esquina) + (255,) if fondo_esquina else (0, 0, 0, 0)
        base = Image.new("RGBA", (grande, grande), esquina)
        ImageDraw.Draw(base).rounded_rectangle([0, 0, grande - 1, grande - 1],
                                               radius=int(radio * k * tema.REDONDEO),
                                               fill=_rgb(fondo_insignia) + (255,))
        lado_icono = int(grande * icono_tam)
        img, d = _lienzo()
        _dibujar(nombre, d, _rgb(color) + (255,))
        img = img.resize((lado_icono, lado_icono), Image.LANCZOS)
        desfase = (grande - lado_icono) // 2
        base.alpha_composite(img, (desfase, desfase))
        _cache[clave] = ctk.CTkImage(light_image=base, dark_image=base, size=(lado, lado))
    return _cache[clave]


def logo(lado=44):
    """Logo de EDUCONTROL: cuadrado azul con una E blanca."""
    return insignia("marca", "#FFFFFF", tema.ACENTO, lado=lado, icono_tam=0.62, radio=12,
                    fondo_esquina=tema.PANEL)

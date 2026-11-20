"""Colores, fuentes y utilidades visuales compartidas por toda la interfaz."""

FONDO = "#0B1220"        # fondo general (azul marino)
PANEL = "#111C2E"        # barra lateral y diálogos
TARJETA = "#172235"      # tarjetas y paneles (gris azulado)
TARJETA_2 = "#1C2A42"    # filas alternas y bloques internos
CAMPO = "#0F1A2B"        # campos de texto
BORDE = "#263A57"
TEXTO = "#F3F6FC"
TEXTO_MEDIO = "#BFCCE0"
TEXTO_SUAVE = "#A6B7D2"

ACENTO = "#2563EB"       # azul eléctrico
ACENTO_HOVER = "#1D4ED8"
GRIS = "#263A57"
GRIS_HOVER = "#344D70"
PELIGRO = "#8B2C3A"
PELIGRO_HOVER = "#A93648"

AZUL = "#4F8CFF"
MORADO = "#A78BFA"
VERDE = "#22C7A5"
AMARILLO = "#F5B942"
OK = "#22C55E"           # detalles verdes (aprobado)
ERROR = "#F87171"        # reprobado
ROSA = "#F472B6"
CIELO = "#38BDF8"
NARANJA = "#FB923C"

PALETA = [AZUL, VERDE, MORADO, AMARILLO, ROSA, CIELO, NARANJA]
FUENTE = "Segoe UI"


def fuente(tamano, negrita=False):
    return (FUENTE, tamano, "bold") if negrita else (FUENTE, tamano)


def color_de(indice):
    """Devuelve un color de la paleta; se usa para que cada asignatura tenga el suyo."""
    return PALETA[indice % len(PALETA)]


def mezclar(color, fondo=TARJETA, proporcion=0.18):
    """Mezcla `color` sobre `fondo`: sirve para crear fondos suaves de iconos y chips."""
    c = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    f = [int(fondo[i:i + 2], 16) for i in (1, 3, 5)]
    mezcla = [round(f[k] + (c[k] - f[k]) * proporcion) for k in range(3)]
    return "#%02X%02X%02X" % tuple(mezcla)


# Redondeo de esquinas. 0 = esquinas rectas (no puede dejar "cuadritos" en ningún equipo).
# Si en tu pantalla se ven bien las esquinas redondeadas, sube este valor a 1.0.
REDONDEO = 0.0


def radio(px):
    """Radio de esquina escalado por REDONDEO (con 0 todo queda recto)."""
    return round(px * REDONDEO)

"""Vista del dashboard: indicadores, gráficas interactivas y alertas."""
import customtkinter as ctk

from interfaz import tema, graficas, componentes as comp

COLUMNAS = 12     # la rejilla del dashboard tiene 12 columnas iguales


def colocar(rejilla, widget, fila, columna, ancho):
    """Ubica un widget en la rejilla ocupando `ancho` columnas y con separación uniforme."""
    izquierda = 0 if columna == 0 else 6
    derecha = 0 if columna + ancho == COLUMNAS else 6
    widget.grid(row=fila, column=columna, columnspan=ancho, sticky="nsew",
                padx=(izquierda, derecha), pady=6)


class VistaDashboard:
    """Mixin de VentanaPrincipal: construye el panel general."""

    def mostrar_dashboard(self):
        self._marcar_nav("Dashboard")
        self._limpiar(desplazable=True)
        self._encabezado("Panel general", f"Resumen del estado académico  ·  {comp.fecha_hoy()}")
        g = self.gestor

        rejilla = ctk.CTkFrame(self.contenido, fg_color=tema.FONDO, corner_radius=0)
        rejilla.pack(fill="x")
        for columna in range(COLUMNAS):
            rejilla.grid_columnconfigure(columna, weight=1, uniform="dash")

        # ---- Fila 1: indicadores -------------------------------------------------
        rendimiento = g.rendimiento_estudiantes()
        con_notas = sum(1 for _, _, cantidad in rendimiento if cantidad)
        docentes_activos = len({a.profesor.identificacion for a in g.asignaturas if a.profesor})
        horas = sum(a.intensidad_horaria for a in g.asignaturas)
        indicadores = [
            ("Estudiantes", len(g.estudiantes), tema.AZUL, "estudiante", f"{con_notas} con notas registradas", None),
            ("Profesores", len(g.profesores), tema.MORADO, "profesor", f"{docentes_activos} con asignaturas a cargo", None),
            ("Asignaturas", len(g.asignaturas), tema.VERDE, "asignatura", f"{horas} horas de intensidad en total", None),
            ("Promedio general", f"{g.promedio_general():.2f}", tema.AMARILLO, "estrella",
             "Mínimo para aprobar: 3.0", g.promedio_general() / 5),
        ]
        for i, (titulo, valor, color, icono, detalle, progreso) in enumerate(indicadores):
            colocar(rejilla, comp.TarjetaKPI(rejilla, titulo, valor, color, icono, detalle, progreso),
                     0, i * 3, 3)

        # ---- Fila 2: aprobación + promedio por asignatura ------------------------
        aprobados, reprobados = g.contar_aprobados(), g.contar_reprobados()
        tarjeta = comp.TarjetaGrafica(rejilla, "Aprobados vs reprobados",
                                      f"{aprobados} de {aprobados + reprobados} registros aprobados")
        colocar(rejilla, tarjeta, 1, 0, 4)
        tarjeta.dibujar(graficas.dona, etiquetas=["Aprobados", "Reprobados"],
                        valores=[aprobados, reprobados], colores=[tema.OK, tema.ERROR],
                        titulo_centro="de aprobación", texto_centro=f"{g.porcentaje_aprobacion():.0f}%")

        datos = g.promedio_por_asignatura()
        tarjeta = comp.TarjetaGrafica(rejilla, "Promedio por asignatura",
                                      "Línea punteada = mínimo para aprobar · clic en una barra para abrirla")
        colocar(rejilla, tarjeta, 1, 4, 8)
        codigos = [a.codigo for a, _, _ in datos]
        tarjeta.dibujar(
            graficas.barras, etiquetas=codigos, valores=[p for _, p, _ in datos],
            colores=[tema.color_de(g.asignaturas.index(a)) for a, _, _ in datos],
            textos=[f"{a.nombre}\nDocente: {a.profesor.nombre if a.profesor else 'Sin asignar'}\n"
                    f"Promedio {p:.2f} · {n} registros" for a, p, n in datos],
            maximo=5.6, marcas=range(6), referencia=3.0,
            al_clic=lambda i: self.ver_asignatura(codigos[i]))

        # ---- Fila 3: distribución, evolución por nota y programas ----------------
        rangos, conteos = g.distribucion_promedios()
        tarjeta = comp.TarjetaGrafica(rejilla, "Distribución de promedios", "Registros por rango de nota")
        colocar(rejilla, tarjeta, 2, 0, 4)
        tarjeta.dibujar(graficas.barras, etiquetas=rangos, valores=conteos,
                        colores=[tema.ERROR] * 3 + [tema.OK] * 2,
                        textos=[f"Promedios entre {r}\n{c} registros" for r, c in zip(rangos, conteos)],
                        formato="{:.0f}")

        tarjeta = comp.TarjetaGrafica(rejilla, "Promedio por nota", "¿Mejora el grupo de la nota 1 a la 3?")
        colocar(rejilla, tarjeta, 2, 4, 4)
        por_nota = g.promedio_por_nota()
        tarjeta.dibujar(graficas.linea, etiquetas=["Nota 1", "Nota 2", "Nota 3"], valores=por_nota,
                        color=tema.AZUL,
                        textos=[f"Promedio de la nota {i + 1}\n{v:.2f}" for i, v in enumerate(por_nota)])

        programas = g.estudiantes_por_programa()
        tarjeta = comp.TarjetaGrafica(rejilla, "Estudiantes por programa", "Distribución de la matrícula")
        colocar(rejilla, tarjeta, 2, 8, 4)
        tarjeta.dibujar(graficas.dona, etiquetas=[graficas.abreviar(p) for p, _ in programas],
                        valores=[n for _, n in programas],
                        colores=[tema.color_de(i) for i in range(len(programas))],
                        titulo_centro="estudiantes", texto_centro=str(len(g.estudiantes)), columnas=2)

        # ---- Fila 4: ranking y alertas -------------------------------------------
        mejores = g.mejores_estudiantes(5)
        tarjeta = comp.TarjetaGrafica(rejilla, "Mejores 5 estudiantes", "Promedio general de cada uno", alto=290)
        colocar(rejilla, tarjeta, 3, 0, 6)
        tarjeta.dibujar(graficas.barras_horizontales, etiquetas=[e.nombre for e, _, _ in mejores],
                        valores=[p for _, p, _ in mejores], colores=[tema.VERDE] * len(mejores),
                        textos=[f"{e.nombre}\n{e.programa}\nPromedio {p:.2f} · {c} asignaturas"
                                for e, p, c in mejores])
        colocar(rejilla, self._bloque_riesgo(rejilla), 3, 6, 6)

        # ---- Tabla de rendimiento (se conserva del diseño anterior) --------------
        ctk.CTkLabel(self.contenido, text="Rendimiento de estudiantes", font=tema.fuente(17, True),
                     text_color=tema.TEXTO).pack(anchor="w", pady=(20, 0))
        tabla = comp.crear_tabla(self.contenido, ("Estudiante", "Programa", "Promedio", "Registros", "Estado"),
                                 (230, 230, 100, 100, 120), altura=7, expandir=False)
        filas = [(e.nombre, e.programa, f"{p:.2f}", c, comp.estado_general(p, c)[0])
                 for e, p, c in rendimiento[:10]]
        comp.llenar_tabla(tabla, filas, [e.identificacion for e, _, _ in rendimiento[:10]],
                          etiqueta=lambda fila: comp.ETIQUETA_ESTADO.get(fila[-1]))
        if not g.estudiantes:
            ctk.CTkLabel(self.contenido, text="Aún no hay estudiantes. Empieza registrando uno.",
                         text_color=tema.TEXTO_SUAVE).pack(anchor="w", pady=8)

    def _bloque_riesgo(self, padre):
        """Lista de estudiantes con promedio por debajo de 3.0."""
        riesgo = self.gestor.estudiantes_en_riesgo()
        tarjeta = ctk.CTkFrame(padre, fg_color=tema.TARJETA, corner_radius=tema.radio(14), border_width=1,
                               border_color=tema.BORDE, height=290, bg_color=tema.FONDO)
        tarjeta.pack_propagate(False)
        cabecera = ctk.CTkFrame(tarjeta, fg_color="transparent", corner_radius=0)
        cabecera.pack(fill="x", padx=18, pady=(14, 0))
        ctk.CTkLabel(cabecera, text="Estudiantes en riesgo", font=tema.fuente(14, True),
                     text_color=tema.TEXTO).pack(side="left")
        comp.insignia(cabecera, str(len(riesgo)), tema.ERROR if riesgo else tema.OK).pack(side="right")
        ctk.CTkLabel(tarjeta, text="Promedio por debajo de 3.0", font=tema.fuente(11),
                     text_color=tema.TEXTO_MEDIO, anchor="w").pack(fill="x", padx=18)
        if not riesgo:
            ctk.CTkLabel(tarjeta, text="✓  Nadie está en riesgo por ahora",
                         text_color=tema.OK, font=tema.fuente(12, True)).pack(expand=True)
            return tarjeta
        for estudiante, promedio, cantidad in riesgo[:4]:
            fila = ctk.CTkFrame(tarjeta, fg_color=tema.TARJETA_2, bg_color=tema.TARJETA, corner_radius=tema.radio(10))
            fila.pack(fill="x", padx=14, pady=(8, 0))
            avatar = ctk.CTkFrame(fila, width=36, height=36, corner_radius=tema.radio(18),
                                  fg_color=tema.mezclar(tema.ERROR, tema.TARJETA_2, 0.3),
                                  bg_color=tema.TARJETA_2)
            avatar.pack(side="left", padx=(10, 10), pady=8)
            avatar.pack_propagate(False)
            ctk.CTkLabel(avatar, text=estudiante.nombre[0], text_color=tema.ERROR,
                         font=tema.fuente(13, True)).pack(expand=True)
            textos = ctk.CTkFrame(fila, fg_color="transparent", corner_radius=0)
            textos.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(textos, text=estudiante.nombre, font=tema.fuente(12, True),
                         text_color=tema.TEXTO, anchor="w").pack(fill="x")
            ctk.CTkLabel(textos, text=f"{estudiante.programa} · {cantidad} asignaturas",
                         font=tema.fuente(11), text_color=tema.TEXTO_MEDIO, anchor="w").pack(fill="x")
            ctk.CTkLabel(fila, text=f"{promedio:.2f}", font=tema.fuente(16, True),
                         text_color=tema.ERROR).pack(side="right", padx=14)
        if len(riesgo) > 4:
            ctk.CTkLabel(tarjeta, text=f"y {len(riesgo) - 4} más en la sección Reportes",
                         font=tema.fuente(10), text_color=tema.TEXTO_SUAVE).pack(pady=(8, 0))
        return tarjeta

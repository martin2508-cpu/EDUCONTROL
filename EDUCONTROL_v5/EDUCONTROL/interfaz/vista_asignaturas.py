"""Vista de asignaturas: una tarjeta por materia y una página de detalle con todos sus datos."""
import customtkinter as ctk
from tkinter import messagebox

from interfaz import tema, graficas, componentes as comp
from interfaz.vista_dashboard import colocar, COLUMNAS


class VistaAsignaturas:
    """Mixin de VentanaPrincipal: lista de asignaturas y detalle de cada una."""

    # ------------------------------------------------------------------
    # Lista: cada asignatura tiene su propia tarjeta
    # ------------------------------------------------------------------
    def vista_asignaturas(self):
        self._marcar_nav("Asignaturas")
        self._limpiar(desplazable=True)
        g = self.gestor
        self._encabezado("Asignaturas",
                         "Cada asignatura tiene su propio espacio: docente, estudiantes y resultados.",
                         [("+ Nueva asignatura", lambda: self._form_asignatura(despues=pintar), "primario")])

        barra = ctk.CTkFrame(self.contenido, fg_color="transparent", corner_radius=0)
        barra.pack(fill="x")
        caja = ctk.CTkEntry(barra, width=300, height=38, placeholder_text="Buscar por nombre, código o docente…",
                            fg_color=tema.CAMPO, border_color=tema.BORDE, corner_radius=tema.radio(10))
        caja.pack(side="left")
        caja.bind("<KeyRelease>", lambda _evento: pintar())
        contador = ctk.CTkLabel(barra, text="", text_color=tema.TEXTO_SUAVE, font=tema.fuente(11))
        contador.pack(side="left", padx=14)

        rejilla = ctk.CTkFrame(self.contenido, fg_color="transparent", corner_radius=0)
        rejilla.pack(fill="x", pady=(8, 0))
        rejilla.grid_columnconfigure(0, weight=1, uniform="asig")
        rejilla.grid_columnconfigure(1, weight=1, uniform="asig")

        def pintar():
            for hijo in rejilla.winfo_children():
                hijo.destroy()
            filtro = caja.get().strip().lower()
            visibles = [a for a in g.asignaturas if filtro in
                        f"{a.codigo} {a.nombre} {a.profesor.nombre if a.profesor else ''}".lower()]
            horas = sum(a.intensidad_horaria for a in visibles)
            contador.configure(text=f"{len(visibles)} de {len(g.asignaturas)} asignaturas  ·  {horas} horas")
            if not visibles:
                ctk.CTkLabel(rejilla, text="No hay asignaturas para mostrar.",
                             text_color=tema.TEXTO_SUAVE).grid(row=0, column=0, pady=30)
                return
            for i, asignatura in enumerate(visibles):
                tarjeta = self._tarjeta_asignatura(rejilla, asignatura, pintar)
                tarjeta.grid(row=i // 2, column=i % 2, sticky="nsew", pady=7,
                             padx=(0, 7) if i % 2 == 0 else (7, 0))

        pintar()

    def _tarjeta_asignatura(self, padre, asignatura, despues):
        g = self.gestor
        color = tema.color_de(g.asignaturas.index(asignatura))
        datos = g.estadisticas_asignatura(asignatura.codigo)
        tarjeta = ctk.CTkFrame(padre, fg_color=tema.TARJETA, bg_color=tema.FONDO, corner_radius=tema.radio(14),
                               border_width=1, border_color=tema.BORDE)

        # Cabecera: sigla de color, nombre, código y horas
        cabecera = ctk.CTkFrame(tarjeta, fg_color="transparent", corner_radius=0)
        cabecera.pack(fill="x", padx=18, pady=(16, 0))
        sigla = "".join(c for c in asignatura.codigo if c.isalpha())[:3] or asignatura.codigo[:3]
        ctk.CTkLabel(cabecera, text=sigla.upper(), width=54, height=54, corner_radius=tema.radio(14),
                     fg_color=tema.mezclar(color, tema.TARJETA, 0.22), text_color=color,
                     font=tema.fuente(14, True)).pack(side="left")
        titulos = ctk.CTkFrame(cabecera, fg_color="transparent", corner_radius=0)
        titulos.pack(side="left", fill="x", expand=True, padx=12)
        ctk.CTkLabel(titulos, text=asignatura.nombre, font=tema.fuente(15, True), text_color=tema.TEXTO,
                     anchor="w", justify="left", wraplength=250).pack(fill="x")
        ctk.CTkLabel(titulos, text=f"Código {asignatura.codigo}", font=tema.fuente(10),
                     text_color=tema.TEXTO_SUAVE, anchor="w").pack(fill="x")
        comp.insignia(cabecera, f"{asignatura.intensidad_horaria} h", color).pack(side="right", anchor="n")

        # Docente
        docente = ctk.CTkFrame(tarjeta, fg_color=tema.TARJETA_2, bg_color=tema.TARJETA, corner_radius=tema.radio(10))
        docente.pack(fill="x", padx=18, pady=(14, 0))
        ctk.CTkLabel(docente, text="DOCENTE", font=tema.fuente(9, True),
                     text_color=tema.TEXTO_SUAVE).pack(side="left", padx=(12, 10), pady=9)
        profesor = asignatura.profesor
        ctk.CTkLabel(docente, text=profesor.nombre if profesor else "Sin asignar",
                     font=tema.fuente(12, True), anchor="w",
                     text_color=tema.TEXTO if profesor else tema.AMARILLO).pack(side="left")

        # Indicadores
        cifras = ctk.CTkFrame(tarjeta, fg_color="transparent", corner_radius=0)
        cifras.pack(fill="x", padx=18, pady=(14, 0))
        hay_notas = datos["inscritos"] > 0
        promedio_color = tema.TEXTO_SUAVE if not hay_notas else (tema.OK if datos["promedio"] >= 3 else tema.ERROR)
        valores = [("Promedio", f"{datos['promedio']:.2f}" if hay_notas else "—", promedio_color),
                   ("Estudiantes", str(datos["inscritos"]), tema.TEXTO),
                   ("Aprobación", f"{datos['porcentaje_aprobacion']:.0f}%" if hay_notas else "—", tema.TEXTO)]
        for i, (titulo, valor, color_valor) in enumerate(valores):
            cifras.grid_columnconfigure(i, weight=1, uniform="cif")
            bloque = ctk.CTkFrame(cifras, fg_color="transparent", corner_radius=0)
            bloque.grid(row=0, column=i, sticky="w")
            ctk.CTkLabel(bloque, text=valor, font=tema.fuente(22, True), text_color=color_valor,
                         anchor="w").pack(anchor="w")
            ctk.CTkLabel(bloque, text=titulo, font=tema.fuente(10), text_color=tema.TEXTO_SUAVE,
                         anchor="w").pack(anchor="w")

        barra = ctk.CTkProgressBar(tarjeta, height=8, fg_color=tema.mezclar(tema.ERROR, tema.TARJETA, 0.55)
                                   if hay_notas else tema.BORDE, progress_color=tema.OK)
        barra.set(datos["porcentaje_aprobacion"] / 100 if hay_notas else 0)
        barra.pack(fill="x", padx=18, pady=(12, 0))
        resumen = (f"✓ {datos['aprobados']} aprobados     ✕ {datos['reprobados']} reprobados"
                   if hay_notas else "Aún sin calificaciones registradas")
        ctk.CTkLabel(tarjeta, text=resumen, font=tema.fuente(10), text_color=tema.TEXTO_SUAVE,
                     anchor="w").pack(fill="x", padx=18, pady=(5, 0))

        # Acciones
        acciones = ctk.CTkFrame(tarjeta, fg_color="transparent", corner_radius=0)
        acciones.pack(fill="x", padx=18, pady=(14, 16))
        comp.boton(acciones, "Ver detalle  →", lambda: self.ver_asignatura(asignatura.codigo),
                   "primario").pack(side="left", fill="x", expand=True)
        comp.boton(acciones, "Editar", lambda: self._form_asignatura(asignatura, despues),
                   "secundario", ancho=80).pack(side="left", padx=(8, 0))
        comp.boton(acciones, "✕", lambda: self._eliminar_asignatura(asignatura, despues),
                   "peligro", ancho=40).pack(side="left", padx=(8, 0))

        comp.hacer_clicable(tarjeta, lambda: self.ver_asignatura(asignatura.codigo))
        comp.resaltar_al_pasar(tarjeta, color)
        return tarjeta

    # ------------------------------------------------------------------
    # Formulario y eliminación
    # ------------------------------------------------------------------
    def _form_asignatura(self, asignatura=None, despues=None):
        g = self.gestor
        campos = ["Código", "Nombre", "Intensidad horaria", "Profesor"]
        profesores = ["Sin asignar"] + [f"{p.identificacion} - {p.nombre}" for p in g.profesores]
        valores, bloqueados = {}, []
        if asignatura:
            p = asignatura.profesor
            valores = {"Código": asignatura.codigo, "Nombre": asignatura.nombre,
                       "Intensidad horaria": asignatura.intensidad_horaria,
                       "Profesor": f"{p.identificacion} - {p.nombre}" if p else "Sin asignar"}
            bloqueados = ["Código"]

        def guardar(v):
            profesor_id = "" if v["Profesor"] == "Sin asignar" else v["Profesor"].split(" - ", 1)[0]
            if asignatura:
                g.actualizar_asignatura(asignatura.codigo, v["Nombre"], v["Intensidad horaria"], profesor_id)
            else:
                g.agregar_asignatura(v["Código"], v["Nombre"], v["Intensidad horaria"], profesor_id)

        guardado = self._formulario("Editar asignatura" if asignatura else "Nueva asignatura", campos,
                                    guardar, valores, {"Profesor": profesores}, bloqueados,
                                    "Asignatura actualizada" if asignatura else "Asignatura creada")
        if guardado and despues:
            despues()
        return guardado

    def _eliminar_asignatura(self, asignatura, despues=None):
        if messagebox.askyesno("Confirmar", f"¿Eliminar {asignatura.nombre} y sus registros de notas?"):
            if self._ejecutar(lambda: self.gestor.eliminar_asignatura(asignatura.codigo), "Asignatura eliminada"):
                if despues:
                    despues()

    # ------------------------------------------------------------------
    # Detalle: todos los datos de una asignatura juntos
    # ------------------------------------------------------------------
    def ver_asignatura(self, codigo):
        g = self.gestor
        asignatura = g.buscar_asignatura(codigo)
        if asignatura is None:
            self.vista_asignaturas()
            return
        self._marcar_nav("Asignaturas")
        self._limpiar(desplazable=True)
        color = tema.color_de(g.asignaturas.index(asignatura))
        datos = g.estadisticas_asignatura(asignatura.codigo)
        profesor = asignatura.profesor
        recargar = lambda: self.ver_asignatura(codigo)

        self._encabezado(asignatura.nombre,
                         f"{asignatura.codigo}  ·  Docente: {profesor.nombre if profesor else 'Sin asignar'}",
                         [("← Asignaturas", self.vista_asignaturas, "secundario"),
                          ("Editar", lambda: self._form_asignatura(asignatura, recargar), "secundario"),
                          ("+ Registrar notas", lambda: self._form_calificaciones(None, codigo, recargar), "primario")])

        rejilla = ctk.CTkFrame(self.contenido, fg_color="transparent", corner_radius=0)
        rejilla.pack(fill="x")
        for columna in range(COLUMNAS):
            rejilla.grid_columnconfigure(columna, weight=1, uniform="det")

        # Indicadores
        hay_notas = datos["inscritos"] > 0
        indicadores = [
            ("Estudiantes", datos["inscritos"], tema.AZUL, "♙", "con notas en esta asignatura", None),
            ("Promedio", f"{datos['promedio']:.2f}" if hay_notas else "—", tema.AMARILLO, "★",
             "Mínimo para aprobar: 3.0", datos["promedio"] / 5),
            ("Aprobación", f"{datos['porcentaje_aprobacion']:.0f}%" if hay_notas else "—", tema.OK, "✓",
             f"{datos['aprobados']} aprobados · {datos['reprobados']} reprobados",
             datos["porcentaje_aprobacion"] / 100),
            ("Intensidad", f"{asignatura.intensidad_horaria} h", color, "⏱", "horas de la asignatura", None),
        ]
        for i, (titulo, valor, color_kpi, icono, detalle, progreso) in enumerate(indicadores):
            colocar(rejilla, comp.TarjetaKPI(rejilla, titulo, valor, color_kpi, icono, detalle, progreso), 0, i * 3, 3)

        # Aprobación y promedio por estudiante
        registros = sorted(g.registros_de_asignatura(codigo), key=lambda r: r.promedio, reverse=True)
        tarjeta = comp.TarjetaGrafica(rejilla, "Aprobados vs reprobados", "Resultado de esta asignatura")
        colocar(rejilla, tarjeta, 1, 0, 4)
        tarjeta.dibujar(graficas.dona, etiquetas=["Aprobados", "Reprobados"],
                        valores=[datos["aprobados"], datos["reprobados"]], colores=[tema.OK, tema.ERROR],
                        titulo_centro="de aprobación", texto_centro=f"{datos['porcentaje_aprobacion']:.0f}%")

        tarjeta = comp.TarjetaGrafica(rejilla, "Promedio por estudiante", "Línea punteada = mínimo para aprobar")
        colocar(rejilla, tarjeta, 1, 4, 8)
        tarjeta.dibujar(
            graficas.barras, etiquetas=[r.estudiante.nombre.split()[0] for r in registros],
            valores=[r.promedio for r in registros],
            colores=[color if r.promedio >= 3 else tema.ERROR for r in registros],
            textos=[f"{r.estudiante.nombre}\nNotas: " + " · ".join(f"{n.nota:.1f}" for n in r.calificaciones)
                    + f"\nPromedio {r.promedio:.2f} · {r.estado}" for r in registros],
            maximo=5.6, marcas=range(6), referencia=3.0)

        # Ficha del docente y evolución por nota
        colocar(rejilla, self._ficha_asignatura(rejilla, asignatura, datos, color), 2, 0, 5)
        tarjeta = comp.TarjetaGrafica(rejilla, "Promedio por nota", "Evolución del grupo en esta asignatura", alto=330)
        colocar(rejilla, tarjeta, 2, 5, 7)
        tarjeta.dibujar(graficas.linea, etiquetas=["Nota 1", "Nota 2", "Nota 3"],
                        valores=datos["promedio_por_nota"], color=color,
                        textos=[f"Promedio de la nota {i + 1}\n{v:.2f}"
                                for i, v in enumerate(datos["promedio_por_nota"])])

        # Tabla de estudiantes con sus notas
        ctk.CTkLabel(self.contenido, text="Estudiantes y calificaciones", font=tema.fuente(17, True),
                     text_color=tema.TEXTO).pack(anchor="w", pady=(20, 0))
        tabla = comp.crear_tabla(
            self.contenido, ("Identificación", "Estudiante", "Programa", "Nota 1", "Nota 2", "Nota 3", "Promedio", "Estado"),
            (105, 190, 190, 70, 70, 70, 90, 100), altura=min(8, max(len(registros), 3)), expandir=False)
        filas = [(r.estudiante.identificacion, r.estudiante.nombre, r.estudiante.programa,
                  *[f"{n.nota:.1f}" for n in r.calificaciones], f"{r.promedio:.2f}", r.estado) for r in registros]
        comp.llenar_tabla(tabla, filas, [r.estudiante.identificacion for r in registros],
                          etiqueta=lambda fila: comp.ETIQUETA_ESTADO.get(fila[-1]))

        def editar_notas():
            elegido = self._seleccion(tabla, "un estudiante de la tabla")
            if elegido:
                self._form_calificaciones(elegido, codigo, recargar)

        def quitar():
            elegido = self._seleccion(tabla, "un estudiante de la tabla")
            if elegido:
                self._eliminar_calificacion(elegido, codigo, recargar)

        tabla.bind("<Double-1>", lambda _evento: editar_notas())
        acciones = ctk.CTkFrame(self.contenido, fg_color="transparent", corner_radius=0)
        acciones.pack(fill="x", pady=(10, 14))
        comp.boton(acciones, "Editar notas del seleccionado", editar_notas, "secundario").pack(side="left")
        comp.boton(acciones, "Quitar de la asignatura", quitar, "peligro").pack(side="left", padx=8)
        if not registros:
            ctk.CTkLabel(acciones, text="Todavía no hay estudiantes con notas en esta asignatura.",
                         text_color=tema.TEXTO_SUAVE).pack(side="left", padx=12)

    def _ficha_asignatura(self, padre, asignatura, datos, color):
        """Tarjeta con la información de la asignatura y de su docente."""
        ficha = ctk.CTkFrame(padre, fg_color=tema.TARJETA, bg_color=tema.FONDO, corner_radius=tema.radio(14), border_width=1,
                             border_color=tema.BORDE, height=330)
        ficha.pack_propagate(False)
        ctk.CTkLabel(ficha, text="Ficha de la asignatura", font=tema.fuente(14, True),
                     text_color=tema.TEXTO, anchor="w").pack(fill="x", padx=18, pady=(14, 6))
        profesor = asignatura.profesor
        mejor, peor = datos["mejor"], datos["peor"]
        filas = [
            ("Código", asignatura.codigo, tema.TEXTO),
            ("Intensidad horaria", f"{asignatura.intensidad_horaria} horas", tema.TEXTO),
            ("Docente", profesor.nombre if profesor else "Sin asignar", tema.TEXTO if profesor else tema.AMARILLO),
            ("Especialidad", profesor.especialidad if profesor else "—", tema.TEXTO),
            ("Correo del docente", profesor.correo if profesor else "—", tema.TEXTO),
            ("Mejor promedio", f"{mejor.estudiante.nombre} · {mejor.promedio:.2f}" if mejor else "—", tema.OK),
            ("Promedio más bajo", f"{peor.estudiante.nombre} · {peor.promedio:.2f}" if peor else "—", tema.ERROR),
        ]
        for titulo, valor, color_valor in filas:
            fila = ctk.CTkFrame(ficha, fg_color="transparent", corner_radius=0)
            fila.pack(fill="x", padx=18, pady=3)
            ctk.CTkLabel(fila, text=titulo, font=tema.fuente(11), text_color=tema.TEXTO_SUAVE,
                         anchor="w", width=130).pack(side="left")
            ctk.CTkLabel(fila, text=valor, font=tema.fuente(11, True), text_color=color_valor,
                         anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkFrame(ficha, height=1, fg_color=tema.BORDE).pack(fill="x", padx=18)
        return ficha

import customtkinter as ctk
from tkinter import messagebox

from servicios.gestor_academico import GestorAcademico
from interfaz import tema, iconos, componentes as comp
from interfaz.vista_dashboard import VistaDashboard
from interfaz.vista_asignaturas import VistaAsignaturas

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CAMPOS_ESTUDIANTE = ["Identificación", "Nombre completo", "Correo", "Código estudiantil", "Programa"]
CAMPOS_PROFESOR = ["Identificación", "Nombre completo", "Correo", "Especialidad"]
COLOR_NAV_ACTIVO = tema.mezclar(tema.ACENTO, tema.PANEL, 0.45)


class VentanaPrincipal(VistaDashboard, VistaAsignaturas, ctk.CTk):
    """Ventana principal: barra lateral, navegación y vistas de administración.

    El dashboard y las asignaturas viven en sus propios módulos (mixins) para que
    este archivo no crezca demasiado; todos comparten `self.gestor`.
    """

    def __init__(self):
        super().__init__()
        self.title("EDUCONTROL | Gestión académica")
        self.geometry("1320x820")
        self.minsize(1100, 700)
        self.configure(fg_color=tema.FONDO)
        try:
            self.attributes("-alpha", 1.0)      # ventana 100 % opaca: sin transparencias raras
        except Exception:
            pass
        self.gestor = GestorAcademico()
        self.gestor.cargar_datos_demo()
        self.contenido = None
        self.botones_nav = {}
        comp.configurar_estilos_tabla()
        self._crear_estructura()
        self.mostrar_dashboard()

    # ------------------------------------------------------------------
    # Estructura general
    # ------------------------------------------------------------------
    def _crear_estructura(self):
        self.sidebar = ctk.CTkFrame(self, width=232, corner_radius=0, fg_color=tema.PANEL)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        marca = ctk.CTkFrame(self.sidebar, fg_color="transparent", corner_radius=0)
        marca.pack(fill="x", padx=18, pady=(26, 26))
        ctk.CTkLabel(marca, text="", width=44, height=44, fg_color=tema.PANEL, bg_color=tema.PANEL,
                     image=iconos.logo(44)).pack(side="left")
        textos = ctk.CTkFrame(marca, fg_color="transparent", corner_radius=0)
        textos.pack(side="left", padx=12)
        ctk.CTkLabel(textos, text="EDUCONTROL", font=tema.fuente(18, True),
                     text_color="#FFFFFF", anchor="w").pack(anchor="w")
        ctk.CTkLabel(textos, text="GESTIÓN ACADÉMICA", font=tema.fuente(10, True),
                     text_color=tema.TEXTO_SUAVE, anchor="w").pack(anchor="w")

        opciones = [
            ("inicio", "Dashboard", self.mostrar_dashboard),
            ("estudiante", "Estudiantes", self.vista_estudiantes),
            ("profesor", "Profesores", self.vista_profesores),
            ("asignatura", "Asignaturas", self.vista_asignaturas),
            ("calificacion", "Calificaciones", self.vista_calificaciones),
            ("reportes", "Reportes", self.vista_reportes),
        ]
        for icono, texto, comando in opciones:
            # Todos los botones comparten icono de 20 px, margen y alineación; bg_color
            # explícito = color de la barra, así no se ven esquinas distintas al fondo.
            boton = ctk.CTkButton(self.sidebar, text=f"  {texto}", anchor="w", height=44,
                                  corner_radius=tema.radio(10), fg_color=tema.PANEL, bg_color=tema.PANEL,
                                  hover_color=tema.TARJETA_2, text_color="#DCE6F5",
                                  font=tema.fuente(13), command=comando, compound="left",
                                  image=iconos.icono(icono, "#DCE6F5", 20))
            boton.pack(fill="x", padx=14, pady=3)
            self.botones_nav[texto] = boton
            self.iconos_nav = getattr(self, "iconos_nav", {})
            self.iconos_nav[texto] = icono

        ctk.CTkLabel(self.sidebar, text="Proyecto académico · Python + POO",
                     text_color="#8398B8", font=tema.fuente(10), wraplength=190).pack(side="bottom", pady=20)
        self.main = ctk.CTkFrame(self, fg_color=tema.FONDO, corner_radius=0)
        self.main.pack(side="right", fill="both", expand=True)

    def _marcar_nav(self, nombre):
        """Resalta en la barra lateral la sección que se está viendo."""
        for texto, boton in self.botones_nav.items():
            activo = texto == nombre
            boton.configure(fg_color=COLOR_NAV_ACTIVO if activo else tema.PANEL,
                            text_color="#FFFFFF" if activo else "#DCE6F5",
                            image=iconos.icono(self.iconos_nav[texto],
                                               "#FFFFFF" if activo else "#DCE6F5", 20))

    def _limpiar(self, desplazable=False):
        if self.contenido is not None:
            self.contenido.destroy()
        if desplazable:
            self.contenido = ctk.CTkScrollableFrame(
                self.main, fg_color=tema.FONDO, corner_radius=0,
                scrollbar_fg_color=tema.FONDO, scrollbar_button_color=tema.GRIS,
                scrollbar_button_hover_color=tema.GRIS_HOVER)
            self.contenido.pack(fill="both", expand=True, padx=(24, 10), pady=(20, 10))
        else:
            self.contenido = ctk.CTkFrame(self.main, fg_color=tema.FONDO, corner_radius=0)
            self.contenido.pack(fill="both", expand=True, padx=28, pady=24)

    def _encabezado(self, titulo, subtitulo, acciones=None):
        """Título de la vista. `acciones` = lista de (texto, comando, estilo) a la derecha."""
        barra = ctk.CTkFrame(self.contenido, fg_color="transparent", corner_radius=0)
        barra.pack(fill="x", pady=(0, 16))
        textos = ctk.CTkFrame(barra, fg_color="transparent", corner_radius=0)
        textos.pack(side="left")
        ctk.CTkLabel(textos, text=titulo, font=tema.fuente(27, True), text_color=tema.TEXTO,
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(textos, text=subtitulo, font=tema.fuente(12), text_color=tema.TEXTO_SUAVE,
                     anchor="w").pack(anchor="w", pady=(2, 0))
        for texto, comando, estilo in reversed(acciones or []):
            comp.boton(barra, texto, comando, estilo, alto=38).pack(side="right", padx=(8, 0))
        return barra

    def _barra_herramientas(self, texto_nuevo, agregar, editar, eliminar, al_buscar):
        """Buscador + contador + botones de acción. Devuelve (caja_busqueda, contador)."""
        barra = ctk.CTkFrame(self.contenido, fg_color="transparent", corner_radius=0)
        barra.pack(fill="x")
        caja = ctk.CTkEntry(barra, width=300, height=38, placeholder_text="Buscar…",
                            fg_color=tema.CAMPO, border_color=tema.BORDE, corner_radius=tema.radio(10))
        caja.pack(side="left")
        caja.bind("<KeyRelease>", lambda _evento: al_buscar())
        contador = ctk.CTkLabel(barra, text="", text_color=tema.TEXTO_SUAVE, font=tema.fuente(11))
        contador.pack(side="left", padx=14)
        for texto, comando, estilo in reversed([(texto_nuevo, agregar, "primario"),
                                                ("Editar", editar, "secundario"),
                                                ("Eliminar", eliminar, "peligro")]):
            comp.boton(barra, texto, comando, estilo).pack(side="right", padx=(8, 0))
        return caja, contador

    # ------------------------------------------------------------------
    # Diálogos y mensajes
    # ------------------------------------------------------------------
    def _dialogo(self, titulo, campos, valores=None, opciones=None, bloqueados=()):
        """Ventana de formulario. Devuelve un diccionario {campo: texto} o None si se cancela."""
        valores, opciones = valores or {}, opciones or {}
        ancho, alto = 450, 150 + 76 * len(campos) + 50
        dialogo = ctk.CTkToplevel(self)
        dialogo.title(titulo)
        dialogo.resizable(False, False)
        dialogo.configure(fg_color=tema.PANEL)
        x = self.winfo_rootx() + (self.winfo_width() - ancho) // 2
        y = self.winfo_rooty() + max(20, (self.winfo_height() - alto) // 2)
        dialogo.geometry(f"{ancho}x{alto}+{x}+{y}")
        dialogo.transient(self)
        ctk.CTkLabel(dialogo, text=titulo, font=tema.fuente(21, True), text_color=tema.TEXTO).pack(
            anchor="w", padx=26, pady=(24, 10))

        entradas = {}
        for campo in campos:
            ctk.CTkLabel(dialogo, text=campo, text_color=tema.TEXTO_MEDIO,
                         font=tema.fuente(11)).pack(anchor="w", padx=26, pady=(8, 3))
            if campo in opciones:
                widget = ctk.CTkOptionMenu(dialogo, values=opciones[campo], width=398, height=38,
                                           fg_color=tema.CAMPO, button_color=tema.GRIS,
                                           button_hover_color=tema.GRIS_HOVER,
                                           dropdown_fg_color=tema.TARJETA)
                if valores.get(campo):
                    widget.set(valores[campo])
            else:
                widget = ctk.CTkEntry(dialogo, width=398, height=38, fg_color=tema.CAMPO,
                                      border_color=tema.BORDE, corner_radius=tema.radio(9))
                if valores.get(campo) is not None:
                    widget.insert(0, str(valores[campo]))
            if campo in bloqueados:
                widget.configure(state="disabled")
            widget.pack(padx=26)
            entradas[campo] = widget

        resultado = {"valores": None}

        def aceptar():
            resultado["valores"] = {campo: widget.get().strip() for campo, widget in entradas.items()}
            dialogo.destroy()

        botones = ctk.CTkFrame(dialogo, fg_color="transparent", corner_radius=0)
        botones.pack(side="bottom", fill="x", padx=26, pady=22)
        comp.boton(botones, "Cancelar", dialogo.destroy, "secundario", ancho=110, alto=38).pack(side="right", padx=(8, 0))
        comp.boton(botones, "Guardar", aceptar, "primario", ancho=110, alto=38).pack(side="right")
        dialogo.bind("<Return>", lambda _evento: aceptar())
        dialogo.bind("<Escape>", lambda _evento: dialogo.destroy())

        def preparar():
            try:
                dialogo.grab_set()
                primero = next((w for c, w in entradas.items()
                                if c not in bloqueados and isinstance(w, ctk.CTkEntry)), None)
                if primero:
                    primero.focus()
            except Exception:
                pass
        dialogo.after(150, preparar)
        self.wait_window(dialogo)
        return resultado["valores"]

    def _ejecutar(self, funcion, mensaje="Operación realizada correctamente."):
        """Ejecuta una acción del gestor: aviso flotante si sale bien, cuadro de error si no."""
        try:
            funcion()
            comp.mostrar_aviso(self, mensaje)
            return True
        except (ValueError, TypeError) as error:
            messagebox.showerror("Revisa la información", str(error))
            return False
        except Exception as error:
            messagebox.showerror("Error inesperado", str(error))
            return False

    def _formulario(self, titulo, campos, accion, valores=None, opciones=None,
                    bloqueados=(), mensaje="Operación realizada correctamente."):
        """Abre el formulario y, si hay un error de validación, lo vuelve a abrir
        conservando lo que la persona había escrito. Devuelve True si se guardó."""
        while True:
            datos = self._dialogo(titulo, campos, valores, opciones, bloqueados)
            if datos is None:
                return False
            if self._ejecutar(lambda: accion(datos), mensaje):
                return True
            valores = datos

    def _seleccion(self, tabla, que):
        elegido = tabla.selection()
        if not elegido:
            messagebox.showwarning("Selecciona un registro", f"Primero selecciona {que}.")
            return None
        return elegido[0]

    # ------------------------------------------------------------------
    # Estudiantes
    # ------------------------------------------------------------------
    def vista_estudiantes(self):
        self._marcar_nav("Estudiantes")
        self._limpiar()
        self._encabezado("Estudiantes", "Administra la información de los estudiantes.")
        g = self.gestor

        def cargar():
            filtro = caja.get().strip().lower()
            visibles = [e for e in g.estudiantes if filtro in
                        f"{e.identificacion} {e.nombre} {e.correo} {e.codigo} {e.programa}".lower()]
            comp.llenar_tabla(tabla, [(e.identificacion, e.nombre, e.correo, e.codigo, e.programa)
                                      for e in visibles], [e.identificacion for e in visibles])
            contador.configure(text=f"{len(visibles)} de {len(g.estudiantes)} estudiantes")

        def agregar():
            if self._formulario("Nuevo estudiante", CAMPOS_ESTUDIANTE,
                                lambda v: g.agregar_estudiante(*[v[c] for c in CAMPOS_ESTUDIANTE]),
                                mensaje="Estudiante registrado"):
                cargar()

        def editar():
            identificacion = self._seleccion(tabla, "un estudiante")
            if not identificacion:
                return
            e = g.buscar_estudiante(identificacion)
            valores = dict(zip(CAMPOS_ESTUDIANTE, [e.identificacion, e.nombre, e.correo, e.codigo, e.programa]))
            if self._formulario("Editar estudiante", CAMPOS_ESTUDIANTE,
                                lambda v: g.actualizar_estudiante(e.identificacion, v["Nombre completo"],
                                                                  v["Correo"], v["Código estudiantil"], v["Programa"]),
                                valores, bloqueados=["Identificación"], mensaje="Estudiante actualizado"):
                cargar()

        def eliminar():
            identificacion = self._seleccion(tabla, "un estudiante")
            if not identificacion:
                return
            e = g.buscar_estudiante(identificacion)
            if messagebox.askyesno("Confirmar", f"¿Eliminar a {e.nombre} y sus calificaciones?"):
                if self._ejecutar(lambda: g.eliminar_estudiante(identificacion), "Estudiante eliminado"):
                    cargar()

        caja, contador = self._barra_herramientas("+ Nuevo estudiante", agregar, editar, eliminar, cargar)
        tabla = comp.crear_tabla(self.contenido, ("Identificación", "Nombre", "Correo", "Código", "Programa"),
                                 (120, 190, 220, 110, 190))
        tabla.bind("<Double-1>", lambda _evento: editar())
        cargar()

    # ------------------------------------------------------------------
    # Profesores
    # ------------------------------------------------------------------
    def vista_profesores(self):
        self._marcar_nav("Profesores")
        self._limpiar()
        self._encabezado("Profesores", "Registra y administra el personal docente.")
        g = self.gestor

        def cargar():
            filtro = caja.get().strip().lower()
            visibles = [p for p in g.profesores if filtro in
                        f"{p.identificacion} {p.nombre} {p.correo} {p.especialidad}".lower()]
            filas = [(p.identificacion, p.nombre, p.correo, p.especialidad,
                      sum(1 for a in g.asignaturas if a.profesor is p)) for p in visibles]
            comp.llenar_tabla(tabla, filas, [p.identificacion for p in visibles])
            contador.configure(text=f"{len(visibles)} de {len(g.profesores)} profesores")

        def agregar():
            if self._formulario("Nuevo profesor", CAMPOS_PROFESOR,
                                lambda v: g.agregar_profesor(*[v[c] for c in CAMPOS_PROFESOR]),
                                mensaje="Profesor registrado"):
                cargar()

        def editar():
            identificacion = self._seleccion(tabla, "un profesor")
            if not identificacion:
                return
            p = g.buscar_profesor(identificacion)
            valores = dict(zip(CAMPOS_PROFESOR, [p.identificacion, p.nombre, p.correo, p.especialidad]))
            if self._formulario("Editar profesor", CAMPOS_PROFESOR,
                                lambda v: g.actualizar_profesor(p.identificacion, v["Nombre completo"],
                                                                v["Correo"], v["Especialidad"]),
                                valores, bloqueados=["Identificación"], mensaje="Profesor actualizado"):
                cargar()

        def eliminar():
            identificacion = self._seleccion(tabla, "un profesor")
            if not identificacion:
                return
            p = g.buscar_profesor(identificacion)
            if messagebox.askyesno("Confirmar", f"¿Eliminar al profesor {p.nombre}?"):
                if self._ejecutar(lambda: g.eliminar_profesor(identificacion), "Profesor eliminado"):
                    cargar()

        caja, contador = self._barra_herramientas("+ Nuevo profesor", agregar, editar, eliminar, cargar)
        tabla = comp.crear_tabla(self.contenido, ("Identificación", "Nombre", "Correo", "Especialidad", "Asignaturas"),
                                 (120, 200, 230, 170, 100))
        tabla.bind("<Double-1>", lambda _evento: editar())
        cargar()

    # ------------------------------------------------------------------
    # Calificaciones
    # ------------------------------------------------------------------
    def vista_calificaciones(self):
        self._marcar_nav("Calificaciones")
        self._limpiar()
        self._encabezado("Calificaciones", "Registra tres notas por estudiante y asignatura.")
        g = self.gestor

        def cargar():
            filtro = caja.get().strip().lower()
            visibles = [r for r in g.registros if filtro in
                        f"{r.estudiante.identificacion} {r.estudiante.nombre} {r.asignatura.codigo} {r.asignatura.nombre}".lower()]
            filas = [(r.estudiante.identificacion, r.estudiante.nombre, r.asignatura.nombre,
                      *[f"{n.nota:.1f}" for n in r.calificaciones], f"{r.promedio:.2f}", r.estado)
                     for r in visibles]
            iids = [f"{r.estudiante.identificacion}|{r.asignatura.codigo}" for r in visibles]
            comp.llenar_tabla(tabla, filas, iids, etiqueta=lambda fila: fila[-1].lower())
            contador.configure(text=f"{len(visibles)} de {len(g.registros)} registros")

        def agregar():
            self._form_calificaciones(despues=cargar)

        def editar():
            elegido = self._seleccion(tabla, "un registro de la tabla")
            if elegido:
                estudiante_id, codigo = elegido.split("|", 1)
                self._form_calificaciones(estudiante_id, codigo, cargar)

        def eliminar():
            elegido = self._seleccion(tabla, "un registro de la tabla")
            if elegido:
                estudiante_id, codigo = elegido.split("|", 1)
                self._eliminar_calificacion(estudiante_id, codigo, cargar)

        caja, contador = self._barra_herramientas("+ Registrar notas", agregar, editar, eliminar, cargar)
        tabla = comp.crear_tabla(
            self.contenido,
            ("Identificación", "Estudiante", "Asignatura", "Nota 1", "Nota 2", "Nota 3", "Promedio", "Estado"),
            (105, 170, 170, 65, 65, 65, 85, 100))
        tabla.bind("<Double-1>", lambda _evento: editar())
        cargar()

    def _form_calificaciones(self, estudiante_id=None, codigo=None, despues=None):
        """Formulario de notas. Si recibe estudiante o asignatura, ese campo queda fijo."""
        g = self.gestor
        if not g.estudiantes or not g.asignaturas:
            messagebox.showwarning("Faltan datos", "Primero registra al menos un estudiante y una asignatura.")
            return False
        campos = ["Estudiante", "Asignatura", "Nota 1", "Nota 2", "Nota 3"]
        opciones = {"Estudiante": [f"{e.identificacion} - {e.nombre}" for e in g.estudiantes],
                    "Asignatura": [f"{a.codigo} - {a.nombre}" for a in g.asignaturas]}
        valores, bloqueados = {}, []
        if estudiante_id:
            e = g.buscar_estudiante(estudiante_id)
            valores["Estudiante"] = f"{e.identificacion} - {e.nombre}"
            bloqueados.append("Estudiante")
        if codigo:
            a = g.buscar_asignatura(codigo)
            valores["Asignatura"] = f"{a.codigo} - {a.nombre}"
            bloqueados.append("Asignatura")
        if estudiante_id and codigo:
            registro = next((r for r in g.registros if r.estudiante.identificacion == str(estudiante_id)
                             and r.asignatura.codigo == str(codigo)), None)
            if registro:
                for i, calificacion in enumerate(registro.calificaciones, start=1):
                    valores[f"Nota {i}"] = f"{calificacion.nota:.1f}"

        def guardar(v):
            estudiante = v["Estudiante"].split(" - ", 1)[0]
            asignatura = v["Asignatura"].split(" - ", 1)[0]
            notas = [v[f"Nota {i}"].replace(",", ".") for i in (1, 2, 3)]   # acepta 4,5 y 4.5
            g.guardar_calificaciones(estudiante, asignatura, notas)

        guardado = self._formulario("Registrar calificaciones", campos, guardar, valores,
                                    opciones, bloqueados, "Calificaciones guardadas")
        if guardado and despues:
            despues()
        return guardado

    def _eliminar_calificacion(self, estudiante_id, codigo, despues=None):
        g = self.gestor
        e, a = g.buscar_estudiante(estudiante_id), g.buscar_asignatura(codigo)
        if not e or not a:
            return False
        if messagebox.askyesno("Confirmar", f"¿Eliminar las notas de {e.nombre} en {a.nombre}?"):
            if self._ejecutar(lambda: g.eliminar_calificaciones(estudiante_id, codigo), "Registro eliminado"):
                if despues:
                    despues()
                return True
        return False

    # ------------------------------------------------------------------
    # Reportes
    # ------------------------------------------------------------------
    def vista_reportes(self):
        self._marcar_nav("Reportes")
        self._limpiar(desplazable=True)
        self._encabezado("Reportes académicos", "Consulta el rendimiento consolidado de los estudiantes.")
        g = self.gestor

        rejilla = ctk.CTkFrame(self.contenido, fg_color="transparent", corner_radius=0)
        rejilla.pack(fill="x")
        indicadores = [
            ("Promedio general", f"{g.promedio_general():.2f}", tema.AMARILLO, "★",
             "Sobre 5.0", g.promedio_general() / 5),
            ("Aprobados", g.contar_aprobados(), tema.OK, "✓",
             f"{g.porcentaje_aprobacion():.0f}% de los registros", g.porcentaje_aprobacion() / 100),
            ("Reprobados", g.contar_reprobados(), tema.ERROR, "✕",
             f"{100 - g.porcentaje_aprobacion() if g.registros else 0:.0f}% de los registros",
             (100 - g.porcentaje_aprobacion() if g.registros else 0) / 100),
        ]
        for i, (titulo, valor, color, icono, detalle, progreso) in enumerate(indicadores):
            rejilla.grid_columnconfigure(i, weight=1, uniform="rep")
            comp.TarjetaKPI(rejilla, titulo, valor, color, icono, detalle, progreso).grid(
                row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 6, 0 if i == 2 else 6))

        ctk.CTkLabel(self.contenido, text="Ranking de estudiantes", font=tema.fuente(17, True),
                     text_color=tema.TEXTO).pack(anchor="w", pady=(22, 0))
        ranking = comp.crear_tabla(self.contenido,
                                   ("Posición", "Estudiante", "Programa", "Promedio", "Asignaturas evaluadas", "Estado"),
                                   (80, 200, 210, 90, 150, 110), altura=min(10, max(len(g.estudiantes), 3)),
                                   expandir=False)
        posiciones = g.rendimiento_estudiantes()
        filas = [(f"{i}°", e.nombre, e.programa, f"{p:.2f}", c, comp.estado_general(p, c)[0])
                 for i, (e, p, c) in enumerate(posiciones, start=1)]
        comp.llenar_tabla(ranking, filas, [e.identificacion for e, _, _ in posiciones],
                          etiqueta=lambda fila: comp.ETIQUETA_ESTADO.get(fila[-1]))

        ctk.CTkLabel(self.contenido, text="Resumen por asignatura", font=tema.fuente(17, True),
                     text_color=tema.TEXTO).pack(anchor="w", pady=(22, 0))
        resumen = comp.crear_tabla(self.contenido,
                                   ("Código", "Asignatura", "Profesor", "Estudiantes", "Promedio", "Aprobación"),
                                   (90, 220, 190, 100, 90, 100), altura=min(8, max(len(g.asignaturas), 3)),
                                   expandir=False)
        filas = []
        for a in g.asignaturas:
            d = g.estadisticas_asignatura(a.codigo)
            filas.append((a.codigo, a.nombre, a.profesor.nombre if a.profesor else "Sin asignar",
                          d["inscritos"], f"{d['promedio']:.2f}" if d["inscritos"] else "—",
                          f"{d['porcentaje_aprobacion']:.0f}%" if d["inscritos"] else "—"))
        comp.llenar_tabla(resumen, filas, [a.codigo for a in g.asignaturas])

        ctk.CTkLabel(self.contenido, text="Los promedios se calculan con los registros disponibles. "
                     "Los datos se conservan únicamente mientras la aplicación está abierta.",
                     text_color=tema.TEXTO_SUAVE, wraplength=800, justify="left").pack(anchor="w", pady=16)

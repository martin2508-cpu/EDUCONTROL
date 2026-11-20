from modelos.estudiante import Estudiante
from modelos.profesor import Profesor
from modelos.asignatura import Asignatura
from modelos.registro_academico import RegistroAcademico


class GestorAcademico:
    """Administra colecciones de objetos y las operaciones del sistema."""
    def __init__(self):
        self.estudiantes = []
        self.profesores = []
        self.asignaturas = []
        self.registros = []

    @staticmethod
    def _buscar_por(lista, atributo, valor):
        for objeto in lista:
            if str(getattr(objeto, atributo)) == str(valor):
                return objeto
        return None

    def buscar_estudiante(self, identificacion):
        return self._buscar_por(self.estudiantes, "identificacion", identificacion)

    def buscar_profesor(self, identificacion):
        return self._buscar_por(self.profesores, "identificacion", identificacion)

    def buscar_asignatura(self, codigo):
        return self._buscar_por(self.asignaturas, "codigo", codigo)

    def agregar_estudiante(self, identificacion, nombre, correo, codigo, programa):
        if self.buscar_estudiante(identificacion):
            raise ValueError("Ya existe un estudiante con esa identificación.")
        if any(e.codigo == str(codigo).strip() for e in self.estudiantes):
            raise ValueError("Ya existe un estudiante con ese código.")
        estudiante = Estudiante(identificacion, nombre, correo, codigo, programa)
        self.estudiantes.append(estudiante)
        return estudiante

    def actualizar_estudiante(self, identificacion, nombre, correo, codigo, programa):
        actual = self.buscar_estudiante(identificacion)
        if not actual:
            raise ValueError("No se encontró el estudiante.")
        if any(e.codigo == str(codigo).strip() and e is not actual for e in self.estudiantes):
            raise ValueError("Ese código estudiantil ya está registrado.")
        reemplazo = Estudiante(identificacion, nombre, correo, codigo, programa)
        indice = self.estudiantes.index(actual)
        self.estudiantes[indice] = reemplazo
        for registro in self.registros:
            if registro.estudiante is actual:
                registro.estudiante = reemplazo
        return reemplazo

    def eliminar_estudiante(self, identificacion):
        estudiante = self.buscar_estudiante(identificacion)
        if not estudiante:
            raise ValueError("No se encontró el estudiante.")
        self.registros = [r for r in self.registros if r.estudiante is not estudiante]
        self.estudiantes.remove(estudiante)

    def agregar_profesor(self, identificacion, nombre, correo, especialidad):
        if self.buscar_profesor(identificacion):
            raise ValueError("Ya existe un profesor con esa identificación.")
        profesor = Profesor(identificacion, nombre, correo, especialidad)
        self.profesores.append(profesor)
        return profesor

    def actualizar_profesor(self, identificacion, nombre, correo, especialidad):
        actual = self.buscar_profesor(identificacion)
        if not actual:
            raise ValueError("No se encontró el profesor.")
        nuevo = Profesor(identificacion, nombre, correo, especialidad)
        self.profesores[self.profesores.index(actual)] = nuevo
        for asignatura in self.asignaturas:
            if asignatura.profesor is actual:
                asignatura.profesor = nuevo
        return nuevo

    def eliminar_profesor(self, identificacion):
        profesor = self.buscar_profesor(identificacion)
        if not profesor:
            raise ValueError("No se encontró el profesor.")
        for asignatura in self.asignaturas:
            if asignatura.profesor is profesor:
                asignatura.profesor = None
        self.profesores.remove(profesor)

    def agregar_asignatura(self, codigo, nombre, intensidad, profesor_id=""):
        if self.buscar_asignatura(codigo):
            raise ValueError("Ya existe una asignatura con ese código.")
        profesor = self.buscar_profesor(profesor_id) if profesor_id else None
        if profesor_id and not profesor:
            raise ValueError("El profesor seleccionado no existe.")
        asignatura = Asignatura(codigo, nombre, intensidad, profesor)
        self.asignaturas.append(asignatura)
        return asignatura

    def actualizar_asignatura(self, codigo, nombre, intensidad, profesor_id=""):
        actual = self.buscar_asignatura(codigo)
        if not actual:
            raise ValueError("No se encontró la asignatura.")
        profesor = self.buscar_profesor(profesor_id) if profesor_id else None
        if profesor_id and not profesor:
            raise ValueError("El profesor seleccionado no existe.")
        nombre = str(nombre).strip()
        try:
            horas = int(intensidad)
        except (TypeError, ValueError):
            raise ValueError("La intensidad horaria debe ser un número entero.")
        if horas <= 0 or not nombre:
            raise ValueError("Verifica el nombre y la intensidad horaria.")
        # Se valida primero y se asigna después: si hay error, la asignatura no cambia.
        actual.nombre = nombre
        actual.intensidad_horaria = horas
        actual.profesor = profesor
        return actual

    def eliminar_asignatura(self, codigo):
        asignatura = self.buscar_asignatura(codigo)
        if not asignatura:
            raise ValueError("No se encontró la asignatura.")
        self.registros = [r for r in self.registros if r.asignatura is not asignatura]
        self.asignaturas.remove(asignatura)

    def guardar_calificaciones(self, estudiante_id, asignatura_codigo, notas):
        estudiante = self.buscar_estudiante(estudiante_id)
        asignatura = self.buscar_asignatura(asignatura_codigo)
        if not estudiante or not asignatura:
            raise ValueError("Selecciona un estudiante y una asignatura válidos.")
        registro = next((r for r in self.registros
                         if r.estudiante is estudiante and r.asignatura is asignatura), None)
        if registro:
            registro.actualizar_notas(notas)
        else:
            registro = RegistroAcademico(estudiante, asignatura, notas)
            self.registros.append(registro)
        return registro

    def eliminar_calificaciones(self, estudiante_id, asignatura_codigo):
        estudiante = self.buscar_estudiante(estudiante_id)
        asignatura = self.buscar_asignatura(asignatura_codigo)
        registro = next((r for r in self.registros
                         if r.estudiante is estudiante and r.asignatura is asignatura), None)
        if not registro:
            raise ValueError("No se encontró el registro de calificaciones.")
        self.registros.remove(registro)


    def cargar_datos_demo(self):
        """Carga datos ficticios de demostración si el sistema está vacío."""
        if self.estudiantes or self.profesores or self.asignaturas or self.registros:
            return

        docentes = [
            ("9001", "Laura Méndez", "laura.mendez@educontrol.demo", "Matemáticas"),
            ("9002", "Carlos Rojas", "carlos.rojas@educontrol.demo", "Programación"),
            ("9003", "Diana Pardo", "diana.pardo@educontrol.demo", "Bases de datos"),
            ("9004", "Andrés Torres", "andres.torres@educontrol.demo", "Inglés"),
        ]
        for datos in docentes:
            self.agregar_profesor(*datos)

        estudiantes = [
            ("1001", "Valentina Gómez", "valentina.gomez@demo.edu", "EST001", "Ingeniería en Sistemas"),
            ("1002", "Santiago Martínez", "santiago.martinez@demo.edu", "EST002", "Ingeniería en Sistemas"),
            ("1003", "Camila Rodríguez", "camila.rodriguez@demo.edu", "EST003", "Diseño Gráfico"),
            ("1004", "Juan David Pérez", "juan.perez@demo.edu", "EST004", "Ingeniería Industrial"),
            ("1005", "Mariana Castro", "mariana.castro@demo.edu", "EST005", "Ingeniería en Sistemas"),
            ("1006", "Samuel Herrera", "samuel.herrera@demo.edu", "EST006", "Administración"),
            ("1007", "Isabella Díaz", "isabella.diaz@demo.edu", "EST007", "Ingeniería Industrial"),
            ("1008", "Nicolás Ramírez", "nicolas.ramirez@demo.edu", "EST008", "Ingeniería en Sistemas"),
            ("1009", "Daniela Silva", "daniela.silva@demo.edu", "EST009", "Diseño Gráfico"),
            ("1010", "Mateo Fernández", "mateo.fernandez@demo.edu", "EST010", "Administración"),
        ]
        for datos in estudiantes:
            self.agregar_estudiante(*datos)

        asignaturas = [
            ("MAT101", "Matemáticas básicas", 4, "9001"),
            ("PROG201", "Programación II", 5, "9002"),
            ("BD101", "Fundamentos de bases de datos", 3, "9003"),
            ("ING101", "Inglés I", 3, "9004"),
            ("ALG202", "Algoritmos", 4, "9002"),
        ]
        for datos in asignaturas:
            self.agregar_asignatura(*datos)

        notas_demo = [
            ("1001", "MAT101", [4.2, 4.5, 4.0]),
            ("1001", "PROG201", [4.6, 4.1, 4.8]),
            ("1002", "MAT101", [3.2, 3.5, 3.8]),
            ("1002", "PROG201", [2.8, 3.1, 3.4]),
            ("1003", "ING101", [4.7, 4.4, 4.9]),
            ("1004", "MAT101", [2.5, 2.8, 3.0]),
            ("1004", "ALG202", [3.4, 3.6, 3.2]),
            ("1005", "PROG201", [4.8, 4.9, 4.6]),
            ("1005", "BD101", [4.1, 4.3, 4.0]),
            ("1006", "ING101", [3.0, 3.2, 3.4]),
            ("1007", "MAT101", [2.2, 2.7, 2.5]),
            ("1007", "ALG202", [3.1, 3.0, 3.3]),
            ("1008", "PROG201", [3.8, 4.0, 3.9]),
            ("1008", "BD101", [3.5, 3.7, 3.6]),
            ("1009", "ING101", [4.3, 4.5, 4.4]),
            ("1010", "BD101", [2.6, 2.9, 2.8]),
        ]
        for estudiante_id, codigo, notas in notas_demo:
            self.guardar_calificaciones(estudiante_id, codigo, notas)

    def promedio_general(self):
        if not self.registros:
            return 0
        return round(sum(r.promedio for r in self.registros) / len(self.registros), 2)

    def contar_aprobados(self):
        return sum(1 for r in self.registros if r.estado == "Aprobado")

    def contar_reprobados(self):
        return sum(1 for r in self.registros if r.estado == "Reprobado")

    def rendimiento_estudiantes(self):
        resultados = []
        for estudiante in self.estudiantes:
            registros = [r for r in self.registros if r.estudiante is estudiante]
            promedio = round(sum(r.promedio for r in registros) / len(registros), 2) if registros else 0
            resultados.append((estudiante, promedio, len(registros)))
        return sorted(resultados, key=lambda item: item[1], reverse=True)

    # ------------------------------------------------------------------
    # Estadísticas para el dashboard, la vista de asignaturas y los reportes
    # ------------------------------------------------------------------
    def registros_de_asignatura(self, codigo):
        return [r for r in self.registros if r.asignatura.codigo == str(codigo)]

    def estadisticas_asignatura(self, codigo):
        """Resume en un diccionario todos los datos de una asignatura."""
        registros = self.registros_de_asignatura(codigo)
        total = len(registros)
        if total == 0:
            return {"inscritos": 0, "promedio": 0.0, "aprobados": 0, "reprobados": 0,
                    "porcentaje_aprobacion": 0.0, "mejor": None, "peor": None,
                    "promedio_por_nota": [0.0, 0.0, 0.0]}
        aprobados = sum(1 for r in registros if r.estado == "Aprobado")
        por_nota = [round(sum(r.calificaciones[i].nota for r in registros) / total, 2)
                    for i in range(3)]
        return {
            "inscritos": total,
            "promedio": round(sum(r.promedio for r in registros) / total, 2),
            "aprobados": aprobados,
            "reprobados": total - aprobados,
            "porcentaje_aprobacion": round(aprobados * 100 / total, 1),
            "mejor": max(registros, key=lambda r: r.promedio),
            "peor": min(registros, key=lambda r: r.promedio),
            "promedio_por_nota": por_nota,
        }

    def promedio_por_asignatura(self):
        """Lista de (asignatura, promedio, registros) solo de asignaturas con notas."""
        resultado = []
        for asignatura in self.asignaturas:
            datos = self.estadisticas_asignatura(asignatura.codigo)
            if datos["inscritos"]:
                resultado.append((asignatura, datos["promedio"], datos["inscritos"]))
        return resultado

    def distribucion_promedios(self):
        """Cuenta cuántos registros caen en cada rango de promedio (0-1, 1-2, ... 4-5)."""
        rangos = ["0 - 1", "1 - 2", "2 - 3", "3 - 4", "4 - 5"]
        conteos = [0] * 5
        for registro in self.registros:
            conteos[min(int(registro.promedio), 4)] += 1
        return rangos, conteos

    def promedio_por_nota(self):
        """Promedio general de la nota 1, la nota 2 y la nota 3."""
        if not self.registros:
            return [0.0, 0.0, 0.0]
        total = len(self.registros)
        return [round(sum(r.calificaciones[i].nota for r in self.registros) / total, 2)
                for i in range(3)]

    def estudiantes_por_programa(self):
        """Lista de (programa, cantidad) ordenada de mayor a menor."""
        conteo = {}
        for estudiante in self.estudiantes:
            conteo[estudiante.programa] = conteo.get(estudiante.programa, 0) + 1
        return sorted(conteo.items(), key=lambda item: item[1], reverse=True)

    def mejores_estudiantes(self, cantidad=5):
        con_notas = [item for item in self.rendimiento_estudiantes() if item[2] > 0]
        return con_notas[:cantidad]

    def estudiantes_en_riesgo(self):
        """Estudiantes con notas cuyo promedio está por debajo de 3.0 (de menor a mayor)."""
        riesgo = [item for item in self.rendimiento_estudiantes()
                  if item[2] > 0 and item[1] < 3.0]
        return sorted(riesgo, key=lambda item: item[1])

    def porcentaje_aprobacion(self):
        if not self.registros:
            return 0.0
        return round(self.contar_aprobados() * 100 / len(self.registros), 1)


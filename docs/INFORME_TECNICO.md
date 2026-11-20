# INFORME TÉCNICO — EDUCONTROL

## 1. Descripción del problema

La administración manual de estudiantes, asignaturas y calificaciones puede dificultar la consulta de información y el cálculo de resultados académicos. EDUCONTROL propone una aplicación de escritorio sencilla para organizar estos datos y calcular promedios.

## 2. Objetivo general

Desarrollar un sistema de gestión académica en Python que permita administrar estudiantes, profesores, asignaturas y calificaciones mediante una interfaz gráfica y aplicando programación orientada a objetos.

## 3. Alcance

El sistema permite crear, consultar, actualizar y eliminar registros principales; asociar docentes a asignaturas; registrar tres notas por estudiante y asignatura; calcular promedios y consultar reportes. La información se conserva únicamente en memoria durante la ejecución.

## 4. Arquitectura

El proyecto se divide en tres áreas:
- `modelos`: clases que representan las entidades del dominio.
- `servicios`: reglas y operaciones del sistema.
- `interfaz`: ventanas, formularios, tablas, gráficas y navegación. Se divide en `ventana_principal`
  (navegación, diálogos y vistas de administración), `vista_dashboard`, `vista_asignaturas`,
  `componentes` (tarjetas, tablas, botones), `graficas` (Matplotlib) y `tema` (colores y fuentes).

`main.py` inicia la aplicación.

## 5. Aplicación de POO

- **Abstracción:** `Persona` define una estructura común y el método abstracto `mostrar_informacion`.
- **Herencia:** `Estudiante` y `Profesor` reutilizan los atributos de `Persona`.
- **Polimorfismo:** cada subclase presenta su información de manera particular.
- **Encapsulamiento:** atributos internos y propiedades controlan el acceso y validación de las notas.
- **Asociación:** `Asignatura` mantiene una referencia al profesor responsable.
- **Agregación:** `GestorAcademico` mantiene colecciones de objetos que administra.
- **Composición:** `RegistroAcademico` crea y contiene los objetos `Calificacion` que forman el registro.

## 6. Reglas de negocio

- Las notas están en el intervalo de 0.0 a 5.0.
- Cada registro académico contiene tres notas.
- El promedio es la media aritmética de las tres notas.
- Una nota final igual o superior a 3.0 se considera aprobada.
- No se permiten identificaciones de estudiante o profesor duplicadas ni códigos de estudiante o asignatura repetidos.

## 7. Interfaz

La interfaz está construida con CustomTkinter y mantiene el tema oscuro (fondo azul marino, paneles gris azulado, acento azul eléctrico y detalles verdes). Cuenta con:

- **Navegación lateral** con la sección activa resaltada.
- **Dashboard** con cuatro indicadores y seis bloques de gráficas hechas con Matplotlib: dona de aprobados/reprobados, barras de promedio por asignatura, distribución de promedios, línea de promedio por nota, dona por programa y ranking de mejores estudiantes, además de un bloque de estudiantes en riesgo y la tabla de rendimiento. Las gráficas son interactivas: tooltip y resaltado al pasar el cursor, centro de la dona que cambia, animación de entrada y clic en una barra para abrir la asignatura.
- **Asignaturas** con una tarjeta por materia (docente, horas, estudiantes, promedio, aprobación) y una página de detalle con indicadores, gráficas, ficha del docente y tabla de notas, donde también se registran y editan las calificaciones de esa asignatura.
- **Formularios y tablas** con buscador, identificadores internos de fila (no dependen del texto mostrado), avisos flotantes y reapertura del formulario con los datos escritos cuando hay un error de validación.
- **Reportes** con ranking de estudiantes y resumen por asignatura.

## 8. Pruebas

Se incluyen pruebas unitarias para el registro de estudiantes, validación de duplicados, cálculo de promedio, rechazo de notas inválidas y estado académico. También se prueban las estadísticas del `GestorAcademico` (por asignatura, distribución de promedios, estudiantes en riesgo, ranking) y las gráficas, que se dibujan sin abrir ventanas y responden a eventos de ratón simulados.

## 9. Limitaciones

La aplicación no utiliza una base de datos ni guarda información en archivos. Por tanto, al cerrar el programa se pierden los datos introducidos. Esta limitación corresponde al alcance académico definido.

## 10. Conclusión

EDUCONTROL integra conceptos de programación, validación de datos, separación de responsabilidades e interfaz gráfica en una aplicación de escritorio de alcance intermedio.

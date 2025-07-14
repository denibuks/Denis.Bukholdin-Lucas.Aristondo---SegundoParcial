# Denis.Bukholdin-Lucas.Aristondo---SegundoParcial
link gameplay: https://youtu.be/WZS2XoLQXWk
FUNCIONALIDADES PRINCIPALES
1. Sistema de Juego Multijugador

Hasta 4 jugadores pueden participar simultáneamente
Turnos rotativos entre jugadores
Validación de nombres (solo letras y espacios, máximo 15 caracteres)
Eliminación progresiva de jugadores sin vidas
Clasificación final por puntaje y porcentaje de aciertos

2. Sistema de Vidas Innovador

3 vidas por categoría para cada jugador
Las vidas se pierden solo al fallar preguntas
Sistema independiente: perder en una categoría no afecta las otras
Visualización en tiempo real del estado de vidas
Eliminación del jugador cuando no tiene vidas en ninguna categoría

3. Minijuego Tateti con Matrices

Recuperación de vidas: gana una vida extra si vences a la IA
Una oportunidad por categoría para jugar tateti
Implementación con NumPy: uso de matrices para lógica, coordenadas y colores
IA inteligente: prioriza ganar, luego bloquear, luego estrategia
Visualización de matrices presionando 'M' durante el juego

4. Sistema de Categorías y Dificultades

Ruleta de categorías: selección aleatoria visual con animación
3 categorías por jugador elegidas automáticamente
3 niveles de dificultad: Fácil (10 pts), Medio (20 pts), Difícil (30 pts)
10 preguntas por categoría
Prevención de repetición de preguntas (configurable)

5. Interfaz Gráfica Avanzada

Diseño responsive con efectos hover y animaciones
Contador de tiempo circular con código de colores (verde → naranja → rojo)
Efectos visuales: sombras, pulsos, gradientes
Feedback inmediato: colores distintivos para respuestas correctas/incorrectas
Animaciones fluidas: ruleta de categorías, transiciones de estado

6. Sistema de Accesibilidad

Modo daltónico: paleta de colores optimizada para daltonismo rojo-verde
Cambio dinámico: activación/desactivación en tiempo real
Colores alternativos: verdes → azules, rojos → naranjas/marrones
Mayor contraste en elementos importantes

7. Gestión de Datos y Configuración

Archivo CSV de preguntas: fácil adición/modificación de contenido
Configuración JSON: personalización completa sin modificar código
Historial de partidas: guardado automático con ordenamiento alfabético
Corrección automática: arreglo de porcentajes incorrectos en partidas guardadas

8. Sistema de Audio

Música de ambiente: reproducción automática en loop
Controles en tiempo real: F1 (pausar/reanudar), +/- (volumen)
Gestión inteligente: limpieza automática al salir
Sistema no intrusivo: el juego funciona sin archivos de audio

ARQUITECTURA DEL SISTEMA
Estructura Modular
main.py              → Punto de entrada y loop principal
gestores.py          → Lógica de estados y coordinación
interfaz.py          → Presentación visual y eventos
configuracion.py     → Manejo de archivos y configuración
funciones.py         → Lógica de preguntas y validaciones
tateti_pygame_matriz.py → Minijuego con implementación matricial
musica.py            → Sistema de audio ambiente
ordenamiento.py      → Algoritmos de ordenamiento
Patrón de Estados
El juego utiliza una máquina de estados para controlar el flujo:
menu → ingreso_jugador → seleccionar_dificultad → ruleta_categoria → 
jugar → mostrar_vidas → tateti_vida → fin_ronda → fin_juego
Separación de Responsabilidades

Gestores: Coordinan la lógica y el estado del juego
Interfaz: Maneja la presentación visual y eventos de usuario
Configuración: Carga y valida datos externos
Funciones: Procesan la lógica específica del juego


MECÁNICAS DE JUEGO DETALLADAS
Flujo de una Partida Completa
1. Inicio del Juego

Los jugadores ingresan sus nombres (validación automática)
Se puede jugar con 1-4 jugadores

2. Selección de Dificultad

Cada jugador elige su nivel de dificultad
El puntaje varía según la dificultad elegida

3. Asignación de Categorías

3 categorías aleatorias por jugador
Inicialización de 3 vidas por categoría

4. Fase de Preguntas

Ruleta animada selecciona la categoría
10 preguntas por categoría con tiempo límite (30 segundos)
Pérdida de vida solo al fallar preguntas

5. Sistema de Vidas

Al perder todas las vidas de una categoría:

Opción de jugar tateti contra IA
Victoria = 1 vida extra en esa categoría
Derrota/empate = eliminación de la categoría



6. Eliminación y Finalización

Jugador eliminado cuando no tiene vidas en ninguna categoría
El juego continúa hasta que quede 1 jugador o todos sean eliminados
Clasificación final por puntaje total

Sistema de Puntuación

Fácil: 10 puntos por respuesta correcta
Medio: 20 puntos por respuesta correcta
Difícil: 30 puntos por respuesta correcta
Sin penalización por respuestas incorrectas
Porcentaje de aciertos calculado sobre preguntas respondidas


CARACTERÍSTICAS TÉCNICAS
Tecnologías Utilizadas

Python 3.x como lenguaje principal
Pygame para gráficos, sonido y eventos
NumPy para operaciones matriciales en tateti
JSON para configuración flexible
CSV para almacenamiento de preguntas

Algoritmos Implementados

Ordenamiento burbuja para clasificación alfabética de jugadores
Búsqueda lineal en validaciones y selecciones
Algoritmos matriciales para el tateti (verificación de patrones)
Generación de números aleatorios para selección de categorías y preguntas

Estructura de Datos

Matrices NumPy para el tablero de tateti (3x3 para lógica, 3x3x2 para coordenadas, 3x3x3 para colores)
Diccionarios anidados para configuración y estado del juego
Listas para manejo de jugadores, preguntas y categorías


CONFIGURACIÓN Y PERSONALIZACIÓN
Archivo configuracion.json
El juego es completamente configurable a través de un archivo JSON que permite modificar:

Colores para modo normal y daltónico
Tiempos de preguntas y animaciones
Puntajes por dificultad
Número de preguntas por categoría
Configuración de vidas del sistema
Textos de la interfaz
Posiciones de elementos gráficos

Archivo preguntas.csv
Las preguntas se almacenan en formato CSV con la estructura:
pregunta, opcion1, opcion2, opcion3, opcion4, respuesta_correcta, categoria, dificultad, puntaje
Personalización Visual

Fuentes: tamaños configurables para diferentes elementos
Colores: paletas completas para accesibilidad
Animaciones: velocidades y efectos ajustables
Layouts: posiciones y tamaños de componentes


INNOVACIONES DEL PROYECTO
1. Sistema de Vidas por Categoría
Diferencia clave: A diferencia de juegos tradicionales donde las vidas son globales, este sistema permite que un jugador continúe en otras categorías aunque haya fallado en una específica.
2. Integración de Tateti Estratégico
Mecánica única: El tateti no es solo un minijuego, sino una segunda oportunidad estratégica que permite a los jugadores recuperar vidas perdidas.



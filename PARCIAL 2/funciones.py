import time
import random
from funcionesaux import * 

def seleccionar_dificultad():
    print("\n Elegí la dificultad:")
    print("1. Fácil\n2. Medio\n3. Difícil")
    opciones = {"1": "Fácil", "2": "Medio", "3": "Difícil"}
    eleccion = input("Opción (1-3): ").strip()
    while eleccion != "1" and eleccion != "2" and eleccion != "3":
        eleccion = input("Opción inválida. Elegí 1, 2 o 3: ").strip()
    return opciones[eleccion]

def obtener_pregunta_aleatoria(preguntas, categoria, dificultad, preguntas_ya_preguntadas, permitir_repetir):
    todas = preguntas[categoria]["Preguntas"]
    filtradas = []
    for i in todas:
        if i["dificultad"] == dificultad:
            filtradas.append(i)

    disponibles = []
    if permitir_repetir == True:
        for i in filtradas:
            disponibles.append(i)
    else:
        for i in filtradas:
            ya_preguntada = False
            for preg in preguntas_ya_preguntadas:
                if i["pregunta"] == preg:
                    ya_preguntada = True
            if ya_preguntada == False:
                disponibles.append(i)

    pregunta_elegida = None
    if len(disponibles) > 0:
        pregunta_elegida = random.choice(disponibles)
        preguntas_ya_preguntadas.append(pregunta_elegida["pregunta"])

    return pregunta_elegida

def mostrar_pregunta(pregunta, categoria):
    print("\nCategoría: " + categoria)
    print(pregunta["pregunta"])
    i = 1
    while i <= 4:
        print(str(i) + ": " + pregunta["opciones"][i-1])
        i += 1

def solicitar_respuesta_con_tiempo(timeout):
    print("Tenés " + str(timeout) + " segundos para responder.")
    inicio = time.time()
    respuesta = input("Tu respuesta (1-4): ").strip()
    duracion = time.time() - inicio

    if duracion > timeout:
        print("\nTiempo agotado. Tardaste " + str(int(duracion)) + " segundos.")
        return None

    while True:
        es_valida = False
        if respuesta == "1" or respuesta == "2" or respuesta == "3" or respuesta == "4":
            es_valida = True

        if es_valida == True:
            break

        if time.time() - inicio > timeout:
            print("\nTiempo agotado mientras corregías la respuesta.")
            return None

        respuesta = input("Opción inválida. Ingresá 1, 2, 3 o 4: ").strip()

    return respuesta

def validar_respuesta(respuesta_usuario, respuesta_correcta, opciones):
    bandera = False
    if respuesta_usuario == respuesta_correcta:
        print("¡Correcto!")
        bandera = True
    else:
        correcta = int(respuesta_correcta) - 1
        print("Incorrecto. La respuesta correcta era: " + opciones[correcta])
    return bandera

def seleccionar_perfil():
    print("\nINGRESO DE PERFIL (máximo 3 letras)")
    while True:
        nombre = input("Ingresá tu nombre (máx 3 letras): ").upper().strip()
        if len(nombre) == 0 or len(nombre) > 3:
            print("El nombre debe tener entre 1 y 3 letras.")
            continue
        valido = True
        for letra in nombre:
            codigo = ord(letra)
            if codigo < 65 or codigo > 90:
                print("Solo se permiten letras.")
                valido = False
        if valido == True:
            print("\nJugas como: " + nombre + "\n")
            return nombre

def jugar_tres_pasadas(preguntas, jugador, configuracion):
    print("BIENVENIDO AL JUEGO DE PREGUNTAS")
    print("Jugador: " + jugador)
    total_preguntas = configuracion["preguntas_por_categoria"] * configuracion["categorias_a_elegir"]
    print("Responderás " + str(total_preguntas) + " preguntas divididas en " + str(configuracion["categorias_a_elegir"]) + " categorías distintas.")
    print("Cada categoría tendrá " + str(configuracion["preguntas_por_categoria"]) + " preguntas.")
    print("Tenes que sumar la mayor cantidad de aciertos posibles.\n")
    input("Presiona ENTER para empezar: ")

    puntaje_total = 0
    respuestas_correctas = 0
    rondas_por_categoria = configuracion["preguntas_por_categoria"]
    dificultad = seleccionar_dificultad()
    preguntas_ya_preguntadas = []
    categorias_elegidas = elegir_tres_categorias(preguntas)

    for categoria in categorias_elegidas:
        print("\nCATEGORÍA ELEGIDA: " + categoria.upper())
        input("Presioná ENTER para empezar esta categoría...")

        for ronda in range(1, rondas_por_categoria + 1):
            print("\nRonda " + str(ronda) + " de " + str(rondas_por_categoria))
            pregunta = obtener_pregunta_aleatoria(
                preguntas,
                categoria,
                dificultad,
                preguntas_ya_preguntadas,
                permitir_repetir=configuracion["permitir_repetir_preguntas"]
            )

            if pregunta == None:
                print("No hay más preguntas disponibles en esta categoría.")
                break

            mostrar_pregunta(pregunta, categoria)
            respuesta = solicitar_respuesta_con_tiempo(configuracion["Tiempo"])

            if respuesta == None:
                print("Pregunta perdida por tiempo.")
            else:
                acierto = validar_respuesta(respuesta, pregunta["respuesta"], pregunta["opciones"])
                if acierto == True:
                    respuestas_correctas += 1
                    puntaje_total += configuracion["puntaje_por_dificultad"][dificultad]

    total_rondas = rondas_por_categoria * len(categorias_elegidas)
    porcentaje = 0
    if total_rondas > 0:
        porcentaje = int((respuestas_correctas / total_rondas) * 100)

    print("\nJuego terminado")
    print("Aciertos: " + str(respuestas_correctas) + "/" + str(total_rondas))
    print("Porcentaje de aciertos: " + str(porcentaje) + "%")
    print("Puntaje acumulado: " + str(puntaje_total) + " puntos")

    return {
        "aciertos": respuestas_correctas,
        "porcentaje": porcentaje,
        "puntaje": puntaje_total
    }

import json

def cargar_configuracion(path="configuracion.json"):
    with open(path, "r", encoding="utf-8") as archivo:
        configuracion = json.load(archivo)
    return configuracion

def cargar_preguntas_desde_csv(preguntas_csv):
    preguntas = {}
    archivo = open(preguntas_csv, "r", encoding="utf-8")
    lineas = archivo.readlines()
    archivo.close()

    for linea in lineas[1:]: 
        fila = linea.strip().split(',')
        if len(fila) < 9:
            continue

        pregunta = fila[0]
        opciones = [fila[1], fila[2], fila[3], fila[4]]
        respuesta = fila[5]
        categoria = fila[6]
        dificultad = fila[7]
        puntaje = int(fila[8])

        existe = False
        for clave in preguntas:
            if clave == categoria:
                existe = True
        if existe == False:
            preguntas[categoria] = {"Preguntas": []}

        preguntas[categoria]["Preguntas"].append({
            "pregunta": pregunta,
            "opciones": opciones,
            "respuesta": respuesta,
            "dificultad": dificultad,
            "puntaje": puntaje
        })

    return preguntas

def guardar_partida(jugadores, resultados, path="partida_guardada.json"):
    partida = {
        "jugadores": jugadores,
        "resultados": resultados
    }

    with open(path, "w", encoding="utf-8") as archivo:
        json.dump(partida, archivo, ensure_ascii=False, indent=2)


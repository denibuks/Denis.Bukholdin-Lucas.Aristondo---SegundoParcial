import json

def cargar_configuracion(path="configuracion.json"):
    try:
        with open(path, "r", encoding="utf-8") as archivo:
            configuracion = json.load(archivo)
        return configuracion
    except Exception as e:
        print("Error al cargar la configuración:", e)
        return {}

def cargar_preguntas_desde_csv(preguntas_csv):
    preguntas = {}
    try:
        archivo = open(preguntas_csv, "r", encoding="utf-8")
        lineas = archivo.readlines()
        archivo.close()
    except Exception as e:
        print("Error al leer el archivo CSV:", e)
        return {}

    for linea in lineas[1:]: 
        fila = linea.strip().split(',')
        if len(fila) < 9:
            continue

        try:
            pregunta = fila[0]
            opciones = [fila[1], fila[2], fila[3], fila[4]]
            respuesta = fila[5]
            categoria = fila[6]
            dificultad = fila[7]
            puntaje = int(fila[8])
        except Exception as e:
            print("Error al procesar una línea del CSV:", e)
            continue

        existe = False
        for clave in preguntas:
            if clave == categoria:
                existe = True
        if not existe:
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
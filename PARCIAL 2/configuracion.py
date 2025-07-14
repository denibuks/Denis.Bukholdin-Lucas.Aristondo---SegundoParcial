import json
import time
import os


def cargar_configuracion(path="PARCIAL 2/configuracion.json"):
    try:
        with open(path, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except Exception as e:
        print("Error al cargar configuración:", e)
        return {}

def guardar_partida(jugadores, resultados, path="partida_guardada.json"):
    partida = {
        "jugadores": jugadores,
        "resultados": resultados,
        "fecha": str(time.time())
    }
    
    try:
        with open(path, "w", encoding="utf-8") as archivo:
            json.dump(partida, archivo, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error al guardar partida:", e)

def cargar_preguntas_desde_csv(preguntas_csv):
    preguntas = {}
    try:
        with open(preguntas_csv, "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
    except Exception as e:
        print("Error al leer CSV:", e)
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
        except Exception:
            continue

        if categoria not in preguntas:
            preguntas[categoria] = {"Preguntas": []}

        preguntas[categoria]["Preguntas"].append({
            "pregunta": pregunta,
            "opciones": opciones,
            "respuesta": respuesta,
            "dificultad": dificultad,
            "puntaje": puntaje
        })

    return preguntas

def obtener_colores(config):
    modo = "daltonico" if config.get("Accesibilidad") == "daltonico" else "normal"
    return config.get("colores", {}).get(modo, {})
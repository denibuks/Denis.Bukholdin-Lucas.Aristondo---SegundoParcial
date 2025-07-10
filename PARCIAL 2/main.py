from funcionesaux import *
from configuracion import *
from funciones import *
#COSAS PARA IMPLEMENTAR: RULETA, ORDENAR NOMBRES DE JUGADORES ALFABETICAMENTE, TATETI (+50 puntos), RECURSIVIDAD, PYGAME, FUNCION PARA LLAMAR A TODAS LAS FUNCIONES EN EL MAIN
# =================== JUEGO PRINCIPAL: 3 PASADAS ===================

from funcionesaux import *
from configuracion import *
from funciones import *

configuracion = cargar_configuracion("PARCIAL 2/configuracion.json")

def gestionar_jugadores(preguntas, configuracion, max_jugadores=3):
    jugadores = []
    resultados = {}

    while len(jugadores) < max_jugadores:
        jugador = seleccionar_perfil()

        existe = False
        for j in jugadores:
            if j == jugador:
                existe = True

        if existe == True:
            print("Ese nombre ya fue usado. Elegí otro.")
            continue

        jugadores.append(jugador)
        resultado = jugar_tres_pasadas(preguntas, jugador, configuracion)
        resultados[jugador] = resultado

        if len(jugadores) == max_jugadores:
            print("\nSe alcanzó el máximo de jugadores.")
            break

        continuar = input("¿Querés que juegue otro jugador? (S/N): ").strip().upper()
        while continuar != "S" and continuar != "N":
            continuar = input("Respuesta inválida. Ingresá S o N: ").strip().upper()

        if continuar == "N":
            break

    return jugadores, resultados


def mostrar_resultados_finales(jugadores, resultados):
    print("\nRESULTADOS FINALES")
    print("Jugador - Aciertos - Porcentaje - Puntaje")
    print("------------------------------------------")
    for jugador in jugadores:
        datos = resultados[jugador]
        print(f"{jugador} - {datos['aciertos']} - {datos['porcentaje']}% - {datos['puntaje']}")


if __name__ == "__main__":
    preguntas = cargar_preguntas_desde_csv("PARCIAL 2/preguntas.csv")
    jugadores, resultados = gestionar_jugadores(preguntas, configuracion, max_jugadores=3)
    mostrar_resultados_finales(jugadores, resultados)
    guardar_partida(jugadores, resultados)

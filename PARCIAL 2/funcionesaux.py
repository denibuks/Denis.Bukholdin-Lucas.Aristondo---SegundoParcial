import random

def elegir_tres_categorias(preguntas):
    categorias_disponibles = list(preguntas.keys())
    categorias_elegidas = []

    while len(categorias_elegidas) < 3:
        categoria = random.choice(categorias_disponibles)
        existe = False

        for elegida in categorias_elegidas:
            if elegida == categoria:
                existe = True

        if existe == False:
            categorias_elegidas.append(categoria)

    return categorias_elegidas

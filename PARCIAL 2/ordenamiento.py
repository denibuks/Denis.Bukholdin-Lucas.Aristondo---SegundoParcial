# ordenamiento.py

def ordenar_jugadores_alfabeticamente(jugadores_dict):
    if not jugadores_dict:
        return []
    
    jugadores_lista = [(nombre, datos) for nombre, datos in jugadores_dict.items()]
    n = len(jugadores_lista)
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if jugadores_lista[j][0].lower() > jugadores_lista[j + 1][0].lower():
                jugadores_lista[j], jugadores_lista[j + 1] = jugadores_lista[j + 1], jugadores_lista[j]
    
    return jugadores_lista
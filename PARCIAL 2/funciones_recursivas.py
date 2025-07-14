def validar_nombre_jugador_recursivo(nombre, indice=0):
    # Caso base: si el índice llegó al final del nombre, todos los caracteres son válidos
    es_valido = True
    if indice < len(nombre):
        # Obtiene el carácter actual en la posición 'indice'
        char = nombre[indice]
        # Convierte el carácter a su valor numérico en ASCII
        codigo = ord(char)

        # Verifica si el carácter es una letra mayúscula (A-Z),
        # una letra minúscula (a-z), o un espacio ( )
        if not ((65 <= codigo <= 90) or (97 <= codigo <= 122) or codigo == 32):
            es_valido = False  # Si no lo es, el nombre no es válido
        else:
            # Si el carácter es valido, continua validando el siguiente carácter recursivamente
            es_valido = validar_nombre_jugador_recursivo(nombre, indice + 1)

    return es_valido

def buscar_categoria_recursiva(preguntas, categoria_buscada, categorias_lista=None, indice=0):
    if categorias_lista == None:
        categorias_lista = list(preguntas.keys())
    
    if indice >= len(categorias_lista):
        return False
    
    if categorias_lista[indice].lower() == categoria_buscada.lower():
        return True
    
    return buscar_categoria_recursiva(preguntas, categoria_buscada, categorias_lista, indice + 1)
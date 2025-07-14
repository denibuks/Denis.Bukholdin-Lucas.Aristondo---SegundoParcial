import time
import random

def obtener_pregunta_aleatoria(preguntas, categoria, dificultad, preguntas_ya_preguntadas, permitir_repetir):
    """Obtiene una pregunta aleatoria filtrada por categoría y dificultad"""
    if categoria not in preguntas:
        return None
    
    # Filtrar por dificultad
    filtradas = [p for p in preguntas[categoria]["Preguntas"] if p["dificultad"] == dificultad]
    
    # Si no permitir repetir, excluir las ya preguntadas
    if not permitir_repetir:
        filtradas = [p for p in filtradas if p["pregunta"] not in preguntas_ya_preguntadas]
    
    if not filtradas:
        return None
    
    # Elegir pregunta aleatoria
    pregunta_elegida = random.choice(filtradas)
    
    # Agregar a preguntas ya preguntadas si no repetimos
    if not permitir_repetir:
        preguntas_ya_preguntadas.append(pregunta_elegida["pregunta"])
    
    return pregunta_elegida

def elegir_tres_categorias(preguntas):
    """Elige 3 categorías aleatorias de las disponibles"""
    categorias_disponibles = list(preguntas.keys())
    
    # Si hay menos de 3 categorías, devolver todas
    if len(categorias_disponibles) <= 3:
        return categorias_disponibles
    
    return random.sample(categorias_disponibles, 3)

def validar_nombre_jugador(nombre):
    """Valida que el nombre del jugador contenga solo letras y espacios y tenga máximo 15 caracteres"""
    if not nombre or len(nombre.strip()) == 0:
        return False
    
    # Verificar longitud máxima
    if len(nombre.strip()) > 15:
        return False
    
    # Verificar que solo contenga letras y espacios
    return all(c.isalpha() or c.isspace() for c in nombre.strip())

def calcular_resultados(respuestas_correctas, total_preguntas, puntaje_total):
    """Calcula los resultados finales del jugador"""
    if total_preguntas == 0:
        porcentaje = 0
    else:
        porcentaje = int((respuestas_correctas / total_preguntas) * 100)
    
    return {
        "aciertos": respuestas_correctas,
        "porcentaje": porcentaje,
        "puntaje": puntaje_total
    }

def validar_configuracion(config):
    """Valida que la configuración tenga los valores necesarios"""
    valores_por_defecto = {
        "Tiempo": 30,
        "Accesibilidad": "neurotipico",
        "preguntas_por_categoria": 10,
        "categorias_a_elegir": 3,
        "permitir_repetir_preguntas": False,
        "max_jugadores": 4,
        "longitud_nombre": 15,
        "puntaje_por_dificultad": {
            "Fácil": 10,
            "Medio": 20,
            "Difícil": 30
        },
        "colores_jugadores": {
            "P1": [0, 255, 255],
            "P2": [255, 0, 255],
            "P3": [50, 205, 50],
            "P4": [255, 255, 0]
        },
        "tiempo_animacion_ruleta": 3,
        "efectos_sonido": True,
        "modo_arcade": True
    }
    
    # Completar configuración con valores por defecto si faltan
    for clave, valor in valores_por_defecto.items():
        if clave not in config:
            config[clave] = valor
    
    return config
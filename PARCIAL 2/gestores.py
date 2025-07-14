import time
import json
import os
import pygame
import sys
from funciones import (
    obtener_pregunta_aleatoria, 
    elegir_tres_categorias, 
    calcular_resultados
)
from configuracion import guardar_partida
from ordenamiento import ordenar_jugadores_alfabeticamente
import musica  # Sistema simple de música de ambiente

# ================== VALIDACIÓN ==================

def validar_nombre_jugador(nombre):
    """Valida que el nombre del jugador contenga solo letras y espacios"""
    if not nombre or len(nombre.strip()) == 0:
        return False
    
    if len(nombre.strip()) > 15:
        return False
    
    return all(c.isalpha() or c.isspace() for c in nombre.strip())

# ================== ESTADO INICIAL ==================

def crear_estado_inicial(config):
    """Crea el estado inicial del juego"""
    vidas_config = config.get("sistema_vidas", {})
    
    return {
        "estado": "menu",
        "jugadores": [],
        "jugador_actual": 0,
        "resultados": {},
        "pregunta_actual": None,
        "categoria_actual": None,
        "dificultad": None,
        "preguntas_ya_preguntadas": [],
        "categorias_disponibles": [],
        "categorias_jugadas": [],
        "pregunta_num": 0,
        "puntaje_temporal": 0,
        "respuestas_correctas_temporal": 0,
        "mostrar_resultado": False,
        "respuesta_correcta": False,
        "puntaje_ganado": 0,
        "tiempo_inicio": 0,
        "tiempo_restante": config.get("Tiempo", 30),
        "animando_ruleta": False,
        "categoria_ruleta": None,
        "tiempo_ruleta": 0,
        # Sistema de vidas
        "vidas_por_categoria": {},
        "tateti_jugado_categoria": {},
        "jugadores_eliminados": [],
        "esperando_tateti": False,
        "categoria_sin_vidas": None,
        "pregunta_incorrecta": False,
        "finalizar_jugador": False,
        "vidas_por_categoria_config": vidas_config.get("vidas_por_categoria", 3),
        "permitir_tateti_vida_extra": vidas_config.get("permitir_tateti_vida_extra", True),
        "max_intentos_tateti": vidas_config.get("max_intentos_tateti_por_categoria", 1),
        "vida_extra_por_tateti": vidas_config.get("vida_extra_por_tateti", 1)
    }

def reiniciar_estado(estado, config):
    """Reinicia el estado del juego"""
    nuevo_estado = crear_estado_inicial(config)
    estado.clear()
    estado.update(nuevo_estado)

# ================== GESTIÓN DE JUGADORES ==================

def agregar_jugador(estado, nombre):
    """Agrega un jugador si es válido"""
    if (validar_nombre_jugador(nombre) and 
        len(estado["jugadores"]) < 4 and 
        nombre not in estado["jugadores"]):
        
        estado["jugadores"].append(nombre)
        estado["resultados"][nombre] = {
            "aciertos": 0,
            "porcentaje": 0,
            "puntaje": 0
        }
        estado["vidas_por_categoria"][nombre] = {}
        estado["tateti_jugado_categoria"][nombre] = {}
        
        return True
    return False

def inicializar_vidas_jugador(estado, jugador, categorias):
    """Inicializa las vidas para un jugador"""
    if jugador not in estado["vidas_por_categoria"]:
        estado["vidas_por_categoria"][jugador] = {}
        estado["tateti_jugado_categoria"][jugador] = {}
    
    vidas_iniciales = estado["vidas_por_categoria_config"]
    
    for categoria in categorias:
        estado["vidas_por_categoria"][jugador][categoria] = vidas_iniciales
        estado["tateti_jugado_categoria"][jugador][categoria] = False

def get_jugador_actual(estado):
    """Obtiene el nombre del jugador actual"""
    if estado["jugadores"]:
        return estado["jugadores"][estado["jugador_actual"]]
    return None

def cambiar_jugador(estado):
    """Cambia al siguiente jugador activo"""
    intentos = 0
    max_intentos = len(estado["jugadores"])
    
    while intentos < max_intentos:
        estado["jugador_actual"] = (estado["jugador_actual"] + 1) % len(estado["jugadores"])
        jugador_actual = get_jugador_actual(estado)
        
        if jugador_actual not in estado.get("jugadores_eliminados", []):
            reiniciar_partida_jugador(estado)
            return
        
        intentos += 1
    
    estado["estado"] = "fin_juego"

def reiniciar_partida_jugador(estado):
    """Reinicia los datos de la partida actual"""
    estado["preguntas_ya_preguntadas"] = []
    estado["categorias_disponibles"] = []
    estado["categorias_jugadas"] = []
    estado["pregunta_num"] = 0
    estado["puntaje_temporal"] = 0
    estado["respuestas_correctas_temporal"] = 0
    estado["pregunta_actual"] = None
    estado["categoria_actual"] = None
    estado["esperando_tateti"] = False
    estado["categoria_sin_vidas"] = None
    estado["finalizar_jugador"] = False

# ================== SISTEMA DE VIDAS ==================

def tiene_vidas_en_categoria(estado, jugador, categoria):
    """Verifica si el jugador tiene vidas en la categoría"""
    return estado["vidas_por_categoria"].get(jugador, {}).get(categoria, 0) > 0

def puede_jugar_tateti_categoria(estado, jugador, categoria):
    """Verifica si el jugador puede jugar tateti para recuperar vida"""
    return not estado["tateti_jugado_categoria"].get(jugador, {}).get(categoria, False)

def usar_vida_categoria(estado, jugador, categoria):
    """Reduce una vida del jugador en la categoría"""
    if jugador in estado["vidas_por_categoria"] and categoria in estado["vidas_por_categoria"][jugador]:
        estado["vidas_por_categoria"][jugador][categoria] -= 1
        vidas_restantes = estado["vidas_por_categoria"][jugador][categoria]
        return vidas_restantes > 0
    return False

def ganar_vida_tateti(estado, jugador, categoria):
    """El jugador gana una vida extra por ganar el tateti"""
    if jugador in estado["vidas_por_categoria"] and categoria in estado["vidas_por_categoria"][jugador]:
        vida_extra = estado["vida_extra_por_tateti"]
        estado["vidas_por_categoria"][jugador][categoria] = vida_extra
        estado["tateti_jugado_categoria"][jugador][categoria] = True

def marcar_tateti_jugado(estado, jugador, categoria):
    """Marca que el jugador ya jugó tateti en esta categoría"""
    if jugador in estado["tateti_jugado_categoria"]:
        estado["tateti_jugado_categoria"][jugador][categoria] = True

def jugador_tiene_categorias_disponibles(estado, jugador):
    """Verifica si el jugador tiene categorías con vidas disponibles"""
    if jugador not in estado["vidas_por_categoria"]:
        return False
    
    for categoria, vidas in estado["vidas_por_categoria"][jugador].items():
        if vidas > 0:
            return True
    return False

def obtener_categorias_con_vidas(estado, jugador):
    """Obtiene las categorías donde el jugador aún tiene vidas"""
    categorias_disponibles = []
    if jugador in estado["vidas_por_categoria"]:
        for categoria, vidas in estado["vidas_por_categoria"][jugador].items():
            if vidas > 0:
                categorias_disponibles.append(categoria)
    return categorias_disponibles

# ================== CONFIGURACIÓN ==================

def cambiar_accesibilidad(config):
    """Cambia entre modo normal y daltónico"""
    actual = config.get("Accesibilidad", "neurotipico")
    nuevo = "daltonico" if actual == "neurotipico" else "neurotipico"
    config["Accesibilidad"] = nuevo
    guardar_configuracion_local(config)
    return nuevo

def guardar_configuracion_local(config, path="PARCIAL 2/configuracion.json"):
    """Guarda la configuración en archivo JSON"""
    try:
        directorio = os.path.dirname(path)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
        
        with open(path, "w", encoding="utf-8") as archivo:
            json.dump(config, archivo, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
        return False

# ================== TIEMPO ==================

def actualizar_tiempo(estado, config):
    """Actualiza el tiempo restante"""
    if estado["tiempo_inicio"] > 0:
        transcurrido = time.time() - estado["tiempo_inicio"]
        estado["tiempo_restante"] = max(0, config.get("Tiempo", 30) - int(transcurrido))
        return estado["tiempo_restante"] > 0
    return True

# ================== CORRECCIÓN DE PARTIDAS GUARDADAS ==================

def corregir_porcentajes_partida_guardada():
    """Corrige porcentajes incorrectos en partidas guardadas existentes"""
    try:
        with open("partida_guardada.json", "r", encoding="utf-8") as archivo:
            partida = json.load(archivo)
        
        if "resultados" in partida:
            print(" Corrigiendo porcentajes en partida guardada...")
            corregidos = 0
            
            for jugador, datos in partida["resultados"].items():
                aciertos = datos.get("aciertos", 0)
                porcentaje_actual = datos.get("porcentaje", 0)
                total_preguntas = datos.get("total_preguntas", None)
                
                # Si no hay total_preguntas, intentar calcularlo
                if total_preguntas is None:
                    categorias = datos.get("categorias_jugadas", [])
                    total_preguntas = len(categorias) * 10 if categorias else aciertos
                    datos["total_preguntas"] = total_preguntas
                
                # Recalcular porcentaje correcto
                if total_preguntas > 0:
                    porcentaje_correcto = round((aciertos / total_preguntas) * 100, 1)
                else:
                    porcentaje_correcto = 0.0
                
                # Solo actualizar si hay diferencia significativa
                if abs(porcentaje_correcto - porcentaje_actual) > 0.1:
                    print(f"   {jugador}: {porcentaje_actual}% → {porcentaje_correcto}% ({aciertos}/{total_preguntas})")
                    datos["porcentaje"] = porcentaje_correcto
                    corregidos += 1
            
            # Ordenar alfabéticamente
            jugadores_ordenados = ordenar_jugadores_alfabeticamente(partida["resultados"])
            partida["jugadores"] = [nombre for nombre, datos in jugadores_ordenados]
            partida["info_ordenamiento"] = "Jugadores ordenados alfabéticamente"
            
            # Guardar archivo corregido
            if corregidos > 0:
                with open("partida_guardada.json", "w", encoding="utf-8") as archivo:
                    json.dump(partida, archivo, ensure_ascii=False, indent=2)
                print(f"✅ Partida corregida: {corregidos} porcentajes actualizados")
            else:
                print("✅ Porcentajes ya están correctos")
                
    except FileNotFoundError:
        print("ℹNo hay partida guardada para corregir")
    except Exception as e:
        print(f"❌ Error corrigiendo partida: {e}")

def guardar_partida_ordenada(jugadores, resultados):
    """Guarda la partida con jugadores ordenados alfabéticamente"""
    try:
        # Usar la función de ordenamiento
        jugadores_ordenados = ordenar_jugadores_alfabeticamente(resultados)
        
        # Extraer solo los nombres en orden alfabético
        jugadores_alfabeticos = [nombre for nombre, datos in jugadores_ordenados]
        
        # Crear la estructura de la partida
        partida = {
            "jugadores": jugadores_alfabeticos,
            "resultados": resultados,
            "fecha": str(time.time()),
            "info_ordenamiento": "Jugadores ordenados alfabéticamente"
        }
        
        # Guardar en archivo
        with open("partida_guardada.json", "w", encoding="utf-8") as archivo:
            json.dump(partida, archivo, ensure_ascii=False, indent=2)
        
        print(f" Partida guardada con {len(jugadores_alfabeticos)} jugadores (orden alfabético)")
        print(f" Orden: {', '.join(jugadores_alfabeticos)}")
        
    except Exception as e:
        print(f" Error al guardar partida: {e}")
        # Fallback: usar la función original
        guardar_partida(jugadores, resultados)

# ================== PROCESAMIENTO PRINCIPAL ==================

def procesar_estado(estado, config, preguntas, estado_interfaz, eventos):
    """Procesa el estado actual del juego con controles de música"""
    
    # Manejar controles de música de ambiente
    for evento in eventos:
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_F1:  # F1 para pausar/reanudar música
                musica.alternar_musica()
            elif evento.key == pygame.K_PLUS or evento.key == pygame.K_EQUALS:  # + para subir volumen
                musica.subir_volumen()
            elif evento.key == pygame.K_MINUS:  # - para bajar volumen
                musica.bajar_volumen()
    
    # Procesar estados del juego
    if estado["estado"] == "menu":
        procesar_menu(estado, config, estado_interfaz, eventos)
    elif estado["estado"] == "accesibilidad":
        procesar_accesibilidad(estado, config, estado_interfaz, eventos)
    elif estado["estado"] == "ingreso_jugador":
        procesar_ingreso_jugador(estado, config, estado_interfaz, eventos)
    elif estado["estado"] == "seleccionar_dificultad":
        procesar_seleccion_dificultad(estado, preguntas, config, estado_interfaz, eventos)
    elif estado["estado"] == "ruleta_categoria":
        procesar_ruleta(estado, preguntas, config, estado_interfaz, eventos)
    elif estado["estado"] == "jugar":
        procesar_juego_con_vidas(estado, config, preguntas, estado_interfaz, eventos)
    elif estado["estado"] == "mostrar_vidas":
        procesar_mostrar_vidas(estado, config, estado_interfaz, eventos, preguntas)
    elif estado["estado"] == "tateti_vida":
        procesar_tateti_vida(estado, config, estado_interfaz, eventos, preguntas)
    elif estado["estado"] == "fin_ronda":
        procesar_fin_ronda(estado, config, estado_interfaz, eventos)
    elif estado["estado"] == "fin_juego":
        procesar_fin_juego(estado, config, estado_interfaz, eventos)
    elif estado["estado"] == "historial":
        procesar_historial(estado, config, estado_interfaz, eventos)
    elif estado["estado"] == "tateti":
        procesar_tateti_normal(estado, config, estado_interfaz, eventos)

# ================== PROCESADORES DE ESTADO ==================

def procesar_menu(estado, config, estado_interfaz, eventos):
    """Procesa el menú principal"""
    import interfaz
    
    for evento in eventos:
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
    
    resultado = interfaz.mostrar_menu_principal(estado_interfaz, eventos, config)
    if resultado and resultado != "menu":
        if resultado == "jugar":
            reiniciar_estado(estado, config)
            estado["estado"] = "ingreso_jugador"
        elif resultado == "salir":
            musica.detener_musica()
            pygame.quit()
            sys.exit()
        else:
            estado["estado"] = resultado

def procesar_accesibilidad(estado, config, estado_interfaz, eventos):
    """Procesa el menú de accesibilidad"""
    import interfaz
    
    resultado = interfaz.mostrar_menu_accesibilidad(estado_interfaz, eventos, config)
    if resultado == "toggle":
        cambiar_accesibilidad(config)
    elif resultado == "menu":
        estado["estado"] = "menu"

def procesar_ingreso_jugador(estado, config, estado_interfaz, eventos):
    """Procesa el ingreso de jugadores"""
    import interfaz
    
    resultado = interfaz.mostrar_ingreso_jugador(
        estado_interfaz,
        estado["jugadores"], 
        len(estado["jugadores"]) < 4, 
        eventos,
        config
    )
    
    if resultado == "menu":
        estado["estado"] = "menu"
    elif resultado == "continuar":
        if estado["jugadores"]:
            estado["jugador_actual"] = 0
            estado["estado"] = "seleccionar_dificultad"
    elif resultado and isinstance(resultado, str) and resultado not in ["menu", "continuar", "agregar"]:
        # Es un nombre de jugador
        agregar_jugador(estado, resultado)

def procesar_seleccion_dificultad(estado, preguntas, config, estado_interfaz, eventos):
    """Procesa la selección de dificultad"""
    import interfaz
    
    jugador_actual = get_jugador_actual(estado)
    if jugador_actual in estado.get("jugadores_eliminados", []):
        cambiar_jugador(estado)
        jugador_actual = get_jugador_actual(estado)
        
        jugadores_activos = [j for j in estado["jugadores"] if j not in estado.get("jugadores_eliminados", [])]
        if len(jugadores_activos) <= 1:
            estado["estado"] = "fin_juego"
            return
    
    resultado = interfaz.mostrar_seleccion_dificultad(estado_interfaz, jugador_actual, eventos, config)
    
    if resultado in ["Fácil", "Medio", "Difícil"]:
        estado["dificultad"] = resultado
        categorias_elegidas = elegir_tres_categorias(preguntas)
        estado["categorias_disponibles"] = categorias_elegidas
        
        inicializar_vidas_jugador(estado, jugador_actual, categorias_elegidas)
        
        estado["animando_ruleta"] = True
        estado["tiempo_ruleta"] = time.time()
        estado["estado"] = "ruleta_categoria"
    elif resultado == "menu":
        estado["estado"] = "menu"

def procesar_ruleta(estado, preguntas, config, estado_interfaz, eventos):
    """Procesa la ruleta de categorías"""
    import interfaz
    
    if estado["animando_ruleta"]:
        tiempo_animacion = time.time() - estado["tiempo_ruleta"]
        if tiempo_animacion < 3:
            interfaz.mostrar_ruleta_categoria(
                estado_interfaz,
                estado["categorias_disponibles"],
                estado["categorias_jugadas"],
                tiempo_animacion,
                config
            )
        else:
            jugador_actual = get_jugador_actual(estado)
            categorias_con_vidas = obtener_categorias_con_vidas(estado, jugador_actual)
            
            if categorias_con_vidas:
                disponibles = [cat for cat in categorias_con_vidas if cat not in estado["categorias_jugadas"]]
                if not disponibles:
                    disponibles = categorias_con_vidas
                
                estado["categoria_actual"] = disponibles[0]
                estado["categorias_jugadas"].append(estado["categoria_actual"])
                estado["animando_ruleta"] = False
                estado["categoria_ruleta"] = estado["categoria_actual"]
            else:
                estado["finalizar_jugador"] = True
                estado["estado"] = "fin_ronda"
    else:
        if interfaz.mostrar_categoria_seleccionada(
            estado_interfaz,
            estado["categoria_ruleta"],
            get_jugador_actual(estado),
            eventos,
            config
        ):
            estado["pregunta_num"] = 0
            obtener_siguiente_pregunta(estado, preguntas, config)
            estado["estado"] = "jugar"

def procesar_juego_con_vidas(estado, config, preguntas, estado_interfaz, eventos):
    """Procesa el estado de juego con sistema de vidas"""
    if estado["mostrar_resultado"]:
        import interfaz
        if interfaz.mostrar_resultado_respuesta(
            estado_interfaz,
            estado["respuesta_correcta"], 
            estado["pregunta_actual"]["respuesta"],
            estado["pregunta_actual"]["opciones"], 
            estado["puntaje_ganado"], 
            eventos,
            config
        ):
            estado["mostrar_resultado"] = False
            
            if not estado["respuesta_correcta"]:
                jugador_actual = get_jugador_actual(estado)
                categoria_actual = estado["categoria_actual"]
                
                tiene_vidas = usar_vida_categoria(estado, jugador_actual, categoria_actual)
                
                if not tiene_vidas:
                    estado["categoria_sin_vidas"] = categoria_actual
                    estado["esperando_tateti"] = True
                    estado["estado"] = "mostrar_vidas"
                    return
            
            obtener_siguiente_pregunta(estado, preguntas, config)
    else:
        if estado["pregunta_actual"] is None:
            estado["estado"] = "fin_ronda"
        else:
            actualizar_tiempo(estado, config)
            
            if estado["tiempo_restante"] <= 0:
                estado["mostrar_resultado"] = True
                estado["puntaje_ganado"] = 0
                estado["respuesta_correcta"] = False
            else:
                import interfaz
                respuesta = interfaz.mostrar_pregunta(
                    estado_interfaz,
                    estado["pregunta_actual"], 
                    estado["categoria_actual"],
                    estado["pregunta_num"], 
                    10, 
                    estado["puntaje_temporal"],
                    eventos, 
                    estado["tiempo_restante"], 
                    get_jugador_actual(estado),
                    config
                )
                
                if respuesta == "menu":
                    estado["estado"] = "menu"
                elif respuesta in ["1", "2", "3", "4"]:
                    procesar_respuesta_con_vidas(estado, config, respuesta)

def procesar_respuesta_con_vidas(estado, config, respuesta):
    """Procesa la respuesta del jugador"""
    if respuesta and str(respuesta) == str(estado["pregunta_actual"]["respuesta"]):
        estado["respuesta_correcta"] = True
        estado["puntaje_ganado"] = config["puntaje_por_dificultad"][estado["dificultad"]]
        estado["puntaje_temporal"] += estado["puntaje_ganado"]
        estado["respuestas_correctas_temporal"] += 1
    else:
        estado["respuesta_correcta"] = False
        estado["puntaje_ganado"] = 0
    
    estado["mostrar_resultado"] = True

def procesar_mostrar_vidas(estado, config, estado_interfaz, eventos, preguntas):
    """Procesa la pantalla que muestra las vidas y opción de tateti"""
    resultado = mostrar_estado_vidas(estado_interfaz, estado, eventos, config)
    
    if resultado == "tateti":
        estado["estado"] = "tateti_vida"
    elif resultado == "continuar":
        jugador_actual = get_jugador_actual(estado)
        if jugador_tiene_categorias_disponibles(estado, jugador_actual):
            estado["estado"] = "ruleta_categoria"
            estado["animando_ruleta"] = True
            estado["tiempo_ruleta"] = time.time()
        else:
            estado["finalizar_jugador"] = True
            estado["estado"] = "fin_ronda"
    elif resultado == "menu":
        estado["estado"] = "menu"

def procesar_tateti_vida(estado, config, estado_interfaz, eventos, preguntas):
    """Procesa el tateti para ganar vida extra"""
    jugador_actual = get_jugador_actual(estado)
    categoria_sin_vidas = estado["categoria_sin_vidas"]
    
    try:
        import tateti_pygame_matriz as tateti
        resultado = tateti.mostrar_tateti_pygame_matriz(estado_interfaz, eventos, config, 'vs_maquina', jugador_actual)
    except ImportError:
        print("❌ No se encontró el módulo de tateti")
        estado["esperando_tateti"] = False
        estado["categoria_sin_vidas"] = None
        estado["estado"] = "ruleta_categoria"
        estado["animando_ruleta"] = True
        estado["tiempo_ruleta"] = time.time()
        return
    
    if resultado == 'vida_extra_ganada':
        ganar_vida_tateti(estado, jugador_actual, categoria_sin_vidas)
        estado["esperando_tateti"] = False
        estado["categoria_sin_vidas"] = None
        estado["estado"] = "jugar"
        obtener_siguiente_pregunta(estado, preguntas, config)
        
    elif resultado == 'vida_extra_perdida':
        marcar_tateti_jugado(estado, jugador_actual, categoria_sin_vidas)
        estado["esperando_tateti"] = False
        estado["categoria_sin_vidas"] = None
        
        if jugador_tiene_categorias_disponibles(estado, jugador_actual):
            estado["estado"] = "ruleta_categoria"
            estado["animando_ruleta"] = True
            estado["tiempo_ruleta"] = time.time()
        else:
            estado["finalizar_jugador"] = True
            estado["estado"] = "fin_ronda"

def procesar_tateti_normal(estado, config, estado_interfaz, eventos):
    """Procesa el minijuego de tateti normal"""
    try:
        import tateti_pygame_matriz as tateti
        resultado = tateti.mostrar_tateti_pygame_matriz(estado_interfaz, eventos, config)
        
        if resultado == "salir" or resultado == "menu":
            estado["estado"] = "menu"
        elif resultado != "tateti":
            estado["estado"] = resultado if resultado in ["menu", "historial", "accesibilidad"] else "menu"
            
    except ImportError:
        print("❌ No se encontró el módulo de tateti")
        estado["estado"] = "menu"

def procesar_fin_ronda(estado, config, estado_interfaz, eventos):
    """Procesa el fin de una ronda"""
    if estado.get("finalizar_jugador", False):
        finalizar_jugador_con_vidas(estado)
    else:
        import interfaz
        resultado = interfaz.mostrar_fin_categoria(
            estado_interfaz,
            estado["categoria_actual"],
            estado["respuestas_correctas_temporal"],
            estado["puntaje_temporal"],
            eventos,
            config
        )
        if resultado == "continuar":
            estado["animando_ruleta"] = True
            estado["tiempo_ruleta"] = time.time()
            estado["estado"] = "ruleta_categoria"
        elif resultado == "menu":
            estado["estado"] = "menu"

def procesar_fin_juego(estado, config, estado_interfaz, eventos):
    """Procesa el fin del juego con guardado ordenado alfabéticamente"""
    import interfaz
    
    resultado = interfaz.mostrar_resultados_finales(
        estado_interfaz,
        estado["jugadores"],
        estado["resultados"],
        eventos,
        config
    )
    
    if resultado == "menu":
        guardar_partida_ordenada(estado["jugadores"], estado["resultados"])
        estado["estado"] = "menu"
    elif resultado == "nuevo":
        guardar_partida_ordenada(estado["jugadores"], estado["resultados"])
        reiniciar_estado(estado, config)
        estado["estado"] = "ingreso_jugador"

def procesar_historial(estado, config, estado_interfaz, eventos):
    """Procesa el historial"""
    import interfaz
    resultado = interfaz.mostrar_historial(estado_interfaz, eventos, config)
    if resultado != "historial":
        estado["estado"] = resultado

# ================== FINALIZACIÓN DE JUGADORES ==================

def finalizar_jugador_con_vidas(estado):
    """Finaliza la partida del jugador actual guardando estadísticas con cálculos corregidos"""
    jugador = get_jugador_actual(estado)
    
    # Calcular correctamente el total de preguntas respondidas
    total_preguntas_respondidas = estado["pregunta_num"]
    aciertos = estado["respuestas_correctas_temporal"]
    
    # Calcular porcentaje correcto (aciertos/total * 100)
    if total_preguntas_respondidas > 0:
        porcentaje = round((aciertos / total_preguntas_respondidas) * 100, 1)
    else:
        porcentaje = 0.0
    
    estado["resultados"][jugador] = {
        "aciertos": aciertos,
        "porcentaje": porcentaje,
        "puntaje": estado["puntaje_temporal"],
        "categorias_jugadas": estado["categorias_jugadas"].copy(),
        "total_preguntas": total_preguntas_respondidas
    }
    
    print(f"📊 {jugador} finalizado:")
    print(f"   Aciertos: {aciertos}/{total_preguntas_respondidas}")
    print(f"   Porcentaje: {porcentaje}%")
    print(f"   Puntaje: {estado['puntaje_temporal']}")
    
    jugadores_activos = [j for j in estado["jugadores"] if j not in estado.get("jugadores_eliminados", [])]
    jugador_indice_actual = estado["jugador_actual"]
    
    if jugador_indice_actual < len(estado["jugadores"]) - 1:
        cambiar_jugador(estado)
        if len(jugadores_activos) > 1:
            estado["estado"] = "seleccionar_dificultad"
        else:
            estado["estado"] = "fin_juego"
    else:
        estado["estado"] = "fin_juego"

# ================== FUNCIONES AUXILIARES ==================

def obtener_siguiente_pregunta(estado, preguntas, config):
    """Obtiene la siguiente pregunta o cambia de categoría"""
    if estado["pregunta_num"] >= 10:
        jugador_actual = get_jugador_actual(estado)
        if jugador_tiene_categorias_disponibles(estado, jugador_actual):
            estado["estado"] = "ruleta_categoria"
            estado["animando_ruleta"] = True
            estado["tiempo_ruleta"] = time.time()
        else:
            estado["finalizar_jugador"] = True
            estado["estado"] = "fin_ronda"
        return
    
    pregunta = obtener_pregunta_aleatoria(
        preguntas, 
        estado["categoria_actual"], 
        estado["dificultad"],
        estado["preguntas_ya_preguntadas"], 
        config["permitir_repetir_preguntas"]
    )
    
    if pregunta:
        estado["pregunta_actual"] = pregunta
        estado["pregunta_num"] += 1
        estado["tiempo_inicio"] = time.time()
        estado["tiempo_restante"] = config.get("Tiempo", 30)
    else:
        jugador_actual = get_jugador_actual(estado)
        if jugador_tiene_categorias_disponibles(estado, jugador_actual):
            estado["estado"] = "ruleta_categoria"
            estado["animando_ruleta"] = True
            estado["tiempo_ruleta"] = time.time()
        else:
            estado["finalizar_jugador"] = True
            estado["estado"] = "fin_ronda"

def mostrar_estado_vidas(estado_interfaz, estado, eventos, config):
    """Muestra el estado de vidas y opción de tateti"""
    import pygame
    from configuracion import obtener_colores
    import interfaz
    
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    textos_config = config.get("textos", {})
    fuentes_config = config.get("interfaz", {}).get("fuentes", {})
    
    font_titulo = interfaz.get_font(font_cache, fuentes_config.get("titulo", 40))
    font_texto = interfaz.get_font(font_cache, fuentes_config.get("texto", 28))
    font_info = interfaz.get_font(font_cache, fuentes_config.get("texto_pequeño", 24))
    
    interfaz.dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=100)
    
    jugador_actual = get_jugador_actual(estado)
    categoria_sin_vidas = estado["categoria_sin_vidas"]
    
    titulo = textos_config.get("sin_vidas_categoria", "¡SIN VIDAS EN CATEGORÍA!")
    interfaz.centrar_texto(pantalla, titulo, font_titulo, colores.get("ROJO", [200, 0, 0]), 60)
    interfaz.centrar_texto(pantalla, f"{jugador_actual} - {categoria_sin_vidas}", font_texto, colores.get("NEGRO", [0, 0, 0]), 120)
    
    y_pos = 180
    estado_texto = textos_config.get("estado_vidas", "Estado de vidas por categoría:")
    interfaz.centrar_texto(pantalla, estado_texto, font_info, colores.get("NEGRO", [0, 0, 0]), y_pos)
    y_pos += 40
    
    if jugador_actual in estado["vidas_por_categoria"]:
        for categoria, vidas in estado["vidas_por_categoria"][jugador_actual].items():
            if vidas > 0:
                color_vidas = colores.get("VERDE", [0, 150, 0])
                texto_template = textos_config.get("vidas_restantes", "❤️ {categoria}: {vidas} vidas")
                texto_vidas = texto_template.format(categoria=categoria, vidas=vidas)
            else:
                color_vidas = colores.get("ROJO", [200, 0, 0])
                tateti_jugado = estado["tateti_jugado_categoria"][jugador_actual].get(categoria, False)
                if tateti_jugado:
                    texto_vidas = textos_config.get("sin_vidas_tateti_usado", "💀 {categoria}: Sin vidas (tateti usado)").format(categoria=categoria)
                else:
                    texto_vidas = textos_config.get("sin_vidas", "💀 {categoria}: Sin vidas").format(categoria=categoria)
            
            interfaz.centrar_texto(pantalla, texto_vidas, font_info, color_vidas, y_pos)
            y_pos += 30
    
    y_pos += 20
    puede_tateti = puede_jugar_tateti_categoria(estado, jugador_actual, categoria_sin_vidas) and estado["permitir_tateti_vida_extra"]
    
    if puede_tateti:
        pregunta_tateti = textos_config.get("pregunta_tateti", "¿Quieres jugar tateti para ganar una vida extra?")
        interfaz.centrar_texto(pantalla, pregunta_tateti, font_info, colores.get("NEGRO", [0, 0, 0]), y_pos)
        y_pos += 30
        interfaz.centrar_texto(pantalla, "Si ganas, recuperas 1 vida en esta categoría", font_info, colores.get("AZUL", [0, 100, 200]), y_pos)
        y_pos += 50
        
        boton_tateti = interfaz.dibujar_boton(pantalla, 150, y_pos, 180, 50, "JUGAR TATETI", 
                                             colores.get("VERDE", [0, 150, 0]), 
                                             colores.get("BLANCO", [255, 255, 255]), 
                                             colores.get("VERDE_HOVER", [50, 200, 50]), font_texto)
        
        boton_continuar = interfaz.dibujar_boton(pantalla, 470, y_pos, 180, 50, "CONTINUAR", 
                                                colores.get("AZUL", [0, 100, 200]), 
                                                colores.get("BLANCO", [255, 255, 255]), 
                                                colores.get("AZUL_HOVER", [50, 150, 255]), font_texto)
        
        botones = [('tateti', boton_tateti), ('continuar', boton_continuar)]
    else:
        tateti_usado_texto = textos_config.get("tateti_usado", "Ya jugaste tateti en esta categoría")
        interfaz.centrar_texto(pantalla, tateti_usado_texto, font_info, colores.get("GRIS", [128, 128, 128]), y_pos)
        y_pos += 50
        
        boton_continuar = interfaz.dibujar_boton(pantalla, 310, y_pos, 180, 50, "CONTINUAR", 
                                                colores.get("AZUL", [0, 100, 200]), 
                                                colores.get("BLANCO", [255, 255, 255]), 
                                                colores.get("AZUL_HOVER", [50, 150, 255]), font_texto)
        
        botones = [('continuar', boton_continuar)]
    
    boton_menu = interfaz.dibujar_boton(pantalla, 50, 520, 120, 40, "MENÚ", 
                                       colores.get("GRIS", [128, 128, 128]), 
                                       colores.get("BLANCO", [255, 255, 255]), 
                                       colores.get("GRIS_HOVER", [180, 180, 180]), font_info)
    botones.append(('menu', boton_menu))
    
    for evento in eventos:
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "menu"
            elif evento.key == pygame.K_t and puede_tateti:
                return "tateti"
            elif evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                return "continuar"
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos_mouse = pygame.mouse.get_pos()
            for accion, boton in botones:
                if boton.collidepoint(pos_mouse):
                    return accion
    
    return None
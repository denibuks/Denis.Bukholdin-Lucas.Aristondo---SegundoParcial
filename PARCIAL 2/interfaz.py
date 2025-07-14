# interfaz.py - INTERFAZ COMPLETAMENTE CORREGIDA

import pygame
import math
import time
import json
import sys
from configuracion import obtener_colores

def inicializar_interfaz(pantalla):
    """Inicializa la interfaz del juego"""
    estado_interfaz = {
        'pantalla': pantalla,
        'font_cache': {},
        'texto_ingreso': "",
        'cursor_visible': True,
        'tiempo_cursor': 0,
        'imagen_fondo': cargar_imagen_fondo(pantalla)
    }
    return estado_interfaz

def cargar_imagen_fondo(pantalla):
    """Carga la imagen de fondo o usa color sólido"""
    try:
        config = cargar_configuracion_simple()
        ruta_imagen = config.get("archivos", {}).get("imagen_fondo", "PARCIAL 2/imagenes/fondo.png")
        
        imagen_fondo = pygame.image.load(ruta_imagen)
        imagen_fondo = pygame.transform.scale(imagen_fondo, pantalla.get_size())
    except (pygame.error, FileNotFoundError, KeyError):
        try:
            config = cargar_configuracion_simple()
            color_fondo = config.get("colores", {}).get("normal", {}).get("FONDO_DEFAULT", [173, 216, 230])
        except:
            color_fondo = [173, 216, 230]
        
        imagen_fondo = pygame.Surface(pantalla.get_size())
        imagen_fondo.fill(color_fondo)
    return imagen_fondo

def cargar_configuracion_simple():
    """Carga configuración de manera simple"""
    try:
        import json
        with open("PARCIAL 2/configuracion.json", "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except:
        return {}

def get_font(font_cache, size):
    """Cache de fuentes para mejor rendimiento"""
    if size not in font_cache:
        font_cache[size] = pygame.font.Font(None, size)
    return font_cache[size]

def dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=None):
    """Dibuja el fondo con overlay opcional"""
    pantalla.blit(imagen_fondo, (0, 0))
    if overlay_alpha:
        overlay = pygame.Surface(pantalla.get_size())
        overlay.set_alpha(overlay_alpha)
        overlay.fill((255, 255, 255))
        pantalla.blit(overlay, (0, 0))

def dibujar_boton(pantalla, x, y, ancho, alto, texto, color_fondo, color_texto, color_hover, font):
    """Dibuja un botón con efectos hover mejorados"""
    mouse_pos = pygame.mouse.get_pos()
    boton_rect = pygame.Rect(x, y, ancho, alto)
    mouse_over = boton_rect.collidepoint(mouse_pos)
    
    color_actual = color_hover if mouse_over else color_fondo
    
    # Sombra para efecto 3D
    if mouse_over:
        sombra_rect = pygame.Rect(x+3, y+3, ancho, alto)
        pygame.draw.rect(pantalla, (50, 50, 50), sombra_rect)
    
    # Dibujar botón
    pygame.draw.rect(pantalla, color_actual, boton_rect)
    pygame.draw.rect(pantalla, (0, 0, 0), boton_rect, 2)
    
    # Texto centrado
    texto_renderizado = font.render(texto, True, color_texto)
    texto_rect = texto_renderizado.get_rect(center=boton_rect.center)
    pantalla.blit(texto_renderizado, texto_rect)
    
    return boton_rect

def centrar_texto(pantalla, texto, font, color, y):
    """Centra texto horizontalmente en la pantalla"""
    texto_renderizado = font.render(texto, True, color)
    x = (pantalla.get_width() - texto_renderizado.get_width()) // 2
    pantalla.blit(texto_renderizado, (x, y))

def dibujar_cuenta_regresiva(pantalla, tiempo_restante, config, tiempo_total=30):
    """Dibuja el contador de tiempo circular"""
    colores = obtener_colores(config)
    
    contador_config = config.get("interfaz", {}).get("posiciones", {}).get("contador_tiempo", {})
    centro_x = contador_config.get("x", 750)
    centro_y = contador_config.get("y", 93)
    radio = contador_config.get("radio", 35)
    
    animaciones_config = config.get("interfaz", {}).get("animaciones", {})
    pulso_velocidad = animaciones_config.get("pulso_tiempo_critico", 10)
    
    progreso = tiempo_restante / tiempo_total if tiempo_total > 0 else 0
    
    # Colores según el tiempo restante
    if tiempo_restante <= 5:
        color_circulo = colores.get("TIEMPO_CRITICO", [200, 0, 0])
        color_texto = colores.get("BLANCO", [255, 255, 255])
        color_borde = tuple(max(0, c - 50) for c in color_circulo)
    elif tiempo_restante <= 10:
        color_circulo = colores.get("TIEMPO_ADVERTENCIA", [255, 165, 0])
        color_texto = colores.get("NEGRO", [0, 0, 0])
        color_borde = tuple(max(0, c - 50) for c in color_circulo)
    else:
        color_circulo = colores.get("TIEMPO_NORMAL", [0, 150, 0])
        color_texto = colores.get("NEGRO", [0, 0, 0])
        color_borde = tuple(max(0, c - 50) for c in color_circulo)
    
    # Fondo del círculo
    pygame.draw.circle(pantalla, colores.get("GRIS_CLARO", [220, 220, 220]), (centro_x, centro_y), radio)
    pygame.draw.circle(pantalla, color_borde, (centro_x, centro_y), radio, 3)
    
    # Progreso circular
    if tiempo_restante > 0 and progreso > 0:
        angulo = 2 * math.pi * progreso
        puntos = [(centro_x, centro_y)]
        num_puntos = max(int(angulo * 30), 3)
        
        for i in range(num_puntos + 1):
            angle = -math.pi/2 + (angulo * i / num_puntos)
            px = centro_x + (radio - 2) * math.cos(angle)
            py = centro_y + (radio - 2) * math.sin(angle)
            puntos.append((px, py))
        
        if len(puntos) > 2:
            pygame.draw.polygon(pantalla, color_circulo, puntos)
    
    # Texto del tiempo
    font = pygame.font.Font(None, 28)
    texto = font.render(str(tiempo_restante), True, color_texto)
    texto_rect = texto.get_rect(center=(centro_x, centro_y))
    pantalla.blit(texto, texto_rect)
    
    # Label "TIEMPO"
    font_pequeño = pygame.font.Font(None, 16)
    color_label = colores.get("TIEMPO_CRITICO", [200, 0, 0]) if tiempo_restante <= 5 else colores.get("NEGRO", [0, 0, 0])
    texto_label = font_pequeño.render("TIEMPO", True, color_label)
    label_rect = texto_label.get_rect(center=(centro_x, centro_y + 40))
    pantalla.blit(texto_label, label_rect)
    
    # Efecto de pulso cuando el tiempo es crítico
    if tiempo_restante <= 5:
        pulso = int(time.time() * pulso_velocidad) % 2
        if pulso:
            pygame.draw.circle(pantalla, colores.get("TIEMPO_CRITICO", [200, 0, 0]), (centro_x, centro_y), radio + 5, 2)

def mostrar_menu_principal(estado_interfaz, eventos, config):
    """Muestra el menú principal completamente funcional"""
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    textos_config = config.get("textos", {})
    fuentes_config = config.get("interfaz", {}).get("fuentes", {})
    botones_config = config.get("interfaz", {}).get("posiciones", {}).get("menu_botones", {})
    
    font_titulo = get_font(font_cache, fuentes_config.get("titulo", 48))
    font_opciones = get_font(font_cache, fuentes_config.get("subtitulo", 36))
    font_info = get_font(font_cache, fuentes_config.get("texto_pequeño", 24))
    font_pequeño = get_font(font_cache, fuentes_config.get("muy_pequeño", 18))
    
    dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=50)
    
    # Títulos desde configuración
    titulo_principal = textos_config.get("titulo_principal", "JUEGO DE PREGUNTAS")
    subtitulo_vidas = textos_config.get("subtitulo_vidas", "🎮 Con Sistema de Vidas")
    info_vidas = textos_config.get("info_vidas", "💖 3 vidas por categoría | 🎯 Tateti para vida extra")
    
    centrar_texto(pantalla, titulo_principal, font_titulo, colores.get("NEGRO", [0, 0, 0]), 60)
    centrar_texto(pantalla, subtitulo_vidas, font_info, colores.get("AZUL", [0, 100, 200]), 100)
    centrar_texto(pantalla, "Selecciona una opción:", font_opciones, colores.get("NEGRO", [0, 0, 0]), 140)
    
    # Configuración de botones desde JSON
    x_botones = botones_config.get("x", 300)
    y_inicial = botones_config.get("y_inicial", 190)
    ancho_boton = botones_config.get("ancho", 200)
    alto_boton = botones_config.get("alto", 55)
    separacion = botones_config.get("separacion", 65)
    
    botones = [
        (x_botones, y_inicial, ancho_boton, alto_boton, "JUGAR", colores.get("BOTON_JUGAR", [80, 200, 255]), "jugar"),
        (x_botones, y_inicial + separacion, ancho_boton, alto_boton, "TATETI", colores.get("VERDE", [0, 150, 0]), "tateti"),
        (x_botones, y_inicial + separacion*2, ancho_boton, alto_boton, "HISTORIAL", colores.get("BOTON_HISTORIAL", [255, 200, 0]), "historial"),
        (x_botones, y_inicial + separacion*3, ancho_boton, alto_boton, "ACCESIBILIDAD", colores.get("BOTON_ACCESIBILIDAD", [150, 100, 255]), "accesibilidad"),
        (x_botones, y_inicial + separacion*4, ancho_boton, alto_boton, "SALIR", colores.get("BOTON_SALIR", [255, 100, 100]), "salir")
    ]
    
    botones_rect = []
    for x, y, w, h, texto, color, accion in botones:
        color_hover = tuple(min(255, max(0, c + 30)) for c in color)
        rect = dibujar_boton(pantalla, x, y, w, h, texto, color, colores.get("NEGRO", [0, 0, 0]), color_hover, font_opciones)
        botones_rect.append((rect, accion))
    
    # Info sobre sistema de vidas
    centrar_texto(pantalla, info_vidas, font_pequeño, colores.get("GRIS", [128, 128, 128]), 520)
    
    # Procesar eventos
    for evento in eventos:
        if evento.type == pygame.QUIT:
            return "salir"
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "salir"
            elif evento.key == pygame.K_1:
                return "jugar"
            elif evento.key == pygame.K_2:
                return "tateti"
            elif evento.key == pygame.K_3:
                return "historial"
            elif evento.key == pygame.K_4:
                return "accesibilidad"
            elif evento.key == pygame.K_5:
                return "salir"
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos_mouse = pygame.mouse.get_pos()
            for rect, accion in botones_rect:
                if rect.collidepoint(pos_mouse):
                    return accion
    
    return "menu"

def mostrar_menu_accesibilidad(estado_interfaz, eventos, config):
    """Muestra el menú de accesibilidad"""
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    font_titulo = get_font(font_cache, 40)
    font_texto = get_font(font_cache, 32)
    font_info = get_font(font_cache, 24)
    font_pequeño = get_font(font_cache, 20)
    
    dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
    centrar_texto(pantalla, "CONFIGURACIÓN DE ACCESIBILIDAD", font_titulo, colores.get("NEGRO", [0, 0, 0]), 60)
    
    modo_actual = config.get("Accesibilidad", "neurotipico")
    
    if modo_actual == "daltonico":
        texto_modo = "🔵 MODO DALTÓNICO ACTIVADO"
        color_modo = (0, 150, 200)
        info_color = "Se han aplicado cambios de colores para daltonismo"
    else:
        texto_modo = "🟢 MODO NORMAL ACTIVADO"  
        color_modo = (0, 150, 0)
        info_color = "Colores estándar activos"
    
    centrar_texto(pantalla, texto_modo, font_texto, color_modo, 120)
    centrar_texto(pantalla, info_color, font_pequeño, colores.get("NEGRO", [0, 0, 0]), 160)
    
    info_lines = [
        "",
        "Cambios aplicados en modo daltónico:",
        "• Verdes → Azules para mejor distinción",
        "• Rojos → Naranjas/Marrones más visibles", 
        "• Mayor contraste en elementos importantes",
        "• Optimizado para daltonismo rojo-verde"
    ]
    
    y_pos = 200
    for linea in info_lines:
        if linea:
            centrar_texto(pantalla, linea, font_info, colores.get("NEGRO", [0, 0, 0]), y_pos)
        y_pos += 25
    
    if modo_actual == "daltonico":
        color_boton_toggle = (0, 150, 200)
        color_hover_toggle = (30, 180, 255)
        texto_boton = "VOLVER A NORMAL"
    else:
        color_boton_toggle = (255, 150, 0)
        color_hover_toggle = (255, 180, 50)
        texto_boton = "ACTIVAR MODO DALTÓNICO"
    
    boton_toggle = dibujar_boton(pantalla, 200, 480, 400, 50, texto_boton, color_boton_toggle, (255, 255, 255), color_hover_toggle, font_texto)
    boton_volver = dibujar_boton(pantalla, 250, 540, 300, 40, "VOLVER AL MENÚ", colores.get("GRIS_CLARO", [220, 220, 220]), colores.get("NEGRO", [0, 0, 0]), colores.get("GRIS_HOVER", [180, 180, 180]), font_info)
    
    for evento in eventos:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos_mouse = pygame.mouse.get_pos()
            if boton_toggle.collidepoint(pos_mouse):
                return "toggle"
            elif boton_volver.collidepoint(pos_mouse):
                return "menu"
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "menu"
            elif evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                return "toggle"
    
    return "accesibilidad"

def mostrar_ingreso_jugador(estado_interfaz, jugadores_actuales, puede_agregar, eventos, config):
    """Muestra la pantalla de ingreso de jugadores corregida"""
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    
    font_titulo = get_font(font_cache, 40)
    font_texto = get_font(font_cache, 32)
    font_pequeño = get_font(font_cache, 24)
    
    dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
    centrar_texto(pantalla, "INGRESO DE JUGADORES", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
    centrar_texto(pantalla, f"Jugadores registrados: {len(jugadores_actuales)}/4", font_texto, colores.get("NEGRO", [0, 0, 0]), 120)
    
    # Mostrar lista de jugadores
    y_pos = 170
    colores_jugadores = [
        colores.get("JUGADOR_1", [0, 100, 200]),
        colores.get("JUGADOR_2", [0, 150, 0]),
        colores.get("JUGADOR_3", [255, 165, 0]),
        colores.get("JUGADOR_4", [200, 0, 0])
    ]
    for i, jugador in enumerate(jugadores_actuales):
        color = colores_jugadores[i]
        texto = f"Jugador {i+1}: {jugador}"
        centrar_texto(pantalla, texto, font_texto, color, y_pos)
        y_pos += 35
    
    # Campo de entrada si se puede agregar
    if puede_agregar and len(jugadores_actuales) < 4:
        y_entrada = 320
        centrar_texto(pantalla, f"Ingresa el nombre del Jugador {len(jugadores_actuales) + 1}:", font_pequeño, colores.get("NEGRO", [0, 0, 0]), y_entrada - 30)
        
        entrada_rect = pygame.Rect(250, y_entrada, 300, 50)
        pygame.draw.rect(pantalla, colores.get("BLANCO", [255, 255, 255]), entrada_rect)
        pygame.draw.rect(pantalla, colores.get("NEGRO", [0, 0, 0]), entrada_rect, 2)
        
        # Cursor parpadeante
        if time.time() - estado_interfaz['tiempo_cursor'] > 0.5:
            estado_interfaz['cursor_visible'] = not estado_interfaz['cursor_visible']
            estado_interfaz['tiempo_cursor'] = time.time()
        
        texto_mostrar = estado_interfaz['texto_ingreso'] + ("|" if estado_interfaz['cursor_visible'] else "")
        texto_render = font_texto.render(texto_mostrar, True, colores.get("NEGRO", [0, 0, 0]))
        texto_rect = texto_render.get_rect(center=entrada_rect.center)
        pantalla.blit(texto_render, texto_rect)
        
        centrar_texto(pantalla, "Presiona ENTER para confirmar", font_pequeño, colores.get("NEGRO", [0, 0, 0]), y_entrada + 70)
    
    # Botones
    y_botones = 450
    botones = []
    
    if jugadores_actuales:
        if len(jugadores_actuales) < 4:
            boton_agregar = dibujar_boton(pantalla, 150, y_botones, 160, 40, "AGREGAR MÁS", colores.get("AZUL", [0, 100, 200]), colores.get("BLANCO", [255, 255, 255]), colores.get("AZUL_HOVER", [50, 150, 255]), font_pequeño)
            botones.append(("agregar", boton_agregar))
        
        boton_iniciar = dibujar_boton(pantalla, 330, y_botones, 160, 40, "INICIAR JUEGO", colores.get("VERDE", [0, 150, 0]), colores.get("BLANCO", [255, 255, 255]), colores.get("VERDE_HOVER", [50, 200, 50]), font_pequeño)
        botones.append(("continuar", boton_iniciar))
    
    boton_volver = dibujar_boton(pantalla, 510, y_botones, 140, 40, "VOLVER", colores.get("GRIS", [128, 128, 128]), colores.get("BLANCO", [255, 255, 255]), colores.get("GRIS_HOVER", [180, 180, 180]), font_pequeño)
    botones.append(("menu", boton_volver))
    
    # Procesar eventos
    for evento in eventos:
        if evento.type == pygame.KEYDOWN:
            if puede_agregar and len(jugadores_actuales) < 4:
                if evento.key == pygame.K_BACKSPACE:
                    estado_interfaz['texto_ingreso'] = estado_interfaz['texto_ingreso'][:-1]
                elif evento.key == pygame.K_RETURN and estado_interfaz['texto_ingreso'].strip():
                    nombre = estado_interfaz['texto_ingreso'].strip()
                    estado_interfaz['texto_ingreso'] = ""
                    return nombre
                elif evento.unicode and len(evento.unicode) == 1 and evento.unicode.isalpha() and len(estado_interfaz['texto_ingreso']) < 15:
                    estado_interfaz['texto_ingreso'] += evento.unicode
            
            if evento.key == pygame.K_ESCAPE:
                return "menu"
        
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos_mouse = pygame.mouse.get_pos()
            for accion, boton in botones:
                if boton.collidepoint(pos_mouse):
                    return accion
    
    return None

def mostrar_seleccion_dificultad(estado_interfaz, jugador, eventos, config):
    """Muestra la selección de dificultad"""
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    fuentes_config = config.get("interfaz", {}).get("fuentes", {})
    sistema_vidas = config.get("sistema_vidas", {})
    
    font_titulo = get_font(font_cache, fuentes_config.get("titulo", 40))
    font_opciones = get_font(font_cache, fuentes_config.get("texto", 32))
    font_info = get_font(font_cache, fuentes_config.get("texto_pequeño", 24))
    
    dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
    centrar_texto(pantalla, f"Turno de: {jugador}", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
    centrar_texto(pantalla, "SELECCIONA LA DIFICULTAD", font_titulo, colores.get("NEGRO", [0, 0, 0]), 120)
    
    # Mostrar información de vidas
    vidas_por_categoria = sistema_vidas.get("vidas_por_categoria", 3)
    info_vidas = f"💖 Tendrás {vidas_por_categoria} vidas por categoría"
    centrar_texto(pantalla, info_vidas, font_info, colores.get("AZUL", [0, 100, 200]), 160)
    
    # Obtener puntajes
    puntajes = config.get("puntaje_por_dificultad", {"Fácil": 10, "Medio": 20, "Difícil": 30})
    
    botones = [
        (250, 200, 300, 60, f"FÁCIL - {puntajes['Fácil']} puntos", colores.get("BOTON_FACIL", [144, 238, 144]), "Fácil"),
        (250, 280, 300, 60, f"MEDIO - {puntajes['Medio']} puntos", colores.get("BOTON_MEDIO", [255, 255, 0]), "Medio"),
        (250, 360, 300, 60, f"DIFÍCIL - {puntajes['Difícil']} puntos", colores.get("BOTON_DIFICIL", [255, 182, 193]), "Difícil"),
        (250, 450, 300, 40, "VOLVER AL MENÚ", colores.get("GRIS_CLARO", [220, 220, 220]), "menu")
    ]
    
    botones_rect = []
    for x, y, w, h, texto, color, accion in botones:
        color_hover = tuple(min(255, c + 50) for c in color)
        rect = dibujar_boton(pantalla, x, y, w, h, texto, color, colores.get("NEGRO", [0, 0, 0]), color_hover, font_opciones)
        botones_rect.append((rect, accion))
    
    # Procesar eventos
    for evento in eventos:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos_mouse = pygame.mouse.get_pos()
            for rect, accion in botones_rect:
                if rect.collidepoint(pos_mouse):
                    return accion
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_1:
                return "Fácil"
            elif evento.key == pygame.K_2:
                return "Medio"
            elif evento.key == pygame.K_3:
                return "Difícil"
            elif evento.key == pygame.K_ESCAPE:
                return "menu"
    
    return None

def mostrar_ruleta_categoria(estado_interfaz, categorias_disponibles, categorias_jugadas, tiempo_animacion, config):
    """Muestra la ruleta de categorías animada"""
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    
    dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=100)
    
    font_titulo = get_font(font_cache, 48)
    font_categoria = get_font(font_cache, 28)
    
    centrar_texto(pantalla, "RULETA DE CATEGORÍAS", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
    
    centro_x, centro_y = 400, 300
    radio = 150
    
    categorias_ruleta = [cat for cat in categorias_disponibles if cat not in categorias_jugadas]
    
    if not categorias_ruleta:
        return
    
    velocidad = max(1, 10 - tiempo_animacion * 3)
    angulo_rotacion = tiempo_animacion * velocidad * 360
    
    num_categorias = len(categorias_ruleta)
    angulo_seccion = 360 / num_categorias
    
    colores_ruleta = [
        colores.get("RULETA_COLOR_1", [144, 238, 144]), 
        colores.get("RULETA_COLOR_2", [255, 255, 0]), 
        colores.get("RULETA_COLOR_3", [255, 182, 193]), 
        colores.get("RULETA_COLOR_4", [173, 216, 230]), 
        colores.get("RULETA_COLOR_5", [255, 165, 0]), 
        colores.get("RULETA_COLOR_6", [220, 220, 220])
    ]
    
    for i in range(num_categorias):
        angulo_inicio = i * angulo_seccion + angulo_rotacion
        angulo_fin = (i + 1) * angulo_seccion + angulo_rotacion
        
        puntos = [(centro_x, centro_y)]
        for angulo in range(int(angulo_inicio), int(angulo_fin) + 1):
            x = centro_x + radio * math.cos(math.radians(angulo))
            y = centro_y + radio * math.sin(math.radians(angulo))
            puntos.append((x, y))
        
        if len(puntos) > 2:
            color_seccion = colores_ruleta[i % len(colores_ruleta)]
            pygame.draw.polygon(pantalla, color_seccion, puntos)
            pygame.draw.polygon(pantalla, colores.get("NEGRO", [0, 0, 0]), puntos, 3)
        
        angulo_texto = math.radians(angulo_inicio + angulo_seccion / 2)
        texto_x = centro_x + (radio * 0.6) * math.cos(angulo_texto)
        texto_y = centro_y + (radio * 0.6) * math.sin(angulo_texto)
        
        nombre_cat = categorias_ruleta[i]
        if len(nombre_cat) > 10:
            nombre_cat = nombre_cat[:8] + ".."
        
        texto = font_categoria.render(nombre_cat, True, colores.get("NEGRO", [0, 0, 0]))
        texto_rect = texto.get_rect(center=(texto_x, texto_y))
        pantalla.blit(texto, texto_rect)
    
    # Flecha indicadora
    pygame.draw.polygon(pantalla, colores.get("ROJO", [200, 0, 0]), 
                      [(centro_x + radio + 10, centro_y),
                       (centro_x + radio + 40, centro_y - 15),
                       (centro_x + radio + 40, centro_y + 15)], 0)
    
    # Centro de la ruleta
    pygame.draw.circle(pantalla, colores.get("NEGRO", [0, 0, 0]), (centro_x, centro_y), 30)
    pygame.draw.circle(pantalla, colores.get("BLANCO", [255, 255, 255]), (centro_x, centro_y), 30, 3)
    
    font_pequeño = get_font(font_cache, 16)
    texto_gira = font_pequeño.render("GIRA", True, colores.get("NEGRO", [0, 0, 0]))
    texto_rect = texto_gira.get_rect(center=(centro_x, centro_y))
    pantalla.blit(texto_gira, texto_rect)

def mostrar_categoria_seleccionada(estado_interfaz, categoria, jugador, eventos, config):
    """Muestra la categoría seleccionada"""
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    
    dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=120)
    
    font_titulo = get_font(font_cache, 48)
    font_texto = get_font(font_cache, 36)
    font_pequeño = get_font(font_cache, 24)
    
    centrar_texto(pantalla, "¡CATEGORÍA SELECCIONADA!", font_titulo, colores.get("NEGRO", [0, 0, 0]), 150)
    centrar_texto(pantalla, categoria.upper(), font_titulo, colores.get("AZUL", [0, 100, 200]), 220)
    
    centrar_texto(pantalla, f"Jugador: {jugador}", font_texto, colores.get("NEGRO", [0, 0, 0]), 320)
    centrar_texto(pantalla, "Presiona ESPACIO para comenzar", font_pequeño, colores.get("NEGRO", [0, 0, 0]), 400)
    
    for evento in eventos:
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                return True
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            return True
    
    return False

def mostrar_pregunta(estado_interfaz, pregunta, categoria, pregunta_num, total_preguntas, puntaje, eventos, tiempo_restante, jugador, config):
    """Muestra una pregunta con opciones"""
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    
    font_info = get_font(font_cache, 20)
    font_pregunta = get_font(font_cache, 24)
    font_opciones = get_font(font_cache, 22)
    
    dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=150)
    
    # Información superior
    info_texto = f"{jugador} | {categoria} | Pregunta {pregunta_num}/{total_preguntas} | Puntaje: {puntaje}"
    centrar_texto(pantalla, info_texto, font_info, colores.get("NEGRO", [0, 0, 0]), 20)
    
    # Contador de tiempo
    dibujar_cuenta_regresiva(pantalla, tiempo_restante, config)
    
    # Dificultad
    dificultad_texto = f"Dificultad: {pregunta['dificultad']}"
    pantalla.blit(font_info.render(dificultad_texto, True, colores.get("NEGRO", [0, 0, 0])), (50, 20))
    
    # Línea separadora
    pygame.draw.line(pantalla, colores.get("NEGRO", [0, 0, 0]), (0, 50), (800, 50), 2)
    
    # Pregunta
    centrar_texto(pantalla, pregunta["pregunta"], font_pregunta, colores.get("NEGRO", [0, 0, 0]), 80)
    
    # Opciones
    y_opciones = 180
    botones_opciones = []
    colores_opciones = [
        colores.get("OPCION_1", [173, 216, 230]),
        colores.get("OPCION_2", [144, 238, 144]), 
        colores.get("OPCION_3", [255, 255, 0]),
        colores.get("OPCION_4", [255, 182, 193])
    ]
    colores_hover = [tuple(min(255, max(0, c + 50)) for c in color) for color in colores_opciones]
    
    for i, opcion in enumerate(pregunta["opciones"]):
        texto_opcion = f"{i+1}. {opcion[:60]}..." if len(opcion) > 60 else f"{i+1}. {opcion}"
        boton = dibujar_boton(pantalla, 100, y_opciones + i * 70, 600, 50, texto_opcion, 
                             colores_opciones[i], colores.get("NEGRO", [0, 0, 0]), colores_hover[i], font_opciones)
        botones_opciones.append(boton)
    
    # Botón menú
    boton_menu = dibujar_boton(pantalla, 50, 520, 120, 40, "MENÚ", colores.get("ROJO_CLARO", [255, 182, 193]), 
                              colores.get("NEGRO", [0, 0, 0]), colores.get("ROJO_HOVER", [255, 50, 50]), font_opciones)
    
    # Procesar eventos
    for evento in eventos:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos_mouse = pygame.mouse.get_pos()
            if boton_menu.collidepoint(pos_mouse):
                return "menu"
            for i, boton in enumerate(botones_opciones):
                if boton.collidepoint(pos_mouse):
                    return str(i + 1)
        elif evento.type == pygame.KEYDOWN:
            if evento.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                return str(evento.key - pygame.K_0)
            elif evento.key == pygame.K_ESCAPE:
                return "menu"
    
    return None

def mostrar_resultado_respuesta(estado_interfaz, correcto, respuesta_correcta, opciones, puntaje_ganado, eventos, config):
    """Muestra el resultado de la respuesta"""
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    
    font_titulo = get_font(font_cache, 48)
    font_texto = get_font(font_cache, 32)
    font_pequeño = get_font(font_cache, 24)
    
    dibujar_fondo(pantalla, imagen_fondo)
    
    # Overlay de color
    overlay = pygame.Surface(pantalla.get_size())
    color_overlay = colores.get("CORRECTO", [144, 238, 144]) if correcto else colores.get("INCORRECTO", [255, 182, 193])
    overlay.fill(color_overlay)
    overlay.set_alpha(120)
    pantalla.blit(overlay, (0, 0))
    
    # Mensaje principal
    mensaje = "¡CORRECTO!" if correcto else "¡INCORRECTO!"
    centrar_texto(pantalla, mensaje, font_titulo, colores.get("NEGRO", [0, 0, 0]), 150)
    
    if correcto:
        centrar_texto(pantalla, f"Has ganado {puntaje_ganado} puntos", font_texto, colores.get("NEGRO", [0, 0, 0]), 220)
    else:
        try:
            indice_correcto = int(respuesta_correcta) - 1
            if 0 <= indice_correcto < len(opciones):
                opcion_correcta = opciones[indice_correcto]
                centrar_texto(pantalla, "La respuesta correcta era:", font_texto, colores.get("NEGRO", [0, 0, 0]), 220)
                centrar_texto(pantalla, f"({respuesta_correcta}) {opcion_correcta}", font_pequeño, colores.get("NEGRO", [0, 0, 0]), 260)
        except (ValueError, TypeError):
            centrar_texto(pantalla, f"La respuesta correcta era: Opción {respuesta_correcta}", font_texto, colores.get("NEGRO", [0, 0, 0]), 220)
        
        centrar_texto(pantalla, "💔 Has perdido una vida en esta categoría", font_texto, colores.get("ROJO", [200, 0, 0]), 320)
    
    centrar_texto(pantalla, "Presiona ESPACIO para continuar", font_pequeño, colores.get("NEGRO", [0, 0, 0]), 400)
    
    # Procesar eventos
    for evento in eventos:
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                return True
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            return True
    
    return False

def mostrar_fin_categoria(estado_interfaz, categoria, respuestas_correctas, puntaje, eventos, config):
    """Muestra el fin de una categoría"""
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    
    dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
    font_titulo = get_font(font_cache, 48)
    font_texto = get_font(font_cache, 32)
    
    centrar_texto(pantalla, "CATEGORÍA COMPLETADA", font_titulo, colores.get("NEGRO", [0, 0, 0]), 100)
    centrar_texto(pantalla, categoria.upper(), font_texto, colores.get("AZUL", [0, 100, 200]), 180)
    
    centrar_texto(pantalla, f"Respuestas correctas: {respuestas_correctas}/10", font_texto, colores.get("NEGRO", [0, 0, 0]), 250)
    centrar_texto(pantalla, f"Puntos en esta ronda: {puntaje}", font_texto, colores.get("VERDE", [0, 150, 0]), 300)
    
    boton_continuar = dibujar_boton(pantalla, 300, 400, 200, 50, "CONTINUAR", 
                                   colores.get("VERDE", [0, 150, 0]), 
                                   colores.get("BLANCO", [255, 255, 255]), 
                                   colores.get("VERDE_HOVER", [50, 200, 50]), font_texto)
    
    # Procesar eventos
    for evento in eventos:
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if boton_continuar.collidepoint(pygame.mouse.get_pos()):
                    return "continuar"
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                return "continuar"
            elif evento.key == pygame.K_ESCAPE:
                return "menu"
    
    return None

def mostrar_resultados_finales(estado_interfaz, jugadores, resultados, eventos, config):
    """Muestra los resultados finales del juego"""
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    
    font_titulo = get_font(font_cache, 48)
    font_texto = get_font(font_cache, 28)
    
    dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=100)
    
    centrar_texto(pantalla, "¡JUEGO TERMINADO!", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
    centrar_texto(pantalla, "RESULTADOS FINALES", font_texto, colores.get("AZUL", [0, 100, 200]), 120)
    
    # Ordenar jugadores por puntaje
    jugadores_ordenados = sorted(jugadores, key=lambda j: resultados[j]["puntaje"], reverse=True)
    
    y_pos = 180
    colores_posicion = [
        colores.get("POSICION_1", [255, 255, 0]),
        colores.get("POSICION_2", [220, 220, 220]),
        colores.get("POSICION_3", [255, 165, 0]),
        colores.get("POSICION_4", [0, 0, 0])
    ]
    
    for i, jugador in enumerate(jugadores_ordenados):
        datos = resultados[jugador]
        color = colores_posicion[min(i, 3)]
        
        texto_pos = f"{i+1}°. {jugador} - {datos['puntaje']} puntos - {datos['porcentaje']}%"
        centrar_texto(pantalla, texto_pos, font_texto, color, y_pos)
        y_pos += 40
    
    # Mostrar ganador
    if jugadores_ordenados:
        ganador = jugadores_ordenados[0]
        centrar_texto(pantalla, f"¡GANADOR: {ganador}!", font_texto, colores.get("ROJO", [200, 0, 0]), 380)
    
    # Botones
    boton_nuevo = dibujar_boton(pantalla, 200, 450, 180, 50, "NUEVO JUEGO", 
                               colores.get("VERDE", [0, 150, 0]), 
                               colores.get("BLANCO", [255, 255, 255]), 
                               colores.get("VERDE_HOVER", [50, 200, 50]), font_texto)
    boton_menu = dibujar_boton(pantalla, 420, 450, 180, 50, "MENÚ PRINCIPAL", 
                              colores.get("AZUL", [0, 100, 200]), 
                              colores.get("BLANCO", [255, 255, 255]), 
                              colores.get("AZUL_HOVER", [50, 150, 255]), font_texto)
    
    # Procesar eventos
    for evento in eventos:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos_mouse = pygame.mouse.get_pos()
            if boton_nuevo.collidepoint(pos_mouse):
                return "nuevo"
            elif boton_menu.collidepoint(pos_mouse):
                return "menu"
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_n:
                return "nuevo"
            elif evento.key == pygame.K_m or evento.key == pygame.K_ESCAPE:
                return "menu"
    
    return None

def mostrar_historial(estado_interfaz, eventos, config):
    """Muestra el historial de partidas con ordenamiento alfabético"""
    pantalla = estado_interfaz['pantalla']
    font_cache = estado_interfaz['font_cache']
    imagen_fondo = estado_interfaz['imagen_fondo']
    
    colores = obtener_colores(config)
    
    font_titulo = get_font(font_cache, 36)
    font_texto = get_font(font_cache, 24)
    
    dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=120)
    
    centrar_texto(pantalla, "HISTORIAL DE PARTIDAS", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
    
    boton_volver = dibujar_boton(pantalla, 50, 520, 120, 40, "VOLVER", 
                                colores.get("GRIS_CLARO", [220, 220, 220]), 
                                colores.get("NEGRO", [0, 0, 0]), 
                                colores.get("GRIS_HOVER", [180, 180, 180]), font_texto)
    
    try:
        with open("partida_guardada.json", "r", encoding="utf-8") as archivo:
            historial = json.load(archivo)
        
        if "resultados" in historial and historial["resultados"]:
            # ARREGLO: Usar ordenamiento alfabético del archivo ordenamiento.py
            try:
                from ordenamiento import ordenar_jugadores_alfabeticamente
                jugadores_ordenados = ordenar_jugadores_alfabeticamente(historial["resultados"])
            except ImportError:
                # Fallback: ordenar manualmente si no está disponible
                jugadores_ordenados = sorted(historial["resultados"].items(), key=lambda x: x[0].lower())
            
            y_pos = 120
            centrar_texto(pantalla, "Última partida guardada (orden alfabético):", font_texto, colores.get("NEGRO", [0, 0, 0]), y_pos)
            y_pos += 50
            
            colores_jugadores = [
                colores.get("JUGADOR_1", [0, 100, 200]), 
                colores.get("JUGADOR_2", [0, 150, 0]), 
                colores.get("JUGADOR_3", [255, 165, 0]), 
                colores.get("JUGADOR_4", [200, 0, 0]), 
                colores.get("GRIS", [128, 128, 128])
            ]
            
            for i, (jugador, datos) in enumerate(jugadores_ordenados[:8]):
                color = colores_jugadores[i % len(colores_jugadores)]
                
                # ARREGLO: Mostrar información corregida con porcentajes reales
                aciertos = datos.get('aciertos', 0)
                porcentaje = datos.get('porcentaje', 0)
                puntaje = datos.get('puntaje', 0)
                total_preguntas = datos.get('total_preguntas', aciertos)  # Usar total si está disponible
                
                # Formato mejorado mostrando fracción y porcentaje
                if total_preguntas > 0:
                    texto = f"{jugador}: {aciertos}/{total_preguntas} ({porcentaje}%) - {puntaje} pts"
                else:
                    texto = f"{jugador}: {aciertos} aciertos ({porcentaje}%) - {puntaje} pts"
                
                centrar_texto(pantalla, texto, font_texto, color, y_pos)
                y_pos += 35
        else:
            centrar_texto(pantalla, "No hay datos en el historial", font_texto, colores.get("GRIS", [128, 128, 128]), 200)
    
    except FileNotFoundError:
        centrar_texto(pantalla, "No hay historial disponible", font_texto, colores.get("NEGRO", [0, 0, 0]), 200)
    except Exception as e:
        centrar_texto(pantalla, f"Error al cargar historial", font_texto, colores.get("ROJO", [200, 0, 0]), 200)
    
    # Procesar eventos
    for evento in eventos:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if boton_volver.collidepoint(pygame.mouse.get_pos()):
                return "menu"
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "menu"
    
    return "historial"


# # interfaz.py - INTERFAZ COMPLETAMENTE CORREGIDA

# import pygame
# import math
# import time
# import json
# import sys
# from configuracion import obtener_colores

# def inicializar_interfaz(pantalla):
#     """Inicializa la interfaz del juego"""
#     estado_interfaz = {
#         'pantalla': pantalla,
#         'font_cache': {},
#         'texto_ingreso': "",
#         'cursor_visible': True,
#         'tiempo_cursor': 0,
#         'imagen_fondo': cargar_imagen_fondo(pantalla)
#     }
#     return estado_interfaz

# def cargar_imagen_fondo(pantalla):
#     """Carga la imagen de fondo o usa color sólido"""
#     try:
#         config = cargar_configuracion_simple()
#         ruta_imagen = config.get("archivos", {}).get("imagen_fondo", "PARCIAL 2/imagenes/fondo.png")
        
#         imagen_fondo = pygame.image.load(ruta_imagen)
#         imagen_fondo = pygame.transform.scale(imagen_fondo, pantalla.get_size())
#     except (pygame.error, FileNotFoundError, KeyError):
#         try:
#             config = cargar_configuracion_simple()
#             color_fondo = config.get("colores", {}).get("normal", {}).get("FONDO_DEFAULT", [173, 216, 230])
#         except:
#             color_fondo = [173, 216, 230]
        
#         imagen_fondo = pygame.Surface(pantalla.get_size())
#         imagen_fondo.fill(color_fondo)
#     return imagen_fondo

# def cargar_configuracion_simple():
#     """Carga configuración de manera simple"""
#     try:
#         import json
#         with open("PARCIAL 2/configuracion.json", "r", encoding="utf-8") as archivo:
#             return json.load(archivo)
#     except:
#         return {}

# def get_font(font_cache, size):
#     """Cache de fuentes para mejor rendimiento"""
#     if size not in font_cache:
#         font_cache[size] = pygame.font.Font(None, size)
#     return font_cache[size]

# def dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=None):
#     """Dibuja el fondo con overlay opcional"""
#     pantalla.blit(imagen_fondo, (0, 0))
#     if overlay_alpha:
#         overlay = pygame.Surface(pantalla.get_size())
#         overlay.set_alpha(overlay_alpha)
#         overlay.fill((255, 255, 255))
#         pantalla.blit(overlay, (0, 0))

# def dibujar_boton(pantalla, x, y, ancho, alto, texto, color_fondo, color_texto, color_hover, font):
#     """Dibuja un botón con efectos hover mejorados"""
#     mouse_pos = pygame.mouse.get_pos()
#     boton_rect = pygame.Rect(x, y, ancho, alto)
#     mouse_over = boton_rect.collidepoint(mouse_pos)
    
#     color_actual = color_hover if mouse_over else color_fondo
    
#     # Sombra para efecto 3D
#     if mouse_over:
#         sombra_rect = pygame.Rect(x+3, y+3, ancho, alto)
#         pygame.draw.rect(pantalla, (50, 50, 50), sombra_rect)
    
#     # Dibujar botón
#     pygame.draw.rect(pantalla, color_actual, boton_rect)
#     pygame.draw.rect(pantalla, (0, 0, 0), boton_rect, 2)
    
#     # Texto centrado
#     texto_renderizado = font.render(texto, True, color_texto)
#     texto_rect = texto_renderizado.get_rect(center=boton_rect.center)
#     pantalla.blit(texto_renderizado, texto_rect)
    
#     return boton_rect

# def centrar_texto(pantalla, texto, font, color, y):
#     """Centra texto horizontalmente en la pantalla"""
#     texto_renderizado = font.render(texto, True, color)
#     x = (pantalla.get_width() - texto_renderizado.get_width()) // 2
#     pantalla.blit(texto_renderizado, (x, y))

# def dibujar_cuenta_regresiva(pantalla, tiempo_restante, config, tiempo_total=30):
#     """Dibuja el contador de tiempo circular"""
#     colores = obtener_colores(config)
    
#     contador_config = config.get("interfaz", {}).get("posiciones", {}).get("contador_tiempo", {})
#     centro_x = contador_config.get("x", 750)
#     centro_y = contador_config.get("y", 93)
#     radio = contador_config.get("radio", 35)
    
#     animaciones_config = config.get("interfaz", {}).get("animaciones", {})
#     pulso_velocidad = animaciones_config.get("pulso_tiempo_critico", 10)
    
#     progreso = tiempo_restante / tiempo_total if tiempo_total > 0 else 0
    
#     # Colores según el tiempo restante
#     if tiempo_restante <= 5:
#         color_circulo = colores.get("TIEMPO_CRITICO", [200, 0, 0])
#         color_texto = colores.get("BLANCO", [255, 255, 255])
#         color_borde = tuple(max(0, c - 50) for c in color_circulo)
#     elif tiempo_restante <= 10:
#         color_circulo = colores.get("TIEMPO_ADVERTENCIA", [255, 165, 0])
#         color_texto = colores.get("NEGRO", [0, 0, 0])
#         color_borde = tuple(max(0, c - 50) for c in color_circulo)
#     else:
#         color_circulo = colores.get("TIEMPO_NORMAL", [0, 150, 0])
#         color_texto = colores.get("NEGRO", [0, 0, 0])
#         color_borde = tuple(max(0, c - 50) for c in color_circulo)
    
#     # Fondo del círculo
#     pygame.draw.circle(pantalla, colores.get("GRIS_CLARO", [220, 220, 220]), (centro_x, centro_y), radio)
#     pygame.draw.circle(pantalla, color_borde, (centro_x, centro_y), radio, 3)
    
#     # Progreso circular
#     if tiempo_restante > 0 and progreso > 0:
#         angulo = 2 * math.pi * progreso
#         puntos = [(centro_x, centro_y)]
#         num_puntos = max(int(angulo * 30), 3)
        
#         for i in range(num_puntos + 1):
#             angle = -math.pi/2 + (angulo * i / num_puntos)
#             px = centro_x + (radio - 2) * math.cos(angle)
#             py = centro_y + (radio - 2) * math.sin(angle)
#             puntos.append((px, py))
        
#         if len(puntos) > 2:
#             pygame.draw.polygon(pantalla, color_circulo, puntos)
    
#     # Texto del tiempo
#     font = pygame.font.Font(None, 28)
#     texto = font.render(str(tiempo_restante), True, color_texto)
#     texto_rect = texto.get_rect(center=(centro_x, centro_y))
#     pantalla.blit(texto, texto_rect)
    
#     # Label "TIEMPO"
#     font_pequeño = pygame.font.Font(None, 16)
#     color_label = colores.get("TIEMPO_CRITICO", [200, 0, 0]) if tiempo_restante <= 5 else colores.get("NEGRO", [0, 0, 0])
#     texto_label = font_pequeño.render("TIEMPO", True, color_label)
#     label_rect = texto_label.get_rect(center=(centro_x, centro_y + 40))
#     pantalla.blit(texto_label, label_rect)
    
#     # Efecto de pulso cuando el tiempo es crítico
#     if tiempo_restante <= 5:
#         pulso = int(time.time() * pulso_velocidad) % 2
#         if pulso:
#             pygame.draw.circle(pantalla, colores.get("TIEMPO_CRITICO", [200, 0, 0]), (centro_x, centro_y), radio + 5, 2)

# def mostrar_menu_principal(estado_interfaz, eventos, config):
#     """Muestra el menú principal completamente funcional"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
#     textos_config = config.get("textos", {})
#     fuentes_config = config.get("interfaz", {}).get("fuentes", {})
#     botones_config = config.get("interfaz", {}).get("posiciones", {}).get("menu_botones", {})
    
#     font_titulo = get_font(font_cache, fuentes_config.get("titulo", 48))
#     font_opciones = get_font(font_cache, fuentes_config.get("subtitulo", 36))
#     font_info = get_font(font_cache, fuentes_config.get("texto_pequeño", 24))
#     font_pequeño = get_font(font_cache, fuentes_config.get("muy_pequeño", 18))
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=50)
    
#     # Títulos desde configuración
#     titulo_principal = textos_config.get("titulo_principal", "JUEGO DE PREGUNTAS")
#     subtitulo_vidas = textos_config.get("subtitulo_vidas", "🎮 Con Sistema de Vidas")
#     info_vidas = textos_config.get("info_vidas", "💖 3 vidas por categoría | 🎯 Tateti para vida extra")
    
#     centrar_texto(pantalla, titulo_principal, font_titulo, colores.get("NEGRO", [0, 0, 0]), 60)
#     centrar_texto(pantalla, subtitulo_vidas, font_info, colores.get("AZUL", [0, 100, 200]), 100)
#     centrar_texto(pantalla, "Selecciona una opción:", font_opciones, colores.get("NEGRO", [0, 0, 0]), 140)
    
#     # Configuración de botones desde JSON
#     x_botones = botones_config.get("x", 300)
#     y_inicial = botones_config.get("y_inicial", 190)
#     ancho_boton = botones_config.get("ancho", 200)
#     alto_boton = botones_config.get("alto", 55)
#     separacion = botones_config.get("separacion", 65)
    
#     botones = [
#         (x_botones, y_inicial, ancho_boton, alto_boton, "JUGAR", colores.get("BOTON_JUGAR", [80, 200, 255]), "jugar"),
#         (x_botones, y_inicial + separacion, ancho_boton, alto_boton, "TATETI", colores.get("VERDE", [0, 150, 0]), "tateti"),
#         (x_botones, y_inicial + separacion*2, ancho_boton, alto_boton, "HISTORIAL", colores.get("BOTON_HISTORIAL", [255, 200, 0]), "historial"),
#         (x_botones, y_inicial + separacion*3, ancho_boton, alto_boton, "ACCESIBILIDAD", colores.get("BOTON_ACCESIBILIDAD", [150, 100, 255]), "accesibilidad"),
#         (x_botones, y_inicial + separacion*4, ancho_boton, alto_boton, "SALIR", colores.get("BOTON_SALIR", [255, 100, 100]), "salir")
#     ]
    
#     botones_rect = []
#     for x, y, w, h, texto, color, accion in botones:
#         color_hover = tuple(min(255, max(0, c + 30)) for c in color)
#         rect = dibujar_boton(pantalla, x, y, w, h, texto, color, colores.get("NEGRO", [0, 0, 0]), color_hover, font_opciones)
#         botones_rect.append((rect, accion))
    
#     # Info sobre sistema de vidas
#     centrar_texto(pantalla, info_vidas, font_pequeño, colores.get("GRIS", [128, 128, 128]), 520)
    
#     # Procesar eventos
#     for evento in eventos:
#         if evento.type == pygame.QUIT:
#             return "salir"
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_ESCAPE:
#                 return "salir"
#             elif evento.key == pygame.K_1:
#                 return "jugar"
#             elif evento.key == pygame.K_2:
#                 return "tateti"
#             elif evento.key == pygame.K_3:
#                 return "historial"
#             elif evento.key == pygame.K_4:
#                 return "accesibilidad"
#             elif evento.key == pygame.K_5:
#                 return "salir"
#         elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             for rect, accion in botones_rect:
#                 if rect.collidepoint(pos_mouse):
#                     return accion
    
#     return "menu"

# def mostrar_menu_accesibilidad(estado_interfaz, eventos, config):
#     """Muestra el menú de accesibilidad"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
#     font_titulo = get_font(font_cache, 40)
#     font_texto = get_font(font_cache, 32)
#     font_info = get_font(font_cache, 24)
#     font_pequeño = get_font(font_cache, 20)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
#     centrar_texto(pantalla, "CONFIGURACIÓN DE ACCESIBILIDAD", font_titulo, colores.get("NEGRO", [0, 0, 0]), 60)
    
#     modo_actual = config.get("Accesibilidad", "neurotipico")
    
#     if modo_actual == "daltonico":
#         texto_modo = "🔵 MODO DALTÓNICO ACTIVADO"
#         color_modo = (0, 150, 200)
#         info_color = "Se han aplicado cambios de colores para daltonismo"
#     else:
#         texto_modo = "🟢 MODO NORMAL ACTIVADO"  
#         color_modo = (0, 150, 0)
#         info_color = "Colores estándar activos"
    
#     centrar_texto(pantalla, texto_modo, font_texto, color_modo, 120)
#     centrar_texto(pantalla, info_color, font_pequeño, colores.get("NEGRO", [0, 0, 0]), 160)
    
#     info_lines = [
#         "",
#         "Cambios aplicados en modo daltónico:",
#         "• Verdes → Azules para mejor distinción",
#         "• Rojos → Naranjas/Marrones más visibles", 
#         "• Mayor contraste en elementos importantes",
#         "• Optimizado para daltonismo rojo-verde"
#     ]
    
#     y_pos = 200
#     for linea in info_lines:
#         if linea:
#             centrar_texto(pantalla, linea, font_info, colores.get("NEGRO", [0, 0, 0]), y_pos)
#         y_pos += 25
    
#     if modo_actual == "daltonico":
#         color_boton_toggle = (0, 150, 200)
#         color_hover_toggle = (30, 180, 255)
#         texto_boton = "VOLVER A NORMAL"
#     else:
#         color_boton_toggle = (255, 150, 0)
#         color_hover_toggle = (255, 180, 50)
#         texto_boton = "ACTIVAR MODO DALTÓNICO"
    
#     boton_toggle = dibujar_boton(pantalla, 200, 480, 400, 50, texto_boton, color_boton_toggle, (255, 255, 255), color_hover_toggle, font_texto)
#     boton_volver = dibujar_boton(pantalla, 250, 540, 300, 40, "VOLVER AL MENÚ", colores.get("GRIS_CLARO", [220, 220, 220]), colores.get("NEGRO", [0, 0, 0]), colores.get("GRIS_HOVER", [180, 180, 180]), font_info)
    
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             if boton_toggle.collidepoint(pos_mouse):
#                 return "toggle"
#             elif boton_volver.collidepoint(pos_mouse):
#                 return "menu"
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_ESCAPE:
#                 return "menu"
#             elif evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
#                 return "toggle"
    
#     return "accesibilidad"

# def mostrar_ingreso_jugador(estado_interfaz, jugadores_actuales, puede_agregar, eventos, config):
#     """Muestra la pantalla de ingreso de jugadores corregida"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_titulo = get_font(font_cache, 40)
#     font_texto = get_font(font_cache, 32)
#     font_pequeño = get_font(font_cache, 24)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
#     centrar_texto(pantalla, "INGRESO DE JUGADORES", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
#     centrar_texto(pantalla, f"Jugadores registrados: {len(jugadores_actuales)}/4", font_texto, colores.get("NEGRO", [0, 0, 0]), 120)
    
#     # Mostrar lista de jugadores
#     y_pos = 170
#     colores_jugadores = [
#         colores.get("JUGADOR_1", [0, 100, 200]),
#         colores.get("JUGADOR_2", [0, 150, 0]),
#         colores.get("JUGADOR_3", [255, 165, 0]),
#         colores.get("JUGADOR_4", [200, 0, 0])
#     ]
#     for i, jugador in enumerate(jugadores_actuales):
#         color = colores_jugadores[i]
#         texto = f"Jugador {i+1}: {jugador}"
#         centrar_texto(pantalla, texto, font_texto, color, y_pos)
#         y_pos += 35
    
#     # Campo de entrada si se puede agregar
#     if puede_agregar and len(jugadores_actuales) < 4:
#         y_entrada = 320
#         centrar_texto(pantalla, f"Ingresa el nombre del Jugador {len(jugadores_actuales) + 1}:", font_pequeño, colores.get("NEGRO", [0, 0, 0]), y_entrada - 30)
        
#         entrada_rect = pygame.Rect(250, y_entrada, 300, 50)
#         pygame.draw.rect(pantalla, colores.get("BLANCO", [255, 255, 255]), entrada_rect)
#         pygame.draw.rect(pantalla, colores.get("NEGRO", [0, 0, 0]), entrada_rect, 2)
        
#         # Cursor parpadeante
#         if time.time() - estado_interfaz['tiempo_cursor'] > 0.5:
#             estado_interfaz['cursor_visible'] = not estado_interfaz['cursor_visible']
#             estado_interfaz['tiempo_cursor'] = time.time()
        
#         texto_mostrar = estado_interfaz['texto_ingreso'] + ("|" if estado_interfaz['cursor_visible'] else "")
#         texto_render = font_texto.render(texto_mostrar, True, colores.get("NEGRO", [0, 0, 0]))
#         texto_rect = texto_render.get_rect(center=entrada_rect.center)
#         pantalla.blit(texto_render, texto_rect)
        
#         centrar_texto(pantalla, "Presiona ENTER para confirmar", font_pequeño, colores.get("NEGRO", [0, 0, 0]), y_entrada + 70)
    
#     # Botones
#     y_botones = 450
#     botones = []
    
#     if jugadores_actuales:
#         if len(jugadores_actuales) < 4:
#             boton_agregar = dibujar_boton(pantalla, 150, y_botones, 160, 40, "AGREGAR MÁS", colores.get("AZUL", [0, 100, 200]), colores.get("BLANCO", [255, 255, 255]), colores.get("AZUL_HOVER", [50, 150, 255]), font_pequeño)
#             botones.append(("agregar", boton_agregar))
        
#         boton_iniciar = dibujar_boton(pantalla, 330, y_botones, 160, 40, "INICIAR JUEGO", colores.get("VERDE", [0, 150, 0]), colores.get("BLANCO", [255, 255, 255]), colores.get("VERDE_HOVER", [50, 200, 50]), font_pequeño)
#         botones.append(("continuar", boton_iniciar))
    
#     boton_volver = dibujar_boton(pantalla, 510, y_botones, 140, 40, "VOLVER", colores.get("GRIS", [128, 128, 128]), colores.get("BLANCO", [255, 255, 255]), colores.get("GRIS_HOVER", [180, 180, 180]), font_pequeño)
#     botones.append(("menu", boton_volver))
    
#     # Procesar eventos
#     for evento in eventos:
#         if evento.type == pygame.KEYDOWN:
#             if puede_agregar and len(jugadores_actuales) < 4:
#                 if evento.key == pygame.K_BACKSPACE:
#                     estado_interfaz['texto_ingreso'] = estado_interfaz['texto_ingreso'][:-1]
#                 elif evento.key == pygame.K_RETURN and estado_interfaz['texto_ingreso'].strip():
#                     nombre = estado_interfaz['texto_ingreso'].strip()
#                     estado_interfaz['texto_ingreso'] = ""
#                     return nombre
#                 elif evento.unicode and len(evento.unicode) == 1 and evento.unicode.isalpha() and len(estado_interfaz['texto_ingreso']) < 15:
#                     estado_interfaz['texto_ingreso'] += evento.unicode
            
#             if evento.key == pygame.K_ESCAPE:
#                 return "menu"
        
#         elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             for accion, boton in botones:
#                 if boton.collidepoint(pos_mouse):
#                     return accion
    
#     return None

# def mostrar_seleccion_dificultad(estado_interfaz, jugador, eventos, config):
#     """Muestra la selección de dificultad"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
#     fuentes_config = config.get("interfaz", {}).get("fuentes", {})
#     sistema_vidas = config.get("sistema_vidas", {})
    
#     font_titulo = get_font(font_cache, fuentes_config.get("titulo", 40))
#     font_opciones = get_font(font_cache, fuentes_config.get("texto", 32))
#     font_info = get_font(font_cache, fuentes_config.get("texto_pequeño", 24))
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
#     centrar_texto(pantalla, f"Turno de: {jugador}", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
#     centrar_texto(pantalla, "SELECCIONA LA DIFICULTAD", font_titulo, colores.get("NEGRO", [0, 0, 0]), 120)
    
#     # Mostrar información de vidas
#     vidas_por_categoria = sistema_vidas.get("vidas_por_categoria", 3)
#     info_vidas = f"💖 Tendrás {vidas_por_categoria} vidas por categoría"
#     centrar_texto(pantalla, info_vidas, font_info, colores.get("AZUL", [0, 100, 200]), 160)
    
#     # Obtener puntajes
#     puntajes = config.get("puntaje_por_dificultad", {"Fácil": 10, "Medio": 20, "Difícil": 30})
    
#     botones = [
#         (250, 200, 300, 60, f"FÁCIL - {puntajes['Fácil']} puntos", colores.get("BOTON_FACIL", [144, 238, 144]), "Fácil"),
#         (250, 280, 300, 60, f"MEDIO - {puntajes['Medio']} puntos", colores.get("BOTON_MEDIO", [255, 255, 0]), "Medio"),
#         (250, 360, 300, 60, f"DIFÍCIL - {puntajes['Difícil']} puntos", colores.get("BOTON_DIFICIL", [255, 182, 193]), "Difícil"),
#         (250, 450, 300, 40, "VOLVER AL MENÚ", colores.get("GRIS_CLARO", [220, 220, 220]), "menu")
#     ]
    
#     botones_rect = []
#     for x, y, w, h, texto, color, accion in botones:
#         color_hover = tuple(min(255, c + 50) for c in color)
#         rect = dibujar_boton(pantalla, x, y, w, h, texto, color, colores.get("NEGRO", [0, 0, 0]), color_hover, font_opciones)
#         botones_rect.append((rect, accion))
    
#     # Procesar eventos
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             for rect, accion in botones_rect:
#                 if rect.collidepoint(pos_mouse):
#                     return accion
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_1:
#                 return "Fácil"
#             elif evento.key == pygame.K_2:
#                 return "Medio"
#             elif evento.key == pygame.K_3:
#                 return "Difícil"
#             elif evento.key == pygame.K_ESCAPE:
#                 return "menu"
    
#     return None

# def mostrar_ruleta_categoria(estado_interfaz, categorias_disponibles, categorias_jugadas, tiempo_animacion, config):
#     """Muestra la ruleta de categorías animada"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=100)
    
#     font_titulo = get_font(font_cache, 48)
#     font_categoria = get_font(font_cache, 28)
    
#     centrar_texto(pantalla, "RULETA DE CATEGORÍAS", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
    
#     centro_x, centro_y = 400, 300
#     radio = 150
    
#     categorias_ruleta = [cat for cat in categorias_disponibles if cat not in categorias_jugadas]
    
#     if not categorias_ruleta:
#         return
    
#     velocidad = max(1, 10 - tiempo_animacion * 3)
#     angulo_rotacion = tiempo_animacion * velocidad * 360
    
#     num_categorias = len(categorias_ruleta)
#     angulo_seccion = 360 / num_categorias
    
#     colores_ruleta = [
#         colores.get("RULETA_COLOR_1", [144, 238, 144]), 
#         colores.get("RULETA_COLOR_2", [255, 255, 0]), 
#         colores.get("RULETA_COLOR_3", [255, 182, 193]), 
#         colores.get("RULETA_COLOR_4", [173, 216, 230]), 
#         colores.get("RULETA_COLOR_5", [255, 165, 0]), 
#         colores.get("RULETA_COLOR_6", [220, 220, 220])
#     ]
    
#     for i in range(num_categorias):
#         angulo_inicio = i * angulo_seccion + angulo_rotacion
#         angulo_fin = (i + 1) * angulo_seccion + angulo_rotacion
        
#         puntos = [(centro_x, centro_y)]
#         for angulo in range(int(angulo_inicio), int(angulo_fin) + 1):
#             x = centro_x + radio * math.cos(math.radians(angulo))
#             y = centro_y + radio * math.sin(math.radians(angulo))
#             puntos.append((x, y))
        
#         if len(puntos) > 2:
#             color_seccion = colores_ruleta[i % len(colores_ruleta)]
#             pygame.draw.polygon(pantalla, color_seccion, puntos)
#             pygame.draw.polygon(pantalla, colores.get("NEGRO", [0, 0, 0]), puntos, 3)
        
#         angulo_texto = math.radians(angulo_inicio + angulo_seccion / 2)
#         texto_x = centro_x + (radio * 0.6) * math.cos(angulo_texto)
#         texto_y = centro_y + (radio * 0.6) * math.sin(angulo_texto)
        
#         nombre_cat = categorias_ruleta[i]
#         if len(nombre_cat) > 10:
#             nombre_cat = nombre_cat[:8] + ".."
        
#         texto = font_categoria.render(nombre_cat, True, colores.get("NEGRO", [0, 0, 0]))
#         texto_rect = texto.get_rect(center=(texto_x, texto_y))
#         pantalla.blit(texto, texto_rect)
    
#     # Flecha indicadora
#     pygame.draw.polygon(pantalla, colores.get("ROJO", [200, 0, 0]), 
#                       [(centro_x + radio + 10, centro_y),
#                        (centro_x + radio + 40, centro_y - 15),
#                        (centro_x + radio + 40, centro_y + 15)], 0)
    
#     # Centro de la ruleta
#     pygame.draw.circle(pantalla, colores.get("NEGRO", [0, 0, 0]), (centro_x, centro_y), 30)
#     pygame.draw.circle(pantalla, colores.get("BLANCO", [255, 255, 255]), (centro_x, centro_y), 30, 3)
    
#     font_pequeño = get_font(font_cache, 16)
#     texto_gira = font_pequeño.render("GIRA", True, colores.get("NEGRO", [0, 0, 0]))
#     texto_rect = texto_gira.get_rect(center=(centro_x, centro_y))
#     pantalla.blit(texto_gira, texto_rect)

# def mostrar_categoria_seleccionada(estado_interfaz, categoria, jugador, eventos, config):
#     """Muestra la categoría seleccionada"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=120)
    
#     font_titulo = get_font(font_cache, 48)
#     font_texto = get_font(font_cache, 36)
#     font_pequeño = get_font(font_cache, 24)
    
#     centrar_texto(pantalla, "¡CATEGORÍA SELECCIONADA!", font_titulo, colores.get("NEGRO", [0, 0, 0]), 150)
#     centrar_texto(pantalla, categoria.upper(), font_titulo, colores.get("AZUL", [0, 100, 200]), 220)
    
#     centrar_texto(pantalla, f"Jugador: {jugador}", font_texto, colores.get("NEGRO", [0, 0, 0]), 320)
#     centrar_texto(pantalla, "Presiona ESPACIO para comenzar", font_pequeño, colores.get("NEGRO", [0, 0, 0]), 400)
    
#     for evento in eventos:
#         if evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
#                 return True
#         elif evento.type == pygame.MOUSEBUTTONDOWN:
#             return True
    
#     return False

# def mostrar_pregunta(estado_interfaz, pregunta, categoria, pregunta_num, total_preguntas, puntaje, eventos, tiempo_restante, jugador, config):
#     """Muestra una pregunta con opciones"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_info = get_font(font_cache, 20)
#     font_pregunta = get_font(font_cache, 24)
#     font_opciones = get_font(font_cache, 22)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=150)
    
#     # Información superior
#     info_texto = f"{jugador} | {categoria} | Pregunta {pregunta_num}/{total_preguntas} | Puntaje: {puntaje}"
#     centrar_texto(pantalla, info_texto, font_info, colores.get("NEGRO", [0, 0, 0]), 20)
    
#     # Contador de tiempo
#     dibujar_cuenta_regresiva(pantalla, tiempo_restante, config)
    
#     # Dificultad
#     dificultad_texto = f"Dificultad: {pregunta['dificultad']}"
#     pantalla.blit(font_info.render(dificultad_texto, True, colores.get("NEGRO", [0, 0, 0])), (50, 20))
    
#     # Línea separadora
#     pygame.draw.line(pantalla, colores.get("NEGRO", [0, 0, 0]), (0, 50), (800, 50), 2)
    
#     # Pregunta
#     centrar_texto(pantalla, pregunta["pregunta"], font_pregunta, colores.get("NEGRO", [0, 0, 0]), 80)
    
#     # Opciones
#     y_opciones = 180
#     botones_opciones = []
#     colores_opciones = [
#         colores.get("OPCION_1", [173, 216, 230]),
#         colores.get("OPCION_2", [144, 238, 144]), 
#         colores.get("OPCION_3", [255, 255, 0]),
#         colores.get("OPCION_4", [255, 182, 193])
#     ]
#     colores_hover = [tuple(min(255, max(0, c + 50)) for c in color) for color in colores_opciones]
    
#     for i, opcion in enumerate(pregunta["opciones"]):
#         texto_opcion = f"{i+1}. {opcion[:60]}..." if len(opcion) > 60 else f"{i+1}. {opcion}"
#         boton = dibujar_boton(pantalla, 100, y_opciones + i * 70, 600, 50, texto_opcion, 
#                              colores_opciones[i], colores.get("NEGRO", [0, 0, 0]), colores_hover[i], font_opciones)
#         botones_opciones.append(boton)
    
#     # Botón menú
#     boton_menu = dibujar_boton(pantalla, 50, 520, 120, 40, "MENÚ", colores.get("ROJO_CLARO", [255, 182, 193]), 
#                               colores.get("NEGRO", [0, 0, 0]), colores.get("ROJO_HOVER", [255, 50, 50]), font_opciones)
    
#     # Procesar eventos
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             if boton_menu.collidepoint(pos_mouse):
#                 return "menu"
#             for i, boton in enumerate(botones_opciones):
#                 if boton.collidepoint(pos_mouse):
#                     return str(i + 1)
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
#                 return str(evento.key - pygame.K_0)
#             elif evento.key == pygame.K_ESCAPE:
#                 return "menu"
    
#     return None

# def mostrar_resultado_respuesta(estado_interfaz, correcto, respuesta_correcta, opciones, puntaje_ganado, eventos, config):
#     """Muestra el resultado de la respuesta"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_titulo = get_font(font_cache, 48)
#     font_texto = get_font(font_cache, 32)
#     font_pequeño = get_font(font_cache, 24)
    
#     dibujar_fondo(pantalla, imagen_fondo)
    
#     # Overlay de color
#     overlay = pygame.Surface(pantalla.get_size())
#     color_overlay = colores.get("CORRECTO", [144, 238, 144]) if correcto else colores.get("INCORRECTO", [255, 182, 193])
#     overlay.fill(color_overlay)
#     overlay.set_alpha(120)
#     pantalla.blit(overlay, (0, 0))
    
#     # Mensaje principal
#     mensaje = "¡CORRECTO!" if correcto else "¡INCORRECTO!"
#     centrar_texto(pantalla, mensaje, font_titulo, colores.get("NEGRO", [0, 0, 0]), 150)
    
#     if correcto:
#         centrar_texto(pantalla, f"Has ganado {puntaje_ganado} puntos", font_texto, colores.get("NEGRO", [0, 0, 0]), 220)
#     else:
#         try:
#             indice_correcto = int(respuesta_correcta) - 1
#             if 0 <= indice_correcto < len(opciones):
#                 opcion_correcta = opciones[indice_correcto]
#                 centrar_texto(pantalla, "La respuesta correcta era:", font_texto, colores.get("NEGRO", [0, 0, 0]), 220)
#                 centrar_texto(pantalla, f"({respuesta_correcta}) {opcion_correcta}", font_pequeño, colores.get("NEGRO", [0, 0, 0]), 260)
#         except (ValueError, TypeError):
#             centrar_texto(pantalla, f"La respuesta correcta era: Opción {respuesta_correcta}", font_texto, colores.get("NEGRO", [0, 0, 0]), 220)
        
#         centrar_texto(pantalla, "💔 Has perdido una vida en esta categoría", font_texto, colores.get("ROJO", [200, 0, 0]), 320)
    
#     centrar_texto(pantalla, "Presiona ESPACIO para continuar", font_pequeño, colores.get("NEGRO", [0, 0, 0]), 400)
    
#     # Procesar eventos
#     for evento in eventos:
#         if evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
#                 return True
#         elif evento.type == pygame.MOUSEBUTTONDOWN:
#             return True
    
#     return False

# def mostrar_fin_categoria(estado_interfaz, categoria, respuestas_correctas, puntaje, eventos, config):
#     """Muestra el fin de una categoría"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
#     font_titulo = get_font(font_cache, 48)
#     font_texto = get_font(font_cache, 32)
    
#     centrar_texto(pantalla, "CATEGORÍA COMPLETADA", font_titulo, colores.get("NEGRO", [0, 0, 0]), 100)
#     centrar_texto(pantalla, categoria.upper(), font_texto, colores.get("AZUL", [0, 100, 200]), 180)
    
#     centrar_texto(pantalla, f"Respuestas correctas: {respuestas_correctas}/10", font_texto, colores.get("NEGRO", [0, 0, 0]), 250)
#     centrar_texto(pantalla, f"Puntos en esta ronda: {puntaje}", font_texto, colores.get("VERDE", [0, 150, 0]), 300)
    
#     boton_continuar = dibujar_boton(pantalla, 300, 400, 200, 50, "CONTINUAR", 
#                                    colores.get("VERDE", [0, 150, 0]), 
#                                    colores.get("BLANCO", [255, 255, 255]), 
#                                    colores.get("VERDE_HOVER", [50, 200, 50]), font_texto)
    
#     # Procesar eventos
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN:
#             if evento.button == 1:
#                 if boton_continuar.collidepoint(pygame.mouse.get_pos()):
#                     return "continuar"
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
#                 return "continuar"
#             elif evento.key == pygame.K_ESCAPE:
#                 return "menu"
    
#     return None

# def mostrar_resultados_finales(estado_interfaz, jugadores, resultados, eventos, config):
#     """Muestra los resultados finales del juego"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_titulo = get_font(font_cache, 48)
#     font_texto = get_font(font_cache, 28)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=100)
    
#     centrar_texto(pantalla, "¡JUEGO TERMINADO!", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
#     centrar_texto(pantalla, "RESULTADOS FINALES", font_texto, colores.get("AZUL", [0, 100, 200]), 120)
    
#     # Ordenar jugadores por puntaje
#     jugadores_ordenados = sorted(jugadores, key=lambda j: resultados[j]["puntaje"], reverse=True)
    
#     y_pos = 180
#     colores_posicion = [
#         colores.get("POSICION_1", [255, 255, 0]),
#         colores.get("POSICION_2", [220, 220, 220]),
#         colores.get("POSICION_3", [255, 165, 0]),
#         colores.get("POSICION_4", [0, 0, 0])
#     ]
    
#     for i, jugador in enumerate(jugadores_ordenados):
#         datos = resultados[jugador]
#         color = colores_posicion[min(i, 3)]
        
#         texto_pos = f"{i+1}°. {jugador} - {datos['puntaje']} puntos - {datos['porcentaje']}%"
#         centrar_texto(pantalla, texto_pos, font_texto, color, y_pos)
#         y_pos += 40
    
#     # Mostrar ganador
#     if jugadores_ordenados:
#         ganador = jugadores_ordenados[0]
#         centrar_texto(pantalla, f"¡GANADOR: {ganador}!", font_texto, colores.get("ROJO", [200, 0, 0]), 380)
    
#     # Botones
#     boton_nuevo = dibujar_boton(pantalla, 200, 450, 180, 50, "NUEVO JUEGO", 
#                                colores.get("VERDE", [0, 150, 0]), 
#                                colores.get("BLANCO", [255, 255, 255]), 
#                                colores.get("VERDE_HOVER", [50, 200, 50]), font_texto)
#     boton_menu = dibujar_boton(pantalla, 420, 450, 180, 50, "MENÚ PRINCIPAL", 
#                               colores.get("AZUL", [0, 100, 200]), 
#                               colores.get("BLANCO", [255, 255, 255]), 
#                               colores.get("AZUL_HOVER", [50, 150, 255]), font_texto)
    
#     # Procesar eventos
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             if boton_nuevo.collidepoint(pos_mouse):
#                 return "nuevo"
#             elif boton_menu.collidepoint(pos_mouse):
#                 return "menu"
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_n:
#                 return "nuevo"
#             elif evento.key == pygame.K_m or evento.key == pygame.K_ESCAPE:
#                 return "menu"
    
#     return None

# def mostrar_historial(estado_interfaz, eventos, config):
#     """Muestra el historial de partidas"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_titulo = get_font(font_cache, 36)
#     font_texto = get_font(font_cache, 24)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=120)
    
#     centrar_texto(pantalla, "HISTORIAL DE PARTIDAS", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
    
#     boton_volver = dibujar_boton(pantalla, 50, 520, 120, 40, "VOLVER", 
#                                 colores.get("GRIS_CLARO", [220, 220, 220]), 
#                                 colores.get("NEGRO", [0, 0, 0]), 
#                                 colores.get("GRIS_HOVER", [180, 180, 180]), font_texto)
    
#     try:
#         with open("partida_guardada.json", "r", encoding="utf-8") as archivo:
#             historial = json.load(archivo)
        
#         if "resultados" in historial and historial["resultados"]:
#             jugadores_ordenados = sorted(historial["resultados"].items(), key=lambda x: x[1].get("puntaje", 0), reverse=True)
            
#             y_pos = 120
#             centrar_texto(pantalla, "Última partida guardada:", font_texto, colores.get("NEGRO", [0, 0, 0]), y_pos)
#             y_pos += 50
            
#             colores_jugadores = [
#                 colores.get("JUGADOR_1", [0, 100, 200]), 
#                 colores.get("JUGADOR_2", [0, 150, 0]), 
#                 colores.get("JUGADOR_3", [255, 165, 0]), 
#                 colores.get("JUGADOR_4", [200, 0, 0]), 
#                 colores.get("GRIS", [128, 128, 128])
#             ]
            
#             for i, (jugador, datos) in enumerate(jugadores_ordenados[:8]):
#                 color = colores_jugadores[i % len(colores_jugadores)]
#                 texto = f"{i+1}. {jugador} - {datos.get('aciertos', 0)} aciertos - {datos.get('porcentaje', 0)}% - {datos.get('puntaje', 0)} pts"
#                 centrar_texto(pantalla, texto, font_texto, color, y_pos)
#                 y_pos += 35
#         else:
#             centrar_texto(pantalla, "No hay datos en el historial", font_texto, colores.get("GRIS", [128, 128, 128]), 200)
    
#     except FileNotFoundError:
#         centrar_texto(pantalla, "No hay historial disponible", font_texto, colores.get("NEGRO", [0, 0, 0]), 200)
#     except Exception as e:
#         centrar_texto(pantalla, f"Error al cargar historial", font_texto, colores.get("ROJO", [200, 0, 0]), 200)
    
#     # Procesar eventos
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             if boton_volver.collidepoint(pygame.mouse.get_pos()):
#                 return "menu"
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_ESCAPE:
#                 return "menu"
    
#     return "historial"


# # # interfaz_modificada.py
# import pygame
# import math
# import time
# import json
# import sys
# from configuracion import obtener_colores

# def inicializar_interfaz(pantalla):
#     """Inicializa la interfaz del juego y retorna el estado inicial"""
#     estado_interfaz = {
#         'pantalla': pantalla,
#         'font_cache': {},
#         'texto_ingreso': "",
#         'cursor_visible': True,
#         'tiempo_cursor': 0,
#         'imagen_fondo': cargar_imagen_fondo(pantalla)
#     }
#     return estado_interfaz

# def cargar_imagen_fondo(pantalla):
#     """Carga la imagen de fondo o usa color sólido"""
#     try:
#         imagen_fondo = pygame.image.load("PARCIAL 2/imagenes/fondo.png")
#         imagen_fondo = pygame.transform.scale(imagen_fondo, pantalla.get_size())
#     except pygame.error:
#         imagen_fondo = pygame.Surface(pantalla.get_size())
#         imagen_fondo.fill((173, 216, 230))
#     return imagen_fondo

# def get_font(font_cache, size):
#     """Cache de fuentes para mejor rendimiento"""
#     if size not in font_cache:
#         font_cache[size] = pygame.font.Font(None, size)
#     return font_cache[size]

# def dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=None):
#     """Dibuja el fondo con overlay opcional"""
#     pantalla.blit(imagen_fondo, (0, 0))
#     if overlay_alpha:
#         overlay = pygame.Surface(pantalla.get_size())
#         overlay.set_alpha(overlay_alpha)
#         overlay.fill((255, 255, 255))
#         pantalla.blit(overlay, (0, 0))

# def dibujar_boton(pantalla, x, y, ancho, alto, texto, color_fondo, color_texto, color_hover, font):
#     """Dibuja un botón con efectos hover"""
#     mouse_pos = pygame.mouse.get_pos()
#     boton_rect = pygame.Rect(x, y, ancho, alto)
#     mouse_over = boton_rect.collidepoint(mouse_pos)
    
#     color_actual = color_hover if mouse_over else color_fondo
    
#     if mouse_over:
#         sombra_rect = pygame.Rect(x+3, y+3, ancho, alto)
#         pygame.draw.rect(pantalla, (50, 50, 50), sombra_rect)
    
#     pygame.draw.rect(pantalla, color_actual, boton_rect)
#     pygame.draw.rect(pantalla, (0, 0, 0), boton_rect, 2)
    
#     texto_renderizado = font.render(texto, True, color_texto)
#     texto_rect = texto_renderizado.get_rect(center=boton_rect.center)
#     pantalla.blit(texto_renderizado, texto_rect)
    
#     return boton_rect

# def centrar_texto(pantalla, texto, font, color, y):
#     """Centra texto horizontalmente en la pantalla"""
#     texto_renderizado = font.render(texto, True, color)
#     x = (pantalla.get_width() - texto_renderizado.get_width()) // 2
#     pantalla.blit(texto_renderizado, (x, y))

# def dibujar_cuenta_regresiva(pantalla, tiempo_restante, config, tiempo_total=30):
#     """Dibuja el contador de tiempo circular"""
#     colores = obtener_colores(config)
    
#     centro_x, centro_y = 750, 93
#     radio = 35
    
#     progreso = tiempo_restante / tiempo_total if tiempo_total > 0 else 0
    
#     if tiempo_restante <= 5:
#         color_circulo = colores.get("TIEMPO_CRITICO", [200, 0, 0])
#         color_texto = colores.get("NEGRO", [0, 0, 0])
#         color_borde = tuple(max(0, c - 50) for c in color_circulo)
#     elif tiempo_restante <= 10:
#         color_circulo = colores.get("TIEMPO_ADVERTENCIA", [255, 165, 0])
#         color_texto = colores.get("NEGRO", [0, 0, 0])
#         color_borde = tuple(max(0, c - 50) for c in color_circulo)
#     else:
#         color_circulo = colores.get("TIEMPO_NORMAL", [0, 150, 0])
#         color_texto = colores.get("NEGRO", [0, 0, 0])
#         color_borde = tuple(max(0, c - 50) for c in color_circulo)
    
#     pygame.draw.circle(pantalla, colores.get("GRIS_CLARO", [220, 220, 220]), (centro_x, centro_y), radio)
#     pygame.draw.circle(pantalla, color_borde, (centro_x, centro_y), radio, 3)
    
#     if tiempo_restante > 0 and progreso > 0:
#         angulo = 2 * math.pi * progreso
#         puntos = [(centro_x, centro_y)]
#         num_puntos = max(int(angulo * 30), 3)
        
#         for i in range(num_puntos + 1):
#             angle = -math.pi/2 + (angulo * i / num_puntos)
#             px = centro_x + (radio - 2) * math.cos(angle)
#             py = centro_y + (radio - 2) * math.sin(angle)
#             puntos.append((px, py))
        
#         if len(puntos) > 2:
#             pygame.draw.polygon(pantalla, color_circulo, puntos)
    
#     font = pygame.font.Font(None, 28)
#     texto = font.render(str(tiempo_restante), True, color_texto)
#     texto_rect = texto.get_rect(center=(centro_x, centro_y))
#     pantalla.blit(texto, texto_rect)
    
#     font_pequeño = pygame.font.Font(None, 16)
#     color_label = colores.get("TIEMPO_CRITICO", [200, 0, 0]) if tiempo_restante <= 5 else colores.get("NEGRO", [0, 0, 0])
#     texto_label = font_pequeño.render("TIEMPO", True, color_label)
#     label_rect = texto_label.get_rect(center=(centro_x, centro_y + 40))
#     pantalla.blit(texto_label, label_rect)
    
#     if tiempo_restante <= 5:
#         pulso = int(time.time() * 10) % 2
#         if pulso:
#             pygame.draw.circle(pantalla, colores.get("TIEMPO_CRITICO", [200, 0, 0]), (centro_x, centro_y), radio + 5, 2)

# def mostrar_menu_principal(estado_interfaz, eventos, config):
#     """Muestra el menú principal"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_titulo = get_font(font_cache, 48)
#     font_opciones = get_font(font_cache, 36)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=50)
    
#     centrar_texto(pantalla, "JUEGO DE PREGUNTAS", font_titulo, colores.get("NEGRO", [0, 0, 0]), 80)
#     centrar_texto(pantalla, "Selecciona una opción:", font_opciones, colores.get("NEGRO", [0, 0, 0]), 160)
    
#     botones = [
#         (300, 220, 200, 60, "JUGAR", colores.get("BOTON_JUGAR", [80, 200, 255]), "jugar"),
#         (300, 300, 200, 60, "HISTORIAL", colores.get("BOTON_HISTORIAL", [255, 200, 0]), "historial"),
#         (300, 380, 200, 60, "ACCESIBILIDAD", colores.get("BOTON_ACCESIBILIDAD", [150, 100, 255]), "accesibilidad"),
#         (300, 460, 200, 60, "SALIR", colores.get("BOTON_SALIR", [255, 100, 100]), "salir")
#     ]
    
#     botones_rect = []
#     for x, y, w, h, texto, color, accion in botones:
#         color_hover = tuple(min(255, max(0, c + 30)) for c in color)
#         rect = dibujar_boton(pantalla, x, y, w, h, texto, color, colores.get("NEGRO", [0, 0, 0]), color_hover, font_opciones)
#         botones_rect.append((rect, accion))
    
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             for rect, accion in botones_rect:
#                 if rect.collidepoint(pos_mouse):
#                     if accion == "salir":
#                         pygame.quit()
#                         sys.exit()
#                     return accion
    
#     return "menu"

# def mostrar_menu_accesibilidad(estado_interfaz, eventos, config):
#     """Muestra el menú de accesibilidad"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
#     font_titulo = get_font(font_cache, 40)
#     font_texto = get_font(font_cache, 32)
#     font_info = get_font(font_cache, 24)
#     font_pequeño = get_font(font_cache, 20)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
#     centrar_texto(pantalla, "CONFIGURACIÓN DE ACCESIBILIDAD", font_titulo, colores.get("NEGRO", [0, 0, 0]), 60)
    
#     modo_actual = config.get("Accesibilidad", "neurotipico")
    
#     if modo_actual == "daltonico":
#         texto_modo = "🔵 MODO DALTÓNICO ACTIVADO"
#         color_modo = (0, 150, 200)
#         info_color = "Se han aplicado cambios de colores para daltonismo"
#     else:
#         texto_modo = "🟢 MODO NORMAL ACTIVADO"  
#         color_modo = (0, 150, 0)
#         info_color = "Colores estándar activos"
    
#     centrar_texto(pantalla, texto_modo, font_texto, color_modo, 120)
#     centrar_texto(pantalla, info_color, font_pequeño, colores.get("NEGRO", [0, 0, 0]), 160)
    
#     info_lines = [
#         "",
#         "Cambios aplicados en modo daltónico:",
#         "• Verdes → Azules para mejor distinción",
#         "• Rojos → Naranjas/Marrones más visibles", 
#         "• Mayor contraste en elementos importantes",
#         "• Optimizado para daltonismo rojo-verde"
#     ]
    
#     y_pos = 200
#     for linea in info_lines:
#         if linea:
#             centrar_texto(pantalla, linea, font_info, colores.get("NEGRO", [0, 0, 0]), y_pos)
#         y_pos += 25
    
#     if modo_actual == "daltonico":
#         color_boton_toggle = (0, 150, 200)
#         color_hover_toggle = (30, 180, 255)
#         texto_boton = "VOLVER A NORMAL"
#     else:
#         color_boton_toggle = (255, 150, 0)
#         color_hover_toggle = (255, 180, 50)
#         texto_boton = "ACTIVAR MODO DALTÓNICO"
    
#     boton_toggle = dibujar_boton(pantalla, 200, 480, 400, 50, texto_boton, color_boton_toggle, (255, 255, 255), color_hover_toggle, font_texto)
#     boton_volver = dibujar_boton(pantalla, 250, 540, 300, 40, "VOLVER AL MENÚ", colores.get("GRIS_CLARO", [220, 220, 220]), colores.get("NEGRO", [0, 0, 0]), colores.get("GRIS_HOVER", [180, 180, 180]), font_info)
    
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             if boton_toggle.collidepoint(pos_mouse):
#                 return "toggle"
#             elif boton_volver.collidepoint(pos_mouse):
#                 return "menu"
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_ESCAPE:
#                 return "menu"
    
#     return "accesibilidad"

# def mostrar_ingreso_jugador(estado_interfaz, jugadores_actuales, puede_agregar, eventos, config):
#     """Muestra la pantalla de ingreso de jugadores"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_titulo = get_font(font_cache, 40)
#     font_texto = get_font(font_cache, 32)
#     font_pequeño = get_font(font_cache, 24)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
#     centrar_texto(pantalla, "INGRESO DE JUGADORES", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
#     centrar_texto(pantalla, f"Jugadores registrados: {len(jugadores_actuales)}/4", font_texto, colores.get("NEGRO", [0, 0, 0]), 120)
    
#     y_pos = 170
#     colores_jugadores = [
#         colores.get("JUGADOR_1", [0, 100, 200]),
#         colores.get("JUGADOR_2", [0, 150, 0]),
#         colores.get("JUGADOR_3", [255, 165, 0]),
#         colores.get("JUGADOR_4", [200, 0, 0])
#     ]
#     for i, jugador in enumerate(jugadores_actuales):
#         color = colores_jugadores[i]
#         texto = f"Jugador {i+1}: {jugador}"
#         centrar_texto(pantalla, texto, font_texto, color, y_pos)
#         y_pos += 35
    
#     if puede_agregar and len(jugadores_actuales) < 4:
#         y_entrada = 320
#         centrar_texto(pantalla, f"Ingresa el nombre del Jugador {len(jugadores_actuales) + 1}:", font_pequeño, colores.get("NEGRO", [0, 0, 0]), y_entrada - 30)
        
#         entrada_rect = pygame.Rect(250, y_entrada, 300, 50)
#         pygame.draw.rect(pantalla, colores.get("BLANCO", [255, 255, 255]), entrada_rect)
#         pygame.draw.rect(pantalla, colores.get("NEGRO", [0, 0, 0]), entrada_rect, 2)
        
#         if time.time() - estado_interfaz['tiempo_cursor'] > 0.5:
#             estado_interfaz['cursor_visible'] = not estado_interfaz['cursor_visible']
#             estado_interfaz['tiempo_cursor'] = time.time()
        
#         texto_mostrar = estado_interfaz['texto_ingreso'] + ("|" if estado_interfaz['cursor_visible'] else "")
#         texto_render = font_texto.render(texto_mostrar, True, colores.get("NEGRO", [0, 0, 0]))
#         texto_rect = texto_render.get_rect(center=entrada_rect.center)
#         pantalla.blit(texto_render, texto_rect)
        
#         centrar_texto(pantalla, "Presiona ENTER para confirmar", font_pequeño, colores.get("NEGRO", [0, 0, 0]), y_entrada + 70)
    
#     y_botones = 450
#     botones = []
    
#     if jugadores_actuales:
#         if len(jugadores_actuales) < 4:
#             boton_agregar = dibujar_boton(pantalla, 150, y_botones, 160, 40, "AGREGAR MÁS", colores.get("AZUL", [0, 100, 200]), colores.get("BLANCO", [255, 255, 255]), colores.get("AZUL_HOVER", [50, 150, 255]), font_pequeño)
#             botones.append(("agregar", boton_agregar))
        
#         boton_iniciar = dibujar_boton(pantalla, 330, y_botones, 160, 40, "INICIAR JUEGO", colores.get("VERDE", [0, 150, 0]), colores.get("BLANCO", [255, 255, 255]), colores.get("VERDE_HOVER", [50, 200, 50]), font_pequeño)
#         botones.append(("continuar", boton_iniciar))
    
#     boton_volver = dibujar_boton(pantalla, 510, y_botones, 140, 40, "VOLVER", colores.get("GRIS", [128, 128, 128]), colores.get("BLANCO", [255, 255, 255]), colores.get("GRIS_HOVER", [180, 180, 180]), font_pequeño)
#     botones.append(("menu", boton_volver))
    
#     for evento in eventos:
#         if evento.type == pygame.KEYDOWN:
#             if puede_agregar and len(jugadores_actuales) < 4:
#                 if evento.key == pygame.K_BACKSPACE:
#                     estado_interfaz['texto_ingreso'] = estado_interfaz['texto_ingreso'][:-1]
#                 elif evento.key == pygame.K_RETURN and estado_interfaz['texto_ingreso'].strip():
#                     nombre = estado_interfaz['texto_ingreso'].strip()
#                     estado_interfaz['texto_ingreso'] = ""
#                     return nombre
#                 elif evento.unicode and len(estado_interfaz['texto_ingreso']) < 15:
#                     estado_interfaz['texto_ingreso'] += evento.unicode
            
#             if evento.key == pygame.K_ESCAPE:
#                 return "menu"
        
#         elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             for accion, boton in botones:
#                 if boton.collidepoint(pos_mouse):
#                     if accion == "agregar":
#                         return None
#                     return accion
    
#     return None

# def mostrar_seleccion_dificultad(estado_interfaz, jugador, eventos, config):
#     """Muestra la selección de dificultad"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_titulo = get_font(font_cache, 40)
#     font_opciones = get_font(font_cache, 32)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
#     centrar_texto(pantalla, f"Turno de: {jugador}", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
#     centrar_texto(pantalla, "SELECCIONA LA DIFICULTAD", font_titulo, colores.get("NEGRO", [0, 0, 0]), 120)
    
#     botones = [
#         (250, 200, 300, 60, "FÁCIL - 10 puntos", colores.get("BOTON_FACIL", [144, 238, 144]), "Fácil"),
#         (250, 280, 300, 60, "MEDIO - 20 puntos", colores.get("BOTON_MEDIO", [255, 255, 0]), "Medio"),
#         (250, 360, 300, 60, "DIFÍCIL - 30 puntos", colores.get("BOTON_DIFICIL", [255, 182, 193]), "Difícil"),
#         (250, 450, 300, 40, "VOLVER AL MENÚ", colores.get("GRIS_CLARO", [220, 220, 220]), "menu")
#     ]
    
#     botones_rect = []
#     for x, y, w, h, texto, color, accion in botones:
#         color_hover = tuple(min(255, c + 50) for c in color)
#         rect = dibujar_boton(pantalla, x, y, w, h, texto, color, colores.get("NEGRO", [0, 0, 0]), color_hover, font_opciones)
#         botones_rect.append((rect, accion))
    
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             for rect, accion in botones_rect:
#                 if rect.collidepoint(pos_mouse):
#                     return accion
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_1:
#                 return "Fácil"
#             elif evento.key == pygame.K_2:
#                 return "Medio"
#             elif evento.key == pygame.K_3:
#                 return "Difícil"
#             elif evento.key == pygame.K_ESCAPE:
#                 return "menu"
    
#     return None

# def mostrar_ruleta_categoria(estado_interfaz, categorias_disponibles, categorias_jugadas, tiempo_animacion, config):
#     """Muestra la ruleta de categorías animada"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=100)
    
#     font_titulo = get_font(font_cache, 48)
#     font_categoria = get_font(font_cache, 28)
    
#     centrar_texto(pantalla, "RULETA DE CATEGORÍAS", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
    
#     centro_x, centro_y = 400, 300
#     radio = 150
    
#     categorias_ruleta = [cat for cat in categorias_disponibles if cat not in categorias_jugadas]
    
#     if not categorias_ruleta:
#         return
    
#     velocidad = max(1, 10 - tiempo_animacion * 3)
#     angulo_rotacion = tiempo_animacion * velocidad * 360
    
#     num_categorias = len(categorias_ruleta)
#     angulo_seccion = 360 / num_categorias
    
#     colores_ruleta = [
#         colores.get("RULETA_COLOR_1", [144, 238, 144]), 
#         colores.get("RULETA_COLOR_2", [255, 255, 0]), 
#         colores.get("RULETA_COLOR_3", [255, 182, 193]), 
#         colores.get("RULETA_COLOR_4", [173, 216, 230]), 
#         colores.get("RULETA_COLOR_5", [255, 165, 0]), 
#         colores.get("RULETA_COLOR_6", [220, 220, 220])
#     ]
    
#     for i in range(num_categorias):
#         angulo_inicio = i * angulo_seccion + angulo_rotacion
#         angulo_fin = (i + 1) * angulo_seccion + angulo_rotacion
        
#         puntos = [(centro_x, centro_y)]
#         for angulo in range(int(angulo_inicio), int(angulo_fin) + 1):
#             x = centro_x + radio * math.cos(math.radians(angulo))
#             y = centro_y + radio * math.sin(math.radians(angulo))
#             puntos.append((x, y))
        
#         if len(puntos) > 2:
#             color_seccion = colores_ruleta[i % len(colores_ruleta)]
#             pygame.draw.polygon(pantalla, color_seccion, puntos)
#             pygame.draw.polygon(pantalla, colores.get("NEGRO", [0, 0, 0]), puntos, 3)
        
#         angulo_texto = math.radians(angulo_inicio + angulo_seccion / 2)
#         texto_x = centro_x + (radio * 0.6) * math.cos(angulo_texto)
#         texto_y = centro_y + (radio * 0.6) * math.sin(angulo_texto)
        
#         nombre_cat = categorias_ruleta[i]
#         if len(nombre_cat) > 10:
#             nombre_cat = nombre_cat[:8] + ".."
        
#         texto = font_categoria.render(nombre_cat, True, colores.get("NEGRO", [0, 0, 0]))
#         texto_rect = texto.get_rect(center=(texto_x, texto_y))
#         pantalla.blit(texto, texto_rect)
    
#     pygame.draw.polygon(pantalla, colores.get("ROJO", [200, 0, 0]), 
#                       [(centro_x + radio + 10, centro_y),
#                        (centro_x + radio + 40, centro_y - 15),
#                        (centro_x + radio + 40, centro_y + 15)], 0)
    
#     pygame.draw.circle(pantalla, colores.get("NEGRO", [0, 0, 0]), (centro_x, centro_y), 30)
#     pygame.draw.circle(pantalla, colores.get("BLANCO", [255, 255, 255]), (centro_x, centro_y), 30, 3)
    
#     font_pequeño = get_font(font_cache, 16)
#     texto_gira = font_pequeño.render("GIRA", True, colores.get("NEGRO", [0, 0, 0]))
#     texto_rect = texto_gira.get_rect(center=(centro_x, centro_y))
#     pantalla.blit(texto_gira, texto_rect)

# def mostrar_categoria_seleccionada(estado_interfaz, categoria, jugador, eventos, config):
#     """Muestra la categoría seleccionada"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=120)
    
#     font_titulo = get_font(font_cache, 48)
#     font_texto = get_font(font_cache, 36)
#     font_pequeño = get_font(font_cache, 24)
    
#     centrar_texto(pantalla, "¡CATEGORÍA SELECCIONADA!", font_titulo, colores.get("NEGRO", [0, 0, 0]), 150)
#     centrar_texto(pantalla, categoria.upper(), font_titulo, colores.get("AZUL", [0, 100, 200]), 220)
    
#     centrar_texto(pantalla, f"Jugador: {jugador}", font_texto, colores.get("NEGRO", [0, 0, 0]), 320)
#     centrar_texto(pantalla, "Presiona ESPACIO para comenzar", font_pequeño, colores.get("NEGRO", [0, 0, 0]), 400)
    
#     for evento in eventos:
#         if evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_SPACE:
#                 return True
#         elif evento.type == pygame.MOUSEBUTTONDOWN:
#             return True
    
#     return False

# def mostrar_pregunta(estado_interfaz, pregunta, categoria, pregunta_num, total_preguntas, puntaje, eventos, tiempo_restante, jugador, config):
#     """Muestra una pregunta con opciones"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_info = get_font(font_cache, 20)
#     font_pregunta = get_font(font_cache, 24)
#     font_opciones = get_font(font_cache, 22)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=150)
    
#     info_texto = f"{jugador} | {categoria} | Pregunta {pregunta_num}/{total_preguntas} | Puntaje: {puntaje}"
#     centrar_texto(pantalla, info_texto, font_info, colores.get("NEGRO", [0, 0, 0]), 20)
    
#     dibujar_cuenta_regresiva(pantalla, tiempo_restante, config)
    
#     dificultad_texto = f"Dificultad: {pregunta['dificultad']}"
#     pantalla.blit(font_info.render(dificultad_texto, True, colores.get("NEGRO", [0, 0, 0])), (50, 20))
    
#     pygame.draw.line(pantalla, colores.get("NEGRO", [0, 0, 0]), (0, 50), (800, 50), 2)
    
#     centrar_texto(pantalla, pregunta["pregunta"], font_pregunta, colores.get("NEGRO", [0, 0, 0]), 80)
    
#     y_opciones = 180
#     botones_opciones = []
#     colores_opciones = [
#         colores.get("OPCION_1", [173, 216, 230]),
#         colores.get("OPCION_2", [144, 238, 144]), 
#         colores.get("OPCION_3", [255, 255, 0]),
#         colores.get("OPCION_4", [255, 182, 193])
#     ]
#     colores_hover = [tuple(min(255, max(0, c + 50)) for c in color) for color in colores_opciones]
    
#     for i, opcion in enumerate(pregunta["opciones"]):
#         texto_opcion = f"{i+1}. {opcion[:60]}..." if len(opcion) > 60 else f"{i+1}. {opcion}"
#         boton = dibujar_boton(pantalla, 100, y_opciones + i * 70, 600, 50, texto_opcion, 
#                              colores_opciones[i], colores.get("NEGRO", [0, 0, 0]), colores_hover[i], font_opciones)
#         botones_opciones.append(boton)
    
#     boton_menu = dibujar_boton(pantalla, 50, 520, 120, 40, "MENÚ", colores.get("ROJO_CLARO", [255, 182, 193]), 
#                               colores.get("NEGRO", [0, 0, 0]), colores.get("ROJO_HOVER", [255, 50, 50]), font_opciones)
    
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             if boton_menu.collidepoint(pos_mouse):
#                 return "menu"
#             for i, boton in enumerate(botones_opciones):
#                 if boton.collidepoint(pos_mouse):
#                     return str(i + 1)
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
#                 return str(evento.key - pygame.K_0)
#             elif evento.key == pygame.K_ESCAPE:
#                 return "menu"
    
#     return None

# def mostrar_resultado_respuesta(estado_interfaz, correcto, respuesta_correcta, opciones, puntaje_ganado, eventos, config):
#     """Muestra el resultado de la respuesta"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_titulo = get_font(font_cache, 48)
#     font_texto = get_font(font_cache, 32)
#     font_pequeño = get_font(font_cache, 24)
    
#     dibujar_fondo(pantalla, imagen_fondo)
    
#     overlay = pygame.Surface(pantalla.get_size())
#     color_overlay = colores.get("CORRECTO", [144, 238, 144]) if correcto else colores.get("INCORRECTO", [255, 182, 193])
#     overlay.fill(color_overlay)
#     overlay.set_alpha(120)
#     pantalla.blit(overlay, (0, 0))
    
#     mensaje = "¡CORRECTO!" if correcto else "¡INCORRECTO!"
#     centrar_texto(pantalla, mensaje, font_titulo, colores.get("NEGRO", [0, 0, 0]), 150)
    
#     if correcto:
#         centrar_texto(pantalla, f"Has ganado {puntaje_ganado} puntos", font_texto, colores.get("NEGRO", [0, 0, 0]), 220)
#     else:
#         try:
#             indice_correcto = int(respuesta_correcta) - 1
#             if 0 <= indice_correcto < len(opciones):
#                 opcion_correcta = opciones[indice_correcto]
#                 centrar_texto(pantalla, "La respuesta correcta era:", font_texto, colores.get("NEGRO", [0, 0, 0]), 220)
#                 centrar_texto(pantalla, f"({respuesta_correcta}) {opcion_correcta}", font_pequeño, colores.get("NEGRO", [0, 0, 0]), 260)
#         except (ValueError, TypeError):
#             centrar_texto(pantalla, f"La respuesta correcta era: Opción {respuesta_correcta}", font_texto, colores.get("NEGRO", [0, 0, 0]), 220)
    
#     centrar_texto(pantalla, "Presiona ESPACIO para continuar", font_pequeño, colores.get("NEGRO", [0, 0, 0]), 400)
    
#     for evento in eventos:
#         if evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_SPACE:
#                 return True
#         elif evento.type == pygame.MOUSEBUTTONDOWN:
#             return True
    
#     return False

# def mostrar_fin_categoria(estado_interfaz, categoria, respuestas_correctas, puntaje, eventos, config):
#     """Muestra el fin de una categoría"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=80)
    
#     font_titulo = get_font(font_cache, 48)
#     font_texto = get_font(font_cache, 32)
    
#     centrar_texto(pantalla, "CATEGORÍA COMPLETADA", font_titulo, colores.get("NEGRO", [0, 0, 0]), 100)
#     centrar_texto(pantalla, categoria.upper(), font_texto, colores.get("AZUL", [0, 100, 200]), 180)
    
#     centrar_texto(pantalla, f"Respuestas correctas: {respuestas_correctas}/10", font_texto, colores.get("NEGRO", [0, 0, 0]), 250)
#     centrar_texto(pantalla, f"Puntos en esta ronda: {puntaje}", font_texto, colores.get("VERDE", [0, 150, 0]), 300)
    
#     boton_continuar = dibujar_boton(pantalla, 300, 400, 200, 50, "CONTINUAR", 
#                                    colores.get("VERDE", [0, 150, 0]), 
#                                    colores.get("BLANCO", [255, 255, 255]), 
#                                    colores.get("VERDE_HOVER", [50, 200, 50]), font_texto)
    
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN:
#             if evento.button == 1:
#                 if boton_continuar.collidepoint(pygame.mouse.get_pos()):
#                     return "continuar"
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_SPACE:
#                 return "continuar"
#             elif evento.key == pygame.K_ESCAPE:
#                 return "menu"
    
#     return None

# def mostrar_resultados_finales(estado_interfaz, jugadores, resultados, eventos, config):
#     """Muestra los resultados finales del juego"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_titulo = get_font(font_cache, 48)
#     font_texto = get_font(font_cache, 28)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=100)
    
#     centrar_texto(pantalla, "¡JUEGO TERMINADO!", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
#     centrar_texto(pantalla, "RESULTADOS FINALES", font_texto, colores.get("AZUL", [0, 100, 200]), 120)
    
#     jugadores_ordenados = sorted(jugadores, key=lambda j: resultados[j]["puntaje"], reverse=True)
    
#     y_pos = 180
#     colores_posicion = [
#         colores.get("POSICION_1", [255, 255, 0]),
#         colores.get("POSICION_2", [220, 220, 220]),
#         colores.get("POSICION_3", [255, 165, 0]),
#         colores.get("POSICION_4", [0, 0, 0])
#     ]
    
#     for i, jugador in enumerate(jugadores_ordenados):
#         datos = resultados[jugador]
#         color = colores_posicion[min(i, 3)]
        
#         texto_pos = f"{i+1}°. {jugador} - {datos['puntaje']} puntos - {datos['porcentaje']}%"
#         centrar_texto(pantalla, texto_pos, font_texto, color, y_pos)
#         y_pos += 40
    
#     if jugadores_ordenados:
#         ganador = jugadores_ordenados[0]
#         centrar_texto(pantalla, f"¡GANADOR: {ganador}!", font_texto, colores.get("ROJO", [200, 0, 0]), 380)
    
#     boton_nuevo = dibujar_boton(pantalla, 200, 450, 180, 50, "NUEVO JUEGO", 
#                                colores.get("VERDE", [0, 150, 0]), 
#                                colores.get("BLANCO", [255, 255, 255]), 
#                                colores.get("VERDE_HOVER", [50, 200, 50]), font_texto)
#     boton_menu = dibujar_boton(pantalla, 420, 450, 180, 50, "MENÚ PRINCIPAL", 
#                               colores.get("AZUL", [0, 100, 200]), 
#                               colores.get("BLANCO", [255, 255, 255]), 
#                               colores.get("AZUL_HOVER", [50, 150, 255]), font_texto)
    
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             pos_mouse = pygame.mouse.get_pos()
#             if boton_nuevo.collidepoint(pos_mouse):
#                 return "nuevo"
#             elif boton_menu.collidepoint(pos_mouse):
#                 return "menu"
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_n:
#                 return "nuevo"
#             elif evento.key == pygame.K_m or evento.key == pygame.K_ESCAPE:
#                 return "menu"
    
#     return None

# def mostrar_historial(estado_interfaz, eventos, config):
#     """Muestra el historial de partidas"""
#     pantalla = estado_interfaz['pantalla']
#     font_cache = estado_interfaz['font_cache']
#     imagen_fondo = estado_interfaz['imagen_fondo']
    
#     colores = obtener_colores(config)
    
#     font_titulo = get_font(font_cache, 36)
#     font_texto = get_font(font_cache, 24)
    
#     dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=120)
    
#     centrar_texto(pantalla, "HISTORIAL DE PARTIDAS", font_titulo, colores.get("NEGRO", [0, 0, 0]), 50)
    
#     boton_volver = dibujar_boton(pantalla, 50, 520, 120, 40, "VOLVER", 
#                                 colores.get("GRIS_CLARO", [220, 220, 220]), 
#                                 colores.get("NEGRO", [0, 0, 0]), 
#                                 colores.get("GRIS_HOVER", [180, 180, 180]), font_texto)
    
#     try:
#         with open("partida_guardada.json", "r", encoding="utf-8") as archivo:
#             historial = json.load(archivo)
        
#         if "resultados" in historial and historial["resultados"]:
#             jugadores_ordenados = sorted(historial["resultados"].items())
            
#             y_pos = 120
#             centrar_texto(pantalla, "Última partida guardada:", font_texto, colores.get("NEGRO", [0, 0, 0]), y_pos)
#             y_pos += 50
            
#             colores_jugadores = [
#                 colores.get("JUGADOR_1", [0, 100, 200]), 
#                 colores.get("JUGADOR_2", [0, 150, 0]), 
#                 colores.get("JUGADOR_3", [255, 165, 0]), 
#                 colores.get("JUGADOR_4", [200, 0, 0]), 
#                 colores.get("GRIS", [128, 128, 128])
#             ]
#             for i, (jugador, datos) in enumerate(jugadores_ordenados[:8]):
#                 color = colores_jugadores[i % len(colores_jugadores)]
#                 texto = f"{i+1}. {jugador} - {datos.get('aciertos', 0)} aciertos - {datos.get('porcentaje', 0)}% - {datos.get('puntaje', 0)} pts"
#                 centrar_texto(pantalla, texto, font_texto, color, y_pos)
#                 y_pos += 35
#         else:
#             centrar_texto(pantalla, "No hay datos en el historial", font_texto, colores.get("GRIS", [128, 128, 128]), 200)
    
#     except FileNotFoundError:
#         centrar_texto(pantalla, "No hay historial disponible", font_texto, colores.get("NEGRO", [0, 0, 0]), 200)
#     except Exception as e:
#         centrar_texto(pantalla, f"Error al cargar historial", font_texto, colores.get("ROJO", [200, 0, 0]), 200)
    
#     for evento in eventos:
#         if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
#             if boton_volver.collidepoint(pygame.mouse.get_pos()):
#                 return "menu"
#         elif evento.type == pygame.KEYDOWN:
#             if evento.key == pygame.K_ESCAPE:
#                 return "menu"
    
#     return "historial"





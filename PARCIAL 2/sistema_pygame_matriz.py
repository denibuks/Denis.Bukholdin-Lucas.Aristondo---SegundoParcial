

def aplicar_solo_tateti_matrices():
    """Aplica SOLO el tateti con matrices sin modificar nada más"""
    
    try:
        import numpy as np
        print("✅ NumPy detectado - tateti con matrices disponible")
    except ImportError:
        print("❌ NumPy no encontrado. Instala con: pip install numpy")
        return False
    
    import interfaz
    from configuracion import obtener_colores
    
    # SOLO modificar el menú para agregar el botón de tateti
    original_mostrar_menu = interfaz.mostrar_menu_principal
    
    def menu_con_tateti(estado_interfaz, eventos, config):
        import pygame
        """Menú que incluye tateti pero mantiene todo lo demás igual"""
        pantalla = estado_interfaz['pantalla']
        font_cache = estado_interfaz['font_cache']
        imagen_fondo = estado_interfaz['imagen_fondo']
        
        colores = obtener_colores(config)
        
        font_titulo = interfaz.get_font(font_cache, 48)
        font_opciones = interfaz.get_font(font_cache, 32)
        
        interfaz.dibujar_fondo(pantalla, imagen_fondo, overlay_alpha=50)
        
        interfaz.centrar_texto(pantalla, "JUEGO DE PREGUNTAS", font_titulo, colores.get("NEGRO", [0, 0, 0]), 60)
        interfaz.centrar_texto(pantalla, "🔢 Con Tateti de Matrices", interfaz.get_font(font_cache, 24), colores.get("AZUL", [0, 100, 200]), 90)
        interfaz.centrar_texto(pantalla, "Selecciona una opción:", font_opciones, colores.get("NEGRO", [0, 0, 0]), 130)
        
        # Botones con tateti incluido
        botones = [
            (300, 170, 200, 45, "JUGAR", colores.get("BOTON_JUGAR", [80, 200, 255]), "jugar"),
            (300, 225, 200, 45, "TATETI", colores.get("VERDE", [0, 150, 0]), "tateti"),
            (300, 280, 200, 45, "HISTORIAL", colores.get("BOTON_HISTORIAL", [255, 200, 0]), "historial"),
            (300, 335, 200, 45, "ACCESIBILIDAD", colores.get("BOTON_ACCESIBILIDAD", [150, 100, 255]), "accesibilidad"),
            (300, 390, 200, 45, "SALIR", colores.get("BOTON_SALIR", [255, 100, 100]), "salir")
        ]
        
        botones_rect = []
        for x, y, w, h, texto, color, accion in botones:
            color_hover = tuple(min(255, max(0, c + 30)) for c in color)
            rect = interfaz.dibujar_boton(pantalla, x, y, w, h, texto, color, colores.get("NEGRO", [0, 0, 0]), color_hover, font_opciones)
            botones_rect.append((rect, accion))
        
        # Info sobre matrices
        info_text = "Presiona 'M' en el tateti para ver las matrices"
        interfaz.centrar_texto(pantalla, info_text, interfaz.get_font(font_cache, 18), colores.get("GRIS", [128, 128, 128]), 450)
        
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()
                for rect, accion in botones_rect:
                    if rect.collidepoint(pos_mouse):
                        if accion == "salir":
                            import pygame
                            import sys
                            pygame.quit()
                            sys.exit()
                        elif accion == "tateti":
                            print("🔢 Iniciando tateti con matrices")
                        return accion
        
        return "menu"
    
    # Reemplazar SOLO el menú
    interfaz.mostrar_menu_principal = menu_con_tateti
    
    print(" Integración simple aplicada:")
    print("    Tateti con matrices agregado al menú")
    print("    Todo lo demás funciona igual")
    print("    Tu gestores_modificado.py funciona perfecto")
    
    return True
# main.py - ARCHIVO PRINCIPAL CON MÚSICA INTEGRADA

import pygame
import sys

def main():
    """Función principal que inicia el juego con música"""
    pygame.init()
    pygame.mixer.init()
    
    # Importar módulos
    import gestores
    import interfaz
    import musica  # Tu nuevo sistema de música
    from configuracion import cargar_configuracion, cargar_preguntas_desde_csv
    
    # Cargar configuración
    config = cargar_configuracion("PARCIAL 2/configuracion.json")
    
    # Configurar ventana
    ventana_config = config.get("interfaz", {}).get("tamaño_ventana", {"ancho": 800, "alto": 600})
    pantalla = pygame.display.set_mode((ventana_config["ancho"], ventana_config["alto"]))
    pygame.display.set_caption("Juego de Preguntas")
    reloj = pygame.time.Clock()
    
    # Cargar preguntas
    ruta_preguntas = config.get("archivos", {}).get("preguntas_csv", "PARCIAL 2/preguntas.csv")
    preguntas = cargar_preguntas_desde_csv(ruta_preguntas)
    
    # ===== INICIALIZAR MÚSICA DE AMBIENTE =====
    print(" Iniciando música de ambiente...")
    musica.iniciar_musica_ambiente()
    
    # ===== CORREGIR PARTIDAS GUARDADAS =====
    print("🔧 Verificando partidas guardadas...")
    gestores.corregir_porcentajes_partida_guardada()
    
    # Inicializar estado del juego
    estado_juego = gestores.crear_estado_inicial(config)
    estado_interfaz = interfaz.inicializar_interfaz(pantalla)
    
    # Loop principal del juego
    running = True
    while running:
        eventos = pygame.event.get()
        
        # Manejar eventos de sistema
        for evento in eventos:
            if evento.type == pygame.QUIT:
                running = False
            elif evento.type == pygame.KEYDOWN:
                # ===== CONTROLES DE MÚSICA DE AMBIENTE =====
                if evento.key == pygame.K_F1:  # F1 para pausar/reanudar
                    musica.alternar_musica()
                elif evento.key == pygame.K_PLUS or evento.key == pygame.K_EQUALS:  # + subir volumen
                    musica.subir_volumen()
                elif evento.key == pygame.K_MINUS:  # - bajar volumen
                    musica.bajar_volumen()
        
        # Procesar estado del juego
        gestores.procesar_estado(estado_juego, config, preguntas, estado_interfaz, eventos)
        
        # Actualizar pantalla
        pygame.display.flip()
        reloj.tick(60)
    
    # ===== LIMPIAR AL SALIR =====
    print(" Deteniendo música de ambiente...")
    musica.limpiar_musica()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()





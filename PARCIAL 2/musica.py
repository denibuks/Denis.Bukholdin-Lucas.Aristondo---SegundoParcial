import pygame
import os

# =================== CONFIGURACIÓN ===================

def inicializar_mixer():
    """Inicializa el mixer de pygame"""
    try:
        pygame.mixer.pre_init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=2048
        )
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        print("🎵 Mixer inicializado para música de ambiente")
        return True
    except pygame.error as e:
        print(f"❌ Error inicializando mixer: {e}")
        return False

def buscar_soundtrack():
    """Busca el archivo soundtrack.mp3"""
    rutas_posibles = [
        "sonidos/soundtrack.mp3",
        "PARCIAL 2/sonidos/soundtrack.mp3",
        "soundtrack.mp3",
        "PARCIAL 2/soundtrack.mp3"
    ]
    
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            print(f"🎵 Soundtrack encontrado: {ruta}")
            return ruta
    
    print("❌ No se encontró soundtrack.mp3")
    return None

# =================== FUNCIONES PRINCIPALES ===================

def iniciar_musica_ambiente():
    """Inicia la música de ambiente automáticamente"""
    if not inicializar_mixer():
        return False
    
    archivo = buscar_soundtrack()
    if not archivo:
        return False
    
    try:
        pygame.mixer.music.load(archivo)
        pygame.mixer.music.set_volume(0.3)  # Volumen bajo para ambiente
        pygame.mixer.music.play(-1)  # Loop infinito
        print("🎵 Música de ambiente iniciada")
        return True
    except pygame.error as e:
        print(f"❌ Error reproduciendo música: {e}")
        return False

def pausar_musica():
    """Pausa la música"""
    try:
        pygame.mixer.music.pause()
        print("⏸️ Música pausada")
    except:
        pass

def reanudar_musica():
    """Reanuda la música"""
    try:
        pygame.mixer.music.unpause()
        print("▶️ Música reanudada")
    except:
        pass

def detener_musica():
    """Detiene la música"""
    try:
        pygame.mixer.music.stop()
        print("⏹️ Música detenida")
    except:
        pass

def alternar_musica():
    """Alterna entre pausa y reproducción"""
    try:
        if pygame.mixer.music.get_busy():
            pausar_musica()
        else:
            reanudar_musica()
    except:
        # Si hay error, intentar iniciar desde cero
        iniciar_musica_ambiente()

def configurar_volumen(volumen):
    """Configura el volumen (0.0 a 1.0)"""
    try:
        volumen = max(0.0, min(1.0, volumen))
        pygame.mixer.music.set_volume(volumen)
        print(f"🔊 Volumen: {int(volumen * 100)}%")
    except:
        pass

def subir_volumen():
    """Sube el volumen en 10%"""
    try:
        volumen_actual = pygame.mixer.music.get_volume()
        nuevo_volumen = min(1.0, volumen_actual + 0.1)
        configurar_volumen(nuevo_volumen)
    except:
        pass

def bajar_volumen():
    """Baja el volumen en 10%"""
    try:
        volumen_actual = pygame.mixer.music.get_volume()
        nuevo_volumen = max(0.0, volumen_actual - 0.1)
        configurar_volumen(nuevo_volumen)
    except:
        pass

def musica_reproduciendose():
    """Verifica si la música está reproduciéndose"""
    try:
        return pygame.mixer.music.get_busy()
    except:
        return False

def limpiar_musica():
    """Limpia el sistema de música"""
    try:
        pygame.mixer.music.stop()
        print("🔧 Música limpiada")
    except:
        pass

# =================== FUNCIONES DE COMPATIBILIDAD ===================
# Estas funciones no hacen nada porque solo tienes música de ambiente
# Pero existen para que el código existente no de error

def inicializar_audio_completo(config):
    """Función de compatibilidad que solo inicia la música"""
    return iniciar_musica_ambiente()

def inicializar_musica_juego():
    """Función de compatibilidad"""
    return iniciar_musica_ambiente()

def obtener_sistema_audio():
    """Función de compatibilidad"""
    return None

def pausar_musica_fondo():
    """Función de compatibilidad"""
    pausar_musica()

def reanudar_musica_fondo():
    """Función de compatibilidad"""
    reanudar_musica()

def detener_musica_fondo():
    """Función de compatibilidad"""
    detener_musica()

def configurar_volumen_musica(volumen):
    """Función de compatibilidad"""
    configurar_volumen(volumen)

# =================== EFECTOS DE SONIDO DUMMY ===================
# Funciones vacías para mantener compatibilidad con gestores.py

def sonido_click():
    pass

def sonido_correcto():
    pass

def sonido_incorrecto():
    pass

def sonido_vida_perdida():
    pass

def sonido_vida_ganada():
    pass

def sonido_tateti_ganado():
    pass

def sonido_tateti_perdido():
    pass

def sonido_tiempo_critico():
    pass

def sonido_categoria_completada():
    pass

def sonido_juego_terminado():
    pass
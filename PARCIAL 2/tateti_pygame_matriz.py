# tateti_pygame_matriz_corregido.py - ARREGLOS DE TODOS LOS PROBLEMAS DEL TATETI

import pygame
import numpy as np
import math
import time
import random

class TatetiPygameMatriz:
    def __init__(self, pantalla, config, modo='vs_humano', jugador_nombre=None):
        self.pantalla = pantalla
        self.config = config
        self.modo = modo
        self.jugador_nombre = jugador_nombre
        
        # Configuración desde JSON
        tateti_config = config.get("tateti", {})
        interfaz_config = config.get("interfaz", {})
        fuentes_config = interfaz_config.get("fuentes", {})
        
        # Configuración visual desde config
        self.tamaño_celda = tateti_config.get("tamaño_celda", 120)
        self.grosor_linea = tateti_config.get("grosor_linea", 4)
        self.radio_simbolos = tateti_config.get("radio_simbolos", 35)
        self.offset_x = tateti_config.get("offset_x", 30)
        self.tiempo_animacion_config = tateti_config.get("tiempo_animacion_linea", 3)
        self.pulso_ganador = tateti_config.get("pulso_ganador", 3)
        
        # Calcular posición centrada
        ventana_config = interfaz_config.get("tamaño_ventana", {"ancho": 800, "alto": 600})
        ancho_ventana = ventana_config.get("ancho", 800)
        
        self.inicio_x = (ancho_ventana - (self.tamaño_celda * 3 + self.grosor_linea * 2)) // 2
        self.inicio_y = 150
        
        # ===== ARREGLO: MATRIZ LÓGICA COMPLETAMENTE VACÍA =====
        self.matriz_juego = np.zeros((3, 3), dtype=int)
        
        # ===== MATRICES PARA PYGAME =====
        self.matriz_coordenadas = self.crear_matriz_coordenadas()
        self.matriz_colores = self.crear_matriz_colores()
        self.matriz_estados = np.zeros((3, 3), dtype=int)
        
        self.jugador_actual = 1  # 1=X, 2=O
        self.estado = 'jugando'
        self.ganador = None
        self.linea_ganadora = None
        self.tiempo_animacion = 0
        self.animando = False
        self.es_vida_extra = modo == 'vs_maquina'
        self.resultado_vida_extra = None
        
        # Colores y fuentes desde configuración
        self.colores = self._obtener_colores()
        self.font_titulo = pygame.font.Font(None, fuentes_config.get("titulo", 48))
        self.font_texto = pygame.font.Font(None, fuentes_config.get("texto", 32))
        
        # Textos desde configuración
        self.textos = config.get("textos", {})
        
        # ARREGLO: Variables para evitar prints excesivos
        self._debug_inicializado = False
        self._ultimo_movimiento_reportado = None
        self._ultimo_estado_reportado = None
        
        # ARREGLO: Solo imprimir debug la primera vez
        if not self._debug_inicializado:
            print("🔢 Tateti iniciado con matrices:")
            print(f"   📊 Matriz lógica vacía: {self.matriz_juego.shape}")
            print(f"   📍 Matriz coordenadas: {self.matriz_coordenadas.shape}")  
            print(f"   🎨 Matriz colores: {self.matriz_colores.shape}")
            print(f"   🎮 Tamaño celda: {self.tamaño_celda}px")
            self._debug_inicializado = True
    
    def crear_matriz_coordenadas(self):
        """Crea una matriz 3x3x2 con las coordenadas (x,y) de cada celda"""
        matriz_coords = np.zeros((3, 3, 2), dtype=int)
        
        for fila in range(3):
            for col in range(3):
                x = self.inicio_x + col * (self.tamaño_celda + self.grosor_linea) + self.tamaño_celda // 2
                y = self.inicio_y + fila * (self.tamaño_celda + self.grosor_linea) + self.tamaño_celda // 2
                matriz_coords[fila, col] = [x, y]
        
        return matriz_coords
    
    def crear_matriz_colores(self):
        """Crea una matriz 3x3x3 con colores RGB para cada celda"""
        color_base = [240, 240, 240]  # Gris claro por defecto
        matriz_colores = np.full((3, 3, 3), color_base, dtype=int)
        
        # Aplicar patrón de colores alternados usando operaciones matriciales
        mascara_patron = np.zeros((3, 3), dtype=bool)
        for i in range(3):
            for j in range(3):
                if (i + j) % 2 == 0:
                    mascara_patron[i, j] = True
        
        matriz_colores[mascara_patron] = [250, 250, 250]  # Más claro
        matriz_colores[~mascara_patron] = [230, 230, 230]  # Más oscuro
        
        return matriz_colores
    
    def actualizar_matriz_estados_hover(self, pos_mouse):
        """Actualiza la matriz de estados para efectos hover"""
        self.matriz_estados.fill(0)
        
        if pos_mouse:
            x, y = pos_mouse
            
            for fila in range(3):
                for col in range(3):
                    celda_x = self.inicio_x + col * (self.tamaño_celda + self.grosor_linea)
                    celda_y = self.inicio_y + fila * (self.tamaño_celda + self.grosor_linea)
                    
                    if (celda_x <= x <= celda_x + self.tamaño_celda and 
                        celda_y <= y <= celda_y + self.tamaño_celda):
                        if self.matriz_juego[fila, col] == 0:
                            self.matriz_estados[fila, col] = 1  # Estado hover
    
    def obtener_coordenadas_desde_mouse(self, pos_mouse):
        """Convierte posición del mouse a coordenadas de matriz"""
        if not pos_mouse:
            return None, None
            
        x, y = pos_mouse
        
        col = (x - self.inicio_x) // (self.tamaño_celda + self.grosor_linea)
        fila = (y - self.inicio_y) // (self.tamaño_celda + self.grosor_linea)
        
        if 0 <= fila < 3 and 0 <= col < 3:
            return int(fila), int(col)
        return None, None
    
    def hacer_movimiento_matriz(self, fila, col):
        """ARREGLO: Realiza un movimiento actualizando las matrices del juego sin prints repetidos"""
        if (0 <= fila < 3 and 0 <= col < 3 and 
            self.matriz_juego[fila, col] == 0 and self.estado == 'jugando'):
            
            self.matriz_juego[fila, col] = self.jugador_actual
            
            # ARREGLO: Solo imprimir si es un movimiento realmente nuevo
            movimiento_actual = (fila, col, self.jugador_actual)
            if self._ultimo_movimiento_reportado != movimiento_actual:
                print(f"🎮 Movimiento: [{fila}, {col}] - {'X' if self.jugador_actual == 1 else 'O'}")
                self._ultimo_movimiento_reportado = movimiento_actual
            
            if self.verificar_ganador_matrices():
                self.estado = 'ganado'
                self.ganador = self.jugador_actual
                self.animando = True
                self.tiempo_animacion = time.time()
                
                if self.es_vida_extra:
                    self.resultado_vida_extra = 'ganada' if self.ganador == 1 else 'perdida'
                    
            elif self.verificar_matriz_llena():
                self.estado = 'empate'
                self.animando = True
                self.tiempo_animacion = time.time()
                if self.es_vida_extra:
                    self.resultado_vida_extra = 'perdida'
            else:
                self.jugador_actual = 2 if self.jugador_actual == 1 else 1
                
                if self.modo == 'vs_maquina' and self.jugador_actual == 2:
                    self.ia_movimiento_matriz()
            
            return True
        return False
    
    def verificar_ganador_matrices(self):
        """Verifica ganador usando operaciones matriciales de numpy"""
        matriz = self.matriz_juego
        
        # Verificar filas
        for fila in range(3):
            if np.all(matriz[fila, :] == self.jugador_actual):
                self.linea_ganadora = ('fila', fila)
                return True
        
        # Verificar columnas
        for col in range(3):
            if np.all(matriz[:, col] == self.jugador_actual):
                self.linea_ganadora = ('columna', col)
                return True
        
        # Verificar diagonal principal
        if np.all(np.diag(matriz) == self.jugador_actual):
            self.linea_ganadora = ('diagonal', 0)
            return True
        
        # Verificar diagonal secundaria
        if np.all(np.diag(np.fliplr(matriz)) == self.jugador_actual):
            self.linea_ganadora = ('diagonal', 1)
            return True
        
        return False
    
    def verificar_matriz_llena(self):
        """Verifica si la matriz está llena"""
        return np.all(self.matriz_juego != 0)
    
    def obtener_posiciones_vacias_matriz(self):
        """Obtiene posiciones vacías usando numpy"""
        filas, cols = np.where(self.matriz_juego == 0)
        return list(zip(filas, cols))
    
    def evaluar_movimiento_matriz(self, fila, col, jugador):
        """Evalúa un movimiento simulándolo en la matriz"""
        matriz_temp = self.matriz_juego.copy()
        matriz_temp[fila, col] = jugador
        
        # Verificar fila
        if np.all(matriz_temp[fila, :] == jugador):
            return True
        
        # Verificar columna
        if np.all(matriz_temp[:, col] == jugador):
            return True
        
        # Verificar diagonales
        if fila == col and np.all(np.diag(matriz_temp) == jugador):
            return True
        
        if fila + col == 2 and np.all(np.diag(np.fliplr(matriz_temp)) == jugador):
            return True
        
        return False
    
    def ia_movimiento_matriz(self):
        """ARREGLO: IA que toma decisiones usando análisis matricial sin prints repetidos"""
        posiciones_vacias = self.obtener_posiciones_vacias_matriz()
        
        # 1. Intentar ganar
        for fila, col in posiciones_vacias:
            if self.evaluar_movimiento_matriz(fila, col, 2):
                self.matriz_juego[fila, col] = 2
                self.verificar_resultado_ia()
                return
        
        # 2. Bloquear al jugador
        for fila, col in posiciones_vacias:
            if self.evaluar_movimiento_matriz(fila, col, 1):
                self.matriz_juego[fila, col] = 2
                self.verificar_resultado_ia()
                return
        
        # 3. Tomar centro
        if self.matriz_juego[1, 1] == 0:
            self.matriz_juego[1, 1] = 2
            self.verificar_resultado_ia()
            return
        
        # 4. Tomar esquinas usando máscara matricial
        esquinas_matriz = np.array([[1, 0, 1], [0, 0, 0], [1, 0, 1]], dtype=bool)
        matriz_vacias = (self.matriz_juego == 0)
        esquinas_disponibles = esquinas_matriz & matriz_vacias
        
        if np.any(esquinas_disponibles):
            filas, cols = np.where(esquinas_disponibles)
            idx = random.randint(0, len(filas) - 1)
            fila, col = filas[idx], cols[idx]
            self.matriz_juego[fila, col] = 2
            self.verificar_resultado_ia()
            return
        
        # 5. Movimiento aleatorio
        if posiciones_vacias:
            fila, col = random.choice(posiciones_vacias)
            self.matriz_juego[fila, col] = 2
            self.verificar_resultado_ia()
    
    def verificar_resultado_ia(self):
        """ARREGLO: Verifica resultado después del movimiento de IA sin prints repetidos"""
        estado_actual = (self.estado, self.ganador)
        
        if self.verificar_ganador_matrices():
            self.estado = 'ganado'
            self.ganador = 2
            self.animando = True
            self.tiempo_animacion = time.time()
            self.resultado_vida_extra = 'perdida'
            
            # Solo imprimir si el estado cambió
            if self._ultimo_estado_reportado != estado_actual:
                print("🤖 IA ganó el tateti")
                self._ultimo_estado_reportado = estado_actual
                
        elif self.verificar_matriz_llena():
            self.estado = 'empate'
            self.animando = True
            self.tiempo_animacion = time.time()
            self.resultado_vida_extra = 'perdida'
            
            # Solo imprimir si el estado cambió
            if self._ultimo_estado_reportado != estado_actual:
                print("🤝 Empate en tateti")
                self._ultimo_estado_reportado = estado_actual
        else:
            self.jugador_actual = 1
    
    def reiniciar_matrices(self):
        """ARREGLO: Reinicia todas las matrices del juego limpiamente"""
        print("🔄 Reiniciando tateti...")
        
        # ARREGLO: Asegurar que la matriz esté completamente vacía
        self.matriz_juego = np.zeros((3, 3), dtype=int)
        self.matriz_estados = np.zeros((3, 3), dtype=int)
        self.matriz_colores = self.crear_matriz_colores()
        
        self.jugador_actual = 1
        self.estado = 'jugando'
        self.ganador = None
        self.linea_ganadora = None
        self.animando = False
        self.tiempo_animacion = 0
        self.resultado_vida_extra = None
        
        # ARREGLO: Reiniciar variables de debug
        self._ultimo_movimiento_reportado = None
        self._ultimo_estado_reportado = None
        
        print("✅ Tateti reiniciado - matriz vacía")
    
    def dibujar_tablero_con_matrices(self):
        """Dibuja el tablero usando las matrices de Pygame"""
        self.pantalla.fill(self.colores['fondo'])
        
        # Título usando configuración
        if self.es_vida_extra:
            titulo = f"{self.jugador_nombre} - ¡VIDA EXTRA!"
            subtitulo = "🔢 Usando matrices de Pygame"
            color_titulo = self.colores['ganador']
        else:
            titulo = "TATETI CON MATRICES PYGAME"
            subtitulo = "🔢 Matrices: Lógica + Coordenadas + Colores"
            color_titulo = self.colores['lineas']
        
        titulo_surf = self.font_titulo.render(titulo, True, color_titulo)
        titulo_rect = titulo_surf.get_rect(center=(400, 40))
        self.pantalla.blit(titulo_surf, titulo_rect)
        
        if subtitulo:
            sub_surf = self.font_texto.render(subtitulo, True, self.colores['lineas'])
            sub_rect = sub_surf.get_rect(center=(400, 70))
            self.pantalla.blit(sub_surf, sub_rect)
        
        self.dibujar_info_estado()
        
        # Actualizar efectos hover
        mouse_pos = pygame.mouse.get_pos()
        if self.estado == 'jugando' and (self.modo != 'vs_maquina' or self.jugador_actual == 1):
            self.actualizar_matriz_estados_hover(mouse_pos)
        
        # Dibujar elementos usando matrices
        self.dibujar_celdas_con_matrices()
        self.dibujar_simbolos_con_matrices()
        self.dibujar_grid_matriz()
        
        if self.linea_ganadora and self.animando:
            self.dibujar_linea_ganadora_matriz()
    
    def dibujar_info_estado(self):
        """Dibuja información del estado actual usando textos de configuración"""
        if self.estado == 'jugando':
            if self.modo == 'vs_maquina':
                info = f"Tu turno ({self.jugador_nombre})" if self.jugador_actual == 1 else "Turno de la IA"
                color_info = self.colores['x'] if self.jugador_actual == 1 else self.colores['o']
            else:
                simbolo = 'X' if self.jugador_actual == 1 else 'O'
                info = f"Turno: {simbolo}"
                color_info = self.colores['x'] if self.jugador_actual == 1 else self.colores['o']
        elif self.estado == 'ganado':
            if self.es_vida_extra:
                if self.resultado_vida_extra == 'ganada':
                    info = f"¡{self.jugador_nombre} GANÓ VIDA EXTRA!"
                    color_info = self.colores['ganador']
                else:
                    info = f"IA ganó. {self.jugador_nombre} eliminado."
                    color_info = self.colores['o']
            else:
                simbolo = 'X' if self.ganador == 1 else 'O'
                info = f"¡Ganó {simbolo}!"
                color_info = self.colores['ganador']
        elif self.estado == 'empate':
            if self.es_vida_extra:
                info = f"Empate. {self.jugador_nombre} eliminado."
                color_info = self.colores['lineas']
            else:
                info = "¡EMPATE!"
                color_info = self.colores['lineas']
        else:
            info = ""
            color_info = self.colores['lineas']
        
        if info:
            texto_info = self.font_texto.render(info, True, color_info)
            info_rect = texto_info.get_rect(center=(400, 110))
            self.pantalla.blit(texto_info, info_rect)
    
    def dibujar_celdas_con_matrices(self):
        """Dibuja las celdas usando la matriz de colores"""
        for fila in range(3):
            for col in range(3):
                x = self.inicio_x + col * (self.tamaño_celda + self.grosor_linea)
                y = self.inicio_y + fila * (self.tamaño_celda + self.grosor_linea)
                
                color_base = self.matriz_colores[fila, col]
                
                if self.matriz_estados[fila, col] == 1:  # Hover
                    color_final = self.colores['hover']
                else:
                    color_final = tuple(color_base)
                
                celda_rect = pygame.Rect(x, y, self.tamaño_celda, self.tamaño_celda)
                pygame.draw.rect(self.pantalla, color_final, celda_rect)
    
    def dibujar_simbolos_con_matrices(self):
        """Dibuja X y O usando las matrices"""
        for fila in range(3):
            for col in range(3):
                valor = self.matriz_juego[fila, col]
                if valor != 0:
                    centro_x, centro_y = self.matriz_coordenadas[fila, col]
                    
                    if valor == 1:  # X
                        self.dibujar_x_matriz(centro_x, centro_y)
                    elif valor == 2:  # O
                        self.dibujar_o_matriz(centro_x, centro_y)
    
    def dibujar_x_matriz(self, centro_x, centro_y):
        """Dibuja una X usando configuración"""
        color = self.colores['x']
        
        pygame.draw.line(self.pantalla, color, 
                        (centro_x - self.offset_x, centro_y - self.offset_x), 
                        (centro_x + self.offset_x, centro_y + self.offset_x), 8)
        pygame.draw.line(self.pantalla, color, 
                        (centro_x + self.offset_x, centro_y - self.offset_x), 
                        (centro_x - self.offset_x, centro_y + self.offset_x), 8)
    
    def dibujar_o_matriz(self, centro_x, centro_y):
        """Dibuja una O usando configuración"""
        color = self.colores['o']
        pygame.draw.circle(self.pantalla, color, (centro_x, centro_y), self.radio_simbolos, 8)
    
    def dibujar_grid_matriz(self):
        """Dibuja las líneas del grid"""
        color_linea = self.colores['lineas']
        
        # Líneas verticales
        for i in range(2):
            x = self.inicio_x + (i + 1) * self.tamaño_celda + i * self.grosor_linea
            pygame.draw.line(self.pantalla, color_linea, 
                           (x, self.inicio_y), 
                           (x, self.inicio_y + 3 * self.tamaño_celda + 2 * self.grosor_linea), 
                           self.grosor_linea)
        
        # Líneas horizontales
        for i in range(2):
            y = self.inicio_y + (i + 1) * self.tamaño_celda + i * self.grosor_linea
            pygame.draw.line(self.pantalla, color_linea, 
                           (self.inicio_x, y), 
                           (self.inicio_x + 3 * self.tamaño_celda + 2 * self.grosor_linea, y), 
                           self.grosor_linea)
    
    def dibujar_linea_ganadora_matriz(self):
        """Dibuja la línea ganadora usando coordenadas matriciales"""
        if not self.linea_ganadora:
            return
        
        tiempo_transcurrido = time.time() - self.tiempo_animacion
        pulso = int(math.sin(tiempo_transcurrido * self.pulso_ganador) * 3) + 8
        
        tipo, indice = self.linea_ganadora
        color = self.colores['ganador']
        
        if tipo == 'fila':
            start_x, start_y = self.matriz_coordenadas[indice, 0]
            end_x, end_y = self.matriz_coordenadas[indice, 2]
            start = (start_x - 50, start_y)
            end = (end_x + 50, end_y)
        elif tipo == 'columna':
            start_x, start_y = self.matriz_coordenadas[0, indice]
            end_x, end_y = self.matriz_coordenadas[2, indice]
            start = (start_x, start_y - 50)
            end = (end_x, end_y + 50)
        elif tipo == 'diagonal' and indice == 0:
            start_x, start_y = self.matriz_coordenadas[0, 0]
            end_x, end_y = self.matriz_coordenadas[2, 2]
            start = (start_x - 30, start_y - 30)
            end = (end_x + 30, end_y + 30)
        else:  # diagonal secundaria
            start_x, start_y = self.matriz_coordenadas[0, 2]
            end_x, end_y = self.matriz_coordenadas[2, 0]
            start = (start_x + 30, start_y - 30)
            end = (end_x - 30, end_y + 30)
        
        pygame.draw.line(self.pantalla, color, start, end, pulso)
    
    def _obtener_colores(self):
        """Obtiene colores del sistema de configuración"""
        try:
            from configuracion import obtener_colores
            colores_config = obtener_colores(self.config)
            return {
                'fondo': colores_config.get('BLANCO', [255, 255, 255]),
                'lineas': colores_config.get('NEGRO', [0, 0, 0]),
                'x': colores_config.get('AZUL', [0, 100, 200]),
                'o': colores_config.get('ROJO', [200, 0, 0]),
                'hover': colores_config.get('HOVER_DEFAULT', [220, 220, 220]),
                'ganador': colores_config.get('VERDE', [0, 150, 0]),
                'boton': colores_config.get('BOTON_JUGAR', [80, 200, 255]),
                'boton_hover': colores_config.get('BOTON_JUGAR_HOVER', [110, 230, 255])
            }
        except:
            return {
                'fondo': [255, 255, 255],
                'lineas': [0, 0, 0],
                'x': [0, 100, 200],
                'o': [200, 0, 0],
                'hover': [220, 220, 220],
                'ganador': [0, 150, 0],
                'boton': [80, 200, 255],
                'boton_hover': [110, 230, 255]
            }
    
    def dibujar_botones(self):
        """ARREGLO: Dibuja los botones de control con mejor manejo"""
        botones = []
        
        if self.estado in ['ganado', 'empate']:
            if self.es_vida_extra:
                if self.resultado_vida_extra == 'ganada':
                    boton_continuar = pygame.Rect(250, 500, 180, 40)
                    mouse_pos = pygame.mouse.get_pos()
                    color = self.colores['boton_hover'] if boton_continuar.collidepoint(mouse_pos) else self.colores['ganador']
                    
                    pygame.draw.rect(self.pantalla, color, boton_continuar)
                    pygame.draw.rect(self.pantalla, self.colores['lineas'], boton_continuar, 2)
                    
                    texto = self.font_texto.render("CONTINUAR", True, self.colores['lineas'])
                    texto_rect = texto.get_rect(center=boton_continuar.center)
                    self.pantalla.blit(texto, texto_rect)
                    
                    botones.append(('vida_extra_ganada', boton_continuar))
                else:
                    boton_eliminar = pygame.Rect(250, 500, 180, 40)
                    mouse_pos = pygame.mouse.get_pos()
                    color = self.colores['hover'] if boton_eliminar.collidepoint(mouse_pos) else self.colores['o']
                    
                    pygame.draw.rect(self.pantalla, color, boton_eliminar)
                    pygame.draw.rect(self.pantalla, self.colores['lineas'], boton_eliminar, 2)
                    
                    texto = self.font_texto.render("ACEPTAR", True, self.colores['lineas'])
                    texto_rect = texto.get_rect(center=boton_eliminar.center)
                    self.pantalla.blit(texto, texto_rect)
                    
                    botones.append(('vida_extra_perdida', boton_eliminar))
            else:
                boton_nuevo = pygame.Rect(250, 500, 150, 40)
                mouse_pos = pygame.mouse.get_pos()
                color = self.colores['boton_hover'] if boton_nuevo.collidepoint(mouse_pos) else self.colores['boton']
                
                pygame.draw.rect(self.pantalla, color, boton_nuevo)
                pygame.draw.rect(self.pantalla, self.colores['lineas'], boton_nuevo, 2)
                
                texto = self.font_texto.render("NUEVO JUEGO", True, self.colores['lineas'])
                texto_rect = texto.get_rect(center=boton_nuevo.center)
                self.pantalla.blit(texto, texto_rect)
                
                botones.append(('nuevo', boton_nuevo))
        
        # ARREGLO: Siempre mostrar botón volver cuando no es vida extra terminada
        if not (self.es_vida_extra and self.estado in ['ganado', 'empate']):
            boton_volver = pygame.Rect(450, 500, 120, 40)
            mouse_pos = pygame.mouse.get_pos()
            color = self.colores['hover'] if boton_volver.collidepoint(mouse_pos) else self.colores['fondo']
            
            pygame.draw.rect(self.pantalla, color, boton_volver)
            pygame.draw.rect(self.pantalla, self.colores['lineas'], boton_volver, 2)
            
            texto = self.font_texto.render("VOLVER", True, self.colores['lineas'])
            texto_rect = texto.get_rect(center=boton_volver.center)
            self.pantalla.blit(texto, texto_rect)
            
            botones.append(('volver', boton_volver))
        
        return botones
    
    def procesar_eventos(self, eventos):
        """ARREGLO COMPLETO: Procesa eventos del tateti con matrices sin problemas"""
        botones = self.dibujar_botones()
        
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos_mouse = pygame.mouse.get_pos()
                
                # Verificar botones primero
                for accion, boton in botones:
                    if boton.collidepoint(pos_mouse):
                        if accion == 'nuevo':
                            self.reiniciar_matrices()
                            return 'continuar'
                        elif accion == 'volver':
                            return 'salir'
                        elif accion == 'vida_extra_ganada':
                            return 'vida_extra_ganada'
                        elif accion == 'vida_extra_perdida':
                            return 'vida_extra_perdida'
                
                # Verificar clicks en tablero solo si el juego está activo
                if (self.estado == 'jugando' and 
                    (self.modo != 'vs_maquina' or self.jugador_actual == 1)):
                    fila, col = self.obtener_coordenadas_desde_mouse(pos_mouse)
                    if fila is not None and col is not None:
                        self.hacer_movimiento_matriz(fila, col)
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if self.es_vida_extra and self.estado in ['ganado', 'empate']:
                        return 'vida_extra_perdida' if self.resultado_vida_extra != 'ganada' else 'vida_extra_ganada'
                    return 'salir'
                elif evento.key == pygame.K_r and self.estado in ['ganado', 'empate'] and not self.es_vida_extra:
                    self.reiniciar_matrices()
                    return 'continuar'
                elif evento.key == pygame.K_m:
                    print("\n🔍 DEBUG - Estado de las matrices:")
                    print("📊 Matriz lógica:")
                    print(self.matriz_juego)
                    print("📍 Matriz coordenadas (centros de cada celda):")
                    for fila in range(3):
                        fila_coords = []
                        for col in range(3):
                            x, y = self.matriz_coordenadas[fila, col]
                            fila_coords.append(f"({x},{y})")
                        print(f"   Fila {fila}: {' '.join(fila_coords)}")
                    print("🎨 Matriz colores (valores R del RGB):")
                    print(self.matriz_colores[:, :, 0])
                    print("⚡ Matriz estados (hover):")
                    print(self.matriz_estados)
        
        return 'continuar'
    
    def actualizar_y_dibujar(self):
        """Actualiza y dibuja el tateti usando matrices"""
        self.dibujar_tablero_con_matrices()
        self.dibujar_botones()

def mostrar_tateti_pygame_matriz(estado_interfaz, eventos, config, modo='vs_humano', jugador_nombre=None):
    """ARREGLO COMPLETO: Función principal para mostrar el tateti con matrices usando configuración optimizada"""
    cache_key = f'tateti_pygame_matriz_{modo}_{jugador_nombre}'
    
    # Verificar si necesitamos crear una nueva instancia
    if not hasattr(mostrar_tateti_pygame_matriz, '_instancias'):
        mostrar_tateti_pygame_matriz._instancias = {}
    
    # ARREGLO: Crear nueva instancia limpia cada vez para evitar estados corruptos
    if (cache_key not in mostrar_tateti_pygame_matriz._instancias or 
        mostrar_tateti_pygame_matriz._instancias[cache_key].estado in ['terminado', 'salir']):
        
        # Limpiar instancia anterior si existe
        if cache_key in mostrar_tateti_pygame_matriz._instancias:
            del mostrar_tateti_pygame_matriz._instancias[cache_key]
        
        # ARREGLO: Solo imprimir cuando realmente se crea una nueva instancia
        if not hasattr(mostrar_tateti_pygame_matriz, '_instancia_creada'):
            print(f"🎮 Creando nueva instancia de tateti: {modo}")
            mostrar_tateti_pygame_matriz._instancia_creada = True
        
        mostrar_tateti_pygame_matriz._instancias[cache_key] = TatetiPygameMatriz(
            estado_interfaz['pantalla'], config, modo, jugador_nombre
        )
    
    tateti = mostrar_tateti_pygame_matriz._instancias[cache_key]
    tateti.actualizar_y_dibujar()
    
    resultado = tateti.procesar_eventos(eventos)
    
    # Limpiar instancia cuando el juego termina
    if resultado in ['salir', 'vida_extra_ganada', 'vida_extra_perdida']:
        if cache_key in mostrar_tateti_pygame_matriz._instancias:
            del mostrar_tateti_pygame_matriz._instancias[cache_key]
        
        # Limpiar flag de instancia creada
        if hasattr(mostrar_tateti_pygame_matriz, '_instancia_creada'):
            delattr(mostrar_tateti_pygame_matriz, '_instancia_creada')
        
        if resultado == 'vida_extra_ganada':
            return 'vida_extra_ganada'
        elif resultado == 'vida_extra_perdida':
            return 'vida_extra_perdida'
        else:
            return 'menu'
    
    return 'tateti'
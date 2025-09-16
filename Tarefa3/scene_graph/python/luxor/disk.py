# luxor/disk.py

import numpy as np
from OpenGL.GL import *
# O nome do arquivo da classe base pode ser diferente, ajuste se necessário
from shape import Shape 

import math

class Disk(Shape):
    """
    Implementa a forma geométrica de um disco com coordenadas de textura.
    """
    def __init__(self, segments=50):
        self.segments = segments
        self.vbo = None
        self.vao = None
        self.vertex_count = self.segments + 2
        self._generate_vertices()

    def _generate_vertices(self):
        """
        Gera os vértices para o disco (leque de triângulos) e as coordenadas de textura.
        """
        vertices = []
        
        # Vértice 0: O centro do disco
        # Posição (0,0,0), Coordenada de Textura (0.5, 0.5)
        vertices.extend([0.0, 0.0, 0.0, 0.5, 0.5])

        # Vértices 1 a segments+1: A borda do disco
        for i in range(self.segments + 1):
            angle = i * (2.0 * math.pi / self.segments)
            
            # Posição do vértice (x, y, z)
            x = math.cos(angle) * 0.5
            y = math.sin(angle) * 0.5
            
            # --- ATENÇÃO: CORREÇÃO APLICADA AQUI ---
            # Mapeia o círculo trigonométrico (cujos valores de seno e cosseno
            # vão de -1 a 1) para o espaço de textura (que vai de 0 a 1).
            u = (math.cos(angle) + 1.0) / 2.0
            v = (math.sin(angle) + 1.0) / 2.0
            
            vertices.extend([x, y, 0.0, u, v])
            
        self.vertex_data = np.array(vertices, dtype=np.float32)

    def Draw(self, st):
        """
        Método de desenho do disco.
        """
        if self.vao is None:
            self.vao = glGenVertexArrays(1)
            self.vbo = glGenBuffers(1)
            
            glBindVertexArray(self.vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, self.vertex_data.nbytes, self.vertex_data, GL_STATIC_DRAW)
            
            stride = 5 * 4  # 5 floats, 4 bytes cada
            
            # Atributo do vértice (posição): layout (location=0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            
            # Atributo de textura: layout (location=3)
            glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
            glEnableVertexAttribArray(3)
            
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.vertex_count)
        glBindVertexArray(0)
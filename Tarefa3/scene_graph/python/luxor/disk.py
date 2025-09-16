# luxor/disk.py

import numpy as np
from OpenGL.GL import *
from shape import Shape  # Assumindo que a classe base se chama Shape em shapes.py

import math

class Disk(Shape):
    """
    Implementa a forma geométrica de um disco com coordenadas de textura.
    """
    def __init__(self, segments=50):
        """
        Construtor da classe Disk.
        
        Args:
            segments (int): O número de segmentos para aproximar o círculo.
                           Mais segmentos resultam em um círculo mais suave.
        """
        self.segments = segments
        self.vbo = None
        self.vao = None
        # O número de vértices será o número de segmentos na borda, mais o vértice central,
        # mais um vértice repetido para fechar o leque.
        self.vertex_count = self.segments + 2
        
        # Gerar os vértices e coordenadas de textura
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
            x = math.cos(angle) * 0.5  # Raio de 0.5
            y = math.sin(angle) * 0.5  # Raio de 0.5
            
            # Mapeia as coordenadas de textura de [-0.5, 0.5] para [0, 1]
            u = x + 0.5
            v = y + 0.5
            
            vertices.extend([x, y, 0.0, u, v])
            
        # Converte a lista para um array numpy
        self.vertex_data = np.array(vertices, dtype=np.float32)

    def Draw(self, st):
        """
        Método de desenho do disco.
        """
        if self.vao is None:
            # Primeira vez que desenha: cria VAO e VBO
            self.vao = glGenVertexArrays(1)
            self.vbo = glGenBuffers(1)
            
            glBindVertexArray(self.vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, self.vertex_data.nbytes, self.vertex_data, GL_STATIC_DRAW)
            
            # Atributo do vértice (posição): layout (location=0)
            # 5 floats por vértice (x, y, z, u, v)
            stride = 5 * 4  # 5 floats, 4 bytes cada
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            
            # Atributo de textura: layout (location=3) (baseado em vertex_texture.glsl)
            glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
            glEnableVertexAttribArray(3)
            
            # Desvincula para evitar modificações acidentais
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)

        # Desenha o objeto
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.vertex_count)
        glBindVertexArray(0)
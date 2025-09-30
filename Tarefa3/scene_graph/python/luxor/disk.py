import numpy as np
from OpenGL.GL import *
from shape import Shape 
import math
import ctypes

class Disk(Shape):
    def __init__(self, segments=50):
        self.segments = segments
        self.vbo = None
        self.vao = None
        self.vertex_count = self.segments + 2
        self._generate_vertices()

    def _generate_vertices(self):
        vertices = []
        normal = [0.0, 0.0, 1.0]

        # Vértice central
        # Posição (x, y, z), Normal (nx, ny, nz), Coordenada de Textura (u, v)
        # O seu shader não usa a posição Z da posição nem as normais, mas vamos mantê-las
        # para compatibilidade caso você mude de ideia. O layout do seu shader é:
        # location 0: coord (vec4)
        # location 1: normal (vec3)
        # location 3: texcoord (vec2)
        # Para simplificar, enviaremos vec3 para posição e o shader o converterá.
        
        # Posição (x, y, z), Normal (nx, ny, nz), TexCoord (u, v)
        # Total de 8 floats por vértice
        
        # Vértice central
        vertices.extend([0.0, 0.0, 0.0])  # Posição
        vertices.extend(normal)           # Normal
        vertices.extend([0.5, 0.5])       # UV - Centro da textura

        # Vértices da borda
        for i in range(self.segments + 1):
            angle = i * (2.0 * math.pi / self.segments)
            x = math.cos(angle) * 0.5
            y = math.sin(angle) * 0.5
            
            u = x + 0.5
            v = y + 0.5
            
            vertices.extend([x, y, 0.0]) # Posição
            vertices.extend(normal)      # Normal
            vertices.extend([u, v])      # UV

        self.vertex_data = np.array(vertices, dtype=np.float32)

    def Draw(self, st):
        if self.vao is None:
            self.vao = glGenVertexArrays(1)
            self.vbo = glGenBuffers(1)
            
            glBindVertexArray(self.vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, self.vertex_data.nbytes, self.vertex_data, GL_STATIC_DRAW)
            
            # Stride é 8 floats (3 pos + 3 normal + 2 uv)
            stride = 8 * 4 
            
            # Atributo 0: Posição do Vértice (vec4 no shader, mas enviamos vec3)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            
            # Atributo 1: Normal do Vértice (vec3)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
            glEnableVertexAttribArray(1)

            # Atributo 3: Coordenada de Textura (vec2) - CONFORME SEU SHADER
            glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))
            glEnableVertexAttribArray(3)
            
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.vertex_count)
        glBindVertexArray(0)
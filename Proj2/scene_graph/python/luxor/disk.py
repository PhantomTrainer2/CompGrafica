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
        self.base_vertex_data = None  # <- guardamos versão "neutra"
        self._generate_vertices()

    def _generate_vertices(self):
        vertices = []
        normal = [0.0, 0.0, 1.0]

        # Vértice central
        vertices.extend([0.0, 0.0, 0.0])
        vertices.extend(normal)
        vertices.extend([0.5, 0.5])  # centro

        for i in range(self.segments + 1):
            angle = i * (2.0 * math.pi / self.segments)
            x = math.cos(angle) * 0.5
            y = math.sin(angle) * 0.5

            u = x + 0.5
            v = y + 0.5

            vertices.extend([x, y, 0.0])
            vertices.extend(normal)
            vertices.extend([u, v])

        self.base_vertex_data = np.array(vertices, dtype=np.float32)
        self.vertex_data = self.base_vertex_data.copy()

    def update_texcoords(self, offset_u=0.0):
        """Atualiza UVs somando offset em U"""
        self.vertex_data = self.base_vertex_data.copy()
        stride = 8
        for i in range(0, len(self.vertex_data), stride):
            # posição (0-2), normal (3-5), texcoord (6-7)
            self.vertex_data[i+6] += offset_u  # desloca apenas U

        if self.vbo is not None:
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0, self.vertex_data.nbytes, self.vertex_data)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def Draw(self, st):
        if self.vao is None:
            self.vao = glGenVertexArrays(1)
            self.vbo = glGenBuffers(1)

            glBindVertexArray(self.vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, self.vertex_data.nbytes, self.vertex_data, GL_DYNAMIC_DRAW)

            stride = 8 * 4
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)

            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
            glEnableVertexAttribArray(1)

            glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))
            glEnableVertexAttribArray(3)

            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.vertex_count)
        glBindVertexArray(0)

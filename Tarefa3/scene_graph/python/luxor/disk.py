import numpy as np
from OpenGL.GL import *
from shape import Shape 

import math

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

        vertices.extend([0.0, 0.0, 0.0])
        vertices.extend(normal)

        for i in range(self.segments + 1):
            angle = i * (2.0 * math.pi / self.segments)
            x = math.cos(angle) * 0.5
            y = math.sin(angle) * 0.5
            
            vertices.extend([x, y, 0.0])
            vertices.extend(normal)
            
        self.vertex_data = np.array(vertices, dtype=np.float32)

    def Draw(self, st):
        if self.vao is None:
            self.vao = glGenVertexArrays(1)
            self.vbo = glGenBuffers(1)
            
            glBindVertexArray(self.vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, self.vertex_data.nbytes, self.vertex_data, GL_STATIC_DRAW)
            
            stride = 6 * 4 
            
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
            glEnableVertexAttribArray(1)
            
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.vertex_count)
        glBindVertexArray(0)
from OpenGL.GL import *
from shape import Shape
import numpy as np

class Polygon(Shape):

    def __init__(self, vertices, colors, indices):
        if len(vertices) < 3:
            raise ValueError("Um polígono deve ter pelo menos 3 vértices.")

        self.index_count = len(indices)

        vertex = np.array(vertices, dtype='float32').flatten()
        color = np.array(colors, dtype='uint8').flatten()
        index = np.array(indices, dtype='uint32')

        
        self.vao = glGenVertexArrays(1)
        vbo, ebo = glGenBuffers(2)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex.nbytes, vertex, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        
        color_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, color_vbo)
        glBufferData(GL_ARRAY_BUFFER, color.nbytes, color, GL_STATIC_DRAW)

        glVertexAttribPointer(1, 3, GL_UNSIGNED_BYTE, GL_TRUE, 0, None)
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index.nbytes, index, GL_STATIC_DRAW)

        glBindVertexArray(0)


    def Draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
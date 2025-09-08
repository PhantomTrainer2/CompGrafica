from OpenGL.GL import *
from shape import Shape
import numpy as np

class Polygon(Shape):
    """
    Representa um polígono renderizado via um conjunto de vértices e índices (EBO).
    A triangulação é fornecida manualmente, não calculada.
    """

    def __init__(self, vertices, colors, indices):
        """
        Inicializa o Polígono.

        Args:
            vertices (list of tuples): Lista de coordenadas dos vértices únicos.
            colors (list of tuples): Lista das cores para cada vértice.
            indices (list of int): Lista que define como os vértices se conectam
                                   para formar triângulos.
        """
        if len(vertices) < 3:
            raise ValueError("Um polígono deve ter pelo menos 3 vértices.")

        self.index_count = len(indices)

        # Converte as listas para arrays numpy no formato correto
        vertex_data = np.array(vertices, dtype='float32').flatten()
        color_data = np.array(colors, dtype='uint8').flatten()
        index_data = np.array(indices, dtype='uint32')

        # --- Configuração do VAO, VBOs e EBO ---
        
        # Gera os nomes (IDs) para os buffers
        self.vao = glGenVertexArrays(1)
        vbo, ebo = glGenBuffers(2)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        
        color_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, color_vbo)
        glBufferData(GL_ARRAY_BUFFER, color_data.nbytes, color_data, GL_STATIC_DRAW)

        glVertexAttribPointer(1, 3, GL_UNSIGNED_BYTE, GL_TRUE, 0, None)
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

        glBindVertexArray(0)


    def Draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
import numpy as np
from OpenGL.GL import *
from shape import Shape

class Polygon(Shape):
    """
    Representa um polígono não convexo que pode ser renderizado com OpenGL.
    O polígono é triangulado usando o algoritmo "ear clipping" na inicialização.
    """

    def __init__(self, vertices, colors):
        """
        Inicializa o objeto Polígono.

        Args:
            vertices (list of tuples): As coordenadas dos vértices do polígono
                                       em ordem anti-horária. Ex: [(-0.5, -0.5), ...].
            colors (list of tuples): As cores RGB para cada vértice correspondente.
                                     Ex: [(255, 0, 0), ...].
        """
        if len(vertices) < 3:
            raise ValueError("Um polígono deve ter pelo menos 3 vértices.")

        triangulated_vertices, triangulated_colors = self._triangulate(vertices, colors)

        # Converte para arrays numpy para o OpenGL
        coord = np.array(triangulated_vertices, dtype='float32').flatten()
        color_data = np.array(triangulated_colors, dtype='uint8').flatten()

        # Configura o VAO e os VBOs
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Buffer de Vértices
        vbo = glGenBuffers(2)
        glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
        glBufferData(GL_ARRAY_BUFFER, coord.nbytes, coord, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        # Buffer de Cores
        glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
        glBufferData(GL_ARRAY_BUFFER, color_data.nbytes, color_data, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_UNSIGNED_BYTE, GL_TRUE, 0, None)
        glEnableVertexAttribArray(1)

        self.vertex_count = len(coord) // 2

    def _area(self, vertices):
        """Calcula a área com sinal de um polígono."""
        n = len(vertices)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        return area / 2.0

    def _is_inside(self, p1, p2, p3, p_test):
        """Verifica se um ponto p_test está dentro do triângulo (p1, p2, p3)."""
        # Usando coordenadas baricêntricas
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

        d1 = sign(p_test, p1, p2)
        d2 = sign(p_test, p2, p3)
        d3 = sign(p_test, p3, p1)

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

    def _triangulate(self, vertices, colors):
        """
        Triangula um polígono não convexo usando o algoritmo "ear clipping".
        Assume que os vértices estão em uma ordem consistente (ex: anti-horário).
        """
        triangles_vertices = []
        triangles_colors = []

        remaining_indices = list(range(len(vertices)))
        
        # Garante a ordem anti-horária
        if self._area(vertices) < 0:
            remaining_indices.reverse()

        while len(remaining_indices) > 3:
            found_ear = False
            for i in range(len(remaining_indices)):
                prev_idx = remaining_indices[i - 1]
                curr_idx = remaining_indices[i]
                next_idx = remaining_indices[(i + 1) % len(remaining_indices)]

                p_prev = vertices[prev_idx]
                p_curr = vertices[curr_idx]
                p_next = vertices[next_idx]

                c_prev = colors[prev_idx]
                c_curr = colors[curr_idx]
                c_next = colors[next_idx]
                
                # Verifica se o vértice é convexo (ângulo interno < 180 graus)
                # Isso é feito verificando a componente z do produto vetorial
                cross_product_z = (p_curr[0] - p_prev[0]) * (p_next[1] - p_curr[1]) - \
                                  (p_curr[1] - p_prev[1]) * (p_next[0] - p_curr[0])
                if cross_product_z < 0:
                    continue  # É um vértice reflexo, não a ponta de uma "orelha"

                # Verifica se algum outro vértice está dentro desta "orelha" potencial
                is_ear = True
                for j in range(len(vertices)):
                    if j not in [prev_idx, curr_idx, next_idx]:
                        if self._is_inside(p_prev, p_curr, p_next, vertices[j]):
                            is_ear = False
                            break
                
                if is_ear:
                    triangles_vertices.extend([p_prev, p_curr, p_next])
                    triangles_colors.extend([c_prev, c_curr, c_next])
                    remaining_indices.pop(i)
                    found_ear = True
                    break
            
            if not found_ear:
                # Pode acontecer com polígonos complexos com autointersecção.
                # Para esta tarefa, assumimos um polígono simples.
                raise RuntimeError("Falha ao encontrar uma 'orelha'. O polígono pode ter autointersecção.")

        # Adiciona o último triângulo restante
        p1_idx, p2_idx, p3_idx = remaining_indices[0], remaining_indices[1], remaining_indices[2]
        triangles_vertices.extend([vertices[p1_idx], vertices[p2_idx], vertices[p3_idx]])
        triangles_colors.extend([colors[p1_idx], colors[p2_idx], colors[p3_idx]])
        
        return triangles_vertices, triangles_colors

    def Draw(self):
        """
        Desenha o polígono triangulado.
        """
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
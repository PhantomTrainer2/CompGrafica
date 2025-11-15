# planarshadow.py
import glm
from appearance import Appearance

class PlanarShadow(Appearance):
    """
    Projeta a sombra de um objeto em um plano usando uma fonte de luz pontual.
    A matriz de sombra é calculada em espaço de mundo e aplicada sobre a
    matriz de model corrente: M_shadow = S * M.
    """
    def __init__(self, light, plane_point, plane_normal):
        self.light = light
        self.plane_point = glm.vec3(plane_point)
        self.plane_normal = glm.normalize(glm.vec3(plane_normal))
        self._saved_matrix = None

    def _shadow_matrix(self):
        # Plano: a*x + b*y + c*z + d = 0
        n = self.plane_normal
        a, b, c = n.x, n.y, n.z
        d = -glm.dot(n, self.plane_point)

        # Luz (em coords de mundo)
        L = self.light.pos
        lx, ly, lz, lw = L.x, L.y, L.z, L.w

        dot = a*lx + b*ly + c*lz + d*lw

        # glm é column-major, então m[col][row]
        m = glm.mat4(1.0)

        # Primeira linha (row 0)
        m[0][0] = dot - lx * a
        m[1][0] = -ly * a
        m[2][0] = -lz * a
        m[3][0] = -lw * a

        # Segunda linha (row 1)
        m[0][1] = -lx * b
        m[1][1] = dot - ly * b
        m[2][1] = -lz * b
        m[3][1] = -lw * b

        # Terceira linha (row 2)
        m[0][2] = -lx * c
        m[1][2] = -ly * c
        m[2][2] = dot - lz * c
        m[3][2] = -lw * c

        # Quarta linha (row 3)
        m[0][3] = -lx * d
        m[1][3] = -ly * d
        m[2][3] = -lz * d
        m[3][3] = dot - lw * d

        return m

    def Load(self, st):
        # Guarda a matriz de model atual (M)
        self._saved_matrix = st.GetCurrentMatrix()
        S = self._shadow_matrix()

        # Matriz final de model para a sombra: S * M
        shadow_model = S * self._saved_matrix
        st.LoadMatrix(shadow_model)

    def Unload(self, st):
        if self._saved_matrix is not None:
            st.LoadMatrix(self._saved_matrix)
            self._saved_matrix = None

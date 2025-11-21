import glm
from OpenGL.GL import *
from appearance import Appearance

class PlanarShadow(Appearance):
    def __init__(self, light, plane_point, plane_normal):
        self.light = light
        self.plane_point = glm.vec3(plane_point)
        self.plane_normal = glm.normalize(glm.vec3(plane_normal))
        self._saved_matrix = None
        
        # Cache da matriz de sombra (se a luz e o plano não se movem, 
        # não precisamos recalcular todo frame, mas recalcularemos aqui por segurança)

    def _shadow_matrix(self):
        n = self.plane_normal
        # Equação do plano: ax + by + cz + d = 0
        # d = - (n . p)
        d = -glm.dot(n, self.plane_point)

        L = self.light.pos
        
        # Produto escalar entre o plano e a luz
        # dot = N.L + d*Lw
        dot = n.x * L.x + n.y * L.y + n.z * L.z + d * L.w

        shadow_mat = glm.mat4(1.0)

        # Primeira Coluna
        shadow_mat[0][0] = dot - L.x * n.x
        shadow_mat[0][1] =     - L.y * n.x
        shadow_mat[0][2] =     - L.z * n.x
        shadow_mat[0][3] =     - L.w * n.x

        # Segunda Coluna
        shadow_mat[1][0] =     - L.x * n.y
        shadow_mat[1][1] = dot - L.y * n.y
        shadow_mat[1][2] =     - L.z * n.y
        shadow_mat[1][3] =     - L.w * n.y

        # Terceira Coluna
        shadow_mat[2][0] =     - L.x * n.z
        shadow_mat[2][1] =     - L.y * n.z
        shadow_mat[2][2] = dot - L.z * n.z
        shadow_mat[2][3] =     - L.w * n.z

        # Quarta Coluna
        shadow_mat[3][0] =     - L.x * d
        shadow_mat[3][1] =     - L.y * d
        shadow_mat[3][2] =     - L.z * d
        shadow_mat[3][3] = dot - L.w * d

        return shadow_mat

    def Load(self, st):
        # 1. Salva estado anterior
        self._saved_matrix = st.GetCurrentMatrix()
        
        # 2. Aplica matriz de sombra sobre o objeto atual
        # M_final = M_sombra * M_objeto
        S = self._shadow_matrix()
        st.LoadMatrix(S * self._saved_matrix)

        # 3. SOLUÇÃO ELEGANTE PARA Z-FIGHTING
        # Em vez de mover a matriz (offset), usamos o Polygon Offset do OpenGL.
        # Isso empurra os pixels da sombra para "trás" no depth buffer, ou traz para frente.
        # Factor = inclinação, Units = valor constante mínimo
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(-1.0, -1.0) 

        # 4. Desativa efeitos de iluminação para a sombra ser "chapada"
        # Nota: Depende de como sua engine trata shaders. 
        # Idealmente você passaria uma flag para o shader usar cor sólida.
        # Exemplo genérico OpenGL fixo ou shader simples:
        glDepthMask(GL_FALSE) # (Opcional) Evita que sombra escreva no Z-Buffer
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Se você tiver acesso ao shader aqui, setaria uma uniform "isShadow = true"
        # st.SetColor(0.0, 0.0, 0.0, 0.5) # Sombra preta 50% opaca

    def Unload(self, st):
        # Restaura Matrix
        if self._saved_matrix is not None:
            st.LoadMatrix(self._saved_matrix)
            self._saved_matrix = None
        
        # Restaura Estados
        glDisable(GL_POLYGON_OFFSET_FILL)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
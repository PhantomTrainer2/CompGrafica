import glfw
from OpenGL.GL import *
import numpy as np
import glm
import datetime

# --- Configurações Iniciais ---
LARGURA_JANELA, ALTURA_JANELA = 800, 800
TITULO_JANELA = "Relógio Analógico"

# --- Shaders (Linguagem de sombreamento do OpenGL) ---

# Vertex Shader: Processa cada vértice da nossa forma geométrica.
# Ele aplica a matriz de transformação para posicionar, rotacionar e escalar o objeto.
vertex_shader_source = """
#version 330 core
layout (location = 0) in vec3 aPos;
uniform mat4 transform;
void main()
{
   gl_Position = transform * vec4(aPos, 1.0);
}
"""

# Fragment Shader: Colore cada pixel do objeto.
# Ele recebe uma cor uniforme e a aplica.
fragment_shader_source = """
#version 330 core
out vec4 FragColor;
uniform vec4 ourColor;
void main()
{
   FragColor = ourColor;
}
"""

def main():
    # --- 1. Inicialização do GLFW (Gerenciador de Janela) ---
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    janela = glfw.create_window(LARGURA_JANELA, ALTURA_JANELA, TITULO_JANELA, None, None)
    if not janela:
        glfw.terminate()
        return

    glfw.make_context_current(janela)

    # --- 2. Compilação dos Shaders ---
    # Compila o vertex shader
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source)
    glCompileShader(vertex_shader)
    # Compila o fragment shader
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)

    # Cria o programa de shader e anexa os shaders compilados
    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    # Libera a memória dos shaders, pois já estão no programa
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    # --- 3. Preparação da Geometria (Vértices) ---
    # Geometria base para os ponteiros (um retângulo que se estende para cima a partir da origem)
    ponteiro_vertices = np.array([
        # posições
        -0.5, 0.0, 0.0, # inferior esquerdo
         0.5, 0.0, 0.0, # inferior direito
         0.5, 1.0, 0.0, # superior direito
        -0.5, 1.0, 0.0  # superior esquerdo
    ], dtype=np.float32)

    indices = np.array([
        0, 1, 2, # primeiro triângulo
        2, 3, 0  # segundo triângulo
    ], dtype=np.uint32)

    # Configuração do Vertex Array Object (VAO) e Vertex Buffer Object (VBO)
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, ponteiro_vertices.nbytes, ponteiro_vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # Atribui os ponteiros dos vértices
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Desvincula o VBO e VAO para não modificar acidentalmente
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    # --- 4. Laço de Renderização (Animação) [cite: 179] ---
    while not glfw.window_should_close(janela):
        # Processa eventos como fechar a janela
        glfw.poll_events()

        # Define a cor de fundo
        glClearColor(0.9, 0.95, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Ativa o programa de shader
        glUseProgram(shader_program)

        # --- Lógica de Atualização da Animação ---
        agora = datetime.datetime.now()
        hora = agora.hour
        minuto = agora.minute
        segundo = agora.second

        # --- Cálculo dos ângulos dos ponteiros ---
        # A rotação em OpenGL é anti-horária por padrão, então usamos ângulos negativos para o movimento horário.
        
        # Ponteiro dos segundos: 360 graus / 60 segundos = 6 graus por segundo
        angulo_segundo = -segundo * 6.0
        
        # Ponteiro dos minutos: 360 / 60 = 6 graus por minuto + avanço proporcional aos segundos
        angulo_minuto = -(minuto * 6.0 + segundo * 0.1)
        
        # Ponteiro das horas: 360 / 12 = 30 graus por hora + avanço proporcional aos minutos
        angulo_hora = -((hora % 12) * 30.0 + minuto * 0.5)

        # Matriz de projeção ortográfica (define a "câmera" 2D) [cite: 144]
        projecao = glm.ortho(-10.0, 10.0, -10.0, 10.0, -1.0, 1.0)

        # --- Desenho de cada ponteiro usando Transformações ---
        glBindVertexArray(VAO)

        # 1. Ponteiro da Hora (curto e grosso)
        escala_hora = glm.scale(glm.vec3(0.8, 5.0, 1.0)) # Espessura, Comprimento, Profundidade
        rotacao_hora = glm.rotate(glm.radians(angulo_hora), glm.vec3(0.0, 0.0, 1.0))
        # A matriz de modelo combina escala e rotação [cite: 217]
        modelo_hora = rotacao_hora * escala_hora
        transformacao_hora = projecao * modelo_hora
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "transform"), 1, GL_FALSE, glm.value_ptr(transformacao_hora))
        glUniform4f(glGetUniformLocation(shader_program, "ourColor"), 0.1, 0.1, 0.1, 1.0) # Cor preta
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # 2. Ponteiro do Minuto (médio)
        escala_minuto = glm.scale(glm.vec3(0.5, 8.0, 1.0))
        rotacao_minuto = glm.rotate(glm.radians(angulo_minuto), glm.vec3(0.0, 0.0, 1.0))
        modelo_minuto = rotacao_minuto * escala_minuto
        transformacao_minuto = projecao * modelo_minuto
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "transform"), 1, GL_FALSE, glm.value_ptr(transformacao_minuto))
        glUniform4f(glGetUniformLocation(shader_program, "ourColor"), 0.2, 0.2, 0.2, 1.0) # Cor cinza escuro
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # 3. Ponteiro do Segundo (fino e vermelho)
        escala_segundo = glm.scale(glm.vec3(0.2, 9.0, 1.0))
        rotacao_segundo = glm.rotate(glm.radians(angulo_segundo), glm.vec3(0.0, 0.0, 1.0))
        modelo_segundo = rotacao_segundo * escala_segundo
        transformacao_segundo = projecao * modelo_segundo
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "transform"), 1, GL_FALSE, glm.value_ptr(transformacao_segundo))
        glUniform4f(glGetUniformLocation(shader_program, "ourColor"), 1.0, 0.0, 0.0, 1.0) # Cor vermelha
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # Troca os buffers da tela para exibir o que foi renderizado [cite: 187]
        glfw.swap_buffers(janela)

    # --- 5. Finalização ---
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteBuffers(1, [EBO])
    glDeleteProgram(shader_program)
    glfw.terminate()

if __name__ == "__main__":
    main()
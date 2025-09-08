from OpenGL.GL import *
import glfw

from polygon import Polygon
from shader import Shader

global poly, shd

def keyboard (win, key, scancode, action, mods):
   if key == glfw.KEY_Q and action == glfw.PRESS:
      glfw.set_window_should_close(win,glfw.TRUE)

def initialize ():
  global poly, shd
  glClearColor(0.1, 0.1, 0.1, 1.0)

  vertices = [
      (-0.8, -0.8),  # 0: Vértice inferior esquerdo (Verde)
      (-0.7, 0.7),   # 1: Vértice superior esquerdo (Azul)
      (0.0, 0.3),    # 2: Vértice interno (Vermelho)
      (0.9, 0.8),    # 3: Vértice superior direito (Amarelo)
      (0.6, -0.7)    # 4: Vértice inferior direito (Roxo)
  ]
  
  colors = [
      (144, 238, 144),  # 0: Verde claro
      (173, 216, 230),  # 1: Azul claro
      (205, 92, 92),    # 2: Vermelho/Marrom
      (255, 255, 224),  # 3: Amarelo claro
      (221, 160, 221)   # 4: Roxo claro
  ]

  # 2. Definir a "receita" dos triângulos manualmente
  indices = [
      0, 1, 2,  # Primeiro triângulo (Verde, Azul, Vermelho)
      0, 2, 4,  # Segundo triângulo (Verde, Vermelho, Roxo)
      2, 3, 4   # Terceiro triângulo (Vermelho, Amarelo, Roxo)
  ]

  # 3. Criar o polígono passando os vértices, cores E os índices
  poly = Polygon(vertices, colors, indices)
  
  # --- FIM DAS ALTERAÇÕES ---
  
  shd = Shader()
  # Use o seu caminho correto para os shaders
  shd.AttachVertexShader("Tarefa1/polygon/shaders/vertex.glsl")
  shd.AttachFragmentShader("Tarefa1/polygon/shaders/fragment.glsl")
  shd.Link()

def display ():
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  shd.UseProgram()
  poly.Draw()


def main():
  if not glfw.init():
      return
  
  glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,4)
  glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,1)
  glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
  glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT,GL_TRUE)
  
  # Usando o tamanho de tela original que você preferiu
  win = glfw.create_window(600, 400, "Polygon test (com Índices)", None, None)
  
  if not win:
      glfw.terminate()
      return
  glfw.set_key_callback(win,keyboard)

  glfw.make_context_current(win)
  print("OpenGL version: ",glGetString(GL_VERSION))

  initialize()

  while not glfw.window_should_close(win):
      display()
      glfw.swap_buffers(win)
      glfw.poll_events()

  glfw.terminate()

if __name__ == "__main__":
  main()
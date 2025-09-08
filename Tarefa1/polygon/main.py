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
  glClearColor(1, 1, 1, 1)

  vertices = [
      (-0.8, -0.8),  
      (-0.7, 0.7),  
      (0.0, 0.3), 
      (0.9, 0.8),
      (0.6, -0.7)
      ]
  
  colors = [
      (0, 255, 0),
      (0, 0, 255),
      (255, 0, 0),
      (255, 255, 0),
      (255, 0, 255)
  ]

  indices = [
      0, 1, 2,
      0, 2, 4,
      2, 3, 4  
  ]

  poly = Polygon(vertices, colors, indices)
  
  
  shd = Shader()
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
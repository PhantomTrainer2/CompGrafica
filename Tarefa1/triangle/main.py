from OpenGL.GL import *
import glfw

from triangle import Triangle
from shader import Shader

global tri, shd

def keyboard (win, key, scancode, action, mods):
   if key == glfw.KEY_Q and action == glfw.PRESS:
      glfw.set_window_should_close(win,glfw.TRUE)

def initialize ():
  global tri, shd
  glClearColor(1,1,1,1)
  tri = Triangle()
  shd = Shader()
  shd.AttachVertexShader("shaders/vertex.glsl")
  shd.AttachFragmentShader("shaders/fragment.glsl")
  shd.Link()

def display ():
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  shd.UseProgram()
  tri.Draw()


def main():
  # Initialize the library
  if not glfw.init():
      return
  # Create a windowed mode window and its OpenGL context
  glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,4)
  glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,1)
  glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
  glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT,GL_TRUE)
  win = glfw.create_window(600, 400, "Triangle test", None, None)
  if not win:
      glfw.terminate()
      return
  glfw.set_key_callback(win,keyboard)

  # Make the window's context current
  glfw.make_context_current(win)
  print("OpenGL version: ",glGetString(GL_VERSION))

  initialize()

  # Loop until the user closes the window
  while not glfw.window_should_close(win):
      # Render here, e.g. using pyOpenGL
      display()

      # Swap front and back buffers
      glfw.swap_buffers(win)

      # Poll for and process events
      glfw.poll_events()

  glfw.terminate()

if __name__ == "__main__":
  main()
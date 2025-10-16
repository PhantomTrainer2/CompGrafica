import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import *
from PIL import Image, ImageOps
import os

import glm
from camera3d import *
from light import *
from shader import *
from material import *
from transform import *
from node import *
from scene import *
from cube import * 
from sphere import * 
from texture import * 
from polyoffset import * 
from quad import *

def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT,GL_TRUE)
    win = glfw.create_window(640, 480, "Tarefa 2.1", None, None)
    if not win:
        glfw.terminate()
        return
    glfw.set_key_callback(win,keyboard)

    # Make the window's context current
    glfw.make_context_current(win)
    print("OpenGL version: ",glGetString(GL_VERSION))

    initialize(win)

    # Loop until the user closes the window
    while not glfw.window_should_close(win):
        # Render here, e.g. using pyOpenGL
        display(win)

        # Swap front and back buffers
        glfw.swap_buffers(win)

        # Poll for and process events
        glfw.poll_events()

viewer_pos = glm.vec3(2.0, 3.5, 4.0)

def initialize (win):
  # set background color: white 
  glClearColor(0.5,0.5,0.5,1.0)
  # enable depth test 
  glEnable(GL_DEPTH_TEST)
  # cull back faces
  glEnable(GL_CULL_FACE)  

  # create objects
  global camera
  camera = Camera3D(viewer_pos[0],viewer_pos[1],viewer_pos[2])
  arcball = camera.CreateArcball()
  arcball.Attach(win)

  light = Light(5.0,5.0,5.0)

  # Materials
  table_material = Material(0.5, 0.25, 0.0)
  box_material = Material(1, 0.5, 0)
  green_material = Material(0.0, 1.0, 0.0)
  red_material = Material(1.0, 0.0, 0.0)

  # Geometries
  cube = Cube() 
  sphere = Sphere()

  # Transformations (hierarchical)
  # Table - This is the base, centered at y=-0.5
  table_trf = Transform()
  table_trf.Scale(3.0, 0.2, 2.0)
  table_trf.Translate(0.0, -2.5, 0.0) # y=-0.5 world -> -0.5/0.2 scale = -2.5 local

  # Box - Relative to table
  box_trf = Transform()
  # World scale 0.8 -> local scale 0.8/3.0, 0.8/0.2, 0.8/2.0
  box_trf.Scale(0.8/3.0, 0.4/0.2, 0.8/2.0)
  # Move up by half table height + half box height (in parent's scaled space)
  # (0.2/2 + 0.8/2) / 0.2 (table y-scale) = 2.5
  box_trf.Translate(0.0, 0.5, 0.0)

  # Green Sphere - Relative to box
  green_sphere_trf = Transform()
  green_sphere_trf.Scale(0.2, 0.4, 0.2)
  # (0.8/2 + 0.3/2) / 0.8 (box y-scale) = 0.6875
  green_sphere_trf.Translate(0.0, 3.5, 0.0)

  # Red Sphere - Relative to table
  red_sphere_trf = Transform()
  red_sphere_trf.Scale(0.6/3.0, 0.6/0.2, 0.6/2.0)
  # Y: (0.2/2 + 0.6/2) / 0.2 = 2.0
  # X: 1.0 / 3.0 (table x-scale)
  # Z: 0.5 / 2.0 (table z-scale)
  red_sphere_trf.Translate(2.0, 1.2, -1)

  # --- Path independent shader loading ---
  # Get the absolute path to the directory containing this script
  script_dir = os.path.dirname(os.path.abspath(__file__))
  # Build absolute paths to the shaders
  vert_shader_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "vertex.glsl")
  frag_shader_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "fragment.glsl")

  # Shader
  shader = Shader(light,"camera")
  shader.AttachVertexShader(vert_shader_path)
  shader.AttachFragmentShader(frag_shader_path)
  shader.Link()

  # Scene Graph (Hierarchical)
  root = Node(shader,
              nodes = [
                  # Table Node is the parent
                  Node(None, table_trf, [table_material], [cube],
                       nodes = [
                           # Box Node is a child of the table
                           Node(None, box_trf, [box_material], [cube],
                                nodes = [
                                    # Green Sphere is a child of the box
                                    Node(None, green_sphere_trf, [green_material], [sphere])
                                ]),
                           # Red Sphere is also a child of the table
                           Node(None, red_sphere_trf, [red_material], [sphere])
                       ])
              ])
  global scene 
  scene = Scene(root)

def display (win):
  global scene
  global camera
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
  scene.Render(camera)

def keyboard (win, key, scancode, action, mods):
   if key == glfw.KEY_Q and action == glfw.PRESS:
      glfw.set_window_should_close(win,glfw.TRUE)

if __name__ == "__main__":
    main()

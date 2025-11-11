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
from cylinder import *
from texture import * 
from polyoffset import * 
from quad import *
from variable import *

def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT,GL_TRUE)
    win = glfw.create_window(640, 480, "Projeto 3", None, None)
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
  glCullFace(GL_BACK)  # Garantir que estamos culling faces traseiras  

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
  wood_material = Material(1.0, 1.0, 1.0)
  earth_material = Material(1.0, 1.0, 1.0)
  orange_material = Material(1.0, 0.5, 0.1) 

  # Geometries
  cube = Cube() 
  sphere = Sphere()
  cylinder = Cylinder()

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
  green_sphere_trf.Translate(1.5, 3.5, -0.8)

  # Red Sphere - Relative to table
  red_sphere_trf = Transform()
  red_sphere_trf.Scale(0.6/3.0, 0.6/0.2, 0.6/2.0)
  red_sphere_trf.Rotate(90, 0, 1, 0)  # Rotate 180 degrees around Y to show terrain
  # Y: (0.2/2 + 0.6/2) / 0.2 = 2.0
  # X: 1.0 / 3.0 (table x-scale)
  # Z: 0.5 / 2.0 (table z-scale)
  red_sphere_trf.Translate(1.3, 1.3, 1.5)

  # Wood Cylinder - Relative to table
  wood_cylinder_trf = Transform()
  # Scale: width/height/depth relative to table scaling
  # Cylinder: radius 0.3, height 0.8 in world space
  wood_cylinder_trf.Scale(0.3/3.0, 0.8/0.2, 0.3/2.0)
  # Y: (0.2/2 + 0.8/2) / 0.2 = 2.5
  # X: -0.8 / 3.0 (table x-scale)
  # Z: 0.5 / 2.0 (table z-scale)
  wood_cylinder_trf.Translate(-4, 0.6, 2)
  
  # Orange Cylinder (solid color, low height, wider) - Relative to table
  blue_cylinder_trf = Transform()
  # Scale: wider radius (0.25), shorter height (0.4)
  blue_cylinder_trf.Scale(0.25/3.0, 0.2/0.2, 0.25/2.0)
  # Y: (0.2/2 + 0.4/2) / 0.2 = 1.5
  # X: -0.8 - 0.5 (to the right of wood cylinder) / 3.0
  # Z: same as wood cylinder
  blue_cylinder_trf.Translate(-1, 3.5, 0.6)

  # --- Path independent shader loading ---
  # Get the absolute path to the directory containing this script
  script_dir = os.path.dirname(os.path.abspath(__file__))
  
  # Shader for solid color objects (table, box, spheres)
  vert_shader_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "vertex.glsl")
  frag_shader_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "fragment.glsl")
  shader = Shader(light,"camera")
  shader.AttachVertexShader(vert_shader_path)
  shader.AttachFragmentShader(frag_shader_path)
  shader.Link()
  
  # Shader for textured objects (cylinder with wood texture)
  vert_shader_tex_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "vertex_texture.glsl")
  frag_shader_tex_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "fragment_texture.glsl")
  shader_texture = Shader(light,"camera")
  shader_texture.AttachVertexShader(vert_shader_tex_path)
  shader_texture.AttachFragmentShader(frag_shader_tex_path)
  shader_texture.Link()
  
  # Textures
  wood_texture_path = os.path.join(script_dir, "..", "images", "wood.jpg")
  wood_texture = Texture("decal", wood_texture_path)
  
  # Earth textures for the red sphere
  earth_texture_path = os.path.join(script_dir, "..", "images", "earth.jpg")
  earth_texture = Texture("decal", earth_texture_path)
  earth_normal_path = os.path.join(script_dir, "..", "images", "earth-normal.png")
  earth_normal = Texture("normalMap", earth_normal_path)

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
                           # Earth Sphere with textures and normal map
                           Node(shader_texture, red_sphere_trf, [earth_material, earth_texture, earth_normal, Variable("useNormalMap", 1)], [sphere]),
                           # Wood Cylinder with texture and its own shader
                           Node(shader_texture, wood_cylinder_trf, [wood_material, wood_texture], [cylinder]),
                           # Blue Cylinder (solid color, no shader override - uses default shader)
                           Node(None, blue_cylinder_trf, [orange_material], [cylinder])
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

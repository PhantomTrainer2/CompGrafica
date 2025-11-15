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
from planarshadow import PlanarShadow
from objmesh import OBJMesh  # novo loader de .obj

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
  glCullFace(GL_BACK)

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
  # Table - base, centered at y=-0.5 (scaled)
  table_trf = Transform()
  table_trf.Scale(3.0, 0.2, 2.0)
  table_trf.Translate(0.0, -2.5, 0.0)

  # Box - Relative to table
  box_trf = Transform()
  box_trf.Scale(0.8/3.0, 0.4/0.2, 0.8/2.0)
  box_trf.Translate(0.0, 0.5, 0.0)

  # Green Sphere - Relative to box
  green_sphere_trf = Transform()
  green_sphere_trf.Scale(0.2, 0.4, 0.2)
  green_sphere_trf.Translate(1.5, 3.5, -0.8)

  # Red Sphere (terra) - Relative to table
  red_sphere_trf = Transform()
  red_sphere_trf.Scale(0.6/3.0, 0.6/0.2, 0.6/2.0)
  red_sphere_trf.Rotate(90, 0, 1, 0)
  red_sphere_trf.Translate(1.3, 1.3, 1.5)

  # Wood Cylinder - Relative to table
  wood_cylinder_trf = Transform()
  wood_cylinder_trf.Scale(0.3/3.0, 0.8/0.2, 0.3/2.0)
  wood_cylinder_trf.Translate(-4, 0.6, 2)
  
  # Blue Cylinder - Relative to table
  blue_cylinder_trf = Transform()
  blue_cylinder_trf.Scale(0.25/3.0, 0.2/0.2, 0.25/2.0)
  blue_cylinder_trf.Translate(-1, 3.5, 0.6)

  # --- Path independent shader loading ---
  script_dir = os.path.dirname(os.path.abspath(__file__))
  
  # Shader for solid color objects (table, box, spheres)
  vert_shader_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "vertex.glsl")
  frag_shader_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "fragment.glsl")
  shader = Shader(light,"camera")
  shader.AttachVertexShader(vert_shader_path)
  shader.AttachFragmentShader(frag_shader_path)
  shader.Link()
  
  # Shader for textured objects (cylinder with wood texture, esfera com normal map)
  vert_shader_tex_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "vertex_texture.glsl")
  frag_shader_tex_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "fragment_texture.glsl")
  shader_texture = Shader(light,"camera")
  shader_texture.AttachVertexShader(vert_shader_tex_path)
  shader_texture.AttachFragmentShader(frag_shader_tex_path)
  shader_texture.Link()

  # Shader para sombras planares
  shadow_vert_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "shadow_vertex.glsl")
  shadow_frag_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "shadow_fragment.glsl")
  shadow_shader = Shader(None, "camera")
  shadow_shader.AttachVertexShader(shadow_vert_path)
  shadow_shader.AttachFragmentShader(shadow_frag_path)
  shadow_shader.Link()

  # Shader para instanciamento com geometry shader
  inst_vert_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "instanced_vertex.glsl")
  inst_geom_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "instanced_geom.glsl")
  inst_frag_path = os.path.join(script_dir, "..", "shaders", "ilum_vert", "instanced_fragment.glsl")
  instanced_shader = Shader(light, "camera")
  instanced_shader.AttachVertexShader(inst_vert_path)
  instanced_shader.AttachGeometryShader(inst_geom_path)
  instanced_shader.AttachFragmentShader(inst_frag_path)
  instanced_shader.Link()

  # Configura offsets de instância (em espaço local do objeto)
  instanced_shader.UseProgram()
  offsets = [
      glm.vec3(-1.5, 0.0, -0.5),
      glm.vec3(-1.0, 0.0,  0.8),
      glm.vec3(-2.0, 0.0,  0.5),
      glm.vec3(-1.8, 0.0, -1.0),
  ]
  instanced_shader.SetUniform("instanceCount", len(offsets))
  instanced_shader.SetUniform("instanceOffsets", offsets)
  glUseProgram(0)

  # Texturas
  wood_texture_path = os.path.join(script_dir, "..", "images", "wood.jpg")
  wood_texture = Texture("decal", wood_texture_path)
  
  earth_texture_path = os.path.join(script_dir, "..", "images", "earth.jpg")
  earth_texture = Texture("decal", earth_texture_path)
  earth_normal_path = os.path.join(script_dir, "..", "images", "earth-normal.png")
  earth_normal = Texture("normalMap", earth_normal_path)

  # Plano da mesa para sombra planar (aprox. y = -2.3)
  table_plane_point = glm.vec3(0.0, -2.3, 0.0)
  table_plane_normal = glm.vec3(0.0, 1.0, 0.0)

  # --- Construção do grafo de cena ---

  # Nó da mesa
  table_node = Node(None, table_trf, [table_material], [cube])

  # Caixa e esfera verde (filha da caixa)
  box_node = Node(None, box_trf, [box_material], [cube])
  green_node = Node(None, green_sphere_trf, [green_material], [sphere])
  box_node.AddNode(green_node)

  # Esfera "terra" texturizada
  red_sphere_node = Node(shader_texture, red_sphere_trf,
                         [earth_material, earth_texture, earth_normal, Variable("useNormalMap", 1)],
                         [sphere])

  # Cilindro de madeira texturizado
  wood_cylinder_node = Node(shader_texture, wood_cylinder_trf,
                            [wood_material, wood_texture],
                            [cylinder])

  # Cilindro azul simples
  blue_cylinder_node = Node(None, blue_cylinder_trf,
                            [orange_material],
                            [cylinder])

  # Sombra da caixa
  box_shadow = Node(
      shadow_shader,
      box_trf,
      [
          PlanarShadow(light, table_plane_point, table_plane_normal),
          PolygonOffset(-1, -1),
          Variable("shadowColor", glm.vec4(0.0, 0.0, 0.0, 0.6))
      ],
      [cube]
  )

  # Sombra da esfera verde
  green_shadow = Node(
      shadow_shader,
      green_sphere_trf,
      [
          PlanarShadow(light, table_plane_point, table_plane_normal),
          PolygonOffset(-1, -1),
          Variable("shadowColor", glm.vec4(0.0, 0.0, 0.0, 0.6))
      ],
      [sphere]
  )

  # Sombra da esfera "terra"
  red_shadow = Node(
      shadow_shader,
      red_sphere_trf,
      [
          PlanarShadow(light, table_plane_point, table_plane_normal),
          PolygonOffset(-1, -1),
          Variable("shadowColor", glm.vec4(0.0, 0.0, 0.0, 0.6))
      ],
      [sphere]
  )

  # Sombra do cilindro de madeira
  wood_shadow = Node(
      shadow_shader,
      wood_cylinder_trf,
      [
          PlanarShadow(light, table_plane_point, table_plane_normal),
          PolygonOffset(-1, -1),
          Variable("shadowColor", glm.vec4(0.0, 0.0, 0.0, 0.6))
      ],
      [cylinder]
  )

  # Sombra do cilindro azul
  blue_shadow = Node(
      shadow_shader,
      blue_cylinder_trf,
      [
          PlanarShadow(light, table_plane_point, table_plane_normal),
          PolygonOffset(-1, -1),
          Variable("shadowColor", glm.vec4(0.0, 0.0, 0.0, 0.6))
      ],
      [cylinder]
  )

  # Nó de instanciamento (ex.: várias esferas pequenas ao lado da mesa)
  instanced_trf = Transform()
  instanced_trf.Scale(0.2, 0.2, 0.2)
  instanced_trf.Translate(-2.0, 0.0, 0.0)  # base

  instanced_node = Node(
      instanced_shader,
      instanced_trf,
      [orange_material],
      [sphere]
  )

  # Tenta carregar um .obj (ex.: models/teapot.obj) se existir
  obj_node = None
  obj_path = os.path.join(script_dir, "..", "models", "teapot.obj")
  if os.path.exists(obj_path):
      obj_trf = Transform()
      obj_trf.Scale(0.4, 0.4, 0.4)
      obj_trf.Translate(-0.5, 0.5, -0.5)
      obj_mesh = OBJMesh(obj_path)
      obj_node = Node(None, obj_trf, [Material(0.7, 0.7, 0.7)], [obj_mesh])

  # Monta filhos da mesa
  table_node.AddNode(box_node)
  table_node.AddNode(red_sphere_node)
  table_node.AddNode(wood_cylinder_node)
  table_node.AddNode(blue_cylinder_node)

  # Sombras (no mesmo nível dos objetos sobre a mesa)
  table_node.AddNode(box_shadow)
  table_node.AddNode(green_shadow)
  table_node.AddNode(red_shadow)
  table_node.AddNode(wood_shadow)
  table_node.AddNode(blue_shadow)

  # Instanciados
  table_node.AddNode(instanced_node)

  # .obj opcional
  if obj_node is not None:
      table_node.AddNode(obj_node)

  # Root com shader padrão
  root = Node(shader, nodes=[table_node])

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

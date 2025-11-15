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
from objmesh import OBJMesh  # loader de .obj (opcional)

viewer_pos = glm.vec3(2.0, 3.5, 4.0)

def keyboard (win, key, scancode, action, mods):
   if key == glfw.KEY_Q and action == glfw.PRESS:
      glfw.set_window_should_close(win,glfw.TRUE)

def initialize (win):
  global camera, scene

  # Cor de fundo e estados básicos
  glClearColor(0.5,0.5,0.5,1.0)
  glEnable(GL_DEPTH_TEST)
  glEnable(GL_CULL_FACE)
  glCullFace(GL_BACK)

  # Câmera e luz
  camera = Camera3D(viewer_pos.x, viewer_pos.y, viewer_pos.z)
  arcball = camera.CreateArcball()
  arcball.Attach(win)

  light = Light(5.0,5.0,5.0)

  # Materiais
  table_material = Material(0.5, 0.25, 0.0)
  box_material = Material(1.0, 0.5, 0.0)
  green_material = Material(0.0, 1.0, 0.0)
  wood_material = Material(1.0, 1.0, 1.0)
  earth_material = Material(1.0, 1.0, 1.0)
  orange_material = Material(1.0, 0.5, 0.1)

  # Geometrias
  cube = Cube()
  sphere = Sphere()
  cylinder = Cylinder()

  # Transforms da cena (hierarquia)
  # Mesa
  table_trf = Transform()
  table_trf.Scale(3.0, 0.2, 2.0)
  table_trf.Translate(0.0, -2.5, 0.0)

  # Caixa em cima da mesa
  box_trf = Transform()
  box_trf.Scale(0.8/3.0, 0.4/0.2, 0.8/2.0)
  box_trf.Translate(0.0, 0.5, 0.0)

  # Esfera verde (filha da caixa)
  green_sphere_trf = Transform()
  green_sphere_trf.Scale(0.2, 0.4, 0.2)
  green_sphere_trf.Translate(1.5, 3.5, -0.8)

  # Esfera "Terra" em cima da mesa
  red_sphere_trf = Transform()
  red_sphere_trf.Scale(0.6/3.0, 0.6/0.2, 0.6/2.0)
  red_sphere_trf.Rotate(90, 0, 1, 0)
  red_sphere_trf.Translate(1.3, 1.3, 1.5)

  # Cilindro de madeira
  wood_cylinder_trf = Transform()
  wood_cylinder_trf.Scale(0.3/3.0, 0.8/0.2, 0.3/2.0)
  wood_cylinder_trf.Translate(-4, 0.6, 2)

  # Cilindro laranja
  blue_cylinder_trf = Transform()
  blue_cylinder_trf.Scale(0.25/3.0, 0.2/0.2, 0.25/2.0)
  blue_cylinder_trf.Translate(-1, 3.5, 0.6)

  # Caminho dos shaders
  script_dir = os.path.dirname(os.path.abspath(__file__))
  sh_dir = os.path.join(script_dir, "..", "shaders", "ilum_vert")

  # Shader padrão com iluminação (objetos sólidos)
  shader = Shader(light, "camera")
  shader.AttachVertexShader(os.path.join(sh_dir, "vertex.glsl"))
  shader.AttachFragmentShader(os.path.join(sh_dir, "fragment.glsl"))
  shader.Link()

  # Shader com textura (terra, cilindro de madeira)
  shader_texture = Shader(light, "camera")
  shader_texture.AttachVertexShader(os.path.join(sh_dir, "vertex_texture.glsl"))
  shader_texture.AttachFragmentShader(os.path.join(sh_dir, "fragment_texture.glsl"))
  shader_texture.Link()

  # Shader para sombras planares (sem iluminação)
  shadow_shader = Shader(None, "camera")
  shadow_shader.AttachVertexShader(os.path.join(sh_dir, "shadow_vertex.glsl"))
  shadow_shader.AttachFragmentShader(os.path.join(sh_dir, "shadow_fragment.glsl"))
  shadow_shader.Link()

  # Shader para instanciamento via geometry shader
  instanced_shader = Shader(light, "camera")
  instanced_shader.AttachVertexShader(os.path.join(sh_dir, "instanced_vertex.glsl"))
  instanced_shader.AttachGeometryShader(os.path.join(sh_dir, "instanced_geom.glsl"))
  instanced_shader.AttachFragmentShader(os.path.join(sh_dir, "instanced_fragment.glsl"))
  instanced_shader.Link()

  # Para esse trabalho, vamos usar 1 instância (offset zero)
  instanced_shader.UseProgram()
  instanced_shader.SetUniform("instanceCount", 1)
  instanced_shader.SetUniform("instanceOffsets", [glm.vec3(0.0, 0.0, 0.0)])
  glUseProgram(0)

  # Texturas
  wood_texture = Texture("decal", os.path.join(script_dir, "..", "images", "wood.jpg"))
  earth_texture = Texture("decal", os.path.join(script_dir, "..", "images", "earth.jpg"))
  earth_normal = Texture("normalMap", os.path.join(script_dir, "..", "images", "earth-normal.png"))

  # Plano da mesa para sombras (topo da mesa em y ≈ -2.3)
  table_plane_point = glm.vec3(0.0, -2.3, 0.0)
  table_plane_normal = glm.vec3(0.0, 1.0, 0.0)

  shadow_color = glm.vec4(0.0, 0.0, 0.0, 0.6)

  # ===========================
  #      GRAFO DE CENA
  # ===========================

  # Nó raiz com shader padrão
  root = Node(shader)

  # Mesa
  table_node = Node(None, table_trf, [table_material], [cube])
  root.AddNode(table_node)

  # Caixa em cima da mesa
  box_node = Node(None, box_trf, [box_material], [cube])
  table_node.AddNode(box_node)

  # Esfera verde filha da caixa
  green_node = Node(None, green_sphere_trf, [green_material], [sphere])
  box_node.AddNode(green_node)

  # Esfera "Terra" texturizada
  red_sphere_node = Node(
      shader_texture,
      red_sphere_trf,
      [earth_material, earth_texture, earth_normal, Variable("useNormalMap", 1)],
      [sphere]
  )
  table_node.AddNode(red_sphere_node)

  # Cilindro de madeira texturizado
  wood_cylinder_node = Node(
      shader_texture,
      wood_cylinder_trf,
      [wood_material, wood_texture],
      [cylinder]
  )
  table_node.AddNode(wood_cylinder_node)

  # Cilindro laranja usando geometry shader de instancing
  blue_cylinder_node = Node(
      instanced_shader,          # <- usa o shader com geometry shader
      blue_cylinder_trf,
      [orange_material],
      [cylinder]
  )
  table_node.AddNode(blue_cylinder_node)

  # ===========================
  #      SOMBRAS PLANARES
  # ===========================

  # Sombra da caixa (filha da mesa)
  box_shadow = Node(
      shadow_shader,
      box_trf,
      [
          PlanarShadow(light, table_plane_point, table_plane_normal),
          PolygonOffset(-1, -1),
          Variable("shadowColor", shadow_color),
      ],
      [cube],
  )
  table_node.AddNode(box_shadow)

  # Sombra da esfera verde (filha da caixa)
  green_shadow = Node(
      shadow_shader,
      green_sphere_trf,
      [
          PlanarShadow(light, table_plane_point, table_plane_normal),
          PolygonOffset(-1, -1),
          Variable("shadowColor", shadow_color),
      ],
      [sphere],
  )
  box_node.AddNode(green_shadow)

  # Sombra da Terra (filha da mesa)
  red_shadow = Node(
      shadow_shader,
      red_sphere_trf,
      [
          PlanarShadow(light, table_plane_point, table_plane_normal),
          PolygonOffset(-1, -1),
          Variable("shadowColor", shadow_color),
      ],
      [sphere],
  )
  table_node.AddNode(red_shadow)

  # Sombra do cilindro de madeira
  wood_shadow = Node(
      shadow_shader,
      wood_cylinder_trf,
      [
          PlanarShadow(light, table_plane_point, table_plane_normal),
          PolygonOffset(-1, -1),
          Variable("shadowColor", shadow_color),
      ],
      [cylinder],
  )
  table_node.AddNode(wood_shadow)

  # Sombra do cilindro laranja
  blue_shadow = Node(
      shadow_shader,
      blue_cylinder_trf,
      [
          PlanarShadow(light, table_plane_point, table_plane_normal),
          PolygonOffset(-1, -1),
          Variable("shadowColor", shadow_color),
      ],
      [cylinder],
  )
  table_node.AddNode(blue_shadow)

  # ===========================
  #  OBJ OPCIONAL (teapot)
  # ===========================

  obj_path = os.path.join(script_dir, "..", "models", "teapot.obj")
  if os.path.exists(obj_path):
      obj_trf = Transform()
      obj_trf.Scale(0.4, 0.4, 0.4)
      obj_trf.Translate(-0.5, 0.5, -0.5)
      obj_mesh = OBJMesh(obj_path)
      obj_node = Node(None, obj_trf, [Material(0.7, 0.7, 0.7)], [obj_mesh])
      table_node.AddNode(obj_node)

  # Cria cena
  scene = Scene(root)

def display (win):
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  scene.Render(camera)

def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT,GL_TRUE)

    win = glfw.create_window(640, 480, "Projeto 3", None, None)
    if not win:
        glfw.terminate()
        return

    glfw.set_key_callback(win, keyboard)
    glfw.make_context_current(win)
    print("OpenGL version:", glGetString(GL_VERSION))

    initialize(win)

    while not glfw.window_should_close(win):
        display(win)
        glfw.swap_buffers(win)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()

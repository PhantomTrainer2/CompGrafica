# python/main_animation.py

import glfw
import time
import os
from OpenGL.GL import *

# Imports da sua biblioteca
from scene import Scene
from state import State
from node import Node
from transform import Transform
from material import Material
from shader import Shader
from texture import Texture
from camera2d import Camera2D
from luxor.disk import Disk
from solar_system_animation import SolarSystemAnimation # Nosso arquivo de animação corrigido

# --- Variáveis Globais ---
scene = None
state = None
# A engine de animação agora será gerenciada pela cena
last_time = 0.0

def init_app():
    global scene, state

    # --- Construção de Caminhos ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    shaders_path = os.path.join(project_root, 'shaders')
    images_path = os.path.join(project_root, 'images')

    # --- Criação de Assets ---
    textured_shader = Shader()
    vertex_shader_file = os.path.join(shaders_path, 'ilum_vert', 'vertex_texture.glsl')
    fragment_shader_file = os.path.join(shaders_path, 'ilum_vert', 'fragment_texture.glsl')
    textured_shader.AttachVertexShader(vertex_shader_file)
    textured_shader.AttachFragmentShader(fragment_shader_file)
    textured_shader.Link()

    sun_texture = Texture(GL_TEXTURE0, os.path.join(images_path, 'sun.jpg'))
    earth_texture = Texture(GL_TEXTURE1, os.path.join(images_path, 'earth.jpg'))
    moon_texture = Texture(GL_TEXTURE2, os.path.join(images_path, 'moon.jpg'))

    sun_material = Material(1.0, 1.0, 1.0)
    earth_material = Material(1.0, 1.0, 1.0)
    moon_material = Material(1.0, 1.0, 1.0)
    disk_shape = Disk(segments=100)

    # --- Construção do Grafo de Cena ---
    root_node = Node()
    
    sun_spin = Transform()
    sun_spin.Scale(2.0, 2.0, 2.0)
    
    earth_orbit = Transform()
    earth_translate = Transform()
    earth_translate.Translate(2.0, 0, 0)
    earth_spin = Transform()
    earth_spin.Scale(0.8, 0.8, 0.8)
    
    moon_orbit = Transform()
    moon_translate = Transform()
    moon_translate.Translate(0.6, 0, 0)
    moon_scale = Transform()
    moon_scale.Scale(0.3, 0.3, 0.3)
    
    moon_leaf_node = Node(trf=moon_scale, apps=[moon_texture, moon_material], shps=[disk_shape])
    moon_translate_node = Node(trf=moon_translate, nodes=[moon_leaf_node])
    moon_orbit_node = Node(trf=moon_orbit, nodes=[moon_translate_node])
    
    earth_leaf_node = Node(trf=earth_spin, apps=[earth_texture, earth_material], shps=[disk_shape])
    earth_translate_node = Node(trf=earth_translate, nodes=[earth_leaf_node, moon_orbit_node])
    earth_orbit_node = Node(trf=earth_orbit, nodes=[earth_translate_node])
    
    sun_leaf_node = Node(shader=textured_shader, trf=sun_spin, apps=[sun_texture, sun_material], shps=[disk_shape])
    earth_orbit_node.SetShader(textured_shader)

    root_node.AddNode(earth_orbit_node)
    root_node.AddNode(sun_leaf_node)

    scene = Scene(root_node)

    engine = SolarSystemAnimation(earth_orbit, moon_orbit, earth_spin, sun_spin)
    scene.AddEngine(engine)

    # ATENÇÃO: Correção final aqui
    # 1. Crie a câmera com os limites desejados no construtor
    camera = Camera2D(xmin=-3, xmax=3, ymin=-2.25, ymax=2.25)
    # 2. Crie o estado passando a câmera já configurada
    state = State(camera)

def update_and_draw():
    global last_time
    
    current_time = glfw.get_time()
    dt = current_time - last_time
    last_time = current_time

    glClearColor(0.0, 0.0, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    if scene and state:
        # A cena agora gerencia a atualização dos engines e a renderização
        # O engine.Update agora deve ser chamado com dt (delta time)
        # Mas a cena já faz isso por nós quando chamamos scene.Update(dt)
        # A animação, no entanto, foi feita com tempo absoluto, então passamos current_time
        for e in scene.engines:
            e.Update(current_time)
            
        scene.Render(state.camera)

def main():
    global last_time
    if not glfw.init():
        return
    window = glfw.create_window(800, 600, "Sistema Solar 2D", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    
    init_app()
    last_time = glfw.get_time() # Inicializa o contador de tempo
    
    while not glfw.window_should_close(window):
        update_and_draw()
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()

if __name__ == "__main__":
    main()
# python/main_animation.py

import glfw
import time
import os
from OpenGL.GL import *
import glm

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

    # --- Configuração da Fonte de Luz ---
    textured_shader.UseProgram()
    light_pos = glm.vec4(0.0, 0.0, 1.0, 0.0)
    light_amb = glm.vec4(0.2, 0.2, 0.2, 1.0)
    light_dif = glm.vec4(1.0, 1.0, 1.0, 1.0)
    light_spe = glm.vec4(1.0, 1.0, 1.0, 1.0)
    textured_shader.SetUniform("lpos", light_pos)
    textured_shader.SetUniform("lamb", light_amb)
    textured_shader.SetUniform("ldif", light_dif)
    textured_shader.SetUniform("lspe", light_spe)
    glUseProgram(0)

    # --- Continuação da Criação de Assets ---
    sun_texture = Texture(GL_TEXTURE0, os.path.join(images_path, 'sun.jpg'))
    earth_texture = Texture(GL_TEXTURE1, os.path.join(images_path, 'earth.jpg'))
    moon_texture = Texture(GL_TEXTURE2, os.path.join(images_path, 'moon.jpg'))

    sun_material = Material(1.0, 1.0, 1.0)
    earth_material = Material(1.0, 1.0, 1.0)
    moon_material = Material(1.0, 1.0, 1.0)
    disk_shape = Disk(segments=100)

    # --- Construção do Grafo de Cena ---
    root_node = Node()
    
    # ATENÇÃO: Mudanças na forma como criamos as transformações
    # 1. Crie transformações SEPARADAS para escala e rotação
    sun_scale = Transform()
    sun_scale.Scale(2.0, 2.0, 2.0) # <--- CONTROLE O TAMANHO DO SOL AQUI
    sun_spin = Transform() # Este será controlado pela animação

    earth_orbit = Transform()
    earth_translate = Transform()
    earth_translate.Translate(2.5, 0, 0)
    earth_scale = Transform()
    earth_scale.Scale(0.8, 0.8, 0.8) # <--- CONTROLE O TAMANHO DA TERRA AQUI
    earth_spin = Transform() # Este será controlado pela animação
    
    moon_orbit = Transform()
    moon_translate = Transform()
    moon_translate.Translate(0.8, 0, 0)
    moon_scale_trf = Transform() # Renomeado para não confundir com a variável moon_scale anterior
    moon_scale_trf.Scale(0.3, 0.3, 0.3)
    
    # 2. Monte a hierarquia com a nova estrutura (escala -> rotação -> objeto)
    moon_leaf_node = Node(trf=moon_scale_trf, apps=[moon_texture, moon_material], shps=[disk_shape])
    moon_translate_node = Node(trf=moon_translate, nodes=[moon_leaf_node])
    moon_orbit_node = Node(trf=moon_orbit, nodes=[moon_translate_node])
    
    earth_spin_node = Node(trf=earth_spin, apps=[earth_texture, earth_material], shps=[disk_shape])
    earth_scale_node = Node(trf=earth_scale, nodes=[earth_spin_node]) # Nó de escala é pai do nó de rotação
    earth_translate_node = Node(trf=earth_translate, nodes=[earth_scale_node, moon_orbit_node])
    earth_orbit_node = Node(trf=earth_orbit, nodes=[earth_translate_node])
    
    sun_spin_node = Node(shader=textured_shader, trf=sun_spin, apps=[sun_texture, sun_material], shps=[disk_shape])
    sun_scale_node = Node(trf=sun_scale, nodes=[sun_spin_node]) # Nó de escala é pai do nó de rotação
    earth_orbit_node.SetShader(textured_shader)

    root_node.AddNode(earth_orbit_node)
    root_node.AddNode(sun_scale_node) # Adiciona o nó de escala do sol à cena

    scene = Scene(root_node)

    # 3. A engine de animação continua controlando os mesmos transforms de rotação
    engine = SolarSystemAnimation(earth_orbit, moon_orbit, earth_spin, sun_spin)
    scene.AddEngine(engine)
    
    camera = Camera2D(xmin=-4, xmax=4, ymin=-4, ymax=4)
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
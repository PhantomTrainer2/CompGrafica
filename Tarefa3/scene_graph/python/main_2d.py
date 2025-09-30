import glfw
import time
import os
from OpenGL.GL import *
import glm
import numpy as np
import ctypes

from scene import Scene
from state import State
from node import Node
from transform import Transform
from texture import Texture
from shader import Shader
from camera2d import Camera2D
from luxor.disk import Disk
from luxor.animation import SolarSystemAnimation

# Variáveis globais
scene = None
state = None
last_time = 0.0

def init_app():
    global scene, state

    # --- CONFIGURAÇÃO DE PATHS ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ilum_vert_path = os.path.join(script_dir, '..', 'shaders', 'ilum_vert')
    images_path = os.path.join(script_dir, '..', 'images')

    sun_image_path = os.path.join(images_path, "sun.jpg")
    earth_image_path = os.path.join(images_path, "earthfull.jpg")
    moon_image_path = os.path.join(images_path, "moon.jpeg")
    venus_image_path = os.path.join(images_path, "venus.jpg")
    
    # --- SHADER PARA OS PLANETAS (COM ILUMINAÇÃO) ---
    planet_shader = Shader()
    vertex_shader_file = os.path.join(ilum_vert_path, 'vertex_texture.glsl')
    fragment_shader_file = os.path.join(ilum_vert_path, 'fragment_texture.glsl')
    planet_shader.AttachVertexShader(vertex_shader_file)
    planet_shader.AttachFragmentShader(fragment_shader_file)
    planet_shader.Link()

    # Configuração dos uniforms para os planetas (material que reflete luz)
    planet_shader.UseProgram()
    planet_shader.SetUniform("lpos", glm.vec4(0.0, 0.0, 4.0, 1.0))
    planet_shader.SetUniform("lamb", glm.vec4(0.2, 0.2, 0.2, 1.0))
    planet_shader.SetUniform("ldif", glm.vec4(1.0, 1.0, 1.0, 1.0))
    planet_shader.SetUniform("lspe", glm.vec4(1.0, 1.0, 1.0, 1.0))
    planet_shader.SetUniform("mamb", glm.vec4(1.0, 1.0, 1.0, 1.0))
    planet_shader.SetUniform("mdif", glm.vec4(0.8, 0.8, 0.8, 1.0))
    planet_shader.SetUniform("mspe", glm.vec4(0.5, 0.5, 0.5, 1.0))
    planet_shader.SetUniform("mshi", 32.0)
    glUseProgram(0)

    # --- NOVO: SHADER PARA O SOL (MATERIAL EMISSIVO) ---
    # Usamos os mesmos arquivos .glsl, mas criamos um programa de shader separado
    # para podermos definir valores de material (uniforms) diferentes para ele.
    sun_shader = Shader()
    sun_shader.AttachVertexShader(vertex_shader_file)
    sun_shader.AttachFragmentShader(fragment_shader_file)
    sun_shader.Link()

    # Configuração dos uniforms para o Sol (material que emite luz)
    sun_shader.UseProgram()
    sun_shader.SetUniform("lpos", glm.vec4(0.0, 0.0, 4.0, 1.0)) # A luz ainda precisa existir
    sun_shader.SetUniform("lamb", glm.vec4(0.2, 0.2, 0.2, 1.0)) # Luz ambiente global
    sun_shader.SetUniform("ldif", glm.vec4(1.0, 1.0, 1.0, 1.0))
    sun_shader.SetUniform("lspe", glm.vec4(1.0, 1.0, 1.0, 1.0))
    
    # A MÁGICA ACONTECE AQUI:
    # 1. Aumentamos o material ambiente para anular o efeito da luz ambiente fraca (0.2 * 5.0 = 1.0)
    sun_shader.SetUniform("mamb", glm.vec4(5.0, 5.0, 5.0, 1.0)) 
    # 2. Zeramos a reflexão difusa e especular. O Sol não reflete luz.
    sun_shader.SetUniform("mdif", glm.vec4(0.0, 0.0, 0.0, 1.0)) 
    sun_shader.SetUniform("mspe", glm.vec4(0.0, 0.0, 0.0, 1.0)) 
    sun_shader.SetUniform("mshi", 1.0)
    glUseProgram(0)

    # --- CARREGAMENTO DAS TEXTURAS ---
    sun_texture = Texture("decal", sun_image_path)
    earth_texture = Texture("decal", earth_image_path)
    moon_texture = Texture("decal", moon_image_path)
    venus_texture = Texture("decal", venus_image_path)
    
    disk_shape = Disk(segments=100)

    # --- CONSTRUÇÃO DA CENA ---
    # O resto do código é o mesmo, apenas trocamos o shader usado em cada nó.
    root_node = Node()
    sun_scale = Transform()
    sun_scale.Scale(3.0, 3.0, 3.0)
    sun_spin = Transform() 

    earth_orbit = Transform()
    earth_translate = Transform()
    earth_translate.Translate(6.0, 0, 0)
    earth_scale = Transform()
    earth_scale.Scale(0.8, 0.8, 0.8)
    earth_spin = Transform() 
    
    venus_orbit = Transform()
    venus_translate = Transform()
    venus_translate.Translate(3.5, 0, 0)
    venus_scale = Transform()
    venus_scale.Scale(0.5, 0.5, 0.5)
    venus_spin = Transform() 

    moon_orbit = Transform()
    moon_translate = Transform()
    moon_translate.Translate(1.2, 0, 0)
    moon_scale_trf = Transform()
    moon_scale_trf.Scale(0.3, 0.3, 0.3)
    
    moon_leaf_node = Node(trf=moon_scale_trf, apps=[moon_texture], shps=[disk_shape])
    moon_translate_node = Node(trf=moon_translate, nodes=[moon_leaf_node])
    moon_orbit_node = Node(trf=moon_orbit, nodes=[moon_translate_node])
    
    earth_spin_node = Node(trf=earth_spin, apps=[earth_texture], shps=[disk_shape])
    earth_scale_node = Node(trf=earth_scale, nodes=[earth_spin_node])
    earth_translate_node = Node(trf=earth_translate, nodes=[earth_scale_node, moon_orbit_node])
    earth_orbit_node = Node(trf=earth_orbit, nodes=[earth_translate_node])

    venus_spin_node = Node(trf=venus_spin, apps=[venus_texture], shps=[disk_shape])
    venus_scale_node = Node(trf=venus_scale, nodes=[venus_spin_node])
    venus_translate_node = Node(trf=venus_translate, nodes=[venus_scale_node])
    venus_orbit_node = Node(trf=venus_orbit, nodes=[venus_translate_node])
    
    # ATRIBUINDO OS SHADERS CORRETOS
    sun_spin_node = Node(shader=sun_shader, trf=sun_spin, apps=[sun_texture], shps=[disk_shape])
    sun_scale_node = Node(trf=sun_scale, nodes=[sun_spin_node])
    
    earth_orbit_node.SetShader(planet_shader)
    venus_orbit_node.SetShader(planet_shader)

    root_node.AddNode(earth_orbit_node)
    root_node.AddNode(venus_orbit_node)
    root_node.AddNode(sun_scale_node)

    scene = Scene(root_node)
    engine = SolarSystemAnimation(earth_orbit, moon_orbit, earth_spin, sun_spin, venus_orbit, venus_spin)
    scene.AddEngine(engine)
    
    camera = Camera2D(xmin=-10, xmax=10, ymin=-10, ymax=10)
    state = State(camera)

def update_and_draw():
    global last_time
    current_time = glfw.get_time()
    last_time = current_time
    
    # Define uma cor de fundo sólida
    glClearColor(0.0, 0.0, 0.1, 1.0) # Azul escuro
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Desenha a cena do sistema solar
    if scene and state:
        for e in scene.engines:
            e.Update(current_time)
        scene.Render(state.camera)

def main():
    global last_time
    if not glfw.init():
        return
    window = glfw.create_window(800, 800, "Sistema Solar 2D com Texturas", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    init_app()
    last_time = glfw.get_time()
    while not glfw.window_should_close(window):
        update_and_draw()
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()

if __name__ == "__main__":
    main()
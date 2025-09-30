import glfw
import time
import os
from OpenGL.GL import *
import glm

from scene import Scene
from state import State
from node import Node
from transform import Transform
from material import Material
from shader import Shader
from camera2d import Camera2D
from luxor.disk import Disk
from solar_system_animation import SolarSystemAnimation

scene = None
state = None
last_time = 0.0

def init_app():
    global scene, state

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    shaders_path = os.path.join(project_root, 'shaders')

    illum_shader = Shader()
    vertex_shader_file = os.path.join(shaders_path, 'ilum_vert', 'vertex.glsl')
    fragment_shader_file = os.path.join(shaders_path, 'ilum_vert', 'fragment.glsl')
    illum_shader.AttachVertexShader(vertex_shader_file)
    illum_shader.AttachFragmentShader(fragment_shader_file)
    illum_shader.Link()

    illum_shader.UseProgram()
    light_pos = glm.vec4(0.0, 0.0, 1.0, 0.0)
    light_amb = glm.vec4(0.3, 0.3, 0.3, 1.0) 
    light_dif = glm.vec4(1.0, 1.0, 1.0, 1.0)
    light_spe = glm.vec4(1.0, 1.0, 1.0, 1.0)
    illum_shader.SetUniform("lpos", light_pos)
    illum_shader.SetUniform("lamb", light_amb)
    illum_shader.SetUniform("ldif", light_dif)
    illum_shader.SetUniform("lspe", light_spe)
    glUseProgram(0)

    sun_material = Material(1.0, 1.0, 0.0)
    earth_material = Material(0.2, 0.2, 1.0)
    moon_material = Material(1.0, 1.0, 1.0)
    venus_material = Material(0.0, 1.0, 0.2)

    disk_shape = Disk(segments=100)

    root_node = Node()
    sun_scale = Transform()
    sun_scale.Scale(3.0, 3.0, 3.0)
    sun_spin = Transform() 

    earth_orbit = Transform()
    earth_translate = Transform()
    earth_translate.Translate(5.0, 0, 0)
    earth_scale = Transform()
    earth_scale.Scale(0.8, 0.8, 0.8)
    earth_spin = Transform() 
    
    venus_orbit = Transform()
    venus_translate = Transform()
    venus_translate.Translate(2.0, 0, 0)
    venus_scale = Transform()
    venus_scale.Scale(0.4, 0.4, 0.4)
    venus_spin = Transform() 

    moon_orbit = Transform()
    moon_translate = Transform()
    moon_translate.Translate(1.0, 0, 0)
    moon_scale_trf = Transform()
    moon_scale_trf.Scale(0.3, 0.3, 0.3)
    
    moon_leaf_node = Node(trf=moon_scale_trf, apps=[moon_material], shps=[disk_shape])
    moon_translate_node = Node(trf=moon_translate, nodes=[moon_leaf_node])
    moon_orbit_node = Node(trf=moon_orbit, nodes=[moon_translate_node])
    
    earth_spin_node = Node(trf=earth_spin, apps=[earth_material], shps=[disk_shape])
    earth_scale_node = Node(trf=earth_scale, nodes=[earth_spin_node])
    earth_translate_node = Node(trf=earth_translate, nodes=[earth_scale_node, moon_orbit_node])
    earth_orbit_node = Node(trf=earth_orbit, nodes=[earth_translate_node])

    venus_spin_node = Node(trf=venus_spin, apps=[venus_material], shps=[disk_shape])
    venus_scale_node = Node(trf=venus_scale, nodes=[venus_spin_node])
    venus_translate_node = Node(trf=venus_translate, nodes=[venus_scale_node])
    venus_orbit_node = Node(trf=venus_orbit, nodes=[venus_translate_node])
    
    sun_spin_node = Node(shader=illum_shader, trf=sun_spin, apps=[sun_material], shps=[disk_shape])
    sun_scale_node = Node(trf=sun_scale, nodes=[sun_spin_node])
    earth_orbit_node.SetShader(illum_shader)
    venus_orbit_node.SetShader(illum_shader)


    root_node.AddNode(earth_orbit_node)
    root_node.AddNode(venus_orbit_node)
    root_node.AddNode(sun_scale_node)

    scene = Scene(root_node)
    engine = SolarSystemAnimation(earth_orbit, moon_orbit, earth_spin, sun_spin, venus_orbit, venus_spin)
    scene.AddEngine(engine)
    
    camera = Camera2D(xmin=-5, xmax=5, ymin=-5, ymax=5)
    state = State(camera)

def update_and_draw():
    global last_time
    current_time = glfw.get_time()
    dt = current_time - last_time
    last_time = current_time
    glClearColor(0.0, 0.0, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if scene and state:
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
    last_time = glfw.get_time()
    while not glfw.window_should_close(window):
        update_and_draw()
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()

if __name__ == "__main__":
    main()
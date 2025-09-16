import glfw
from OpenGL.GL import *
import glm
import time

from python.node import Node
from python.scene import Scene
from python.state import State
from python.camera2d import Camera2D

from python.luxor.disk import Disk
from python.luxor.solar_engine import OrbitEngine

def init():
    camera = Camera2D()
    state = State(camera)

    # cria nó raiz
    root = Node()
    scene = Scene(root)

    # Sol
    sun = Node()
    sun.AddShape(Disk(radius=0.2))
    root.AddNode(sun)

    # Terra
    earth = Node()
    earth.AddShape(Disk(radius=0.1))
    sun.AddNode(earth)
    earth_engine = OrbitEngine(earth, radius=0.6, speed=1.0)
    scene.AddEngine(earth_engine)

    # Lua
    moon = Node()
    moon.AddShape(Disk(radius=0.05))
    earth.AddNode(moon)
    moon_engine = OrbitEngine(moon, radius=0.2, speed=3.0)
    scene.AddEngine(moon_engine)

    return scene, state

def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 800, "Mini Sistema Solar", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    scene, state = init()

    last_time = time.time()
    while not glfw.window_should_close(window):
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        scene.Update(dt)
        scene.Draw(state)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()

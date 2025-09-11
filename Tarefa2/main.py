import glfw
from OpenGL.GL import *
import numpy as np
import math
import datetime
import ctypes
from shader import Shader

# ---------- Cria um VAO para o círculo (face do relógio) ----------
def create_circle_vao(radius=0.9, segments=64):
    verts = []
    verts.extend([0.0, 0.0, 0.0, 1.0,  1.0, 1.0, 1.0, 1.0])
    for i in range(segments + 1):
        theta = 2.0 * math.pi * i / segments
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        verts.extend([x, y, 0.0, 1.0,  1.0, 1.0, 1.0, 1.0])
    data = np.array(verts, dtype=np.float32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    stride = 8 * data.itemsize
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(4 * data.itemsize))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    count = 1 + segments + 1
    return vao, count

# ---------- Cria um VAO + VBO + EBO para um retângulo atualizável ----------
_base_quad = [(0.0, -0.5), (1.0, -0.5), (1.0, 0.5), (0.0, 0.5)]

def create_quad_vao():
    initial = np.zeros((4 * 8,), dtype=np.float32)
    indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, initial.nbytes, initial, GL_DYNAMIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    stride = 8 * initial.itemsize
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(4 * initial.itemsize))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return vao, vbo, ebo, len(indices)

# ---------- Atualiza vértices de um retângulo transformado ----------
def draw_quad_cpu(vao, vbo, count, angle_deg, length, thickness, color, offset=0.0):
    rad = math.radians(-angle_deg)
    c = math.cos(rad)
    s = math.sin(rad)
    r, g, b = color
    a = 1.0

    data = []
    for (x0, y0) in _base_quad:
        xs = x0 * length
        ys = y0 * thickness
        xr = c * xs - s * ys
        yr = s * xs + c * ys
        # aplica offset para "empurrar" para a borda do círculo
        xr += offset * c
        yr += offset * s
        data.extend([xr, yr, 0.0, 1.0, r, g, b, a])

    arr = np.array(data, dtype=np.float32)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferSubData(GL_ARRAY_BUFFER, 0, arr.nbytes, arr)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES, count, GL_UNSIGNED_INT, None)
    glBindVertexArray(0)

# ---------- Main ----------
def main():
    if not glfw.init():
        return

    win = glfw.create_window(800, 800, "Relogio Analogico", None, None)
    if not win:
        glfw.terminate()
        return
    glfw.make_context_current(win)

    def framebuffer_size_cb(win, w, h):
        glViewport(0, 0, w, h)
    glfw.set_framebuffer_size_callback(win, framebuffer_size_cb)
    fb = glfw.get_framebuffer_size(win)
    glViewport(0, 0, fb[0], fb[1])

    glClearColor(0.678, 0.847, 0.902, 1.0)
    glDisable(GL_DEPTH_TEST)

    shader = Shader()
    shader.AttachVertexShader("shaders/vertex.glsl")
    shader.AttachFragmentShader("shaders/fragment.glsl")
    shader.Link()
    shader.UseProgram()

    circle_vao, circle_count = create_circle_vao(radius=0.9, segments=128)
    pointer_vao, pointer_vbo, _, pointer_count = create_quad_vao()
    mark_vao, mark_vbo, _, mark_count = create_quad_vao()

    hour_len, minute_len, second_len = 0.45, 0.7, 0.85
    hour_thick, minute_thick, second_thick = 0.06, 0.04, 0.02

    # loop principal
    while not glfw.window_should_close(win):
        glClear(GL_COLOR_BUFFER_BIT)
        shader.UseProgram()

        now = datetime.datetime.now()
        sec = now.second + now.microsecond / 1e6
        minute = now.minute + sec / 60.0
        hour = (now.hour % 12) + minute / 60.0

        angle_sec = sec * 6.0 + -90
        angle_min = minute * 6.0 + -90
        angle_hour = hour * 30.0 + -90


        # círculo branco (fundo do relógio)
        glBindVertexArray(circle_vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, circle_count)
        glBindVertexArray(0)

        # marcações das horas
        for h in range(12):
            angle = h * 30.0
            draw_quad_cpu(mark_vao, mark_vbo, mark_count,
                          angle, 0.08, 0.02, (0.0, 0.0, 0.0), offset=0.82)

        # ponteiros
        draw_quad_cpu(pointer_vao, pointer_vbo, pointer_count, angle_hour, hour_len, hour_thick, (0.0, 0.0, 0.0))
        draw_quad_cpu(pointer_vao, pointer_vbo, pointer_count, angle_min, minute_len, minute_thick, (0.0, 0.0, 0.0))
        draw_quad_cpu(pointer_vao, pointer_vbo, pointer_count, angle_sec, second_len, second_thick, (1.0, 0.0, 0.0))

        glfw.swap_buffers(win)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()

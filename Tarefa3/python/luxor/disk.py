import math
from OpenGL.GL import *
from python.shape import Shape

class Disk(Shape):
    def __init__(self, radius=1.0, slices=64):
        super().__init__()
        self.radius = radius
        self.slices = slices

    def Draw(self, state):
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0.0, 0.0, 0.0)  # centro
        for i in range(self.slices + 1):
            theta = 2.0 * math.pi * i / self.slices
            x = self.radius * math.cos(theta)
            y = self.radius * math.sin(theta)
            glVertex3f(x, y, 0.0)
        glEnd()

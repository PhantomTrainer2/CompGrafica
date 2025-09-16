import glm
import math
from python.engine import Engine

class OrbitEngine(Engine):
    def __init__(self, node, radius, speed):
        self.node = node
        self.radius = radius
        self.speed = speed
        self.angle = 0.0

    def Update(self, dt):
        self.angle += self.speed * dt
        x = self.radius * math.cos(self.angle)
        y = self.radius * math.sin(self.angle)
        transform = glm.translate(glm.mat4(1.0), glm.vec3(x, y, 0.0))
        self.node.SetTransform(transform)

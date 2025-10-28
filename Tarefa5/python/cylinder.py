from OpenGL.GL import *
from shape import Shape
from grid import Grid
import numpy as np
import math

class Cylinder(Shape):
  def __init__(self, nstack=32, nslice=32):
    # nstack: número de divisões ao longo da altura (eixo Y)
    # nslice: número de divisões ao redor do círculo
    
    grid = Grid(nslice, nstack)
    self.nind = grid.IndexCount()
    
    coord = np.empty(3*grid.VertexCount(), dtype = 'float32')
    normal = np.empty(3*grid.VertexCount(), dtype = 'float32')
    tangent = np.empty(3*grid.VertexCount(), dtype = 'float32')
    texcoord = grid.GetCoords()
    
    nc = 0
    radius = 0.5  # Raio do cilindro
    
    for i in range(0, 2*grid.VertexCount(), 2):
      # texcoord[i] = u (0 a 1 ao redor do círculo)
      # texcoord[i+1] = v (0 a 1 ao longo da altura)
      u = texcoord[i+0]
      v = texcoord[i+1]
      
      # Coordenada cilíndrica
      theta = u * 2 * math.pi  # Ângulo ao redor do círculo
      y = v - 0.5  # Altura: de -0.5 a 0.5 (cilindro de altura 1, centrado na origem)
      
      # Coordenadas 3D
      coord[nc+0] = radius * math.cos(theta)
      coord[nc+1] = y  # Altura do cilindro de -0.5 a 0.5
      coord[nc+2] = radius * math.sin(theta)
      
      # Normal apontando radialmente para fora
      normal[nc+0] = math.cos(theta)
      normal[nc+1] = 0.0
      normal[nc+2] = math.sin(theta)
      
      # Tangente na direção tangencial ao círculo
      tangent[nc+0] = -math.sin(theta)
      tangent[nc+1] = 0.0
      tangent[nc+2] = math.cos(theta)
      
      nc += 3
    
    # create VAO
    self.vao = glGenVertexArrays(1)
    glBindVertexArray(self.vao)
    
    # create buffers
    id = glGenBuffers(5)
    
    # Coordenadas de vértices
    glBindBuffer(GL_ARRAY_BUFFER,id[0])
    glBufferData(GL_ARRAY_BUFFER, coord.nbytes, coord, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)
    
    # Normais
    glBindBuffer(GL_ARRAY_BUFFER,id[1])
    glBufferData(GL_ARRAY_BUFFER, normal.nbytes, normal, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)
    
    # Tangentes
    glBindBuffer(GL_ARRAY_BUFFER,id[2])
    glBufferData(GL_ARRAY_BUFFER, tangent.nbytes, tangent, GL_STATIC_DRAW)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(2)
    
    # Coordenadas de textura
    glBindBuffer(GL_ARRAY_BUFFER,id[3])
    glBufferData(GL_ARRAY_BUFFER, texcoord.nbytes, texcoord, GL_STATIC_DRAW)
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, 0, None) 
    glEnableVertexAttribArray(3)
    
    # create index buffer
    indices = grid.GetIndices()
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,id[4])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

  def Draw(self, st):
    # Desabilitar culling temporariamente para este cilindro devido ao winding order do Grid
    cull_enabled = glIsEnabled(GL_CULL_FACE)
    glDisable(GL_CULL_FACE)
    glBindVertexArray(self.vao)
    glDrawElements(GL_TRIANGLES, self.nind, GL_UNSIGNED_INT, None)
    # Restaurar o estado anterior do culling
    if cull_enabled:
      glEnable(GL_CULL_FACE)


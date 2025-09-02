from OpenGL.GL import *
from shape import Shape
import numpy as np

class Triangle (Shape):
  def __init__ (self):
    coord = np.array([
      -0.5,-0.5,
      0.5,-0.5, 
      0.0, 0.5, 
    ], dtype = 'float32')
    color = np.array([
      255, 0, 0,
      0, 255, 0,
      0, 0, 255
    ], dtype = 'uint8')
    self.vao = glGenVertexArrays(1)
    glBindVertexArray(self.vao)
    id = glGenBuffers(2)
    glBindBuffer(GL_ARRAY_BUFFER,id[0])
    glBufferData(GL_ARRAY_BUFFER,coord.nbytes,coord,GL_STATIC_DRAW)
    glVertexAttribPointer(0,2,GL_FLOAT,GL_FALSE,0,None)
    glEnableVertexAttribArray(0) 
    glBindBuffer(GL_ARRAY_BUFFER,id[1])
    glBufferData(GL_ARRAY_BUFFER,color.nbytes,color,GL_STATIC_DRAW)
    glVertexAttribPointer(1,3,GL_UNSIGNED_BYTE,GL_TRUE,0,None)
    glEnableVertexAttribArray(1) 

  def Draw (self):
    glBindVertexArray(self.vao)
    glDrawArrays(GL_TRIANGLES,0,3)
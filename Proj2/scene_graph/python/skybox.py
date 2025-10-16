from OpenGL.GL import * 
from shape import *
import glm
import numpy as np

class SkyBox (Shape):
  def __init__ (self):
    coords = np.array([
      -1.0,  1.0, -1.0,
      -1.0, -1.0, -1.0,
      1.0, -1.0, -1.0,
      1.0, -1.0, -1.0,
      1.0,  1.0, -1.0,
      -1.0,  1.0, -1.0,

      -1.0, -1.0,  1.0,
      -1.0, -1.0, -1.0,
      -1.0,  1.0, -1.0,
      -1.0,  1.0, -1.0,
      -1.0,  1.0,  1.0,
      -1.0, -1.0,  1.0,

      1.0, -1.0, -1.0,
      1.0, -1.0,  1.0,
      1.0,  1.0,  1.0,
      1.0,  1.0,  1.0,
      1.0,  1.0, -1.0,
      1.0, -1.0, -1.0,

      -1.0, -1.0,  1.0,
      -1.0,  1.0,  1.0,
      1.0,  1.0,  1.0,
      1.0,  1.0,  1.0,
      1.0, -1.0,  1.0,
      -1.0, -1.0,  1.0,

      -1.0,  1.0, -1.0,
      1.0,  1.0, -1.0,
      1.0,  1.0,  1.0,
      1.0,  1.0,  1.0,
      -1.0,  1.0,  1.0,
      -1.0,  1.0, -1.0,

      -1.0, -1.0, -1.0,
      -1.0, -1.0,  1.0,
      1.0, -1.0, -1.0,
      1.0, -1.0, -1.0,
      -1.0, -1.0,  1.0,
      1.0, -1.0,  1.0
    ], dtype='float32')
    # generate per-vertex spherical texcoords from direction
    nverts = coords.size // 3
    texcoords = np.empty(nverts * 2, dtype='float32')
    normals = np.empty(nverts * 3, dtype='float32')
    for i in range(nverts):
      x = coords[3*i+0]
      y = coords[3*i+1]
      z = coords[3*i+2]
      length = max(1e-6, (x*x + y*y + z*z) ** 0.5)
      nx = x / length
      ny = y / length
      nz = z / length
      # inward-facing normal (we see inside faces)
      normals[3*i+0] = -nx
      normals[3*i+1] = -ny
      normals[3*i+2] = -nz
      # equirectangular mapping
      u = (np.arctan2(nz, nx) / (2.0*np.pi)) + 0.5
      v = (np.arcsin(np.clip(ny, -1.0, 1.0)) / np.pi) + 0.5
      texcoords[2*i+0] = u
      texcoords[2*i+1] = v
    
    # create VAO
    self.vao = glGenVertexArrays(1)
    glBindVertexArray(self.vao)
    # create coord, normal, and texcoord buffers
    id = glGenBuffers(3)
    # coords @ location 0
    glBindBuffer(GL_ARRAY_BUFFER,id[0])
    glBufferData(GL_ARRAY_BUFFER,coords.nbytes,coords,GL_STATIC_DRAW)
    glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,0,None)
    glEnableVertexAttribArray(0)
    # normals @ location 1 (dummy)
    glBindBuffer(GL_ARRAY_BUFFER,id[1])
    glBufferData(GL_ARRAY_BUFFER,normals.nbytes,normals,GL_STATIC_DRAW)
    glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,0,None)
    glEnableVertexAttribArray(1)
    # texcoords @ location 3
    glBindBuffer(GL_ARRAY_BUFFER,id[2])
    glBufferData(GL_ARRAY_BUFFER,texcoords.nbytes,texcoords,GL_STATIC_DRAW)
    glVertexAttribPointer(3,2,GL_FLOAT,GL_FALSE,0,None)
    glEnableVertexAttribArray(3)


  def Draw (self, st):
  # draw at camera position
    camera = st.GetCamera()
    origin = glm.vec4(0,0,0,1)
    peye = glm.vec3(glm.inverse(camera.GetViewMatrix()) * origin)
    M = glm.translate(glm.mat4(1),peye)
    st.PushMatrix()
    st.LoadMatrix(M)
    st.LoadMatrices()    # update loaded matrices
    glDepthMask(GL_FALSE)
    # disable culling so we can see inside faces
    glDisable(GL_CULL_FACE)
    glBindVertexArray(self.vao)
    glDrawArrays(GL_TRIANGLES,0,36)
    glEnable(GL_CULL_FACE)
    glDepthMask(GL_TRUE)
    st.PopMatrix()

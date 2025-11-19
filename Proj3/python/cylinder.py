import math
import numpy as np
from OpenGL.GL import *

# Constantes de layout (devem corresponder aos shaders)
ATTRIB_LOC_POSITION = 0
ATTRIB_LOC_NORMAL   = 1
ATTRIB_LOC_TEXCOORD = 3

TWO_PI = 2.0 * math.pi

class Cylinder:
    def __init__(self, nstack = 32, nslice=32):
        self.m_vao = glGenVertexArrays(1)
        self.m_vbos = glGenBuffers(3)
        self.m_ebo = glGenBuffers(1)
        self.m_nindices = 0

        coords = []
        normals = []
        texcoords = []
        indices = []

        # --- 1. Vértices da Parede Lateral ---
        for i in range(nstack + 1):
            y = i / float(nstack)
            for j in range(nslice + 1):
                theta = TWO_PI * j / float(nslice)
                x = math.cos(theta)
                z = math.sin(theta)

                coords.extend([x, y, z])
                normals.extend([x, 0.0, z])
                texcoords.extend([j / float(nslice), y])

        # --- 2. Índices da Parede Lateral ---
        vertices_per_stack = nslice + 1
        for i in range(nstack):
            for j in range(nslice):
                v0 = i * vertices_per_stack + j
                v1 = v0 + 1
                v2 = (i + 1) * vertices_per_stack + j
                v3 = v2 + 1

                indices.extend([v0, v2, v1])
                indices.extend([v1, v2, v3])

        # --- 3. Vértices das Tampas ---
        # Base
        base_center_index = len(coords) // 3
        coords.extend([0.0, 0.0, 0.0])
        normals.extend([0.0, -1.0, 0.0])
        texcoords.extend([0.5, 0.5])

        base_start_index = base_center_index + 1
        for j in range(nslice + 1):
            theta = TWO_PI * j / float(nslice)
            x = math.cos(theta)
            z = math.sin(theta)
            coords.extend([x, 0.0, z])
            normals.extend([0.0, -1.0, 0.0])
            texcoords.extend([x * 0.5 + 0.5, z * 0.5 + 0.5])

        # Topo
        top_center_index = len(coords) // 3
        coords.extend([0.0, 1.0, 0.0])
        normals.extend([0.0, 1.0, 0.0])
        texcoords.extend([0.5, 0.5])

        top_start_index = top_center_index + 1
        for j in range(nslice + 1):
            theta = TWO_PI * j / float(nslice)
            x = math.cos(theta)
            z = math.sin(theta)
            coords.extend([x, 1.0, z])
            normals.extend([0.0, 1.0, 0.0])
            texcoords.extend([x * 0.5 + 0.5, z * 0.5 + 0.5])

        # --- 4. Índices das Tampas ---
        for j in range(nslice):
            # Base (CW)
            indices.extend([base_center_index, base_start_index + j, base_start_index + j + 1])
            # Topo (CCW)
            indices.extend([top_center_index, top_start_index + j + 1, top_start_index + j])

        # --- 5. Configuração do VAO e Buffers ---
        self.m_nindices = len(indices)

        glBindVertexArray(self.m_vao)

        # Buffer de Coordenadas
        glBindBuffer(GL_ARRAY_BUFFER, self.m_vbos[0])
        glBufferData(GL_ARRAY_BUFFER, np.array(coords, dtype=np.float32), GL_STATIC_DRAW)
        glVertexAttribPointer(ATTRIB_LOC_POSITION, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(ATTRIB_LOC_POSITION)

        # Buffer de Normais
        glBindBuffer(GL_ARRAY_BUFFER, self.m_vbos[1])
        glBufferData(GL_ARRAY_BUFFER, np.array(normals, dtype=np.float32), GL_STATIC_DRAW)
        glVertexAttribPointer(ATTRIB_LOC_NORMAL, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(ATTRIB_LOC_NORMAL)

        # Buffer de Coordenadas de Textura
        glBindBuffer(GL_ARRAY_BUFFER, self.m_vbos[2])
        glBufferData(GL_ARRAY_BUFFER, np.array(texcoords, dtype=np.float32), GL_STATIC_DRAW)
        glVertexAttribPointer(ATTRIB_LOC_TEXCOORD, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(ATTRIB_LOC_TEXCOORD)

        # Buffer de Índices
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.m_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array(indices, dtype=np.uint32), GL_STATIC_DRAW)

        # Desvincula
        glBindVertexArray(0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def __del__(self):
        glDeleteVertexArrays(1, [self.m_vao])
        glDeleteBuffers(3, self.m_vbos)
        glDeleteBuffers(1, [self.m_ebo])

    def Draw(self, st):
      # Desabilitar culling temporariamente para este cilindro devido ao winding order do Grid
      cull_enabled = glIsEnabled(GL_CULL_FACE)
      glDisable(GL_CULL_FACE)
      glBindVertexArray(self.m_vao)
      glDrawElements(GL_TRIANGLES, self.m_nindices, GL_UNSIGNED_INT, None)
      # Restaurar o estado anterior do culling
      if cull_enabled:
        glEnable(GL_CULL_FACE)

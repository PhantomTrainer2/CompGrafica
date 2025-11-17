# objmesh.py
from OpenGL.GL import *
from shape import Shape
import numpy as np

class OBJMesh(Shape):
    """
    Loader simples para OBJ triangular com v / vt / vn.
    """
    def __init__(self, filename):
        verts = []
        norms = []
        uvs = []

        positions = []
        normals = []
        texcoords = []

        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:

            for line in f:
                if line.startswith("#") or line.strip() == "":
                    continue
                parts = line.strip().split()
                if parts[0] == "v":
                    verts.append(tuple(map(float, parts[1:4])))
                elif parts[0] == "vt":
                    uvs.append(tuple(map(float, parts[1:3])))
                elif parts[0] == "vn":
                    norms.append(tuple(map(float, parts[1:4])))
                elif parts[0] == "f":
                    for vtx in parts[1:4]:
                        values = vtx.split("/")
                        vi = int(values[0]) - 1
                        ti = int(values[1]) - 1 if len(values) > 1 and values[1] != "" else None
                        ni = int(values[2]) - 1 if len(values) > 2 and values[2] != "" else None

                        positions.append(verts[vi])
                        normals.append(norms[ni] if ni is not None else (0,1,0))
                        texcoords.append(uvs[ti] if ti is not None else (0,0))

        positions = np.array(positions, dtype=np.float32)
        normals   = np.array(normals, dtype=np.float32)
        texcoords = np.array(texcoords, dtype=np.float32)
        tangents  = np.zeros_like(positions, dtype=np.float32)

        self.nvert = len(positions)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        ids = glGenBuffers(4)

        glBindBuffer(GL_ARRAY_BUFFER, ids[0])
        glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_STATIC_DRAW)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,0,None)
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, ids[1])
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,0,None)
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, ids[2])
        glBufferData(GL_ARRAY_BUFFER, tangents.nbytes, tangents, GL_STATIC_DRAW)
        glVertexAttribPointer(2,3,GL_FLOAT,GL_FALSE,0,None)
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, ids[3])
        glBufferData(GL_ARRAY_BUFFER, texcoords.nbytes, texcoords, GL_STATIC_DRAW)
        glVertexAttribPointer(3,2,GL_FLOAT,GL_FALSE,0,None)
        glEnableVertexAttribArray(3)

    def Draw(self, st):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.nvert)

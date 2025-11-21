# objmesh.py
from OpenGL.GL import *
from shape import Shape
import numpy as np

class OBJMesh(Shape):
    """
    Loader simples para OBJ triangular com v / vt / vn e calculo automatico de Tangentes.
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
                    
                    # Triangulação forçada (assume que o OBJ já é triangular)
                    for vtx in parts[1:4]: 
                        values = vtx.split("/")
                        vi = int(values[0]) - 1
                        ti = int(values[1]) - 1 if len(values) > 1 and values[1] != "" else None
                        ni = int(values[2]) - 1 if len(values) > 2 and values[2] != "" else None

                        positions.append(verts[vi])
                        normals.append(norms[ni] if ni is not None else (0,1,0))
                        texcoords.append(uvs[ti] if ti is not None else (0,0))

        # Converte para Numpy Arrays
        positions = np.array(positions, dtype=np.float32)
        normals   = np.array(normals, dtype=np.float32)
        texcoords = np.array(texcoords, dtype=np.float32)
        
        # Inicializa array de tangentes
        tangents  = np.zeros_like(positions, dtype=np.float32)
        
        # ---------------------------------------------------------
        # 2. CÁLCULO DAS TANGENTES
        # ---------------------------------------------------------
        # Como os arrays são "flat" (sopa de triângulos), iteramos a cada 3 vértices
        num_verts = len(positions)
        for i in range(0, num_verts, 3):
            # Pega os 3 vértices do triângulo atual
            p0 = positions[i]
            p1 = positions[i+1]
            p2 = positions[i+2]
            
            # Pega os 3 UVs
            uv0 = texcoords[i]
            uv1 = texcoords[i+1]
            uv2 = texcoords[i+2]

            # Arestas do triângulo (Posição)
            edge1 = p1 - p0
            edge2 = p2 - p0

            # Diferença no UV (Delta UV)
            deltaUV1 = uv1 - uv0
            deltaUV2 = uv2 - uv0

            # Cálculo do determinante
            f = 1.0
            det = (deltaUV1[0] * deltaUV2[1] - deltaUV2[0] * deltaUV1[1])
            
            if abs(det) > 1e-6: # Evita divisão por zero
                f = 1.0 / det
            
            # Fórmula da Tangente
            tx = f * (deltaUV2[1] * edge1[0] - deltaUV1[1] * edge2[0])
            ty = f * (deltaUV2[1] * edge1[1] - deltaUV1[1] * edge2[1])
            tz = f * (deltaUV2[1] * edge1[2] - deltaUV1[1] * edge2[2])
            
            tangent = np.array([tx, ty, tz], dtype=np.float32)
            
            # Normaliza a tangente
            norm_val = np.linalg.norm(tangent)
            if norm_val > 0:
                tangent = tangent / norm_val

            # Aplica a mesma tangente para os 3 vértices do triângulo
            tangents[i]   = tangent
            tangents[i+1] = tangent
            tangents[i+2] = tangent

        # (Opcional) Ortogonalização de Gram-Schmidt para garantir T perpendicular a N
        # Isso melhora a qualidade visual, removendo distorções
        for i in range(num_verts):
            t = tangents[i]
            n = normals[i]
            # T = normalize(T - N * dot(N, T))
            ortho_t = t - n * np.dot(n, t)
            norm_val = np.linalg.norm(ortho_t)
            if norm_val > 0:
                tangents[i] = ortho_t / norm_val

        # ---------------------------------------------------------
        # 3. Configuração OpenGL
        # ---------------------------------------------------------
        self.nvert = len(positions)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        ids = glGenBuffers(4)

        # Location 0: Position
        glBindBuffer(GL_ARRAY_BUFFER, ids[0])
        glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        # Location 1: Normal
        glBindBuffer(GL_ARRAY_BUFFER, ids[1])
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        # Location 2: Tangent (AGORA TEM DADOS REAIS!)
        glBindBuffer(GL_ARRAY_BUFFER, ids[2])
        glBufferData(GL_ARRAY_BUFFER, tangents.nbytes, tangents, GL_STATIC_DRAW)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(2)

        # Location 3: TexCoord
        glBindBuffer(GL_ARRAY_BUFFER, ids[3])
        glBufferData(GL_ARRAY_BUFFER, texcoords.nbytes, texcoords, GL_STATIC_DRAW)
        glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(3)

    def Draw(self, st):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.nvert)

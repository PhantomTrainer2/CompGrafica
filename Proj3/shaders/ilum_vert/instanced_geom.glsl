#version 410 core

layout(triangles) in;
layout(triangle_strip, max_vertices = 48) out;

in VS_OUT {
    vec3 pos;
    vec3 normal;
    vec3 tangent;
    vec2 tex;
} gs_in[];

out GS_OUT {
    vec3 FragPos;
    vec3 Normal;
    vec2 TexCoords;
} gs_out;

uniform mat4 Mvp;
uniform mat4 Mv;
uniform mat4 Mn;
uniform mat4 Mmodel;

uniform int instanceCount;
uniform vec3 instanceOffsets[16];

void main()
{
    for (int i = 0; i < instanceCount; i++)
    {
        for (int v = 0; v < 3; v++)
        {
            vec3 local = gs_in[v].pos + instanceOffsets[i];

            // Corrigido: transformar para espaço do mundo
            vec4 world = Mmodel * vec4(local, 1.0);

            gs_out.FragPos = (Mv * world).xyz;
            gs_out.Normal = normalize(mat3(Mn) * gs_in[v].normal);
            gs_out.TexCoords = gs_in[v].tex;

            // Corrigido: MVP no world pos
            gl_Position = Mvp * world;
            EmitVertex();
        }
        EndPrimitive();
    }
}

#version 410 core

layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec3 aTangent;
layout(location = 3) in vec2 aTex;

out VS_OUT {
    vec3 pos;
    vec3 normal;
    vec3 tangent;
    vec2 tex;
} vs_out;

void main()
{
    vs_out.pos    = aPos;
    vs_out.normal = aNormal;
    vs_out.tangent = aTangent;
    vs_out.tex    = aTex;
}

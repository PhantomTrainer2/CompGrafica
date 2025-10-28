#version 410

layout(location = 0) in vec4 coord;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec3 tangent; // tangent for normal mapping
layout(location = 3) in vec2 texcoord;

uniform mat4 Mv; 
uniform mat4 Mn; 
uniform mat4 Mvp;

out data {
  vec3 veye;
  vec3 neye;
  vec3 teye;
  vec2 texcoord;
} v;

void main (void) 
{
  v.veye = vec3(Mv * coord);
  v.neye = vec3(Mn * vec4(normal, 0.0f)); // normalize per-fragment
  v.teye = vec3(Mn * vec4(tangent, 0.0f));
  v.texcoord = texcoord;
  gl_Position = Mvp * coord; 
}

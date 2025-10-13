#version 410

layout(location = 0) in vec4 coord;
layout(location = 1) in vec3 normal;

uniform mat4 Mv;  // Model-View matrix
uniform mat4 Mn;  // Normal matrix
uniform mat4 Mvp; // Model-View-Projection matrix

// Dados que serão interpolados e enviados ao fragment shader
out data {
  vec3 position_eye;  // Posição do vértice no espaço da câmera
  vec3 normal_eye;    // Normal no espaço da câmera
} v;

void main (void) 
{
  // Transforma a posição do vértice para o espaço da câmera
  v.position_eye = vec3(Mv * coord);
  
  // Transforma a normal para o espaço da câmera
  v.normal_eye = normalize(vec3(Mn * vec4(normal, 0.0)));
  
  // Calcula a posição final do vértice
  gl_Position = Mvp * coord; 
}
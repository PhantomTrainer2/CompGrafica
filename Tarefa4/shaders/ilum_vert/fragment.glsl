#version 410

// Dados interpolados vindos do vertex shader
in data {
  vec3 position_eye;  // Posição do fragmento no espaço da câmera
  vec3 normal_eye;    // Normal no espaço da câmera
} f;

out vec4 outcolor;

// Propriedades da luz
uniform vec4 lpos;  // Posição da luz no espaço da câmera
uniform vec4 lamb;  // Componente ambiente da luz
uniform vec4 ldif;  // Componente difusa da luz
uniform vec4 lspe;  // Componente especular da luz

// Propriedades do material
uniform vec4 mamb;  // Componente ambiente do material
uniform vec4 mdif;  // Componente difusa do material
uniform vec4 mspe;  // Componente especular do material
uniform float mshi; // Brilho especular (shininess)

void main (void)
{
  // Normaliza a normal (pode ter sido desnormalizada pela interpolação)
  vec3 N = normalize(f.normal_eye);
  
  // Calcula o vetor da luz
  vec3 L;
  if (lpos.w == 0.0) {
    // Luz direcional
    L = normalize(vec3(lpos));
  } else {
    // Luz pontual
    L = normalize(vec3(lpos) - f.position_eye);
  }
  
  // Calcula o vetor de visão (da superfície para a câmera)
  vec3 V = normalize(-f.position_eye);
  
  // Componente ambiente
  vec4 ambient = mamb * lamb;
  
  // Componente difusa (Lambertiana)
  float NdotL = max(dot(N, L), 0.0);
  vec4 diffuse = mdif * ldif * NdotL;
  
  // Componente especular (Phong)
  vec4 specular = vec4(0.0);
  if (NdotL > 0.0) {
    vec3 R = normalize(reflect(-L, N));
    float RdotV = max(dot(R, V), 0.0);
    specular = mspe * lspe * pow(RdotV, mshi);
  }
  
  // Cor final: ambiente + difusa + especular
  outcolor = ambient + diffuse + specular;
  outcolor.a = 1.0;  // Alpha = 1 (opaco)
}
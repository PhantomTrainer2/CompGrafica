#version 410

in vec3 veye;
in vec3 neye;

uniform vec4 lpos;  // light pos in eye space
uniform vec4 lamb;
uniform vec4 ldif;
uniform vec4 lspe;

uniform vec4 mamb;
uniform vec4 mdif;
uniform vec4 mspe;
uniform float mshi;
uniform float mopacity;

out vec4 fcolor;

void main (void)
{
  // Normalize interpolated inputs to avoid artifacts from perspective interpolation
  vec3 n = normalize(neye);
  vec3 v = normalize(-veye); // view direction from point to eye in eye space

  vec3 light;
  if (lpos.w == 0) 
    light = normalize(vec3(lpos)); // directional light already in lighting space (eye)
  else 
    light = normalize(vec3(lpos) - veye); // point light vector from point to light

  float ndotl = max(0.0, dot(n, light));
  vec4 color = mamb * lamb + mdif * ldif * ndotl; 

  if (ndotl > 0) {
    // Blinn-Phong half-vector for more stable highlights
    vec3 h = normalize(light + v);
    float ndoth = max(0.0, dot(n, h));
    color += mspe * lspe * pow(ndoth, mshi); 
  }
  
  fcolor = vec4(color.rgb, mopacity);
}
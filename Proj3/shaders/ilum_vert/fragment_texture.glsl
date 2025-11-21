#version 410

in data {
  vec3 veye;
  vec3 neye;
  vec3 teye;
  vec2 texcoord;
} f;

out vec4 color;

uniform sampler2D decal;
uniform sampler2D normalMap; // optional normal map
uniform bool useNormalMap = false;

uniform vec4 lpos;  // light pos in eye space
uniform vec4 lamb;
uniform vec4 ldif;
uniform vec4 lspe;

uniform vec4 mamb;
uniform vec4 mdif;
uniform vec4 mspe;
uniform float mshi;
uniform float mopacity;

void main (void)
{
  // base normal from geometry
  vec3 n = normalize(f.neye);

  // normal mapping (tangent space) if enabled
  if (useNormalMap) {
    vec3 T = normalize(f.teye);
    vec3 N = normalize(n);
    vec3 B = normalize(cross(N, T));
    mat3 TBN = mat3(T, B, N);
    vec3 nMap = texture(normalMap, f.texcoord).xyz * 2.0 - 1.0;
    nMap.y = -nMap.y;
    n = normalize(TBN * nMap);
  }

  vec3 v = normalize(-f.veye);
  vec3 light;
  if (lpos.w == 0)
    light = normalize(vec3(lpos));
  else
    light = normalize(vec3(lpos) - f.veye);

  float ndotl = max(0.0, dot(n, light));
  vec4 lit = mamb * lamb + mdif * ldif * ndotl;
  if (ndotl > 0.0) {
    vec3 h = normalize(light + v);
    float ndoth = max(0.0, dot(n, h));
    lit += mspe * lspe * pow(ndoth, mshi);
  }

  vec4 tex = texture(decal, f.texcoord);
  color = vec4(lit.rgb * tex.rgb, mopacity * tex.a);
}


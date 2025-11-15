#version 410 core

out vec4 FragColor;

in GS_OUT {
    vec3 FragPos;
    vec3 Normal;
    vec2 TexCoords;
} fs_in;

uniform vec4 mamb;
uniform vec4 mdif;
uniform vec4 mspe;
uniform float mshi;
uniform float mopacity;

uniform vec4 lamb;
uniform vec4 ldif;
uniform vec4 lspe;
uniform vec4 lpos;

uniform vec4 cpos;

void main()
{
    vec3 N = normalize(fs_in.Normal);
    vec3 L = normalize(lpos.xyz - fs_in.FragPos);
    vec3 V = normalize(cpos.xyz - fs_in.FragPos);
    vec3 R = reflect(-L, N);

    vec3 ambient = lamb.rgb * mamb.rgb;
    float diff = max(dot(N, L), 0.0);
    vec3 diffuse = diff * ldif.rgb * mdif.rgb;

    float spec = diff > 0.0 ? pow(max(dot(R, V), 0.0), mshi) : 0.0;
    vec3 specular = spec * lspe.rgb * mspe.rgb;

    FragColor = vec4(ambient + diffuse + specular, mopacity);
}

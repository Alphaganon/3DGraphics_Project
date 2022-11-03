#version 330 core

in vec2 frag_tex_coords;
in vec3 w_position, w_normal;

uniform sampler2D diffuse_map;
uniform vec3 light_dir;
uniform vec3 k_d;
uniform vec3 k_s;
uniform vec3 k_a;
uniform float s;
uniform vec3 w_camera_position;

// output fragment color for OpenGL
out vec4 out_color;

void main() {
    vec3 n = normalize(w_normal);
    vec3 v = normalize(w_camera_position);
    vec3 l = normalize(-light_dir);
    out_color = texture(diffuse_map, frag_tex_coords) * vec4(k_d * max(0, dot(n, l)) + k_a + k_s * pow(max(0, dot(reflect(l, n), v)), s), 1);
}
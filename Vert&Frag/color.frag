#version 330 core

// // receiving interpolated color for fragment shader
// in vec3 fragment_color;
// in vec2 frag_tex_coords;

// // output fragment color for OpenGL
// out vec4 out_color;

// uniform sampler2D diffuse_map;

// void main() {
//     out_color = texture(diffuse_map, frag_tex_coords);
// }


uniform sampler2D diffuse_map;
in vec2 frag_tex_coords;
in vec3 w_position, w_normal;   // in world coodinates

// light dir, in world coordinates
uniform vec3 light_dir;

// material properties
uniform vec3 k_d;
uniform vec3 k_a;
uniform vec3 k_s;

// world camera position
uniform vec3 w_camera_position;
uniform float s;
//Creer par moi
vec3 n;
float scal;
float scal2;
vec3 r;
out vec4 out_color;

void main() {
    n = normalize(w_normal);
    r = reflect(-normalize(light_dir), n);
    vec3 v = normalize(w_camera_position - w_position);
    // scal = max(dot(n, normalize(light_dir)), 0);
    // out_color = vec4(k_d*scal, 1);
    scal = max(dot(n, -normalize(light_dir)), 0);
    scal2 = max(dot(r, v), 0);
    out_color = texture(diffuse_map, frag_tex_coords) + vec4(k_a + k_d*scal + k_s*pow(scal2,s), 1);
}

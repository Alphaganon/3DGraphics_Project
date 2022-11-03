#version 330 core

in vec3 position;
in vec3 normal;
in vec2 tex_coord;

uniform mat4 view; 
uniform mat4 projection;

out vec2 frag_tex_coords;
out vec3 w_position, w_normal;

void main() {
    vec4 w_position4 = vec4(position, 1.0);
    gl_Position =  projection * view * w_position4;
    frag_tex_coords = position.xz;
    w_position = w_position4.xyz / w_position4.w;
    w_normal = normal; 
}

#version 330 core

in vec3 position;
in vec3 normal;
in vec2 tex_coord;

uniform mat4 view; 
uniform mat4 projection;
uniform float time;

out vec2 frag_tex_coords;
out vec3 w_position, w_normal;

void main() {
    float y = position.y + cos(5*time * (position.x/257) * (position.z/257))/5;
    vec4 w_position4 = vec4(position.x, y, position.z, 1.0);
    gl_Position =  projection * view * w_position4;
    frag_tex_coords = position.xz;
    w_position = w_position4.xyz/ w_position4.w;
    w_normal = normal; 
}

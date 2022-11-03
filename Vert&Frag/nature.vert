#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
in vec3 position;
in vec3 tex_coord;
in vec3 normal;

// out vec3 w_normal;   // in world coordinates

out vec2 frag_tex_coords;
out vec3 frag_tex_color;

out vec3 w_normal, w_position;

void main() {

    vec4 w_position4 = model * vec4(position, 1.0);
    gl_Position = projection * view * w_position4;
    frag_tex_color = normal;

    frag_tex_coords = tex_coord.xy;

    w_normal = (model * vec4(normal, 0)).xyz;
    gl_Position = projection * view * model * vec4(position, 1);

    w_position = position;
    w_normal = (model * vec4(normal, 0)).xyz;
}
#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texture;
out vec3 frag_tex_coords;

void main() {
    mat4 skybox_view = view;
    skybox_view[3] = vec4(0, 0, 0, view[3].w);
    gl_Position = projection * skybox_view * vec4(position, 1);
    frag_tex_coords = position;
}

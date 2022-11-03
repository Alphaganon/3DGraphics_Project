#version 330 core

uniform sampler2D diffuse_map;
in vec2 frag_tex_coords;
in vec3 w_position, w_normal, frag_tex_color;
uniform vec3 w_camera_position;

out vec4 out_color;

void main() {
    vec3 light_dir = vec3(0, 0, 0);

    vec3 n = normalize(w_normal);
    vec3 l = -light_dir;
    vec3 r = reflect(light_dir, n);
    vec3 v = normalize(w_camera_position - w_position);
    
    vec4 tex = texture(diffuse_map, frag_tex_coords);
    vec4 phong = vec4(vec3(0.5, 0.5, 0.5)
                    +vec3(1, 1, 1) * max(0, dot(n, l))
                    +vec3(1, 1, 1) * pow(max(0, dot(r, v)), 16.0)
                    , 1);

    out_color = tex * phong;
}

#version 330 core
// TODO: complete the loop for TP7 exercise 1

// ---- camera geometry
uniform mat4 projection, view;

// ---- skinning globals and attributes
const int MAX_VERTEX_BONES=4, MAX_BONES=128;
uniform mat4 bone_matrix[MAX_BONES];

// ---- vertex attributes
in vec3 position;
in vec3 normal;
in vec4 bone_ids;
in vec4 bone_weights;
in vec2 tex_coord;

uniform mat4 model;

// ----- interpolated attribute variables to be passed to fragment shader
out vec3 fragment_color;
out vec2 frag_tex_coords;
out vec3 w_position, w_normal; 

void main() {

    // ------ creation of the skinning deformation matrix
    mat4 skin_matrix = mat4(0);  // TODO complete shader here for exercise 1!
     for (int b = 0; b<MAX_VERTEX_BONES; b++) {
         skin_matrix += bone_weights[b] * bone_matrix[int(bone_ids[b])];
     }

    // ------ compute world and normalized eye coordinates of our vertex
    vec4 w_position4 = skin_matrix * vec4(position, 1.0);
    gl_Position = projection * view * w_position4;

    frag_tex_coords = tex_coord.xy;
     w_position = w_position4.xyz / w_position4.w;
    
    mat3 nit_matrix = transpose(inverse(mat3(model)));
    w_normal = normalize(nit_matrix * normal);
}


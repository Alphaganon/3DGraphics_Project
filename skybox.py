#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

import sys                          # for system arguments
import os
from math import exp, cos, sin, pi
from turtle import position

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
import assimpcy                     # 3D resource loader

from core import Shader, Mesh, Node, Viewer, VertexArray, Texture
from transform import translate, rotate, scale


from PIL import Image               # load images for textures
from itertools import cycle

class TexturedCubeMesh(Mesh):
    """ Simple cube textured object """
    def __init__(self, shader, texture, attributes, uniforms=None, index=None):
        super().__init__(shader, attributes, uniforms, index)
        loc = GL.glGetUniformLocation(shader.glid, 'skybox')
        self.texture = texture

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        GL.glUseProgram(self.shader.glid)
        self.shader.set_uniforms({**self.uniforms, **uniforms})
        self.vertex_array.execute(primitives)

class CubeTexture:
    """ Helper class to create and automatically destroy cube textures """
    def __init__(self, tex_files, wrap_mode=GL.GL_REPEAT, min_filter=GL.GL_LINEAR,
                 mag_filter=GL.GL_LINEAR_MIPMAP_LINEAR):
        self.glid = GL.glGenTextures(1)
        try:
            # imports image as a numpy array in exactly right format
            GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.glid)
            for i, tex_file in enumerate(tex_files):
                tex = np.asarray(Image.open(tex_file).convert('RGBA'))
                GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL.GL_RGBA, tex.shape[1],
                                tex.shape[0], 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, tex)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, wrap_mode)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, wrap_mode)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, min_filter)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, mag_filter)
            GL.glGenerateMipmap(GL.GL_TEXTURE_CUBE_MAP)
            message = 'Loaded texture %s\t(%s, %s, %s, %s)'
            print(message % (tex_files, tex.shape, wrap_mode, min_filter, mag_filter))
        except FileNotFoundError:
            print("ERROR: unable to load texture file %s" % tex_files)

    def __del__(self):  # delete GL texture from GPU when object dies
        GL.glDeleteTextures(self.glid)

class Skybox(TexturedCubeMesh):
    def __init__(self, shader, position, index, normals):
        self.shader = shader
        self.position = np.array(position, np.float32)
        self.index = np.array(index, np.uint32)
        self.normals = normals
        self.light_dir = (0,1,1)
        self.k_d = (0.2, 0.2, 0.2)
        self.k_s = (1, 1, 1)
        self.k_a = (0, 0, 0)
        self.s = 1.
        attributes = dict(position=self.position, normal=self.normals)
        
        self.textures = []
        self.textures.append("Resources/right.png")
        self.textures.append("Resources/left.png")
        self.textures.append("Resources/top.png")
        self.textures.append("Resources/bottom.png")
        self.textures.append("Resources/back.png")
        self.textures.append("Resources/front.png")
        
        super().__init__(shader, CubeTexture(self.textures), attributes, index=self.index)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        super().draw(primitives=primitives, k_d=self.k_d, k_s=self.k_s, k_a=self.k_a, s=self.s, light_dir=self.light_dir, **uniforms)


def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts"""

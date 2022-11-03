#!/usr/bin/env python3

# Python built-in modules
from math import pi, acos, sqrt
from gettext import translation
from math import floor
import sys
from turtle import position
from unittest import skip
from anyio import current_time

# External, non built-in modules
import numpy as np
from sympy import false, true                  # all matrix manipulations & OpenGL args

from transform import identity, sincos, quaternion, quaternion_from_euler, vec, scale, rotate, translate, lerp, lookat, perspective
from core import Shader, Mesh, Viewer, load, Node, Camera
from animation import KeyFrameControlNode, Skinned
from texture import Texture, Textured
from skybox import Skybox

from PIL import Image               # load texture maps
import OpenGL.GL as GL              # standard Python OpenGL wrapper
from itertools import cycle
import glfw

# --------------Terrain class -----------------------------------------------
class Terrain(Mesh):
    """Class for drawing the generated terrain"""

    def __init__(self, shader, position, index, normals):
        self.shader = shader
        self.position = np.array(position, np.float32)
        self.index = np.array(index, np.uint32)
        self.normals = normals
        self.light_dir = (0,1,0)
        self.k_d = (0.2, 0.2, 0.2)
        self.k_s = (1, 1, 1)
        self.k_a = (0, 0, 0)
        self.s = .2
        attributes = dict(position=self.position, normal=self.normals)
        super().__init__(shader=shader, attributes=attributes, index=self.index)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        super().draw(primitives=primitives, k_d=self.k_d, k_s=self.k_s, k_a=self.k_a, s=self.s, light_dir=self.light_dir, **uniforms)


class Water(Mesh) :
    """Class for drawing the generated water"""

    def __init__(self, shader, position, index, normals):
        self.shader = shader
        self.position = np.array(position, np.float32)
        self.index = np.array(index, np.uint32)
        self.normals = np.array(normals, np.float32)
        self.light_dir = (0,1,0)
        self.k_d = (0.2, 0.2, 0.2)
        self.k_s = (1, 1, 1)
        self.k_a = (0, 0, 0)
        self.s = 1.
        attributes = dict(position=self.position, normal=self.normals)
        super().__init__(shader=shader, attributes=attributes, index=self.index)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        super().draw(primitives=primitives, k_d=self.k_d, k_s=self.k_s, k_a=self.k_a, s=self.s, light_dir=self.light_dir, time=glfw.get_time(), **uniforms)

class Knight(Node) :
    """Class for drawing a Knight entity"""

    def __init__(self, height) :
        self.shader = Shader("Vert&Frag/skinning.vert", "Vert&Frag/color.frag")
        self.height = height
        self.position = [30, self.height[30][30][0], 30]
        self.angle = 0
        self.angle_speed = 0
        self.anim_time = 0
        super().__init__(transform=translate(y=self.position[1])@scale(0.01))
        self.attack1 = load("FantasyCharacters/Knight/Knight_attack_1.fbx", self.shader, light_dir = (0.8, 0, -1), k_d=(.3, .3, .3), s=10)
        self.attack2 = load("FantasyCharacters/Knight/Knight_attack_2.fbx", self.shader, light_dir = (0.8, 0, -1), k_d=(.3, .3, .3), s=10)        
        self.idle = load("FantasyCharacters/Knight/Knight_Idle.fbx", self.shader, light_dir = (.8, 0, -1), k_d=(.3, .3, .3), s=10)
        self.pose = load("FantasyCharacters/Knight/Knight_Pose.fbx", self.shader, light_dir = (0.8, 0, -1), k_d=(.3, .3, .3), s=10)
        self.run = load("FantasyCharacters/Knight/Knight_run.fbx", self.shader, light_dir = (.8, 0, -1), k_d=(.3, .3, .3), s=10)
        self.state = 5
        self.periods = [1, 1, 1, 4, 0.6, 8, 1, 2, 1]
        self.add(*self.idle)

    def remove(self, child):
        self.children.remove(child)

    def update(self, period, delta):
        self.angle += delta*self.angle_speed
        if self.state == 8 :
            self.position[0] += delta*5*sincos(self.angle)[1]
            self.position[2] -= delta*5*sincos(self.angle)[0]
            if (floor(self.position[2])+1-self.position[0]<self.position[2]) :
                p1 = (floor(self.position[0]), self.height[floor(self.position[0])][floor(self.position[2])+1][0], floor(self.position[2])+1)
                p2 = (floor(self.position[0]), self.height[floor(self.position[0])][floor(self.position[2])][0], floor(self.position[2]))
                p3 = (floor(self.position[0])+1, self.height[floor(self.position[0])+1][floor(self.position[2])][0], floor(self.position[2]))
                
            else :
                p1 = (floor(self.position[0]), self.height[floor(self.position[0])][floor(self.position[2])+1][0], floor(self.position[2])+1)
                p2 = (floor(self.position[0])+1, self.height[floor(self.position[0])+1][floor(self.position[2])][0], floor(self.position[2]))
                p3 = (floor(self.position[0])+1, self.height[floor(self.position[0])+1][floor(self.position[2])+1][0], floor(self.position[2])+1)
            a = (p2[1]-p1[1])*(p3[2]-p1[2]) - (p3[1]-p1[1])*(p2[2]-p1[2])
            b = (p2[2]-p1[2])*(p3[0]-p1[0]) - (p3[2]-p1[2])*(p2[0]-p1[0])
            c = (p2[0]-p1[0])*(p3[1]-p1[1]) - (p3[0]-p1[0])*(p2[1]-p1[1])
            d = -(a*p1[0] + b*p1[1] + c*p1[2])
            y = (-d - a*self.position[0] - c*self.position[2])/b
            self.position[1] = y
        if self.state == 0:
            if (glfw.get_time() - self.anim_time) - self.periods[0] >= 0.0001:
                self.state = 5
                self.remove(*self.attack1)
                self.add(*self.idle)
        if self.state == 1:
            if (glfw.get_time() - self.anim_time) - self.periods[1] >= 0.0001:
                self.state = 5
                self.remove(*self.attack2)
                self.add(*self.idle)
        self.transform = translate(self.position)@rotate((0, 1, 0), self.angle + 90)@scale(0.01)
        for child in self.children:
            child.update(self.periods[self.state], delta)


    def key_handler(self, key, action):
        if key == glfw.KEY_UP and (action == glfw.PRESS or action == glfw.REPEAT):
            if self.state != 8:
                self.state = 8
                self.remove(*self.idle)
                self.add(*self.run)

        if key == glfw.KEY_UP and action == glfw.RELEASE :
            self.state = 5
            self.remove(*self.run)
            self.add(*self.idle)

        if key == glfw.KEY_LEFT and (action == glfw.PRESS or action == glfw.REPEAT) :
            self.angle_speed = 75

        if key == glfw.KEY_RIGHT and (action == glfw.PRESS or action == glfw.REPEAT) :
            self.angle_speed = -75

        if (key == glfw.KEY_LEFT or key == glfw.KEY_RIGHT) and action == glfw.RELEASE :
            self.angle_speed = 0

        if key == glfw.KEY_F3 and action == glfw.RELEASE:
            print(self.position)

        if key == glfw.KEY_SPACE and action == glfw.PRESS :
            if self.state != 0 :
                self.anim_time = glfw.get_time()
                self.state = 0
                self.remove(*self.idle)
                self.add(*self.attack1)

        if key == glfw.KEY_U and action == glfw.PRESS :
            if self.state != 1 :
                self.anim_time = glfw.get_time()
                self.state = 1
                self.remove(*self.idle)
                self.add(*self.attack2)

        super().key_handler(key, action)

class Golem(Node) :
    """Class for drawing a golem entity"""

    def __init__(self, height, x, z, knight) :
        self.shader = Shader("Vert&Frag/skinning.vert", "Vert&Frag/color.frag")
        self.height = height
        self.position = [x, self.height[x][z][0], z]
        self.knight = knight
        self.angle = 0
        self.dead = false
        super().__init__(transform=translate(self.position)@scale(0.05))
        self.death = load("FantasyCharacters/Golem/Golem_death.fbx", self.shader, light_dir = (0.8, 0, -1), k_d=(.3, .3, .3), s=100)
        self.idle = load("FantasyCharacters/Golem/Golem_idle.fbx", self.shader, light_dir = (0.8, 0, -1), k_d=(.3, .3, .3), s=100)
        self.stun = load("FantasyCharacters/Golem/Golem_stun.fbx", self.shader, light_dir = (0.8, 0, -1), k_d=(.3, .3, .3), s=100)
        self.state = 4
        self.periods = [1.7, 1.8, 1.3, 4, 2.7, 2, 1, 0.7, 2.65, 1.3]
        self.add(*self.idle)

    def remove(self, child):
        self.children.remove(child)

    def update(self, period, delta):
        tan = sqrt((self.knight.position[0] - self.position[0])**2 + (self.knight.position[2] - self.position[2])**2)
        dir = [(self.knight.position[0] - self.position[0])/tan, (self.knight.position[2] - self.position[2])/tan]
        if dir[1] < 0 :
            self.angle = 180*acos(dir[0])/pi
        else :
            self.angle = -180*acos(dir[0])/pi
        if np.linalg.norm(np.array(self.position) - np.array(self.knight.position)) < 5:
            if self.knight.state == 1:
                if self.state == 4:
                    self.state = 8
                    self.remove(*self.idle)
                    self.add(*self.stun)
            if self.state == 8 and self.dead == false:
                if self.knight.state == 0:
                    self.state = 3
            if self.state == 3 and self.dead == false:
                self.state = 0
                self.dead = true
                self.remove(*self.stun)
                self.add(*self.death)
        self.transform=translate(self.position)@rotate((0, 1, 0), self.angle + 90)@scale(0.05)       

        for child in self.children:
            if self.dead:
                child.update(1000, delta)
            else :
                child.update(self.periods[self.state], delta)

class Player(Node):
    """Class for a player character"""

    def __init__(self, knight):
        super().__init__()
        self.knight = knight
        self.add(knight)
        self.angle = knight.angle

    def update(self, period, delta):
        for child in self.children:
            child.update(self.knight.periods[self.knight.state], delta)
        self.angle = self.knight.angle
        super().update(period, delta)

class Tree(Node) :
    """Class for drawing a tree entity"""

    def __init__(self, x, y, z, texture) :
        self.texture = texture
        self.position = (x, y, z)
        self.transform = translate(self.position) @ rotate((0,1,0),90) @ scale(0.5)
        super().__init__(transform=self.transform)
        self.add(*self.texture)

# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    terrain_height = np.asarray_chkfinite(Image.open("Resources/hmm.png"))/5
    
    viewer = Viewer()
    
    points = []
    water = []
    index = []
    normals = []
    water_normals = []
    for i in range(-int(terrain_height.shape[0]/2), int(terrain_height.shape[0]/2)):
        for j in range(-int(terrain_height.shape[1]/2), int(terrain_height.shape[1]/2)):
            points.append((i, terrain_height[i][j][0], j))
            normals.append((terrain_height[i-1][j][0]-terrain_height[i+1][j][0], 2, terrain_height[i][j-1][0]-terrain_height[i][j+1][0]))
            water.append((i, 2, j))
            water_normals.append((0, 1, 0))

    for i in range(terrain_height.shape[0]-1) :
        for j in range(terrain_height.shape[1]-1) :
            index.append((i + j*terrain_height.shape[0], i+j*terrain_height.shape[0]+1, i+1+(j+1)*terrain_height.shape[0]))
            index.append((i+1+(j+1)*terrain_height.shape[0], i+(j+1)*terrain_height.shape[0], i + j*terrain_height.shape[0]))

    terrain_shader = Shader("Vert&Frag/terrain.vert", "Vert&Frag/terrain.frag")
    terrain_tex = Texture("Resources/grass.png")
    terrain = Terrain(terrain_shader, position=points, index=index, normals=normals)
    textured_terrain = Textured(terrain, diffuse_map=terrain_tex)
    viewer.add(textured_terrain)

    water_tex = Texture("Resources/water.jpeg")
    water_shader = Shader("Vert&Frag/water.vert", "Vert&Frag/terrain.frag")
    water_terrain = Water(water_shader, position=water, index=index, normals=water_normals)
    textured_water = Textured(water_terrain, diffuse_map=water_tex)
    viewer.add(textured_water)
    
    shader_skybox = Shader("Vert&Frag/skybox.vert", "Vert&Frag/skybox.frag")

    a = 150
    b = -150

    position = np.array(((a, a, a), (a, a, b), (a, b, a), (a, b, b),
                            (b, a, a), (b, a, b), (b, b, a), (b, b, b)), 'f')

    index_sky = np.array((5, 7, 3,
                            3, 1, 5,

                            6, 7, 5,
                            5, 4, 6,

                            3, 2, 0,
                            0, 1, 3,

                            6, 4, 0,
                            0, 2, 6,

                            5, 1, 0,
                            0, 4, 5,

                            7, 6, 3,
                            3, 6, 2), 'f')
    viewer.add(Skybox(shader_skybox, position, index_sky, normals=None))

    knight = Knight(terrain_height)

    player = Player(knight)

    golem = Golem(terrain_height, 55, -28, knight)

    entities = [golem]

    viewer.set_entities(entities)

    viewer.add(player)

    camera = Camera(player)
    viewer.set_camera(camera)
    viewer.add(camera)
    
    nature_shader = Shader("Vert&Frag/nature.vert", "Vert&Frag/nature.frag")

    tree_texture_1 = load("FantasyWorld/NatureAssets/Tree_01.FBX", nature_shader)
    tree_texture_2 = load("FantasyWorld/NatureAssets/Tree_02.FBX", nature_shader)
    tree_texture_3 = load("FantasyWorld/NatureAssets/Tree_03.FBX", nature_shader)
    tree_texture_4 = load("FantasyWorld/NatureAssets/Tree_04.FBX", nature_shader)
    tree_texture_5 = load("FantasyWorld/NatureAssets/Tree_05.FBX", nature_shader)
    mother_tree_texture = load("FantasyWorld/NatureAssets/Mother_Tree.FBX", nature_shader)
    
    
    tree1 = Tree(52, terrain_height[52][34][0], 34, tree_texture_1)
    tree2 = Tree(57, terrain_height[57][65][0], 65, tree_texture_2)
    tree3 = Tree(80, terrain_height[80][72][0], 72, tree_texture_2)
    tree4 = Tree(85, terrain_height[85][52][0], 52, tree_texture_3)
    tree5 = Tree(101, terrain_height[101][36][0], 36, tree_texture_5)
    tree6 = Tree(101, terrain_height[101][8][0], 8, tree_texture_2)
    tree7 = Tree(73, terrain_height[73][0][0], 0, tree_texture_3)
    tree8 = Tree(69, terrain_height[69][-31][0], -31, tree_texture_4)
    tree9 = Tree(67, terrain_height[67][-52][0], -52, tree_texture_1)
    tree10 = Tree(23, terrain_height[23][-69][0], -69, tree_texture_4)
    tree11 = Tree(-3, terrain_height[-3][-71][0], -71, tree_texture_1)
    tree12 = Tree(-43, terrain_height[-43][-30][0], -30, tree_texture_1)
    tree13 = Tree(-48, terrain_height[-48][-4][0], -4, tree_texture_5)
    tree14 = Tree(-33, terrain_height[-33][33][0], 33, tree_texture_3)
    tree15 = Tree(0, terrain_height[0][58][0], 58, tree_texture_2)
    tree16 = Tree(21, terrain_height[21][45][0], 45, tree_texture_4)
    tree17 = Tree(45, terrain_height[45][73][0], 73, tree_texture_4)
    mother_tree = Tree(73, terrain_height[73][65][0]-10, 65, mother_tree_texture)

    viewer.add(tree1, tree2, tree3, tree4, tree5, tree6, tree7, tree8, tree9, tree10, tree11, tree12, tree13, tree14, tree15, tree16, tree17, mother_tree,)

    print("\nBonjour et bienvenue sur notre animation 3D !\n")
    print("Vous allez pouvoir vous aventurer et découvrir notre monde grâce aux touches directionnelles du clavier \n")
    print("Vous pourrez également effectuer des attaques grâce à la touche espace et donner des coups critiques pour stun vos adversaires grâce à la touche u\n")
    print("Petit conseil : Les golems sont résistants et commencer par une simple attaque risque de ne pas avoir beaucoup d'effet...\n")
    print("(Veuillez bien attendre la fin de chaque animation d'attaque ou de coup critique avant de commencer une autre action d'attaque ou de déplacement)\n")
    print("Bonne aventure !")

    # start rendering loop
    viewer.run()

if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped

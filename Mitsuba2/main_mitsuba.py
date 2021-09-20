import os
import numpy as np
import mitsuba
import matplotlib
import matplotlib.pyplot as plt

# Set the desired mitsuba variant
mitsuba.set_variant('scalar_spectral_polarized')

from mitsuba.core import Bitmap, Struct, Thread
from mitsuba.core.xml import load_file
from mitsuba.render import register_bsdf

# from BSDF.diff_pol_bsdf import MyDiffuseBSDF
from Mitsuba2.core.Renderer import Renderer

if __name__ == '__main__':
    """
    out_path = '/home/ubuntu/PycharmProjects/MistubaRenderer/Mitsuba2/cup/'
    # bmp = Bitmap(out_path + ".exr")
    scene = '/home/ubuntu/renders/cup/cup_scene'
    scenes = [scene + '_filtered.xml'] * 4 + [scene + '.xml']
    camera_file = '/home/ubuntu/renders/cup/output/bop_data/train_pbr/000000/scene_camera.json'
    res_x, res_y = 512, 512
    spp = 256
    RenderObj = Renderer(output_dir=out_path, scene=scene, camera_file=camera_file, res_x=res_x, res_y=res_y,
                         spp=spp)

    RenderObj.render_all()
    """
    out_path = '/home/arturo/PycharmProjects/MistubaRenderer/Mitsuba2/material-testball'
    # bmp = Bitmap(out_path + ".exr")
    scene = '/home/arturo/PycharmProjects/MistubaRenderer/Mitsuba2/material-testball/scene'
    scenes = [scene + '_filtered.xml'] * 4 + [scene + '.xml']
    camera_file = '/home/ubuntu/renders/cup/output/bop_data/train_pbr/000000/scene_camera.json'
    res_x, res_y = 512, 512
    spp = 256
    RenderObj = Renderer(output_dir=out_path, scene=scene, camera_file=camera_file, res_x=res_x, res_y=res_y,
                         spp=spp)

    RenderObj.render_all()
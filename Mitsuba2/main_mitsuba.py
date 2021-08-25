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
    out_path = '/home/ubuntu/PycharmProjects/MistubaRenderer/Mitsuba2/new_test/test_scene_'
    # bmp = Bitmap(out_path + ".exr")
    scene = '/home/ubuntu/PycharmProjects/MistubaRenderer/Mitsuba2/new_test/example2'
    scenes = [scene + '_filtered.xml'] * 4 + [scene + '.xml']
    camera_file = "/home/ubuntu/PycharmProjects/MistubaRenderer/examples/datasets/bop_object_on_surface_sampling/output/bop_data/lm/train_pbr/000000/scene_camera.json"

    RenderObj = Renderer(output_path=out_path, scene=scene, camera_file=camera_file)

    RenderObj.render_all()


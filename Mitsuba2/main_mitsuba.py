import os
import mitsuba

# Set the desired mitsuba variant
mitsuba.set_variant('scalar_spectral_polarized')

from mitsuba.core import Bitmap, Struct, Thread
from mitsuba.core.xml import load_file
from mitsuba.render import register_bsdf

# from BSDF.diff_pol_bsdf import MyDiffuseBSDF
from Mitsuba2.core.Renderer import Renderer

if __name__ == '__main__':
    out_path = '/home/arturo/renders/cup/mitsuba_cup/'
    # bmp = Bitmap(out_path + ".exr")
    scene = '/home/arturo/PycharmProjects/MistubaRenderer/Mitsuba2/cup/cup'
    scenes = [scene + '_filtered.xml'] * 4 + [scene + '.xml']
    camera_file = '/home/arturo/renders/cup/output/bop_data/train_pbr/000000/scene_camera.json'
    floor_textures = [
        "/home/arturo/PycharmProjects/MistubaRenderer/resources/cctextures/Marble023/Marble023_2K_Color.jpg",
        "/home/arturo/PycharmProjects/MistubaRenderer/resources/cctextures/PavingStones001/PavingStones001_2K_Color.jpg",
        "/home/arturo/PycharmProjects/MistubaRenderer/resources/cctextures/Tiles016/Tiles016_2K_Color.jpg",
        "/home/arturo/PycharmProjects/MistubaRenderer/resources/cctextures/Wood001/Wood001_2K_Color.jpg"]
    res_x, res_y = 612, 512
    spp = 1024
    RenderObj = Renderer(output_dir=out_path, scene=scene, camera_file=camera_file, res_x=res_x, res_y=res_y,
                         spp=spp, floor_textures=floor_textures)

    # RenderObj.render_all_one_pose(out_path)
    RenderObj.render_all_images()
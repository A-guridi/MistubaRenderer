import os
import mitsuba

# Set the desired mitsuba variant
mitsuba.set_variant('scalar_spectral_polarized')

from core.Renderer import Renderer

if __name__ == '__main__':
    out_path = '/home/arturo/renders/glass/mitsuba_glass/'
    # bmp = Bitmap(out_path + ".exr")
    scene = '/home/arturo/PycharmProjects/MistubaRenderer/Mitsuba2/glass/glass'
    camera_file = '/home/arturo/renders/glass/output/bop_data/train_pbr/000000/scene_camera.json'
    floor_textures = [
        "/home/arturo/PycharmProjects/MistubaRenderer/resources/cctextures/Marble023/Marble023_2K_Color.jpg",
        "/home/arturo/PycharmProjects/MistubaRenderer/resources/cctextures/PavingStones001/PavingStones001_2K_Color.jpg",
        "/home/arturo/PycharmProjects/MistubaRenderer/resources/cctextures/Tiles016/Tiles016_2K_Color.jpg",
        "/home/arturo/PycharmProjects/MistubaRenderer/resources/cctextures/Wood001/Wood001_2K_Color.jpg"]
    res_x, res_y = 612, 512
    spp = 256
    starting_number = 217
    RenderObj = Renderer(output_dir=out_path, scene=scene, camera_file=camera_file, res_x=res_x, res_y=res_y,
                         spp=spp, floor_textures=floor_textures, starting_number=starting_number)

    # RenderObj.render_all_one_pose(out_path)
    RenderObj.render_all_images()

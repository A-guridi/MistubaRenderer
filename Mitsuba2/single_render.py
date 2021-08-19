import os
import numpy as np
import mitsuba
import matplotlib
import matplotlib.pyplot as plt
import json

# Set the desired mitsuba variant
mitsuba.set_variant('scalar_spectral_polarized')

from mitsuba.core import Bitmap, Struct, Thread
from mitsuba.core.xml import load_file
from mitsuba.render import register_bsdf


# from BSDF.diff_pol_bsdf import MyDiffuseBSDF

def render_stokes_images(p_bitmap, outpath):
    # note that for rendering meaninful stokes parameters, the filter should be removed from the .xml file
    array = np.array(p_bitmap).astype('float32')  # Matplotlib doesn't support saving of 16bit images
    # Channels 0-3: RGBA normal image
    rgba = array[:, :, :4]

    # Save normal image. Here, we apply the most simple form of tonemapping + clipping
    plt.imsave(f"{outpath}_s0.jpg", np.clip(rgba ** (1 / 2.2), 0, 1))

    # Channels 4-6:   S0 same as normal, s0 = intensity
    s0 = array[:, :, 4:7]
    # Channels 7-9:   S1 (written as RGB)
    s1 = array[:, :, 7:10]
    # Channels 10-12: S2 (written as RGB)
    s2 = array[:, :, 10:13]
    # Channels 13-15: S3 (written as RGB)
    s3 = array[:, :, 13:]

    # S1 - S3 encode positive and negative values, so as an example we just write
    # out the "R" channels using a colormap and some arbitrary scale.
    vmin = -0.01
    vmax = 0.01
    plt.imsave(f"{outpath}_s1.jpg", s1[:, :, 0], cmap='turbo', vmin=vmin, vmax=vmax)
    plt.imsave(f"{outpath}_s2.jpg", s2[:, :, 0], cmap='turbo', vmin=vmin, vmax=vmax)
    plt.imsave(f"{outpath}_s3.jpg", s3[:, :, 0], cmap='gray', vmin=vmin * 0.1, vmax=vmax * 0.1)

    # AOLP and DOLP calculation

    dolp = np.sqrt(s1 ** 2 + s2 ** 2) / s0  # dolp=sqrt(s1**2+s2**2)/s0
    aolp = 0.5 * np.arctan(s1 / (s2 + 1e-10))  # aolp =0.5*arctan(s1/s2)

    plt.imsave(f"{outpath}_dolp.jpg", dolp[:, :, 0], cmap='Greys', vmin=vmin * 10, vmax=vmax * 10)
    plt.imsave(f"{outpath}_aolp.jpg", aolp[:, :, 0], cmap='Greys', vmin=vmin * 10, vmax=vmax * 10)


def get_camera_angles(cam_file):
    cam_file = os.path.abspath(cam_file)
    with open(cam_file, 'r') as cfile:
        cam = json.load(cfile)
    camR = cam["0"]["cam_R_w2c"]
    camT = cam["0"]["cam_t_w2c"]
    x_rot = [str(c) for c in camR[0:3]] + [str(camT[0])]
    y_rot = [str(c) for c in camR[3:6]] + [str(camT[1])]
    z_rot = [str(c) for c in camR[6:]] + [str(camT[2])]
    rot_mat = x_rot + y_rot + z_rot + ["0", "0", "0", "1"]
    rot_string = ""
    for ele in rot_mat:
        rot_string += ele + " "
    return rot_string


def render_scene(outpath, scene, filter_angle=None, camera_file=None):
    """
    Function to render a scene
    :param outpath: the output folder where the images will be sotred
    :param scene: the .xml file where the scene is to be rendered
    :param filter_angle: the polarizing angle of the filter. If None, the renderer will generate instead the 4 stokes
                        parameters and the dolp and aolp
    :return: saves a .jpg image for the renderer, if filter angle is None, it generates 6 .jpg + 1 .exr image files
   """
    # Add the scene directory to the FileResolver's search path
    Thread.thread().file_resolver().append(os.path.dirname(scene))

    if filter_angle is None:
        # for the case where we have no polarizing filter
        stokes = True
        outpath += "stokes"
        filter_angle = 0  # this is just a dummy angle for calling the function, but it wont be used in the rendering
    else:
        stokes = False
        outpath += str(int(filter_angle))

    # Load the actual scene
    res_x = 1080
    res_y = 720
    spp = 121
    # load the axes of camera rotation
    rot_mat = get_camera_angles(camera_file)
    scene = load_file(scene, filter_angle=filter_angle, resx=res_x, resy=res_y, spp=spp, rot_matrix=rot_mat)
    # Call the scene's integrator to render the loaded scene
    scene.integrator().render(scene, scene.sensors()[0])

    # After rendering, the rendered data is stored in the film
    film = scene.sensors()[0].film()

    if stokes:
        # Write out rendering as high dynamic range OpenEXR file
        film.set_destination_file(outpath + ".exr")
        film.develop()
        bmp = Bitmap(outpath + ".exr")
        # render all the stokes parameters and the aolp and dolp
        render_stokes_images(bmp, outpath)

    else:
        bmp = film.bitmap(raw=True)
        bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write(outpath + ".jpg")

        # plot out the rendered image
        # plt.imshow(outpath + ".jpg")
        # plt.show()

        # Get linear pixel values as a numpy array for further processing
        bmp_linear_rgb = bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)
        image_np = np.array(bmp_linear_rgb)
        print(image_np.shape)


if __name__ == '__main__':
    out_path = '/home/ubuntu/PycharmProjects/MistubaRenderer/Mitsuba2/test_blender/test_scene_'
    # bmp = Bitmap(out_path + ".exr")
    scene = '/home/ubuntu/PycharmProjects/MistubaRenderer/Mitsuba2/test_blender/example'
    scenes = [scene + '_filtered.xml'] * 4 + [scene + '.xml']
    camera_file = "C:/Users/Arturo/PycharmProjects/MistubaRenderer/examples/datasets/bop_object_on_surface_sampling/out/bop_data/lm/train_pbr/000000/scene_camera.json"
    angles = [0.0, 45.0, 90.0, 135.0, None]

    # uncomment the loop for full render
    for sc, angle in zip(scenes, angles):
        render_scene(out_path, sc, angle, camera_file)
    # uncomment this one for rendering only the stokes parameters given an existing .exr file
    # render_stokes_images(Bitmap(out_path + "stokes.exr"), out_path+"stokes")

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

def render_scene():
    # register the custom bsdf
    # register_bsdf("mydiffusebsdf", lambda props: MyDiffuseBSDF(props))

    # Absolute or relative path to the XML file
    filename = '/home/ubuntu/PycharmProjects/MistubaRenderer/material-testball/scene.xml'

    # Add the scene directory to the FileResolver's search path
    Thread.thread().file_resolver().append(os.path.dirname(filename))

    # Load the actual scene
    filter_angle = 0  # the polarizing filter angle
    scene = load_file(filename, filter_angle=filter_angle)

    # Call the scene's integrator to render the loaded scene
    scene.integrator().render(scene, scene.sensors()[0])

    # After rendering, the rendered data is stored in the film
    film = scene.sensors()[0].film()

    # Write out rendering as high dynamic range OpenEXR file
    out_path = '/home/ubuntu/PycharmProjects/MistubaRenderer/material-testball/testball_stokes' + str(filter_angle)

    film.set_destination_file(out_path + ".exr")
    film.develop()

    # Write out a tonemapped JPG of the same rendering
    stokes = True
    bmp = film.bitmap(raw=True)
    images = bmp.split()
    print(len(images))
    height = images[0][1].height()
    width = images[0][1].width()

    image = images[0][1]
    image.accumulate(images[1][1])
    image.accumulate(images[2][1])
    image.accumulate(images[3][1])
    image.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write(out_path + f"original.jpg")
    if stokes:
        image = images[4][1]
        image.convert(Bitmap.PixelFormat.Y, Struct.Type.UInt8, srgb_gamma=True).write(out_path + f"{0}.jpg")
        for i in range(5, 17, 4):
            image = images[i][1]
            image.accumulate(images[i + 1][1])
            image.accumulate(images[i + 2][1])
            image.accumulate(images[i + 3][1])
            image.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write(out_path + f"{i}.jpg")

    else:
        bmp = film.bitmap(raw=True)
        bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write(out_path + ".jpg")

    # plot out the rendered image
    # plt.show(out_path + ".jpg")

    # Get linear pixel values as a numpy array for further processing
    # bmp_linear_rgb = bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)
    # image_np = np.array(bmp_linear_rgb)
    # print(image_np.shape)


if __name__ == '__main__':
    render_scene()

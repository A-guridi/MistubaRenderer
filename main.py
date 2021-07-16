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

def render_stokes_images(p_bitmap, outpath):
    # note that for rendering meaninful stokes parameters, the filter should be removed from the .xml file
    array = np.array(p_bitmap).astype('float32')  # Matplotlib doesn't support saving of 16bit images
    print("Numpy array shape", array.shape)
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
    print(np.max(s1))
    print(np.min(s1))
    vmin = -0.01
    vmax = 0.01
    plt.imsave(f"{outpath}_s1.jpg", s1[:, :, 1], cmap='turbo', vmin=vmin, vmax=vmax)
    plt.imsave(f"{outpath}_s2.jpg", s2[:, :, 1], cmap='turbo', vmin=vmin, vmax=vmax)
    plt.imsave(f"{outpath}_s3.jpg", s3[:, :, 1], cmap='jet', vmin=vmin * 0.1, vmax=vmax * 0.1)

    # AOLP and DOLP calculation

    dolp = np.sqrt(s1 ** 2 + s2 ** 2) / 2.0  # dolp=sqrt(s1**2+s2**2)/s0
    aolp = 0.5 * np.arctan(s1 / s2)  # aolp =0.5*arctan(s1/s2)

    plt.imsave(f"{outpath}_dolp.jpg", dolp[:, :, 1], cmap='Greys', vmin=vmin, vmax=vmax)
    plt.imsave(f"{outpath}_aolp.jpg", aolp[:, :, 1], cmap='Greys', vmin=vmin, vmax=vmax)


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
    if stokes:
        bmp = Bitmap(out_path + ".exr")
        render_stokes_images(bmp, out_path)
    else:
        bmp = film.bitmap(raw=True)
        bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write(out_path + ".jpg")

        # plot out the rendered image
        plt.imshow(out_path + ".jpg")
        plt.show()

        # Get linear pixel values as a numpy array for further processing
        bmp_linear_rgb = bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)
        image_np = np.array(bmp_linear_rgb)
        print(image_np.shape)


if __name__ == '__main__':
    out_path = '/home/ubuntu/PycharmProjects/MistubaRenderer/material-testball/testball_stokes' + str(0)
    bmp = Bitmap(out_path + ".exr")
    render_stokes_images(bmp, out_path)

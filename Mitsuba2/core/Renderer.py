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

from Mitsuba2.tools.Camera_files import CameraReader


class Renderer:
    def __init__(self, output_dir, scene, filter_angle=None, camera_file=None, res_x=1080, res_y=720, spp=121):
        """
        :param output_dir: the output folder where the images will be sotred
        :param scene: the .xml file where the scene is to be rendered
        :param filter_angle: the polarizing angle of the filter. If None, the renderer will generate instead the 4 stokes
                            parameters and the dolp and aolp
        """
        self.output_dir = output_dir
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        self.output_path = self.output_dir + "output/"
        if not os.path.isdir(self.output_path):
            os.mkdir(self.output_path)
        self.scene = scene
        self.scenes = [self.scene + '_filtered.xml'] * 4 + [self.scene + '.xml']
        self.stokes = [False] * 4 + [True]
        if filter_angle is not None:
            if type(filter_angle) is not list:
                raise TypeError("Filter Angle must be a list of anlges")
            else:
                self.filter_angles = filter_angle
        else:
            self.filter_angles = [0.0, 45.0, 90.0, 135.0]
        if camera_file is not None:
            self.CameraReader = CameraReader(camera_file)
            self.num_images = self.CameraReader.get_amount_of_pictures()
        self.res_x = res_x
        self.res_y = res_y
        self.spp = spp

    def render_stokes_images(self, p_bitmap, current_path):
        # note that for rendering meaninful stokes parameters, the filter should be removed from the .xml file
        array = np.array(p_bitmap).astype('float32')  # Matplotlib doesn't support saving of 16bit images
        # Channels 0-3: RGBA normal image
        rgba = array[:, :, :4]

        # Save normal image. Here, we apply the most simple form of tonemapping + clipping
        plt.imsave(f"{current_path}_s0.jpg", np.clip(rgba ** (1 / 2.2), 0, 1))

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
        plt.imsave(f"{current_path}_s1.jpg", s1[:, :, 0], cmap='turbo', vmin=vmin, vmax=vmax)
        plt.imsave(f"{current_path}_s2.jpg", s2[:, :, 0], cmap='turbo', vmin=vmin, vmax=vmax)
        plt.imsave(f"{current_path}_s3.jpg", s3[:, :, 0], cmap='gray', vmin=vmin * 0.1, vmax=vmax * 0.1)

        # AOLP and DOLP calculation

        dolp = np.sqrt(s1 ** 2 + s2 ** 2) / s0  # dolp=sqrt(s1**2+s2**2)/s0
        aolp = 0.5 * np.arctan(s1 / (s2 + 1e-10))  # aolp =0.5*arctan(s1/s2)

        plt.imsave(f"{current_path}_dolp.jpg", dolp[:, :, 0], cmap='Greys', vmin=vmin * 10, vmax=vmax * 10)
        plt.imsave(f"{current_path}_aolp.jpg", aolp[:, :, 0], cmap='Greys', vmin=vmin * 10, vmax=vmax * 10)

    def render_scene(self, current_path, current_scene, filter_angle=0.0, stokes=False, im_number=13):
        """
        Function to render a scene
        """
        # Add the scene directory to the FileResolver's search path
        Thread.thread().file_resolver().append(os.path.dirname(current_scene))

        print("saving scene to", current_path)
        if stokes:
            # for the case where we have no polarizing filter
            current_path += "stokes"
            filter_angle = 0  # this is just a dummy angle for calling the function, but it wont be used in the render
        else:
            current_path += str(int(filter_angle))

        # Load the actual scene
        # load the axes of camera rotation
        rot_mat = self.CameraReader.get_camera_angles_one_pic(im_number)
        local_scene = load_file(current_scene, filter_angle=filter_angle, resx=self.res_x, resy=self.res_y,
                                spp=self.spp,
                                rot_matrix=rot_mat)
        # Call the scene's integrator to render the loaded scene
        local_scene.integrator().render(local_scene, local_scene.sensors()[0])

        # After rendering, the rendered data is stored in the film
        film = local_scene.sensors()[0].film()

        if stokes:
            # Write out rendering as high dynamic range OpenEXR file
            film.set_destination_file(current_path + ".exr")
            film.develop()
            bmp = Bitmap(current_path + ".exr")
            # render all the stokes parameters and the aolp and dolp
            self.render_stokes_images(bmp)

        else:
            bmp = film.bitmap(raw=True)
            bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write(current_path + ".jpg")

            # plot out the rendered image
            # plt.imshow(outpath + ".jpg")
            # plt.show()

            # Get linear pixel values as a numpy array for further processing
            # bmp_linear_rgb = bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)

    def render_all_one_pose(self, current_dir, image_numer=13):
        # renders all the images with the 4 angles and the stokes parameters
        for cur_scene, curr_angle, stokes in zip(self.scenes, self.filter_angles, self.stokes):
            self.render_scene(current_path=current_dir, current_scene=cur_scene, filter_angle=curr_angle, stokes=stokes,
                              im_number=image_numer)

    def render_all_images(self):
        for i in range(self.num_images):
            current_path = self.output_path + str(i)+"/"
            if not os.path.isdir(current_path):
                os.mkdir(current_path)
            self.render_all_one_pose(current_path, image_numer=i)

    def render_given_exr(self, exr_file):
        # for rendering only the stokes parameters given an existing .exr file
        self.render_stokes_images(Bitmap(exr_file))

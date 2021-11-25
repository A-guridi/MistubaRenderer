"""
This simple file will create the camera.txt, diameter.txt files and npy matrices for the PVnet input
"""
import os
import shutil
import json
import numpy as np
import sys


class PoseParser:
    def __init__(self, camera_json, gt_json, images_path, diameter, output_path):
        self.camera_file_path = camera_json
        with open(os.path.abspath(camera_json), 'r') as cfile:
            cam = json.load(cfile)
        self.cam_dict = cam

        self.gt_file_path = gt_json
        with open(os.path.abspath(gt_json), 'r') as gtfile:
            gt = json.load(gtfile)
        self.gt_dict = gt
        if type(diameter) == list and len(diameter) == 3:
            self.diameter = self.calculate_diameter(diameter)
        else:
            self.diameter = diameter

        self.output_path = output_path
        self.images_path = images_path

    @staticmethod
    def calculate_diameter(bbox_sizes):
        return np.sqrt(bbox_sizes[0] ** 2 + bbox_sizes[1] ** 2 + bbox_sizes[2] ** 2)

    def create_txt_files(self):
        cam_K = self.cam_dict["0"]["cam_K"]
        cam_out_file = self.output_path + "camera.txt"
        if os.path.exists(cam_out_file):
            os.remove(cam_out_file)

        cam_str = ""
        for i, k in enumerate(cam_K):
            if i in [2, 5]:
                cam_str += str(k).zfill(16) + " \n"
            else:
                cam_str += str(k).zfill(16) + " "

        with open(os.path.abspath(cam_out_file), 'w') as cam_file:
            cam_file.write(cam_str)

        diam_out_file = self.output_path + "diameter.txt"
        if os.path.exists(diam_out_file):
            os.remove(diam_out_file)
        with open(os.path.abspath(diam_out_file), 'w') as diam_file:
            diam_file.write(str(self.diameter))

    def create_npy_files(self, example_file="pose1.npy"):
        out_path = self.output_path + "pose/"
        if os.path.exists(out_path):
            shutil.rmtree(out_path)
        os.mkdir(out_path)
        ex_file = np.load("/home/arturo/datasets/custom_download/pose/" + example_file)
        print(ex_file)
        print(ex_file.shape)
        for i in range(len(self.gt_dict.keys())):
            gt_params = [gt_dict for gt_dict in self.gt_dict[str(i)] if gt_dict["obj_id"] == 1]
            assert len(gt_params) == 1, "Error, only one object with obj_id==1 should be found"
            gt_params = gt_params[0]
            cam_R = np.array(gt_params["cam_R_m2c"]).reshape((3, 3))
            cam_T = np.array(gt_params["cam_t_m2c"]) / 1000.0
            rot_mat = np.zeros(shape=(3, 4))
            rot_mat[:3, :3] = cam_R
            rot_mat[:3, 3] = cam_T.flatten()
            np.save(out_path + f"pose{i}.npy", rot_mat)

        print("All poses successfully created")

    def create_test_images(self):
        rgb_path = self.output_path + "rgb/"
        if os.path.exists(rgb_path):
            shutil.rmtree(rgb_path)
        os.mkdir(rgb_path)
        all_folders = sorted(os.listdir(self.images_path))
        try:
            all_folders.remove("lava")
        except:
            pass
        for fold in all_folders:
            shutil.copy2(self.images_path + fold + "/stokes_s0.jpg", rgb_path + str(fold) + ".jpg")

    def assert_all_folders_okay(self):
        # this function asserts that all the poses and values are stored correctly
        list_files = os.listdir(self.output_path)
        assert "model.ply" in list_files, "Error, no model.ply found in the dataset"
        assert "camera.txt" in list_files, "Error, no camera file found in the dataset"
        assert "diameter.txt" in list_files, "Error, no diameter file found in the dataset"
        assert "rgb" in list_files, "Error, no RGB folder found in the dataset"
        assert "mask" in list_files, "Error, no mask folder found in the dataset"
        assert "pose" in list_files, "Error, no pose folder found in the dataset"

        len_rgb_pics = len(os.listdir(self.output_path + "rgb/"))
        len_mask_pics = len(os.listdir(self.output_path + "mask/"))
        len_poses = len(os.listdir(self.output_path + "pose/"))

        assert len_rgb_pics == len_mask_pics and len_rgb_pics == len_poses, "Error, the amount of images does not " \
                                                                            "match the masks or poses "

    def run_all(self):
        self.create_test_images()
        self.create_txt_files()
        self.create_npy_files()
        print("All processes finished and tested okay")


if __name__ == "__main__":
    files_path = "/home/arturo/datasets/custom_glass/"
    camera_json = "/home/arturo/renders/glass/output/bop_data/train_pbr/000000/scene_camera.json"
    ground_truth_json = "/home/arturo/renders/glass/output/bop_data/train_pbr/000000/scene_gt.json"
    images_path = "/home/arturo/renders/glass/mitsuba_glass/output/"
    diameter = 0.163514
    new_diameter_glass = [0.131568, 0.086612, 0.16365]      # 3D sizes of the bbox are also supported
    simple_parser = PoseParser(camera_json=camera_json, gt_json=ground_truth_json, images_path=images_path,
                               diameter=new_diameter_glass, output_path=files_path)
    try:
        arg = sys.argv[1]
    except:
        arg = None

    if arg == "txt":
        print("Creating txt files")
        simple_parser.create_txt_files()
    elif arg == "npy":
        print("Creating npy poses")
        simple_parser.create_npy_files()
    else:
        print("No argument provided, creating both txt and npy poses")
        simple_parser.run_all()

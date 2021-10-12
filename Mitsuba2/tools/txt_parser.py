"""
This simple file will create the camera.txt and diameter.txt files for the PVnet input
"""
import os
import json
import numpy as np


class Simple_files:
    def __init__(self, camera_json, gt_json, diameter, output_path):
        self.camera_file_path = camera_json
        with open(os.path.abspath(camera_json), 'r') as cfile:
            cam = json.load(cfile)
        self.cam_dict = cam

        self.gt_file_path = gt_json
        with open(os.path.abspath(gt_json), 'r') as gtfile:
            gt = json.load(gtfile)
        self.gt_dict = gt

        self.diameter = diameter
        self.output_path = output_path

    def create_txt_files(self):
        cam_K = self.cam_dict["0"]["cam_K"]
        cam_out_file = self.output_path + "camera.txt"
        if os.path.exists(cam_out_file):
            os.remove(cam_out_file)

        cam_str = ""
        for i, k in enumerate(cam_K):
            if i in [2, 5]:
                cam_str += str(k).zfill(8) + " \n"
            else:
                cam_str += str(k).zfill(8) + " "

        with open(os.path.abspath(cam_out_file), 'w') as cam_file:
            cam_file.write(cam_str)

        diam_out_file = self.output_path + "diameter.txt"
        if os.path.exists(diam_out_file):
            os.remove(diam_out_file)
        with open(os.path.abspath(diam_out_file), 'w') as diam_file:
            diam_file.write(self.diameter)

    def create_npy_files(self, example_file="pose0.npy"):
        out_path = self.output_path + "pose/"
        if os.path.exists(out_path):
            os.remove(out_path)
        os.mkdir(out_path)
        ex_file = np.load("/home/arturo/datasets/custom_download/pose/" + example_file)
        print(ex_file)
        print(ex_file.shape)
        for i in range(len(self.gt_dict.keys())):
            gt_params = [gt_dict for gt_dict in self.gt_dict[str(i)] if gt_dict["obj_id"] == 1]
            assert len(gt_params) == 1, "Error, only one object with obj_id==1 should be found"
            gt_params = gt_params[0]
            cam_R = np.array(gt_params["cam_R_m2c"]).reshape((3, 3))
            cam_T = np.array(gt_params["cam_R_m2c"])
            rot_mat = np.zeros(shape=(4, 4))
            rot_mat[:3, :3] = cam_R
            rot_mat[:3, 3] = cam_T.flatten()
            rot_mat[3, 3] = 1
            np.save(out_path + f"pose{i}.npy", rot_mat)

        print("All poses successfully created")

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
        self.create_txt_files()
        self.create_npy_files()
        print("All processes finished and tested okay")


if __name__ == "__main__":
    files_path = "/home/arturo/datasets/custom/"
    camera_json = "/home/arturo/renders/cup/output/bop_data/train_pbr/000000/scene_camera.json"
    ground_truth_json = "/home/arturo/renders/cup/output/bop_data/train_pbr/000000/scene_gt.json"
    diameter = 0.163514
    simple_parser = Simple_files(camera_json=camera_json, gt_json=ground_truth_json,
                                 diameter=diameter, output_path=files_path)
    simple_parser.run_all()

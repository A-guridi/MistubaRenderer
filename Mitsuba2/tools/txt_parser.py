"""
This simple file will create the camera.txt and diameter.txt files for the PVnet input
"""
import os
import json
import numpy as np


class Simple_files:
    def __init__(self, camera_json, diameter, output_path):
        self.camera_file_path = camera_file
        with open(os.path.abspath(camera_json), 'r') as cfile:
            cam = json.load(cfile)
        self.cam_dict = cam
        self.diameter = diameter
        self.output_path = output_path

    def create_txt_files(self):
        cam_K = self.cam_dict["0"]["cam_K"]
        cam_out_file = self.output_path + "/camera.txt"
        with open(os.path.abspath(cam_out_file), 'w') as cam_file:
            cam_file.write(cam_K[:3])
            cam_file.write('\n')
            cam_file.write(cam_K[3:6])
            cam_file.write('\n')
            cam_file.write(cam_K[6:])

        diam_out_file = output_path + "/diameter.txt"
        with open(os.path.abspath(diam_out_file), 'w') as diam_file:
            diam_file.write(self.diameter)

    def create_npy_files(self, example_file="pose0.npy"):
        ex_file=np.load(example_file)
        print(ex_file)
        print(ex_file.shape)


if __name__ == "__main__":
    files_path = "/home/arturo/datasets/custom"
    json_file="/home/arturo/renders/cup/output/bop_data/train_pbr/000000/scene_camera.json"
    simple_parser = Simple_files(files_path)
    normals_parser.save_all_normals()



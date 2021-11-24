"""
This file has the normals parser class
This tool takes all created normals in a hdf5 format created from blender proc and saves them
in a subfolder as png images. This tool expects all the hdf5 files to be saved in the same folder
Additionally, it can be used for any other key by just changing the key value and the output folder
"""

import os
import h5py
import numpy as np
from matplotlib import pyplot as plt
import sys
import json


class NormalsParser:

    def __init__(self, files_path, key="normals"):
        self.key = key
        self.files_path = files_path
        self.out_path = files_path + f"/{self.key}_png/"
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

    def save_data(self, key, data, file_label):
        plt.figure()
        plt.title("{} in {}".format(key, file_label))
        plt.imsave(self.out_path + str(file_label) + ".png", data)

    def vis_file(self, path, label):
        # Check if file exists
        if os.path.exists(path):
            if os.path.isfile(path):
                with h5py.File(path, 'r') as data:
                    print(path + " contains the following keys: " + str(data.keys()))

                    if self.key in data.keys():
                        value = np.array(data[self.key])
                        if len(value.shape) >= 3 and value.shape[0] == 2:
                            # Visualize both eyes separately
                            for i, img in enumerate(value):
                                self.save_data(self.key, img, label)
                        else:
                            self.save_data(self.key, value, label)
            else:
                print("The path is not a file")
        else:
            print("The file does not exist: {}".format(args.hdf5))

    def save_all_normals(self):
        files = sorted(os.listdir(self.files_path))
        for image_path in files:
            full_path = os.path.join(self.files_path, image_path)
            self.vis_file(full_path, image_path[:-5])


if __name__ == "__main__":
    files_path = "/home/arturo/renders/cup/output/normals"
    normals_parser = NormalsParser(files_path)
    normals_parser.save_all_normals()

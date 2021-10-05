import os
import h5py
import argparse
import numpy as np
from matplotlib import pyplot as plt
import sys
import json


class NormalsParser():

    def __init__(self, files_path):
        self.files_path = files_path
        self.out_path = files_path + "/normals_png/"
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

    def vis_data(self, key, data, file_label):
        # If key is valid and does not contain segmentation data, create figure and add title
        plt.figure()
        plt.title("{} in {}".format(key, file_label))
        plt.imsave(self.out_path + str(file_label) + ".png", data)

    def vis_file(self, path, label):
        # Check if file exists
        if os.path.exists(path):
            if os.path.isfile(path):
                with h5py.File(path, 'r') as data:
                    print(path + " contains the following keys: " + str(data.keys()))

                    # Select only a subset of keys if args.keys is given
                    if "normals" in data.keys():
                        key = "normals"
                        value = np.array(data[key])
                        if len(value.shape) >= 3 and value.shape[0] == 2:
                            # Visualize both eyes separately
                            for i, img in enumerate(value):
                                self.vis_data(key, img, label)
                        else:
                            self.vis_data(key, value, label)
            else:
                print("The path is not a file")
        else:
            print("The file does not exist: {}".format(args.hdf5))

    def save_all_normals(self):
        files = os.listdir(self.files_path)
        for i, image_path in enumerate(files):
            full_path = os.path.join(self.files_path, image_path)
            self.vis_file(full_path, image_path[:-5])


if __name__ == "__main__":
    files_path = "/home/arturo/renders/cup/output/normals"
    normals_parser = NormalsParser(files_path)
    normals_parser.save_all_normals()

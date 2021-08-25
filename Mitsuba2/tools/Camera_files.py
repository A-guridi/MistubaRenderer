import numpy as np
import json
import os


class CameraReader:
    def __init__(self, camera_file):
        self.camera_file_path = camera_file
        with open(os.path.abspath(self.camera_file_path), 'r') as cfile:
            cam = json.load(cfile)
        self.cam_dict = cam

    def get_amount_of_pictures(self):
        return len(self.cam_dict.keys())

    def get_camera_angles_one_pic(self, picture_number=None):
        # open the matrices and shape them like rotation matrices
        if picture_number is None:
            picture_number = 12

        cam_R = np.array(self.cam_dict[str(picture_number)]["cam_R_w2c"]).reshape((3, 3))
        cam_T = np.array(self.cam_dict[str(picture_number)]["cam_t_w2c"]) / 1000.0

        # we store them in a 4x4 matrix with the rotation and translation vectors
        rot_mat = np.zeros(shape=(4, 4))
        rot_mat[:3, :3] = cam_R
        rot_mat[:3, 3] = cam_T.flatten()
        rot_mat[3, 3] = 1
        # we invert to have a camera-to-world matrix
        rot_mat = np.linalg.inv(rot_mat)
        # swicth -second row with third row, because of the format of saving
        sec_row = -rot_mat[1, :]
        rot_mat[1, :] = rot_mat[2, :]
        rot_mat[2, :] = sec_row
        # transform it into a string list
        rot_mat = list(rot_mat.flatten())
        rot_mat = [str(c) for c in rot_mat]
        rot_string = ""
        for ele in rot_mat:
            rot_string += ele + " "
        print(rot_string)
        return rot_string

    def get_camera_angles_all_pics(self):
        number_of_pics = self.get_amount_of_pictures()
        camera_angles = []
        for pic in range(number_of_pics):
            camera_angles.append(self.get_camera_angles_one_pic(pic))
        return camera_angles

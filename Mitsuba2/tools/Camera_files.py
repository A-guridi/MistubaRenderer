import numpy as np
import json
import os


def rot_z(angle):
    # get angle in degress and create a rotation matrix in Z
    angle *= np.pi / 180
    return np.array([[np.cos(angle), -np.sin(angle), 0, 0], [np.sin(angle), np.cos(angle), 0, 0],
                     [0, 0, 1, 0], [0, 0, 0, 1]])


class CameraReader:
    def __init__(self, camera_file):
        self.camera_file_path = camera_file
        with open(os.path.abspath(self.camera_file_path), 'r') as cfile:
            cam = json.load(cfile)
        self.cam_dict = cam

    def get_amount_of_pictures(self):
        return len(self.cam_dict.keys())

    def get_camera_angles_one_pic(self, picture_number=2):
        # open the matrices and shape them like rotation matrices

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
        # rot_mat[0, 0] *= -1
        # rot_mat[0, 2] *= -1
        # transform it into a string list
        rot_mat_z = rot_z(180)
        rot_mat = np.matmul(rot_mat, rot_mat_z)
        rot_mat = list(rot_mat.flatten())
        rot_mat = [str(c) for c in rot_mat]
        rot_string = ""
        for ele in rot_mat:
            rot_string += ele + " "
        # print(rot_string)
        return rot_string

    def get_camera_angles_all_pics(self):
        camera_angles = []
        for pic in range(self.get_amount_of_pictures()):
            camera_angles.append(self.get_camera_angles_one_pic(pic))
        return camera_angles

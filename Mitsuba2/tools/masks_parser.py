"""
This parser creates mask files from Coco annotations
From this, it reads a json file in the coco format and saves all the masks in a subfolder
called "coco_masks"
"""

import os
import numpy as np
from matplotlib import pyplot as plt
from pycocotools.coco import COCO
import skimage.io as io
import shutil


class MasksParser:

    def __init__(self, files_path, ann_file, file_format=".png", class_id=None, def_size=(512, 512)):
        self.files_path = files_path
        self.ann_file = ann_file
        self.out_path = self.files_path + f"/coco_masks/"

        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)
        else:
            shutil.rmtree(self.out_path)
            os.mkdir(self.out_path)
        self.file_format = file_format
        self.coco = COCO(self.ann_file)
        self.ids = self.create_ids(class_id)
        cat_ids = self.coco.getCatIds()
        self.num_files = len(self.coco.getImgIds(catIds=cat_ids))
        self.def_size = def_size

    def create_ids(self, class_id):
        if class_id is None:
            return None
        if type(class_id) != list:
            class_id = [class_id]
        if 333 not in class_id:
            class_id.append(333)
        elif 333 != class_id[-1]:
            class_id.remove(333)
            class_id.append(333)

        return class_id

    def save_all_masks(self):
        if self.ids is not None:
            cat_ids = self.coco.getCatIds(catIds=self.ids)
            print(f"Getting masks for the class ids {self.ids}")
        else:
            cat_ids = self.coco.getCatIds()
        img_ids = self.coco.getImgIds(catIds=cat_ids)
        for im_id in img_ids:
            img = self.coco.loadImgs(im_id)[0]
            anns_ids = self.coco.getAnnIds(imgIds=img['id'], catIds=cat_ids, iscrowd=None)
            anns = self.coco.loadAnns(anns_ids)
            def_image = np.zeros((img['height'], img['width']))
            for ann in anns:
                val = ann["category_id"] if ann["category_id"] != 333 else 0
                def_image = np.maximum(def_image, self.coco.annToMask(ann) * val)

            # def_image = np.where(def_image == 0, 255, 0)
            plt.imsave(self.out_path + str(img['id']) + self.file_format, def_image, cmap="gray")

        if len(img_ids) != self.num_files:
            for i in range(self.num_files):
                if not os.path.isfile(self.out_path + str(i) + self.file_format):
                    plt.imsave(self.out_path + str(i) + self.file_format, np.zeros(self.def_size), cmap="gray")


if __name__ == "__main__":
    files_path = "/home/arturo/renders/complexscene/output/coco_data"
    ann_file = files_path + "/coco_annotations.json"
    class_id = [1, 333]  # 1 for the cup, 2 for the beer glass
    default_size = (512, 612)
    masks_parser = MasksParser(files_path=files_path, ann_file=ann_file, class_id=class_id, def_size=default_size)
    masks_parser.save_all_masks()

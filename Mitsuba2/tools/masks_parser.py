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


class MasksParser:

    def __init__(self, files_path, ann_file, file_format=".png"):
        self.files_path = files_path
        self.ann_file = ann_file
        self.out_path = self.files_path + "/coco_masks/"
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)
        self.file_format = file_format
        self.coco = COCO(self.ann_file)

    def save_all_masks(self):
        cat_ids = self.coco.getCatIds()
        img_ids = self.coco.getImgIds(catIds=cat_ids)
        for im_id in img_ids:
            img = self.coco.loadImgs(im_id)[0]
            anns_ids = self.coco.getAnnIds(imgIds=img['id'], catIds=cat_ids, iscrowd=None)
            anns = self.coco.loadAnns(anns_ids)
            def_image = np.zeros((img['height'], img['width']))
            for ann in anns:
                def_image = np.maximum(def_image, self.coco.annToMask(ann) * ann['category_id'])

            plt.imsave(self.out_path + str(img['id']) + self.file_format, def_image, cmap="binary")


if __name__ == "__main__":
    files_path = "/home/arturo/renders/cup/output/coco_data"
    ann_file = files_path + "/coco_annotations.json"
    masks_parser = MasksParser(files_path=files_path, ann_file=ann_file)
    masks_parser.save_all_masks()

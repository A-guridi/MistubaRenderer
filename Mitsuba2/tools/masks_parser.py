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
        self.file_format = file_format
        self.coco = COCO(self.ann_file)

    def save_mask(self, img, anns):
        def_image = np.zeros((img['height'], img['width']))
        for ann in anns:
            def_image = np.maximum(def_image, coco.annToMask(ann) * ann['category_id'])

        plt.imsave(self.out_path + str(img['id']) + self.file_format, def_image)

    def save_all_masks(self):
        cat_ids = self.coco.getCatIds()
        img_ids = self.coco.getImgIds(catIds=cat_ids)
        for im_id in img_ids:
            image = coco.loadImgs(im_id)[0]
            anns_ids = self.coco.getAnnIds(imgIds=image['id'], catIds=cat_ids, iscrowd=None)
            anns = self.coco.loadAnns(anns_ids)
            self.save_mask(image, anns)

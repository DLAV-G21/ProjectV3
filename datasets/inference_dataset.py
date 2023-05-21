# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
"""
COCO dataset which returns image_id for evaluation.

Mostly copy-paste from https://github.com/pytorch/vision/blob/13b35ff/references/detection/coco_utils.py
"""
from pathlib import Path
from PIL import Image
from numpy.core.defchararray import array
import torch
from pycocotools.coco import COCO
import numpy as np
import torch.utils.data
import cv2
import torchvision
from pycocotools import mask as coco_mask

from os import listdir
from os.path import isfile, isdir, join
import datasets.transforms as T

import albumentations as al

class InferenceDataset(torch.utils.Dataset):
    def __init__(self, img_folder, transforms):
        super().__init__()
        self._transforms = transforms
        if not isdir(img_folder):
            raise ValueError("The given path should be a folder containing all the images for which the model should make predictions.")
        self.imgs = [f for f in listdir(img_folder) if isfile(join(img_folder,f)) and (f.endsWith(".png") or f.endsWith(".jpg"))]

    def __len__(self):
        return len(self.imgs)

    def __getitem__(self, idx):
        img_name = self.imgs[idx]
        filename = join(self.img_folder,img_name)
        img = Image.open(filename)
        target = {'image_id': idx, 'annotations': {}, "image": img, "filename":img_name}

        if self._transforms is not None:
            img, target = self._transforms(img, target)

        return img, target


def transform(size):
    normalize = T.Compose([
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    return T.Compose([
        T.Resize(size),
        normalize,
    ])


def build_inference(image_set, args):
    dataset = InferenceDataset(img_folder=args.image_folder, 
        transforms=transform(args.input_image_resize)
        )
    return dataset
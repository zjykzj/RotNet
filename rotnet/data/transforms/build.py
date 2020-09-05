# -*- coding: utf-8 -*-

"""
@date: 2020/8/22 下午9:40
@file: trainer.py
@author: zj
@description: 
"""

import torchvision.transforms as transforms
from .rotate import Rotate
from .togray import ToGray
from .compose import Compose


def build_transform(cfg, train=True):
    size = cfg.MODEL.INPUT_SIZE

    if train:
        transform = transforms.Compose([
            transforms.Resize(size),
            transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1),
            transforms.Grayscale(),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,)),
            transforms.RandomErasing()
        ])
    else:
        transform = transforms.Compose([
            transforms.Resize(size),
            transforms.Grayscale(),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,)),
        ])
    # 对测试集和训练集都进行随机旋转
    target_transform = Compose([
        Rotate(random=True),
        ToGray(),
    ])

    return transform, target_transform

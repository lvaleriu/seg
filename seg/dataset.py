import torch.utils.data as data
import torch

import numpy as np
from torchvision import transforms
import torchvision.transforms.functional as tf
import os
from PIL import Image


class BaselineSet(data.Dataset):
    def __init__(self, imgs):
        super(BaselineSet, self).__init__()
        self.imgs = imgs
        self.targets = [os.path.splitext(x)[0] + '.png' for x in imgs]

    def __getitem__(self, idx):
        input = Image.open(self.imgs[idx]).convert('RGB')
        target = Image.open(self.targets[idx])
        return self.transform(input, target)

    def transform(self, image, target):
        resize = transforms.Resize(1200)
        jitter = transforms.ColorJitter()
        norm = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

        image = jitter(resize(image))
        target = resize(target)

        if np.random.random() > 0.5:
            image = tf.hflip(image)
            target = tf.hflip(target)

        angle = np.random.uniform(-10, 10)
        image = tf.rotate(image, angle, resample=Image.BICUBIC)
        target = tf.rotate(target, angle, resample=Image.NEAREST)
        image = tf.to_tensor(image)

        target = np.array(target)[:,:,2]
        l = np.zeros(target.shape, 'i')
        vals = [(3, 0b1000), (2, 0b0100), (1, 0b0010)]
        for v, m in vals:
            l[np.bitwise_and(m, target) != 0] = v
        target = torch.LongTensor(l)
        return norm(image), target

    def __len__(self):
        return len(self.imgs)


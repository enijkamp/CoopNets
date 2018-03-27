import sys
import math
import logging

import numpy as np
import tensorflow as tf
import scipy.misc


def init_log(path):
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    formatter_cs = logging.Formatter('%(message)s')

    cs = logging.StreamHandler(sys.stdout)
    cs.setLevel(logging.INFO)
    cs.setFormatter(formatter_cs)
    log.addHandler(cs)

    log = logging.getLogger('tensorflow')
    log.setLevel(logging.INFO)
    log.handlers = []

    formatter_fh = logging.Formatter('%(asctime)s - %(message)s')

    fh = logging.FileHandler(path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter_fh)
    log.addHandler(fh)


def make_dir(dir):
    if not tf.gfile.Exists(dir):
        tf.gfile.MakeDirs(dir)
    return dir


def cell2img(cell_image, image_size=100, margin_syn=2):
    num_cols = cell_image.shape[1] // image_size
    num_rows = cell_image.shape[0] // image_size
    images = np.zeros((num_cols * num_rows, image_size, image_size, 3))
    for ir in range(num_rows):
        for ic in range(num_cols):
            temp = cell_image[ir*(image_size+margin_syn):image_size + ir*(image_size+margin_syn),
                   ic*(image_size+margin_syn):image_size + ic*(image_size+margin_syn),:]
            images[ir*num_cols+ic] = temp
    return images


def clip_by_value(input_, min=0, max=1):
    return np.minimum(max, np.maximum(min, input_))


def img2cell(images, row_num=10, col_num=10, margin_syn=2):
    [num_images, image_size] = images.shape[0:2]
    num_cells = int(math.ceil(num_images / (col_num * row_num)))
    cell_image = np.zeros((num_cells, row_num * image_size + (row_num-1)*margin_syn,
                           col_num * image_size + (col_num-1)*margin_syn, 3))
    for i in range(num_images):
        cell_id = int(math.floor(i / (col_num * row_num)))
        idx = i % (col_num * row_num)
        ir = int(math.floor(idx / col_num))
        ic = idx % col_num
        temp = clip_by_value(np.squeeze(images[i]), -1, 1)
        temp = (temp + 1) / 2 * 255
        temp = clip_by_value(np.round(temp), min=0, max=255)
        low = np.min(temp, axis=(0, 1, 2))
        high = np.max(temp, axis=(0, 1, 2))
        temp = (temp - low) / (high - low)
        cell_image[cell_id, (image_size+margin_syn)*ir:image_size + (image_size+margin_syn)*ir,
                    (image_size+margin_syn)*ic:image_size + (image_size+margin_syn)*ic,:] = temp
    return cell_image


def save_sample_results(sample_results, filename, col_num=10, margin_syn=2):
    cell_image = img2cell(sample_results, col_num, col_num, margin_syn)
    scipy.misc.imsave(filename, np.squeeze(cell_image))
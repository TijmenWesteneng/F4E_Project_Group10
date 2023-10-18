from random import gauss
import numpy as np


def get_white_noise_array(size, mean, std_dev):
    white_noise_array = np.empty(size)

    for i in range(white_noise_array.size):
        rand = gauss(mean, std_dev)
        white_noise_array[i] = rand

    return white_noise_array

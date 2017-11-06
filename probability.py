import numpy as np
from math import sqrt, log

def hist_static_init(source, key_len=0):
    keys_list = [source[max(0,k-key_len):k] for k in xrange(len(source))]
    hist = dict((key, np.zeros([256])) for key in keys_list)

    # Histogramming data
    for key, ch in zip(keys_list, source):
        hist[key][ord(ch)] += 1

    return hist


def hist_dynamic_check(hist, key, bias):
    if key not in hist:
        hist[key] = bias*np.ones([256])


def hist_dynamic_update(hist, key, ch, key_len=0):
    hist[key][ord(ch)] += 200/(1 + key_len)


def hist_to_prob(hist, key):
    prob = hist[key] / np.sum(hist[key])

    return prob
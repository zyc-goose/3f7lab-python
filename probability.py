import numpy as np

def gen_prob(source, cond_len=0):

    keys_list = [source[max(0,k-cond_len):k] for k in xrange(len(source))]
    prob = dict((key, np.zeros([256])) for key in keys_list)

    # Histogramming data
    for key, ch in zip(keys_list, source):
        prob[key][ord(ch)] += 1

    # Normalise
    for key in prob:
        prob[key] /= np.sum(prob[key])

    return prob
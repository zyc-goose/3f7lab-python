import numpy as np
from math import floor, ceil
from probability import *

# Interval [0,1] simulation using integers
precision = 60
one = 1 << precision
half = one >> 1
quarter = half >> 1
threequarters = quarter*3

def arith_encode(source, key_len=0, dynamic=False, alphabet=[chr(x) for x in xrange(256)]):
    code_list = []
    lo = 0
    hi = one
    straddle = 0

    # Initialise histogram
    if dynamic:
        hist = {}
    else:
        hist = hist_static_init(source, key_len)

    # MAIN ENCODING ROUTINE
    for k, ch in enumerate(source):

        hl_diff = hi - lo + 1     # range of the interval (+1 to avoid rounding issues)
        ind = alphabet.index(ch)  # index of the current symbol
        key = source[max(0,k-key_len):k]
        if dynamic:
            hist_dynamic_check(hist, key, bias=1)

        # Get probability and CDF
        prob = hist_to_prob(hist, key)
        cprob = np.cumsum(prob) - prob

        # update the boundaries
        lo += int(ceil(hl_diff * cprob[ind]))
        hi = lo + int(floor(hl_diff * prob[ind]))

        # update the histogram if the mode is dynamic
        if dynamic:
            hist_dynamic_update(hist, key, ch, key_len)

        # check that the interval has not narrowed to 0
        assert hi > lo, 'Error: interval has become zero. lo = %d, hi = %d' % (lo, hi)

        # RESCALING LOOP
        while True:
            if hi < half:
                code_list.append('0')
                for i in xrange(straddle):
                    code_list.append('1')
                straddle = 0
            elif lo >= half:
                code_list.append('1')
                for i in xrange(straddle):
                    code_list.append('0')
                straddle = 0
                # take a half away
                lo -= half
                hi -= half
            elif lo >= quarter and hi < threequarters:
                # take a quarter away
                lo -= quarter
                hi -= quarter
                straddle += 1
            else:
                break
            # Now we re-stretch the interval
            lo = lo*2
            hi = hi*2 + 1

    # Wrap up: ensure the final dyadic interval lies in the source interval.
    # This statement is true: (lo < half <= hi) and (lo < quarter or hi >= threequarters)
    straddle += 1     # zoom in again around 0.5
    if lo < quarter:  # LHS of 0.5
        code_list.append('0')
        for i in xrange(straddle):
            code_list.append('1')
    else:             # RHS of 0.5
        code_list.append('1')
        for i in xrange(straddle):
            code_list.append('0')

    # Return the final string of code
    code = ''.join(code_list)
    return code


def arith_decode(code, source_len, key_len=0, dynamic=False, hist=None, alphabet=[chr(x) for x in xrange(256)]):
    source_list = []
    lo = 0
    hi = one
    straddle = 0

    code += ('0'*(precision + 1))
    code_len = len(code)
    tail_ptr = precision
    target = int(code[0:precision], 2)

    # Initialise histogram
    if dynamic:
        hist = {}
    else:
        assert hist is not None, 'Function in static mode, but no histogram is provided'

    # MAIN ENCODING ROUTINE
    for k in xrange(source_len):
        hl_diff = hi - lo + 1     # range of the interval (+1 to avoid rounding issues)
        key = ''.join(source_list[max(0,k-key_len):k])
        if dynamic:
            hist_dynamic_check(hist, key, bias=1)

        # Get probability and CDF
        prob = hist_to_prob(hist, key)
        cprob = np.cumsum(prob) - prob

        # Now find the index of the symbol
        ind = np.max(np.nonzero((lo + np.ceil(hl_diff * cprob).astype('int')) <= target))
        ch = alphabet[ind]
        source_list.append(ch)

        # update the boundaries
        lo += int(ceil(hl_diff * cprob[ind]))
        hi = lo + int(floor(hl_diff * prob[ind]))

        # update the histogram if the mode is dynamic
        if dynamic:
            hist_dynamic_update(hist, key, ch, key_len)

        # check that the interval has not narrowed to 0
        assert hi > lo, 'Error: interval has become zero. Check for zero probabilities and precision issues'

        # RESCALING LOOP
        while True:
            if hi < half:
                pass
            elif lo >= half:
                lo -= half
                hi -= half
                target -= half
            elif lo >= quarter and hi < threequarters:
                lo -= quarter
                hi -= quarter
                target -= quarter
            else:
                break
            # Now we re-stretch the interval
            lo = lo*2
            hi = hi*2 + 1
            target = 2*target + int(code[tail_ptr])
            tail_ptr += 1

            assert tail_ptr < code_len, 'Unable to decompress.'

    source = ''.join(source_list)
    return source
import numpy as np
from math import floor, ceil

# Interval [0,1] simulation using integers
precision = 60
one = 1 << precision
half = one >> 1
quarter = half >> 1
threequarters = quarter*3

def arith_encode(source, prob, cond_len=0, alphabet=[chr(x) for x in xrange(256)]):

    # Initialisation
    code_list = []
    lo = 0
    hi = one
    straddle = 0

    # MAIN ENCODING ROUTINE
    for k, ch in enumerate(source):
        hl_diff = hi - lo + 1     # range of the interval (+1 to avoid rounding issues)
        ind = alphabet.index(ch)  # index of the current symbol

        # Calculate CDF (excluding the probability at each index itself)
        cond = source[max(0,k-cond_len):k]
        cprob = np.cumsum(prob[cond]) - prob[cond]

        # update the boundaries
        lo += int(ceil(hl_diff * cprob[ind]))
        hi = lo + int(floor(hl_diff * prob[cond][ind]))

        # check that the interval has not narrowed to 0
        assert hi > lo, 'Error: interval has become zero. Check for zero probabilities and precision issues'

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


def arith_decode(code, prob, source_len, cond_len=0, alphabet=[chr(x) for x in xrange(256)]):
    # Initialisation
    source_list = []
    lo = 0
    hi = one
    straddle = 0

    code += ('0'*(precision + 1))
    code_len = len(code)
    tail_ptr = precision
    target = int(code[0:precision], 2)

    # MAIN ENCODING ROUTINE
    for k in xrange(source_len):
        hl_diff = hi - lo + 1     # range of the interval (+1 to avoid rounding issues)

        # Calculate CDF (excluding the probability at each index itself)
        cond = ''.join(source_list[max(0,k-cond_len):k])
        cprob = np.cumsum(prob[cond]) - prob[cond]

        # Now find the index of the symbol
        ind = np.max(np.nonzero((lo + np.ceil(hl_diff * cprob).astype('int')) <= target))
        source_list.append(alphabet[ind])

        # update the boundaries
        lo += int(ceil(hl_diff * cprob[ind]))
        hi = lo + int(floor(hl_diff * prob[cond][ind]))

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
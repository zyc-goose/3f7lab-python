from __future__ import print_function
from arithmetic import *
import sys, time

fin = open('hamlet.txt','r')
source = ''.join(fin.readlines())
L = len(source)

key_len = 2
print ('\nkey_len = %d :\n' % key_len)

print ('Encoding source file...', end='')
sys.stdout.flush()
code = arith_encode(source, key_len, True)
print ('done')

print ('Decoding source file...', end='')
sys.stdout.flush()

decoded = arith_decode(code, L, key_len, True)
print ('done')

print ('\nBits per symbol =', float(len(code))/float(L))
print ('Encode & Decode successful:', decoded == source)

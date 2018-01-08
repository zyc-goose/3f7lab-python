from arithmetic import *
import sys, time

key_len = 0
source_name = 'hamlet.txt'
uppercase_mode = True;
dynamic = False

fin = open(source_name,'r')
source = ''.join(fin.readlines())
if uppercase_mode:
    source = source.upper()
L = len(source)

print ('\nkey_len = %d :\n' % key_len)

print ('Encoding source file...', end='')
sys.stdout.flush()
code, hist = arith_encode(source, key_len, dynamic)
print ('done')

print ('Decoding source file...', end='')
sys.stdout.flush()

decoded = arith_decode(code, L, key_len, dynamic, hist)
print ('done')

print ('\nBits per symbol =', float(len(code))/float(L))
print ('Encode & Decode successful:', decoded == source)

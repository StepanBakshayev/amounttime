import time
import datetime
import gc

with open('pypy.output', 'rt') as stream:
    data = eval(stream.read())

gc.collect(0)
input()

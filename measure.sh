#!/bin/sh
/usr/bin/time -v /home/stepan/develop/amount-time/.venv/bin/python ./amounttime.py big_sample.xml --filter-by-interval '11-10-2017..08-10-2020' --split-by-person --no-pretty-print > pypy.output
/usr/bin/time -v /usr/bin/python3.7 ./amounttime.py big_sample.xml --filter-by-interval '11-10-2017..08-10-2020' --split-by-person --no-pretty-print > cpython.output

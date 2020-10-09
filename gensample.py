#!/usr/bin/env python3
from xml.etree import ElementTree
from datetime import datetime, timedelta, date
from russian_names import RussianNames
import random
import math


PEOPLE_COUNT = 500
full_names = tuple(
    map(
        lambda s: s.lower().replace(' ', ''),
        RussianNames(count=PEOPLE_COUNT, name_reduction=True, patronymic=False, transliterate=True)
    )
)

INTERVAL_DATES = timedelta(days=365*3)
interval_end = date.today()
interval_start = interval_end - INTERVAL_DATES

HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<people>""".encode('utf-8')
FOOTER = """
</people>
""".encode('utf-8')
RECORD = """
    <person full_name="{full_name}">
        <start>{start}</start>
        <end>{end}</end>
    </person>"""
DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'

WORKDAY_CHANCE = 0.80
MINIMUM_WORKERS = 0.75
INTERVAL_SAMPLE = (0, 1, 2, 3, 4), (10, 25, 40, 15, 10) # ill, overtime, normal, bustle, reception
WORK_HOURS = 9
START_RANGE = 8*60*60, 11*60*60
WEEKEND = 0, 7


def range_date(start, end):
    current = start
    while current < end:
        yield current
        current += timedelta(days=1)


with open('big_sample.xml', 'wb') as stream:
    stream.write(HEADER)
    stream.flush()

    max_workers = tuple(range(math.ceil(len(full_names)*MINIMUM_WORKERS), len(full_names)+1))
    for day in range_date(interval_start, interval_end):
        if day.weekday() in WEEKEND:
            continue
        if random.random() > WORKDAY_CHANCE:
            continue
        workers = random.sample(full_names, random.choice(max_workers))
        for full_name in workers:
            intervals = random.choices(*INTERVAL_SAMPLE)[0]
            i = 0
            total_hours = 0
            start = datetime(day.year, day.month, day.day) + timedelta(seconds=random.randrange(*START_RANGE))
            while i < intervals:
                free_hours = WORK_HOURS - total_hours - (intervals - i)
                work_interval = random.choice(range(1, free_hours+1))
                end = start + timedelta(hours=work_interval)

                stream.write(RECORD.format(
                    full_name=full_name,
                    start=start.strftime(DATETIME_FORMAT),
                    end=end.strftime(DATETIME_FORMAT),
                ).encode('utf-8'))
                stream.flush()

                i += 1
                start = end
                total_hours += work_interval

    stream.write(FOOTER)
    stream.flush()

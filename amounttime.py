#!/usr/bin/env python3
from xml.etree import ElementTree
from dataclasses import dataclass, field, fields, make_dataclass, replace
from datetime import datetime, timedelta, date
from collections import defaultdict


@dataclass(frozen=True)
class Record:
    full_name: str
    start: datetime
    end: datetime


def parse(file):
    DATE_FORMAT = '%d-%m-%Y %H:%M:%S'
    start = None
    end = None
    lanes = (
        ('people',),
        ('people', 'person',),
        ('people', 'person', 'start',),
        ('people', 'person', 'end',),
    )
    lane = ()
    for (event, element) in ElementTree.iterparse(file, events=('start', 'end',)):
        if event == 'start':
            lane += element.tag,
            if lane not in lanes:
                raise ValueError(f'{file!r} does not match schema. Wrong heirary is {lane}.')
        elif event == 'end':
            lane = lane[:-1]
            if element.tag == 'start':
                start = datetime.strptime(element.text, DATE_FORMAT)
            elif element.tag == 'end':
                end = datetime.strptime(element.text, DATE_FORMAT)
            elif element.tag == 'person':
                if not (start < end):
                    raise ValueError(f'{file!r} contains inverted time inverval. Wrong is {start}..{end}.')
                if not (start.date() == end.date()):
                    raise ValueError(f'{file!r} contains inverval exeeded one date. Wrong is {start}..{end}.')
                yield Record(element.attrib['full_name'], start, end)
                start = None
                end = None


def collect_by_day():
    dates = defaultdict(timedelta)
    while True:
        record = yield
        if record is None:
            break
        dates[record.start.date()] += record.end - record.start

    yield sorted(dates.items())


def send(gen):
    gen.send(None)
    return gen


def split_by_person(collector):
    persons = defaultdict(lambda: send(collector()))
    while True:
        record = yield
        if record is None:
            break
        persons[record.full_name].send(record)

    yield sorted((full_name, tuple(collector.send(None))) for full_name, collector in persons.items())


def filter_dates(start, end, collector):
    collector = send(collector())
    while True:
        record = yield
        if record is None:
            break
        if start <= record.start.date() <= end:
            collector.send(record)

    yield collector.send(None)


def main():
    for x in parse(open('sample.xml')):
        print(x)


if __name__ == '__main__':
    main()

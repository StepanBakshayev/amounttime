#!/usr/bin/env python3
from xml.etree import ElementTree
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from collections import defaultdict
from functools import partial
import pprint


@dataclass(frozen=True)
class Record:
    full_name: str
    start: datetime
    end: datetime


def parse(file):
    DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'
    lanes = (
        ('people',),
        ('people', 'person',),
        ('people', 'person', 'start',),
        ('people', 'person', 'end',),
    )
    lane = ()
    start = None
    end = None
    for (event, element) in ElementTree.iterparse(file, events=('start', 'end',)):
        if event == 'start':
            lane += element.tag,
            if lane not in lanes:
                raise ValueError(f'{file!r} does not match schema. Wrong heirary is {lane}.')
        elif event == 'end':
            lane = lane[:-1]
            if element.tag == 'start':
                start = datetime.strptime(element.text, DATETIME_FORMAT)
            elif element.tag == 'end':
                end = datetime.strptime(element.text, DATETIME_FORMAT)
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


def kick(gen):
    gen.send(None)
    return gen


def split_by_person(collector_factory):
    persons = defaultdict(lambda: kick(collector_factory()))
    while True:
        record = yield
        if record is None:
            break
        persons[record.full_name].send(record)

    yield sorted((full_name, tuple(collector.send(None))) for full_name, collector in persons.items())


def filter_dates(start, end, collector_factory):
    collector = kick(collector_factory())
    while True:
        record = yield
        if record is None:
            break
        if start <= record.start.date() <= end:
            collector.send(record)

    yield collector.send(None)


DATE_FORMAT = '%d-%m-%Y'


def main(args):
    collector_factory = collect_by_day
    if args.split_by_person:
        collector_factory = partial(split_by_person, collector_factory)
    if args.filter_by_interval:
        convert = lambda s: datetime.strptime(s, DATE_FORMAT).date()
        start, end = map(convert, args.filter_by_interval[0].split('..'))
        collector_factory = partial(filter_dates, start, end, collector_factory)
    collector = kick(collector_factory())

    with open(args.path, 'rb') as stream:
        for record in parse(stream):
            collector.send(record)

    printer = pprint.pprint
    if args.no_pretty_print:
        printer = lambda x: print(repr(x))
    printer(collector.send(None))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Calculate amout of time from xml.')
    parser.add_argument('path', type=str, help='Path to xml file')
    parser.add_argument('--split-by-person', action='store_true', help='Group time by person')
    parser.add_argument('--filter-by-interval', nargs='+', help='Use only this inverval in computation. '
        f'Format \'{DATE_FORMAT.replace("%", "%%")}..{DATE_FORMAT.replace("%", "%%")}\'')
    parser.add_argument('--no-pretty-print', action='store_true', help='Switch off pretty print')

    args = parser.parse_args()
    main(args)

#!/usr/bin/env python3
from xml.etree import ElementTree
from dataclasses import dataclass, field, fields, make_dataclass, replace
from datetime import datetime


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
                yield Record(element.attrib['full_name'], start, end)
                start = None
                end = None


def main():
    for x in parse(open('sample.xml')):
        print(x)


if __name__ == '__main__':
    main()

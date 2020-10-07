from amounttime import parse, Record, collect_by_day
from io import BytesIO
import datetime
import pytest


def test_parse():
    correct = """<?xml version="1.0" encoding="UTF-8"?>
    <people>
        <person full_name="i.ivanov">
            <start>21-12-2011 10:54:47</start>
            <end>21-12-2011 19:43:02</end>
        </person>
        <person full_name="a.stepanova">
            <start>21-12-2011 09:40:10</start>
            <end>21-12-2011 17:59:15</end>
        </person>
    </people>
    """.encode('utf-8')
    correct_parsed = [
        Record(full_name='i.ivanov', start=datetime.datetime(2011, 12, 21, 10, 54, 47), end=datetime.datetime(2011, 12, 21, 19, 43, 2)),
        Record(full_name='a.stepanova', start=datetime.datetime(2011, 12, 21, 9, 40, 10), end=datetime.datetime(2011, 12, 21, 17, 59, 15))
    ]

    assert list(parse(BytesIO(correct))) == correct_parsed

    with pytest.raises(ValueError):
        list(parse(BytesIO("""<?xml version="1.0" encoding="UTF-8"?>
            <p></p>""".encode('utf-8'))))

    with pytest.raises(ValueError):
        list(parse(BytesIO("""<?xml version="1.0" encoding="UTF-8"?>
            <people>
                <person>
                    <start>
                        <a>test</>
                    </start>
                </person>
            </people>""".encode('utf-8'))))

    with pytest.raises(ValueError):
        list(parse(BytesIO("""<?xml version="1.0" encoding="UTF-8"?>
            <people>
                <person>
                    <end>21-12-2011 09:40:10</end>
                    <start>21-12-2011 17:59:15</start>
                </person>
            </people>""".encode('utf-8'))))


def test_collect_by_day():
    records = [
        Record(full_name='i.ivanov', start=datetime.datetime(2011, 12, 21, 8, 22, 30), end=datetime.datetime(2011, 12, 21, 18, 22, 30)),
        Record(full_name='a.stepanova', start=datetime.datetime(2011, 12, 21, 9, 44, 30), end=datetime.datetime(2011, 12, 21, 19, 44, 30)),
        Record(full_name='i.ivanov', start=datetime.datetime(2011, 12, 22, 8, 22, 30), end=datetime.datetime(2011, 12, 22, 18, 22, 30)),
        Record(full_name='a.stepanova', start=datetime.datetime(2011, 12, 22, 9, 44, 30), end=datetime.datetime(2011, 12, 22, 19, 44, 30)),
    ]

    assert collect_by_day(records) == [
        (datetime.date(2011, 12, 21), datetime.timedelta(seconds=72000)),
        (datetime.date(2011, 12, 22), datetime.timedelta(seconds=72000))
    ]

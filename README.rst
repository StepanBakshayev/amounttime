================
Время прибывания
================


Задание
=======

Необходимо написать программу на Python, которая вычисляет общее время пребывания всех людей за каждое число.

Ограничения:

1. Сделать реализацию, потребление памяти которой не зависит от размера входного файла.
2. Сделать возможность разбивки по работникам и фильтрации по интервалам дат (например, с 01-08-2020 по 31-08-2020).
3. Можно использовать любой фреймворк.
4. Продемонстрировать работу с помощью тестов.
5. Обеспечить максимально простое развёртывание приложения (например docker-контейнер).

Файл

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <people>
        <person full_name="i.ivanov">
            <start>21-12-2011 10:54:47</start>
            <end>21-12-2011 19:43:02</end>
        </person>
        <person full_name="a.stepanova">
            <start>21-12-2011 09:40:10</start>
            <end>21-12-2011 17:59:15</end>
        </person>
    ...
    </people>


Использование
=============


Развертывание
-------------

Программа требует только интерпретатор python 3.7. Можно использовать `PyPy 3.7 <https://www.pypy.org/download.html>`_.


Запуск
------

.. code-block:: sh

    $ ./amounttime.py sample.xml
    [(datetime.date(2011, 12, 21), datetime.timedelta(seconds=61640)),
     (datetime.date(2011, 12, 22), datetime.timedelta(seconds=61640))]

    $ ./amounttime.py sample.xml --filter-by-interval '21-12-2011..21-12-2011'
    [(datetime.date(2011, 12, 21), datetime.timedelta(seconds=61640))]

    $ ./amounttime.py sample.xml --split-by-person
    [('a.stepanova',
      ((datetime.date(2011, 12, 21), datetime.timedelta(seconds=29945)),
       (datetime.date(2011, 12, 22), datetime.timedelta(seconds=29945)))),
     ('i.ivanov',
      ((datetime.date(2011, 12, 21), datetime.timedelta(seconds=31695)),
       (datetime.date(2011, 12, 22), datetime.timedelta(seconds=31695))))]

    $ ./amounttime.py sample.xml --filter-by-interval '21-12-2011..22-12-2011' --split-by-person
    [('a.stepanova',
      ((datetime.date(2011, 12, 21), datetime.timedelta(seconds=29945)),
       (datetime.date(2011, 12, 22), datetime.timedelta(seconds=29945)))),
     ('i.ivanov',
      ((datetime.date(2011, 12, 21), datetime.timedelta(seconds=31695)),
       (datetime.date(2011, 12, 22), datetime.timedelta(seconds=31695))))]

    $ pytest tests.py --capture=no -vv
    ================================= test session starts ==================================
    platform linux -- Python 3.7.4[pypy-7.3.2-alpha], pytest-6.1.1, py-1.9.0, pluggy-0.13.1 -- /home/stepan/develop/amount-time/.venv/bin/pypy3
    cachedir: .pytest_cache
    rootdir: /home/stepan/develop/amount-time
    collected 4 items

    tests.py::test_parse PASSED
    tests.py::test_collect_by_day PASSED
    tests.py::test_split_by_person PASSED
    tests.py::test_filter_dates PASSED

    ================================== 4 passed in 0.04s ===================================


Реализация
==========

Дизайн
------

По заданию не ясно какой интерфейс предполагается для взаимодействия.
Я выбиру командный.

Требование "Независимость потребления памяти от размера входного файла" удволетворяет sax парсер. Я набил руку на ET. Буду использовать его, хотя таких гарантий он не дает.
Требование "Независимость потребления памяти от размера входного файла" подразумевает заведение значений для расчета и накопление результатов. Однако заранее не известно количество дней. В моём представлении память все равно будет расти от дней (брать на себя вызов `как это сделал Гвидо <https://web.archive.org/web/20200703041750/https://neopythonic.blogspot.com/2008/10/sorting-million-32-bit-integers-in-2mb.html>`_ я не собираюсь в данном случае).
Требование "Независимость потребления памяти от размера входного файла" можно замаскировать ленивыми вычислениями. Генераторы будут в помощь.

Не хотел делать валидацию входных данных. Потом засвербело: вдруг подсунут xml, а у меня либо зависнет, либо на выходе будет не верный результат.
Решил поместить в парсер только те утверждения, на которые потом опирается обработка данных. Там образом обработчики не будут засоряться условиями и будет соблюден принцип: если ``Record`` создали, тогда он корректный.

Собрав все требования о сумме, группировке, фильтрации, мне показалось, что это "мини" движок sql. Вот бы у меня получилось выполнить операции над "строками", а не нагромождение несвязных концепций прибитых гвоздями друг к другу.

"Можно использовать любой фреймворк" - я не совсем понял про какие фреймворки идет речь. Я сделал только одно предположение для себя.
Наверняка, это разработчиков, занимающихся для обработкой данных. Может быть они пишут какие-то конверторы данных на вход pandas, потом заказывают манипуляции с данными с помощью API и получает результат на выходе.

Черт, либо я глуп, либо на трансдюсерах не собрать группировки.


Воплощение
----------

Я ставил перед собой задачу не делать многоуровневые циклы. Был опыт: с ними тяжело.
Результат удовлетворяет требованиям, но я не скажу, что стало как-то сильно понятнее и проще в поддержке.
Приём: сопрограммы (coroutine) для композиции разных обработчиков данных. Pypy будет не доволен.


Из любопытства
==============

А что будет, если скормить моей программе что-то более существенное? Например, сотни мегабайт xml. Да ещё и сопоставить pypy и cpython!
Сотни мегабайтного xml у меня нет - придется написать генератор.

От генератора ``gensample.py`` я хотел получить разнообразие данных. В его реализации присутствуют следующие события:

- по выходным никто не работает
- есть вероятность, что день будет выходным
- есть вероятность невыхода части сотрудников
- есть вероятность того, что сотрудник может заболеть (только сейчас понял, что это пересекается с вышестоящим событием)
- есть вероятность того, что сотрудник может просидеть целый день или разбить интервал рабочего дня до 4 раз
- есть вероятность того, что сотрудник начнет свой день в определенном интервале
- сотрудник отрабатывает в сумме по установленному количеству часов

При 3 годах интервала дат, 500 сотрудников и других параметрах я получил всего 80 МБ данных в xml.

Я не занимался профилирование программ. По первой ссылке из поиска по инструментам замера времени и памяти был выбран time `по совету SO <https://stackoverflow.com/a/774601>`_.

Команда запуска ``./amounttime.py big_sample.xml --filter-by-interval '11-10-2017..08-10-2020' --split-by-person > /dev/null`` из ``measure.sh``.

============================================ ======= =======
Параметр                                     PyPy    CPython
============================================ ======= =======
User time (seconds):                         19.97   33.52
System time (seconds):                       0.43    0.41
Percent of CPU this job got:                 99%     99%
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:20.41 0:33.96
Average shared text size (kbytes):           0       0
Average unshared data size (kbytes):         0       0
Average stack size (kbytes):                 0       0
Average total size (kbytes):                 0       0
Maximum resident set size (kbytes):          1147132 968424
Average resident set size (kbytes):          0       0
Major (requiring I/O) page faults:           0       0
Minor (reclaiming a frame) page faults:      295024  265496
Voluntary context switches:                  1       1
Involuntary context switches:                121     253
Swaps:                                       0       0
File system inputs:                          0       0
File system outputs:                         0       0
Socket messages sent:                        0       0
Socket messages received:                    0       0
Signals delivered:                           0       0
Page size (bytes):                           4096    4096
Exit status:                                 0       0
============================================ ======= =======

Для меня есть радостная находка и совсем печальная.
Меня приятно удивило, что pypy смог переварить генераторы.
Меня огорчило потребление ресурсов. Соотношение 80 МБ исходника к 1 ГБ в памяти - это ужас ужасный.


Моя память
----------

Возможно я ошибся с ET.
Для начала я хочу узнать сколько в памяти занимают чисто результат - это список, редкие строки, частые даты в картежах.
На помощь придет вычитывание файла и ``eval``.
В пике у конкурирующих реализаций получилось за 2 ГБ (по данным того же time 2610976 kbytes). Но при комбинации ``gc.collect(); input()`` htop на моменте ожидания ввода в программе рапортует в колонке ``RES`` всё теже 2 ГБ только для pypy, а для python - 280 МБ.
Странно. Однако есть цель - 280 МБ.

Возвращаемся к ET. Жалко от него отказываться. Есть гипотеза, что ET создает дерево в памяти. Нужно вего лишь избавляться от элементов ``<person>`` своевременно.
Накатываю изменения:

.. code-block:: diff

    diff --git a/amounttime.py b/amounttime.py
    index ffa4553..3eeea7e 100755
    --- a/amounttime.py
    +++ b/amounttime.py
    @@ -5,6 +5,7 @@ from datetime import datetime, timedelta, date
     from collections import defaultdict
     from functools import partial
     import pprint
    +from itertools import chain
     
     
     @dataclass(frozen=True)
    @@ -25,7 +26,12 @@ def parse(file):
         lane = ()
         start = None
         end = None
    -    for (event, element) in ElementTree.iterparse(file, events=('start', 'end',)):
    +    parser = ElementTree.iterparse(file, events=('start', 'end',))
    +    nothing = (None, None)
    +    event, root = next(parser, nothing)
    +    if (event, root) == nothing:
    +        return
    +    for (event, element) in chain(((event, root),), parser):
             if event == 'start':
                 lane += element.tag,
                 if lane not in lanes:
    @@ -44,6 +50,7 @@ def parse(file):
                     yield Record(element.attrib['full_name'], start, end)
                     start = None
                     end = None
    +                root.remove(element)
     
     
     def collect_by_day():

Запуск ``measure.sh`` даёт:

============================================ ======= =======
Параметр                                     PyPy    CPython
============================================ ======= =======
Maximum resident set size (kbytes):          285640  109556
============================================ ======= =======

Все! Работа над ошибками завершена.

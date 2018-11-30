import logging
from pycrontab import CronTab


def fn(a):
    print(a)


def test():
    logging.basicConfig(
        level=logging.DEBUG,
        format='{asctime} {levelname} {name}({processName}|{threadName})>{filename}:{funcName}()#{lineno} : {message}',
        style='{',
    )

    center = CronTab()
    center.add_task('a', '1 1 2 3 *', fn, args=('hello',))
    center.add_task('b', '1 2 3 4 5', fn, args=('world',))
    center.add_task('c', '* * * * *', fn, args=('all',))
    print(list(center))
    center.run()


if __name__ == '__main__':
    test()

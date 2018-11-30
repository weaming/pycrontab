import logging
from pycrontab import CronTab


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='{asctime} {levelname} {name}({processName}|{threadName})>{filename}:{funcName}()#{lineno} : {message}',
        style='{',
    )
    tab = CronTab()
    tab.add_task('a', '1 1 2 3 *', fib, args=(13,))
    tab.add_task('b', '1 2 3 4 5', fib, args=(14,))
    tab.add_task('c', '* * * * *', fib, args=(15,))
    print(list(tab))
    tab.run()

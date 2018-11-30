import time
import logging
import os
from pycrontab.worker import run_command, ThreadWorker, ProcessWorker


def test_thread_worker():
    worker = ThreadWorker()
    worker.add_background_task(run_command, ["ls"], cwd=os.path.expandvars("$HOME"))


def fn(cwd='/'):
    print('zzz')
    time.sleep(3)
    return run_command(['ls'], cwd=cwd)


def test_process_worker():
    worker = ProcessWorker()
    worker.add_func_task(fn, cwd='/')


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='{asctime} {levelname} {name}({processName}|{threadName})>{filename}:{funcName}()#{lineno} : {message}',
        style='{',
    )
    test_process_worker()
    while 1:
        time.sleep(1)

import time
import logging
from pycrontab.worker import run_command, ThreadWorker


def test():
    worker = ThreadWorker()
    worker.add_background_task(run_command, ["ls"], cwd="$HOME")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test()
    while 1:
        time.sleep(1)

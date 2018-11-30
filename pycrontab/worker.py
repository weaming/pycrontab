import logging
import subprocess
import queue
import threading
import datetime
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from .log import logger


def run_command(
    command, stderr=None, redirect_stderr=False, cwd=None, environment: dict = None
):
    assert isinstance(command, list), "command must be a list of string"
    if stderr is None:
        if redirect_stderr:
            stderr = subprocess.STDOUT
        else:
            stderr = subprocess.PIPE

    try:
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=stderr,
            cwd=cwd,
            env=environment,
            encoding="utf8",
        )
    except Exception as e:
        logger.warning(e)
        return 1, None, str(e)

    while True:
        if proc.poll() is not None:
            break

    stdout_str = proc.stdout and proc.stdout.read()
    stderr_str = proc.stderr and proc.stderr.read()

    rv = proc.returncode, stdout_str, stderr_str
    logger.debug(f"result of command {command} is {rv}")
    return rv


def thread_spawn(target, name: str, daemon=True, args=(), kwargs=None):
    thread = threading.Thread(
        target=target, name=name, daemon=daemon, args=args, kwargs=kwargs
    )
    thread.start()
    return thread


def run_in_thread(func, name=None):
    """run function in thread"""
    thread_spawn(
        func, name or "{} {}".format(func.__name__, str(datetime.datetime.now()))
    )


class ThreadWorker(object):
    def __init__(self, pool_size=8, queue_size=0):
        """
        :param pool_size:
        :param queue_size: If <= 0, the queue size is infinite.
        """
        self.pool_size = pool_size + 1  # one to run self.poll_tasks
        self.executor = None

        # for background poll
        self.done = False
        self._q = queue.Queue(queue_size)

        self.thread = None

    def run_in_thread_pool(self, func, *args, **kwargs):
        future = self.executor.submit(func, *args, **kwargs)
        return future

    def poll_tasks(self):
        while not self.done:
            task = self._q.get()
            self.run_in_thread_pool(task)
            logger.debug(f"start running {task}")

    def ensure_started(self):
        if self.thread is None:
            self.executor = ThreadPoolExecutor(max_workers=self.pool_size)
            self.thread = thread_spawn(self.poll_tasks, name="background_tasks_poll")

    def add_background_task(self, func, *args, **kwargs):
        self.ensure_started()

        @wraps(func)
        def new_func():
            func(*args, **kwargs)

        self._q.put(new_func)
        logger.debug(f"added task {func} {args} {kwargs}")


class ProcessWorker:
    def __init__(self, size=None):
        self.pool_size = size
        self.pool = None

    def callback(self, rv):
        logger.info(rv)

    def error_callback(self, err):
        logger.info(err)

    def ensure_inited(self):
        if not self.pool:
            self.pool = Pool(self.pool_size)

    def add_func_task(self, func, *args, **kwargs):
        self.ensure_inited()
        self.pool.apply_async(
            func,
            args=args,
            kwds=kwargs,
            callback=self.callback,
            error_callback=self.error_callback,
        )

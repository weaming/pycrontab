from typing import Callable, List, Set
from datetime import datetime, timedelta
import time
from .worker import ThreadWorker
from .event import Event
from .errors import *

WORKER = ThreadWorker()

_ranges = [
    # (0, 59),  # seconds
    (0, 59),  # min
    (0, 23),  # hour
    (1, 31),  # day
    (1, 12),  # month
    (0, 6),  # day of week
    (1970, 2099),  # year
]

_aliases = {
    '@yearly': '0 0 1 1 *',
    '@annually': '0 0 1 1 *',
    '@monthly': '0 0 1 * *',
    '@weekly': '0 0 * * 0',
    '@daily': '0 0 * * *',
    '@hourly': '0 * * * *',
    '@minutely': '* * * * *',
}


def range_to_set(rg, step=1):
    return set(range(rg[0], rg[1] + 1, step))


def parse_cron(cron: str, must_contains_year=False) -> List[Set]:
    items = cron.split()
    if not items:
        raise InvalidCron(cron)
    if items[0].startswith('@'):
        if items[0] in _aliases:
            return parse_cron(_aliases[items[0]])
        else:
            raise InvalidCron(cron)

    if len(items) < 5:
        raise InvalidCron(cron)

    # append year
    if must_contains_year and len(items) == 5:
        items.append("*")

    rv = []
    for which, cron in enumerate(items):
        and_set = cron.split(',')
        values = set()
        for c in and_set:
            if c == '*':
                v = range_to_set(_ranges[which])
            elif c.startswith('*/'):
                v = range_to_set(_ranges[which], step=int(c[2:]))
            else:
                v = [int(c)]

            values |= set(v)
        rv.append(values)
    return rv


class Job:
    def __init__(self, name, fn: Callable, cron: str):
        self.name = name
        self.fn = fn
        self.cron = cron

    def start(self):
        """start without waiting"""
        WORKER.add_background_task(self.fn)

    def __repr__(self):
        return f"<task(name={self.name}, fn={self.fn}, cron='{self.cron}')>"


class CronTab:
    def __init__(self):
        # {<name>: <event>}
        self.crontab = {}

    def add_task(self, name: str, cron: str, fn: Callable):
        cron_args = parse_cron(cron)
        job = Job(name, fn, cron=cron)
        event = Event(job.start, *cron_args)
        event.job = job

        if name in self.crontab:
            raise DuplicateTaskName(name)
        self.crontab[name] = event
        return event

    def run(self):
        while 1:
            t = datetime(*datetime.now().timetuple()[:5])
            for cron in self.crontab.values():
                cron.check(t)

            # have one minutes to fire the checks, or may be later for firing actions on next minute
            t += timedelta(minutes=1)
            while datetime.now() < t:
                time.sleep((t - datetime.now()).seconds)

    def __iter__(self):
        for event in self.crontab.values():
            yield event

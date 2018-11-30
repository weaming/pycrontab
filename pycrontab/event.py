class AllMatch(set):
    """Universal set - match everything"""

    def __contains__(self, item):
        return True


allMatch = AllMatch()


def convert_to_set(obj):
    # Allow single integer to be provided
    if isinstance(obj, int):
        return {obj}  # Single item
    if not isinstance(obj, set):
        obj = set(obj)
    return obj


class Event(object):
    def __init__(
            self, action, min=allMatch, hour=allMatch,
            day=allMatch, month=allMatch,
            dow=allMatch, year=allMatch,
            args=(), kwargs=None,
    ):
        self.mins = convert_to_set(min)
        self.hours = convert_to_set(hour)
        self.days = convert_to_set(day)
        self.months = convert_to_set(month)
        self.dow = convert_to_set(dow)
        self.years = convert_to_set(year)

        # action of time event
        self.action = action
        self.args = args
        self.kwargs = kwargs or {}

        # the action will be a method of job, added here for reference
        self.job = None

    def match_time(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return ((t.minute in self.mins) and
                (t.hour in self.hours) and
                (t.day in self.days) and
                (t.month in self.months) and
                (t.weekday() in self.dow) and
                (t.year in self.years))

    def check(self, t):
        if self.match_time(t):
            self.action(*self.args, **self.kwargs)

    def __repr__(self):
        return f"<Event([{self.mins}, {self.hours}, {self.days}, {self.months}, {self.dow}, {self.years}], {self.job})>"

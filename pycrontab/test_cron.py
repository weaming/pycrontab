from cbss_cron.cron import CronTab


def get_fn(a):
    def f():
        print(a)

    return f


center = CronTab()
center.add_task('a', '1 1 2 3 *', get_fn('hello'))
center.add_task('b', '1 2 3 4 5', get_fn('world'))
center.add_task('c', '* * * * *', get_fn('all'))
print(list(center))
center.run()

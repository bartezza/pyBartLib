
import json
import threading
import copy
import logging
import sys
import traceback
import schedule
from functools import wraps


g_key_value_use_update_end = True


def init_logging(debug_ibinsync: bool = False, default_level: str = logging.INFO):
    # use colored logs
    import coloredlogs
    # configuration guide: https://pypi.org/project/coloredlogs/#format-of-log-messages
    # coloredlogs.install()
    # coloredlogs.install(fmt='%(asctime)s,%(msecs)03d %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s')
    coloredlogs.install(fmt='[%(name)s %(levelname)s]  %(message)s', stream=sys.stdout, level=logging.DEBUG)

    # default level
    logging.getLogger("root").setLevel(default_level)

    # change logging level
    new_log_level = logging.WARNING
    loggers = [
        "ibapi",
        "matplotlib"
    ]
    for i in loggers:
        logging.getLogger(i).setLevel(new_log_level)

    if not debug_ibinsync:
        logging.getLogger("ib_insync.client").setLevel(logging.INFO)
        logging.getLogger("ib_insync.wrapper").setLevel(logging.WARNING)


def format_expiration(expir, short=False):
    if expir is not None:
        if short:
            return expir.strftime("%d-%m-%Y")
        else:
            return expir.strftime("%d %b %Y")
    else:
        return None


def format_float(num):
    return "{0:.2f}".format(num)


def format_perc(num):
    return "{0:.2f} %".format(num * 100.0)


def format_pos_sign(sign):
    if sign > 0.0:
        return "long"
    else:
        return "short"


# import concurrent.futures
# from asyncio import coroutines, futures
# def run_coroutine_threadsafe_my(coro, loop):
#     """Submit a coroutine object to a given event loop.
#         Return a concurrent.futures.Future to access the result.
#     """
#     if not coroutines.iscoroutine(coro):
#         raise TypeError('A coroutine object is required')
#     future = concurrent.futures.Future()
#
#     def callback():
#         print("DA CALLBACK")
#         try:
#             print("BEFORE CHAINFUTURE")
#             futures._chain_future(asyncio.ensure_future(coro, loop=loop), future)
#             print("AFTER CHAINFUTURE")
#         except Exception as exc:
#             if future.set_running_or_notify_cancel():
#                 future.set_exception(exc)
#             raise
#         print("FINISHING")
#
#     print("BEFORE CALLSOON")
#     loop.call_soon_threadsafe(callback)
#     print("AFTER CALLSOON")
#     return future


def dump_exception():
    traceback.print_exc()


class KeyValueStore:
    def __init__(self):
        self.update_time = None
        self.updating = False
        self.data = {}
        self.lock = threading.Lock()

    def set_value(self, key, value, currency):
        if g_key_value_use_update_end:
            if not self.updating:
                self.data = {
                    key: value
                }
                self.updating = True
                self.lock.acquire()
            else:
                self.data[key] = (value, currency)
            # self.lock.release()
        else:
            self.lock.acquire()
            self.data[key] = (value, currency)
            self.lock.release()

    def update_end(self):
        self.updating = False
        if g_key_value_use_update_end:
            self.lock.release()

    def get_data(self, to_string=False):
        self.lock.acquire()
        data = copy.deepcopy(self.data)
        self.lock.release()
        # add currency or keep tuples?
        if to_string:
            data2 = {}
            for k, v in data.items():
                if len(v) == 2:
                    data2[k] = "{} {}".format(v[0], v[1])
                else:
                    data2[k] = "{}".format(v[0])
            return data2
        else:
            return data


def add_weekday_schedule(hours, min_start, min_end, job):
    for hour in hours:
        for idx in range(min_start, min_end + 5, 5):
            what = "{:02}:{:02}".format(hour, idx)
            schedule.every().monday.at(what).do(job)
            schedule.every().tuesday.at(what).do(job)
            schedule.every().wednesday.at(what).do(job)
            schedule.every().thursday.at(what).do(job)
            schedule.every().friday.at(what).do(job)


def add_day_schedule(hours, min_start, min_end, job):
    for hour in hours:
        for idx in range(min_start, min_end + 5, 5):
            what = "{:02}:{:02}".format(hour, idx)
            schedule.every().day.at(what).do(job)


def cached(filename: str = "func"):
    def cached_dec(func):
        @wraps(func)
        def inner_func(*args, **kwargs):
            filename2 = f"{filename}.json"
            # print(f'Before Calling {func.__name__}')
            if os.path.isfile(filename2):
                with open(filename2, "r") as fp:
                    ret = json.load(fp)
                print(f"Loaded results of {func.__name__} from cache file {filename2}")
            else:
                ret = func(*args, **kwargs)
                with open(filename2, "w") as fp:
                    json.dump(ret, fp, indent=2)
                print(f"Saved results of {func.__name__} to cache file {filename2}")
            # print(f'After Calling {func.__name__}')
            return ret
        return inner_func
    return cached_dec

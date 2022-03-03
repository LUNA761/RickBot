"""
Copyright (c) 2022, Zach Lagden
All rights reserved.
"""

import re
import time
import os
from typing import Union
from configparser import ConfigParser

config = ConfigParser()
config.read('./rickconfig.ini')


def bot_owner(ctx):
    return ctx.author.id == int(config.get("RICK", "owner"))


def rmtree_error(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def unix() -> int:
    return int(time.time())


def trim(string: str, max_length: int = 250) -> str:
    return string[: max_length - 3] + "..." if len(string) > max_length else string


def plural(amount: Union[int, float], string: str, *, s: str = "s", comma: bool = True) -> str:
    if abs(amount) == 1:
        s = ""
    if comma:
        return f"{amount:,} {string}{s}"
    return f"{amount} {string}{s}"


def perms_format(perms):
    if type(perms) == list:
        return list(map(perms_format, perms))
    elif type(perms) == str:
        perms = re.sub(r"_", " ", perms)
        return perms.title()
    else:
        return None


def format_time(sec: Union[int, float], *, short: bool = True) -> str:
    if sec <= 0:
        return f'0{"s" if short else " seconds"}'

    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    mo, d = divmod(d, 30)
    y, mo = divmod(mo, 12)
    y, mo, d, h, m, s = int(y), int(mo), int(d), int(h), int(m), int(s)

    if y > 100:
        return f'> 100{"y" if short else " years"}'

    if short:
        mapping = ((y, "y"), (mo, "mo"), (d, "d"), (h, "h"), (m, "m"), (s, "s"))
    else:
        mapping = (
            (y, "year"),
            (mo, "month"),
            (d, "day"),
            (h, "hour"),
            (m, "minute"),
            (s, "second"),
        )
    return ", ".join(
        f'{m[0]}{"" if short else " "}{m[1]}{"s" if m[0] != 1 and not short else ""}'
        for m in mapping
        if m[0] > 0
    )


class Timer:
    def __init__(self):
        self._start = None
        self._end = None

    def start(self):
        self._start = time.perf_counter()

    def stop(self):
        self._end = time.perf_counter()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __int__(self):
        return round(self.time)

    def __float__(self):
        return self.time

    def __str__(self):
        return str(self.time)

    def __repr__(self):
        return f"<Timer time={self.time}>"

    @property
    def time(self):
        if self._end is None:
            raise ValueError("Timer has not been ended.")
        return self._end - self._start

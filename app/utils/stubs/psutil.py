"""
Stub implementation of psutil for when the real module is not installed.
"""

import logging

logger = logging.getLogger(__name__)
logger.warning("Using stub psutil module. System metrics may be incorrect.")


def virtual_memory():
    class VM:
        total = 0
        available = 0
        percent = 0.0

    return VM()


def disk_usage(path):
    class DU:
        total = 0
        free = 0
        percent = 0.0

    return DU()


def cpu_percent(interval=None):
    return 0.0


def cpu_count(logical=True):
    return 1


class Process:
    def memory_info(self):
        class MI:
            rss = 0

        return MI()

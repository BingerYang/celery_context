import logging
import sys

from celery._state import get_current_task
from celery.utils.log import ColorFormatter
from celery.signals import after_setup_logger

from .model import Celery


class TaskFormatter(ColorFormatter):
    """Formatter for tasks, adding the trace_id, task_name and task_id"""

    def format(self, record):
        task = get_current_task()
        if task and task.request:
            record.__dict__.update(
                task_id=task.request.id,
                task_name=task.name,
                **{Celery.TRACE_FIELD: task.request.content.get(Celery.TRACE_FIELD, '???')}
            )
        else:
            record.__dict__.setdefault(Celery.TRACE_FIELD, "???")
            record.__dict__.setdefault('task_name', "???")
            record.__dict__.setdefault('task_id', "???")
        return ColorFormatter.format(self, record)


def __setup_celery_format(logger, loglevel, format, colorize, **kwargs):
    _formatter = TaskFormatter(format, colorize)
    for index, _handler in enumerate(logger.handlers):
        if getattr(_handler, 'stream', None):
            logger.handlers[index].setFormatter(_formatter)
            break
    else:
        handler = logging.StreamHandler(sys.stderr)
        logger.addHandler(handler)


@after_setup_logger.connect
def _after_setup_logger(*args, **kwargs):
    __setup_celery_format(**kwargs)

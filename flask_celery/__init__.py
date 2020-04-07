# -*- coding: utf-8 -*-
# @Time     : 2020-02-07 11:26
# @Author   : binger

name = "flask_celery_context"
version_info = (0, 0, 1, 20040717)
__version__ = ".".join([str(v) for v in version_info])
__description__ = '实现celery在flask下的上下文一致性的简单扩展'

from .model import Celery, reload_celery_task

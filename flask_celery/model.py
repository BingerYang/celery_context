# -*- coding: utf-8 -*-
# @Time     : 2020-02-07 11:26
# @Author   : binger

__all__ = ["reload_celery_task", "Celery"]
from celery import Celery as CeleryBase

# 在异步处理时使用，如下：
# from celery import current_task
# current_task.request.content
from celery.worker import request as celery_request


class Request(celery_request.Request):
    def __init__(self, message, *args, **kwargs):
        super(Request, self).__init__(message, *args, **kwargs)
        self._request_dict["content"] = message.properties.get("content", {})

    @property
    def content(self):
        return self._request_dict["content"]


celery_request.Request = Request

# 使产生的任务，带有 content 内容值， content 位于重载的 celery.Task 实例中
from celery.app import task

task.extract_exec_options = task.mattrgetter(
    'queue', 'routing_key', 'exchange', 'priority', 'expires',
    'serializer', 'delivery_mode', 'compression', 'time_limit',
    'soft_time_limit', 'immediate', 'mandatory', 'content',  # imm+man is deprecated
)


def reload_celery_task(celery, app=None, setup_task_context_cb=None):
    class ContextTask(celery.Task):
        abstract = True
        content = {}

        def __call__(self, *args, **kwargs):
            if app:
                with app.app_context():
                    return super(ContextTask, self).__call__(*args, **kwargs)
            else:
                return super(ContextTask, self).__call__(*args, **kwargs)

        def set_task_context(self, f, *args, **kwargs):
            f = f or getattr(celery, "_setup_task_context_cb", None)
            if f:
                data = f(*args, **kwargs) or {}
                self.content.update(data)

        def apply_async(self, args=None, kwargs=None, task_id=None, **rest):
            self.set_task_context(setup_task_context_cb)
            return super(ContextTask, self).apply_async(args, kwargs, task_id, **rest)

        def apply(self, args=None, kwargs=None, task_id=None, **rest):
            self.set_task_context(setup_task_context_cb)
            return super(ContextTask, self).apply(args, kwargs, task_id, **rest)

        def retry(self, args=None, kwargs=None, task_id=None, **rest):
            self.set_task_context(setup_task_context_cb)
            return super(ContextTask, self).retry(args, kwargs, task_id, **rest)

    setattr(celery, 'Task', ContextTask)


class Celery(CeleryBase):
    _setup_task_context_cb = None

    def __init__(self, app=None, *args, **kwargs):
        super(Celery, self).__init__(*args, **kwargs)
        if app:
            self.init_app(app)

    def init_app(self, app):
        # Instantiate celery and read config.
        super(Celery, self).__init__(app.import_name, broker=app.config['CELERY_BROKER_URL'])

        # Set result backend default.
        if 'CELERY_RESULT_BACKEND' in app.config:
            self._preconf['CELERY_RESULT_BACKEND'] = app.config['CELERY_RESULT_BACKEND']

        self.conf.update(app.config)
        self.reload_task(app)

    def setup_task_context(self, f):
        self._setup_task_context_cb = f

    def reload_task(self, app):
        reload_celery_task(self, app, self._setup_task_context_cb)

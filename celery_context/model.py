# -*- coding: utf-8 -*-
# @Time     : 2020-02-07 11:26
# @Author   : binger

__all__ = ('set_task_context_under_flask', "reload_celery_task", "Celery")

# 在异步处理时使用，如下：
from celery import current_task
# current_task.request.content
from celery import Celery as CeleryBase
from celery.worker import request as celery_request


class Request(celery_request.Request):
    # at celery Worker
    def __init__(self, message, *args, **kwargs):
        super(Request, self).__init__(message, *args, **kwargs)
        self._request_dict["content"] = message.properties.get("content", {})

    @property
    def content(self):
        # 保证在触发器传递的content信息，可被worker获取
        return self._request_dict["content"]


celery_request.Request = Request

# celery 与 celery 均可能使用到
# 存储 content 使celery worker运营时，可获取 content 传递的内容
# 使产生的任务，带有 content 内容值， content 位于重载的 celery.Task 实例中
from celery.app import task

task.extract_exec_options = task.mattrgetter(
    'queue', 'routing_key', 'exchange', 'priority', 'expires',
    'serializer', 'delivery_mode', 'compression', 'time_limit',
    'soft_time_limit', 'immediate', 'mandatory', 'content',  # imm+man is deprecated
)


def reload_celery_task(celery, app=None, setup_task_context_cb=None):
    # at flask or celery worker 触发新异步时
    class ContextTask(celery.Task):
        abstract = True
        content = {}

        def __call__(self, *args, **kwargs):
            if app is not None:
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
    TRACE_FIELD = 'trace_id'
    _setup_task_context_cb = None

    def __init__(self, *args, **kwargs):
        self.__sig_work_init = None
        app = kwargs.get("app", None)
        if app:
            self.init_app(app)
        else:
            super(Celery, self).__init__(*args, **kwargs)

    def init_app(self, app):
        # Instantiate celery and read config.
        super(Celery, self).__init__(app.import_name, broker=app.config.get('CELERY_BROKER_URL', None))

        # Set result backend default.
        if 'CELERY_RESULT_BACKEND' in app.config:
            self._preconf['CELERY_RESULT_BACKEND'] = app.config['CELERY_RESULT_BACKEND']
            app.config['result_backend'] = app.config['CELERY_RESULT_BACKEND']

        # self.conf.update(app.config)
        self.reload_task(app)

    def setup_task_context(self, f):
        self._setup_task_context_cb = f

    def reload_task(self, app):
        reload_celery_task(self, app, self._setup_task_context_cb)

    def add_flask_content(self, app, setup_task_context_cb=None):
        setup_task_context_cb = setup_task_context_cb or set_task_context_under_flask
        if setup_task_context_cb:
            self.setup_task_context(setup_task_context_cb)
        self.reload_task(app)
        return app


def set_task_context_under_flask(*args, **kwargs):
    trace_id_key = Celery.TRACE_FIELD
    from flask import request

    trace_id = "???"
    try:
        # 保证从web导入的统一标识输入
        trace_id = getattr(request, trace_id_key, None)
    except RuntimeError as e:
        if current_task:
            trace_id = current_task.request.content.get(trace_id_key, None)
    return {trace_id_key: trace_id}

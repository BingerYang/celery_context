celery_context
==============

Documentation
-------------

The documentation is hosted at https://github.com/BingerYang/celery_context


Installation
------------

.. code:: shell

     pip install celery_context

Usage
-----

example:

::


    # -*- coding: utf-8 -*-
    from flask import Flask
    from celery_context import Celery
    from flask import request

    config = dict(redis={"host": "*****", "port": 31320, "password": "lab@2019"})
    redis_url = "redis://:{password}@{host}:{port}".format(**config["redis"])
    app = Flask("example.run")
    app.config['CELERY_BROKER_URL'] = "{}/1".format(redis_url)
    app.config['CELERY_RESULT_BACKEND'] = "{}/2".format(redis_url)
    celery = Celery(app=app)
    celery.setup_task_context(lambda: dict(path=request.path))


    @celery.task(bind=True)
    def add(self, a, b):
        print("a+ n:", a + b, self.request.content)
        return a + b


    @app.route("/")
    def index():
        ret = add.delay(1, 3)
        print(ret.get())
        return ret.id


    if __name__ == "__main__":
        app.run()

# celery_context

## Documentation
The documentation is hosted at [https://github.com/BingerYang/celery_context](https://github.com/BingerYang/celery_context)

## Installation
```shell
 pip install flask_celery_context
```
## Usage
adding the trace_id, task_name and task_id at celery log format

```python
# -*- coding: utf-8 -*- 
# at flask
from flask import Flask
from celery_context import Celery
from flask import request
from .. import celery_settings  # 存放celery 配置的文件
"""celery_settings
worker_log_format = '[%(trace_id)s%(task_name)s%(task_id)s%(process)s %(thread)s %(asctime)s %(pathname)s:%(lineno)s] %(levelname)s: %(message)s'
worker_task_log_format = worker_log_format
"""


config = dict(redis={"host": "*****", "port": 31320, "password": "lab@2019"})
redis_url = "redis://:{password}@{host}:{port}".format(**config["redis"])
app = Flask("example.run")
#app.config['CELERY_BROKER_URL'] = "{}/1".format(redis_url)
#app.config['CELERY_RESULT_BACKEND'] = "{}/2".format(redis_url)
celery = Celery(app=app, broker=redis_url, backend=redis_url)
celery.config_from_object(celery_settings)
celery.add_flask_content(app)

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

```

import os
from setuptools import setup, find_packages
from flask_celery import name, __description__, __version__

# read dev requirements
fname = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(fname) as f:
    install_requires = [l.strip() for l in f.readlines()]
root = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

with open("MAINTAINERS") as f:
    lines = [l.strip() for l in f.readlines()]
    author, author_email = lines[0].split(sep=" ")
    if len(lines) > 1:
        maintainer, maintainer_email = lines[1].split(sep=" ")
    else:
        maintainer, maintainer_email = author, author_email

setup(
    name=name,
    version=__version__,
    packages=find_packages(exclude=['examples', 'tests']),
    url='https://github.com/BingerYang/{}'.format(root),
    license='',
    author=author,
    author_email=author_email,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    description=__description__,
    long_description=open('README.rst', encoding='utf-8').read(),
    long_description_content_type="text/x-rst",

    python_requires='>=3.4',
    platforms=['all'],
    include_package_data=True,
)

from setuptools import setup, find_packages
import os

name = "photo_chooser"
version = "0.1"


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name=name,
    version=version,
    description="Photo viewer",
    long_description=read('README.md'),
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[],
    keywords="",
    author="Tomasz Maćkowiak",
    author_email='kurazu@kurazu.net',
    url='',
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Pillow',
        'exifread'
    ],
    entry_points="""
    [console_scripts]
    photo_chooser = photo_chooser.main:startup
    """
)

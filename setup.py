import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE/"README.md").read_text()

setup(
    name='colordict',
    version='1.2.5',
    packages=['colordict'],
    url='https://github.com/aleferna12/colordict',
    license='MIT',
    author='aleferna',
    description='A package to allow for easy maintenance of a color dictionary with palettes, so you can use the colors that you like in your different projects.',
    long_description=README,
    long_description_content_type="text/markdown",
    include_package_data=True,
)

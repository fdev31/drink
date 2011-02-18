import setuptools
from setuptools import setup, find_packages

setup(
    name="drink",
    version="0.0.5",
    author="Fabien Devaux",
    author_email="fdev31@gmail.com",
    license="GPL",
    platform="all",
    description="High-level micro CMS inspired by BlueBream (Zope) and Django, with simplicity of use & extend in mind. Based on ZODB & bottle.",
    long_description=open('README.rst').read(),
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        "console_scripts": [
            'drink = drink:startup',
            ],
        "setuptools.installation" : [
            'eggsecutable = drink:startup'
            ]
        },
    packages=find_packages(),
    install_requires = ['jinja2', 'markdown', 'ZODB3', 'whoosh'],
)


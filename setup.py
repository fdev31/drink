import setuptools
from setuptools import setup, find_packages

setup(
    name="drink",
    version="0.0.1",
    author="Fabien Devaux",
    author_email="fdev31@gmail.com",
    license="BSD",
    platform="all",
    description="my web sandbox (ZODB + Bottle)",
    long_description="""
    Drink
    =====

    Alpha program, base for a lightweight CMS / Intranet / etc...
    """,
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
    install_requires = ['jinja2', 'markdown', 'ZODB3'],
)


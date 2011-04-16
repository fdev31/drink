try:
    import setuptools
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages

setup(
    name="drink",
    version="0.0.10",
    author="Fabien Devaux",
    author_email="fdev31@gmail.com",
    license="GPL",
    platform="all",
    description="High-level Web Object-managing framework on top of ZODB and Jinja2",
    long_description=open('README.rst').read(),
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        "console_scripts": [
            'drink = drink:startup',
            ],
        "setuptools.installation" : [
            'eggsecutable = drink:startup'
            ],
        "zodbupdate": [
            'renames = drink.migration:database_renames',
        ]

        },
    packages=find_packages(),
    install_requires = ['setuptools', 'jinja2', 'markdown', 'ZODB3', 'whoosh', 'fs'],
)

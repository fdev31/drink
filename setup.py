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
    install_requires = ['setuptools', 'jinja2', 'markdown', 'ZODB3', 'whoosh>=2.2', 'fs>=0.3', 'bottle>=0.9.6'],
)
# mkvirtualenv foo --no-site-packages
# source foo/bin/activate
# foo/bin/pip install  bottle jinja2 markdown ZODB3 whoosh fs || (echo "Basic dependencies installation failed!" ; exit 1)
# foo/bin/pip install setproctitle
# foo/bin/pip install repoze.debug
# foo/bin/pip install weberror
# foo/bin/pip install gevent
# foo/bin/pip install Paste
# foo/bin/pip install bjoern

try:
    import setuptools
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()

import os
import re
from setuptools import setup, find_packages

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements

def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))

    return dependency_links

setup(
    name="drink",
    version="0.0.10",
    author="Fabien Devaux",
    author_email="fdev31@gmail.com",
    license="GPL",
    platform="all",
    description="High-level Web Object-managing framework on top of ZODB and Jinja2",
    long_description=open(os.path.join('drink_defaults', 'README.rst')).read(),
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
    install_requires = parse_requirements('requirements.txt'),
    dependency_links = parse_dependency_links('requirements.txt'),
)


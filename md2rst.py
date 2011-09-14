#!/usr/bin/env python2
# equivalent to
# markdown README.md -e utf-8 | ./html2rst.py > README.rst
import markdown
import html2rst

md = markdown.Markdown()
html = md.convert(open('README.md').read())
open('README.rst', 'w').write(html2rst.html2text(html))

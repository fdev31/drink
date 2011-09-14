#!/usr/bin/env python2
# equivalent to
# markdown README.md -e utf-8 -x tables -x wikilinks -x fenced_code -x toc -x def_list | ./html2rst.py > README.rst
import sys
import markdown
import html2rst

md = markdown.Markdown(
            extensions = ['tables', 'fenced_code', 'toc', 'def_list', 'codehilite(force_linenos=True)'],
            extension_configs = {
                "codehilite": ("force_linenos", True),
                }
            )
html = md.convert(open(sys.argv[1] if len(sys.argv) > 1 else 'README.md').read())
open('/tmp/x', 'w').write(html)
print html2rst.html2text(html).decode('utf-8')

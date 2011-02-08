#!/usr/bin/env python
import os
from drink import init, startup, db

if __name__ == "__main__":
    if not 'BOTTLE_CHILD' in os.environ:
        if len(db.db.open().root()) < 3: # users, groups + pages at least
            init()

    startup()

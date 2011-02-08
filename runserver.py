#!/usr/bin/env python

if __name__ == "__main__":
    from drink import init, startup, db
    if len(db.db.open().root()) == 0:
        init()
    startup()

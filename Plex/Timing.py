"""Platform independent-ish timing routines for speed testing."""

import os
import sys

if hasattr(os, 'times'):
    def time():
        t = os.times()
        return t[0] + t[1]
    timekind = 'cpu'
elif sys.platform == 'mac':
    # Fallback for older Mac versions of python
    import MacOS
    def time():
        return MacOS.GetTicks() / 60.0
    timekind = 'real'
else:
    sys.stderr.write("Don't know how to get time on platform %s\n"
                     % repr(platform))
    sys.exit(1)


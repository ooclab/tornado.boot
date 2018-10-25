#!/bin/bash

RESULT_PATH=$(python3 -c 'import os, nose2; print(os.path.join(os.path.dirname(nose2.__file__), "plugins/result.py"))')
# support sed in linux and macos
sed \
    -e '/self._report.*reportSuccess/s@ok@\\033[92m\\u2713\\033[0m@' \
    -e '/self._report.*reportError/s@ERROR@\\033[91m\\u2718\\033[0m@' \
    -e 's@desc = .*doc_first_line.*@desc = doc_first_line@' \
    ${RESULT_PATH} > /tmp/_result.py
mv /tmp/_result.py ${RESULT_PATH}

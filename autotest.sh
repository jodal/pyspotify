#! /bin/sh
#
# Runs tests on changes to the spotify/ and tests/ dirs. Any arguments are
# passed on to nosetests.
#
# The script requires a Linux system with inotify-tools.
#

while true; do
    clear;
    python setup.py build --with-mock \
        && PYTHONPATH=$(echo build/lib.linux-*/) nosetests $@;
    inotifywait -e modify -e create -e delete -r \
        --exclude "\..*\.sw." spotify/ tests/;
done

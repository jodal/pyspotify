.PHONY: autotest build clean default install test

BUILD_DIR="build/lib/"
PYTHON ?= python
NOSETESTS ?= nosetests

default: build

clean:
	@rm -rf build/

build: clean
	@$(PYTHON) setup.py build --with-mock --build-lib ${BUILD_DIR}

test: build
	@PYTHONPATH=${BUILD_DIR} $(NOSETESTS)

autotest: build
	@which inotifywait || (echo "inotifywait not found"; exit 1)
	@while true; do \
	  clear; \
	  PYTHONPATH=${BUILD_DIR} $(NOSETESTS); \
	  inotifywait -q -e create -e modify -e delete \
	    --exclude ".*\.(pyc|sw.)" \
	    -r spotify/ src/ tests/; \
	done

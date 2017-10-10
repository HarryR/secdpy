PYTHON ?= python

all: test

test:
	$(PYTHON) test.py tests/*.lsp | $(PYTHON) test.py | $(PYTHON) test.py


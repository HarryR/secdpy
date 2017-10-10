PYTHON ?= python
SECD = $(PYTHON) -msecd

all: test repl

test:
	$(SECD).test tests/*.lsp | $(SECD).test | $(SECD).test

repl:
	$(SECD).repl

clean:
	find . -name '*.pyc' | xargs rm -f


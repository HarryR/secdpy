PYTHON ?= python
SECD = $(PYTHON) -msecd
PYLINT = $(PYTHON) -mpylint

all: test repl

test:
	$(SECD).test tests/*.lsp 

testtest:
	$(SECD).test tests/*.lsp | $(SECD).test | $(SECD).test

lint:
	$(PYLINT) secd

repl:
	$(SECD).repl

clean:
	find . -name '*.pyc' | xargs rm -f


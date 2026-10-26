PREFIX ?= $(HOME)/.local

compfile=share/bash-completion/completions/_compget


install-dev:
	python3 -m pip install --user -e .
	ln -s $(PWD)/$(compfile) $(PREFIX)/$(compfile)

install:
	python3 -m pip install --user .
	install -D $(PREFIX)/share/bash-completion/completions
	install $(compfile) $(PREFIX)/$(compfile)

uninstall:
	python3 -m pip uninstall comptest
	rm -f $(PREFIX)/$(compfile)

# The file is tracked
compfile:
	PYTHONPATH=$(PWD)/src/python GENERATE_COMPLETION=1 \
	    python3 -c "import comptest.compget; comptest.compget.main()" > $(compfile)

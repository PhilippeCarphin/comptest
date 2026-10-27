PREFIX ?= $(HOME)/.local

compfile=share/bash-completion/completions/_compget
pythonpath = PYTHONPATH=$(PWD)/src/python3


install-dev: compfile
	python3 -m pip install -e .
	ln -sf $(PWD)/$(compfile) $(PREFIX)/$(compfile)

install: compfile
	python3 -m pip install -e .
	install -D $(PREFIX)/share/bash-completion/completions
	install $(compfile) $(PREFIX)/$(compfile)

uninstall:
	python3 -m pip uninstall comptest
	rm -f $(PREFIX)/$(compfile)

# The file is tracked
compfile:
	$(pythonpath) GENERATE_COMPLETION=1 \
	    python3 -c "import comptest.compget; comptest.compget.main()" > $(compfile)

examples/salad/_salad:
	$(pythonpath) GENERATE_COMPLETION=1 \
	    python3 examples/salad/salad.py >$@
demo-compgen: examples/salad/_salad
demo-compget: examples/salad/_salad
	@printf "\033[1;36mGetting completions for arguments to --vegetable\033[0m\n"
	bin/compget --load-bash-completion --init-files $< -- 'salad --vegetable '
	@printf "\033[1;36mGetting options for command\033[0m\n"
	bin/compget --load-bash-completion --init-files $< -- 'salad --'
demo-comptest: examples/salad/_salad
	python3 examples/salad/test-salad-comp.py

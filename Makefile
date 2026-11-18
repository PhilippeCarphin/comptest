PREFIX ?= $(HOME)/.local

compget_functions=share/bash-completion/completions/compget_functions.bash
compfile=share/bash-completion/completions/compget
pythonpath = PYTHONPATH=$(PWD)/src/python

all: new

install-dev: compfile
	python3 -m pip install -e .
	mkdir -p $(PREFIX)/share/bash-completion/completions
	ln -sf $(PWD)/$(compfile) $(PREFIX)/$(compfile)

install: compfile
	python3 -m pip install -e .
	install -D $(PREFIX)/share/bash-completion/completions
	install $(compfile) $(PREFIX)/$(compfile)

uninstall:
	python3 -m pip uninstall comptest
	rm -f $(PREFIX)/$(compfile)


# The file is tracked
compfile: $(compfile)
$(compfile): src/python/compgen/compgen.py $(compget_functions)
	$(pythonpath) GENERATE_COMPLETION=1 \
	    python3 -c "import comptest.compget; comptest.compget.main()" > $@_base
	cat $@_base $(compget_functions) > $@
	rm $@_base

#
# Testing and demos
#
examples/%/generated_comp.bash: examples/%/cmd.py src/python/compgen/compgen.py
	GENERATE_COMPLETION=1 python3 $< >$@

test-%: examples/%/test.py examples/%/generated_comp.bash
	python3 $^

examples/%/test.py: examples/%/cmd.py src/python/compgen/compgen.py
	COMPLETION_ANALYSIS=1 python3 $< >examples/$*/test.py

analyze-%: examples/%/cmd.py
	COMPLETION_ANALYSIS=1 python3 $<

demo-%: examples/%/generated_comp.bash
	bin/compget --load-bash-completion --init-files $< -- '$* '


# TODO: Investigate why --load-bash-completion makes a difference.  It looks
# like there is only a difference when colons are involved. And does it depend
# on the version of bash-completion?
#
# It seems like git-completion.bash defines its own _get_comp_words_by_ref
# if it does not already exist (provided by bash-completion) but they don't
# seem to work exactly the same way in this case.  This may be due to the
# particular versions of bash-completion and git-completion.
#
# Anyway on my mac with git-completion from the git master branch, and
# bash-completion version 2.16, the following target produces no results
# when '--load-bash-completion' is not used.
git_compget = bin/compget --load-bash-completion --init-files examples/git-comp-extras/git-completion-extras.bash

demo-git-comptest: demo-git-comptest-protocol demo-git-comptest-domain demo-git-comptest-users
demo-git-comptest-protocol:
	$(git_compget) -- 'git remote add origin '
demo-git-comptest-domain:
	$(git_compget) -- 'git remote add origin git@'
demo-git-comptest-users:
	$(git_compget) -- 'git remote add origin https://github.com/'
	$(git_compget) -- 'git remote add origin git@github.com:'

clean:
	examples/salad/_salad

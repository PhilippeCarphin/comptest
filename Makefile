PREFIX ?= $(HOME)/.local

compfile=share/bash-completion/completions/_compget
pythonpath = PYTHONPATH=$(PWD)/src/python


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
compfile:
	$(pythonpath) GENERATE_COMPLETION=1 \
	    python3 -c "import comptest.compget; comptest.compget.main()" > $(compfile)

examples/salad/_salad:
	$(pythonpath) GENERATE_COMPLETION=1 \
	    python3 examples/salad/salad.py >$@
salad_compget = bin/compget --load-bash-completion --init-files examples/salad/_salad --

demo-compgen: examples/salad/_salad

demo-compget: examples/salad/_salad
	$(salad_compget) 'salad --vegetable '
	$(salad_compget) 'salad '
demo-comptest: examples/salad/_salad
	python3 examples/salad/test-salad-comp.py

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

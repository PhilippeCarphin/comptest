# vim: ts=8:sw=8:sts=8:noet
#
PREFIX ?= localinstall

ifeq ($(shell uname),Darwin)
	INSTALL=ginstall
else
	INSTALL=install
endif


COMPFILE=share/bash-completion/completions/compget

compfile: $(COMPFILE)

$(COMPFILE): src/python/comptest/comptest.py
	bin/compget --generate-completion dummy_cmd > $@

man: share/man/man1/comptest.1

share/man/man1/%.1:share/man/man1/%.org
	pandoc -s -t man -f org $< -o $@

install: man
	$(INSTALL) -D share/man/man1/comptest.1 $(DESTDIR)$(PREFIX)/share/man/man1/comptest.1
	$(INSTALL) -D share/bash-completion/completions/compget $(DESTDIR)$(PREFIX)/share/bash-completion/completions/compget
	$(INSTALL) -D bin/comptest $(DESTDIR)$(PREFIX)/bin/comptest
	$(INSTALL) -D python/comptest.py $(DESTDIR)$(PREFIX)/python/comptest.py

install-dev: man comp
	$(INSTALL) -d localinstall/{bin,share/man/man1,lib/python/,share/bash-completion/completions}
	ln -snf ../../../../share/bash-completion/completions/compget    localinstall/share/bash-completion/completions/compget
	ln -snf ../../../../share/man/man1/comptest.1		localinstall/share/man/man1/comptest.1
	ln -snf ../../../src/python/comptest			localinstall/lib/python/comptest
	ln -snf ../../src/python/comptest/comptest.py		localinstall/bin/compget


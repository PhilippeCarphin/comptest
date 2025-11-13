# vim: ts=8:sw=8:sts=8:noet
#
PREFIX ?= localinstall

ifeq ($(shell uname),Darwin)
	INSTALL=ginstall
else
	INSTALL=install
endif

man: share/man/man1/comptest.1

share/man/man1/%.1:share/man/man1/%.org
	pandoc -s -t man -f org $< -o $@

install: man
	$(INSTALL) -D share/man/man1/comptest.1 $(DESTDIR)$(PREFIX)/share/man/man1/comptest.1
	$(INSTALL) -D bin/comptest $(DESTDIR)$(PREFIX)/bin/comptest
	$(INSTALL) -D python/comptest.py $(DESTDIR)$(PREFIX)/python/comptest.py

install-dev: man
	$(INSTALL) -d localinstall/{bin,share/man/man1,lib/python/comptest}
	ln -snf ../../../../share/man/man1/comptest.1		localinstall/share/man/man1/comptest.1
	ln -snf ../../../../src/python/comptest			localinstall/lib/python/comptest
	ln -snf ../../src/python/comptest/comptest.py		localinstall/bin/compget


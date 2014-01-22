all:
	@echo pass

build_reveal_js:
	git submodule add https://github.com/hakimel/reveal.js.git reveal.js
	git submodule init 
	git submodule update


commit:
	@-make push

push:
	make
	git status
	git add Makefile
	git add src
	git add *.md
	git commit -a
	git push


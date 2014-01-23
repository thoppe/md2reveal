all:
	@echo pass

build_deps:
	make build_reveal.js
	git submodule init 
	git submodule update

build_reveal.js:
	-git submodule add https://github.com/hakimel/reveal.js.git reveal.js

demo:
	python md2reveal.py demo.md --output demo.html
	@echo "demo.html created"


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

clean:
	find . -name "*~" | xargs -I {} rm {}
	find . -name "\#" | xargs -I {} rm {}
	find . -name "*.pyc" | xargs -I {} rm {}
	rm -fv demo.html
	rm -rfv .render_cache/

# md2reveal
python tool to convert extended markdown to reveal.js. `make demo` builds a reveal.js version of this text.

## slide control
	====  horizontal slide
	====* vertical slide
	====+ slide pause
	==== [name] named slide, useful for linking

## text formatting
    #      h1     (headers) 
    ##     h2     (headers) etc for h6
	*text* strong (bold)
	_text_ emph   (italics)
	$LaTeX$ LaTeX rendered to SVG
	       four spaces or \t is a code block

## images
	!(image src)[optional image link] <<options>>
	
For example
	!(examples/cc.svg) <<width:200>> <<transparent>>

## links
	[link text](link src)
	

# md2reveal
[python tool](https://github.com/thoppe/md2reveal) to convert extended markdown to reveal.js

==== [formating]

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

_formating_ in *action!*
## $\rho \left(\frac{\partial \mathbf{v}}{\partial t} + \mathbf{v} \cdot \nabla \mathbf{v} \right) = -\nabla p + \nabla \cdot\boldsymbol{\mathsf{T}} + \mathbf{f}$

====*
### images
	!(image src)[optional image link] <<options>>
    ...
	!(cc.svg) <<width:200; transparent >>
!(cc.svg) <<width:200; transparent>>

### links & footnotes
    [link text](link src)
    && Footnote text
	
For example [google](https://www.google.com), or [formating page](#/formating)

&& A really important footnote or reference!, [google](https://www.google.com)<br>This spans two lines!

====* [ZoomCC_Slide] !(cc.svg 30% zoom)


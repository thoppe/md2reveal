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

=====
  
# $\rho \left(\frac{\partial \mathbf{v}}{\partial t} + \mathbf{v} \cdot \nabla \mathbf{v} \right) = -\nabla p + \nabla \cdot\boldsymbol{\mathsf{T}} + \mathbf{f}$

Small inline equation $B_2 = \int x dx$.

====* 
### images
	!(image src)[optional image link] <<options>> caption markdown
    ...
    !(cc.svg) <<width:200; transparent>>  this is the cc _caption_
!(cc.svg) <<width:200; transparent>>  this is the cc _caption_

### movies
	(image src.m4v)[optional image link] <<options>>
    ...
	!(small.m4v) <<height:200>>
!(small.m4v) <<height:200>>

====*
{"include":"include_example.md"}
====*

### links & footnotes
    [link text](link src)
    && Footnote text
	
For example [google](https://www.google.com), or [formating page](#/formating)

&& A really important footnote or reference!, [google](https://www.google.com)<br>This spans two lines!

### Comments in md slides
    % This line won't be displayed below since it starts with a "%"

% This line won't be displayed below since it starts with a "%"
<br>

====* [ZoomCC_Slide] !(cc.svg 30% zoom)


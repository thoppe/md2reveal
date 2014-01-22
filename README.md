reveal_easy_pres
================

Transforms extended Markdown into reveal.js compatible slides


# Uses a modified version of Markdown to interface with reveal.js to 
# create beautiful web-based presentations.
## Run `make build` to see build current example.
## Run `make view`  to load the example.

# TO DO:

* Draw a box around equations so that they are always sized correctly
* Use \align{} for ### headings and $$ for inline
* Split parsing into single slides
* Space after emph?
* Use | at the start of a line to left-justify

# Notes:

You can mix html in the slides, but this may be a bit buggy. If you encounter an error doing this let me know!

Change the styling by picking a new (CSS) stylesheet. An example is given as the first line.

Insert images like this:

    !(images/picture.png)

To make them transparent use do this:

    !(images/picture.png)<<transparent>>

To make more than one per line do this:

    !(images/A.png)<<span>>
    !(images/B.png)<<span>>

To add size and alignment information do this:

    ![100][200][right](images/A.png)
    ![200][][left](images/B.png)
    
The brackets go in order of [width][height][alignment], all 3 must be present for any one to work (but they can be left empty)!

All reveal.js initialization parameters (except theme) can now be set at the top of the markdown file.  Example:

    <transition: "page">
    <controls: false>
    
For a full list of parameters see reveal.js README.

A single line space will force a line break, a double will force a vertical gap between them.

# Low priority features requests...
* Export entire presentation to single file
* Preload fonts loaded from the web....?

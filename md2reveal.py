import os, sys, argparse, logging
from src.slides import markdown_presentation
import src.markdown_slide
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Command-line parse
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

desc = '''
Transforms markdown (with LaTeX) into a webpage that can be opened with 
reveal.js
'''.strip()

parser = argparse.ArgumentParser(description=desc)
parser.add_argument('markdown', help='Input Markdown file')
parser.add_argument('--html_title',  default="")
parser.add_argument('--html_author', default="")
parser.add_argument('--html_desc',   default="")
parser.add_argument('--verbose', '-v', action='store_true', 
                    default=False, dest='verbose',
                    help='Logging information')
parser.add_argument('--keep_equations', action='store_true', 
                    default=False, 
                    help='Do not render the equations to svg')
parser.add_argument('--prettify', action='store_true', 
                    default=False, help="html output is prettified")
msg = "Output html file, if none defaults to [markdown input].html"
parser.add_argument('--output',help=msg, default="")
cmdline_args = parser.parse_args()

# Start the logger
if cmdline_args.verbose: 
    logging.root.setLevel(logging.INFO)

# See README.md in the reveal.js folder for what these options do 
# (default values); note the transition value needs to be in quotes ""

reveal_init={
    'width':1200,
    'height':900,

    'margin': 0.05,
    'minScale': 0.2,
    'maxScale': 1.2,

    'controls': 'true', 
    'progress': 'true', 

    'history': 'true', 

    'overview': 'true', 
    'center': 'true', 
    'touch' : 'true',
    'loop': 'false', 
    'rtl': 'false',
    'fragments':'true',
    'embedded':'true',   
    'autoSlide':0,
    'autoSlideStoppable':'true',
    'mouseWheel':'false', 
    'hideAddressBar':'true',
    'previewLinks':'false',
    'transition': '"default"',
    'transitionSpeed': '"default"',
    'backgroundtransition': '"default"',
    'viewDistance':3,
    'rollingLinks': 'false',

    'right_left_arrow_keys':False,
    
    }

# Set the global for keeping equations
src.markdown_slide.keep_equations = cmdline_args.keep_equations

# Load reveal arguments if present
theme = None
f_reveal_json_args = "reveal_options.json"
if os.path.exists(f_reveal_json_args):
    import json

    with open(f_reveal_json_args) as FIN:
        js = json.load(FIN)

    # Pop out the theme if present
    if "theme" in js:
        theme = js.pop("theme")

    reveal_init.update(js)

# Custom key bindings
is_right_left_arrow_keys = reveal_init.pop("right_left_arrow_keys")
if not is_right_left_arrow_keys:
    reveal_init["keyboard"] = {
        39 : "next",
        37 : "prev",
    }

if not cmdline_args.output:
    cmdline_args.output = cmdline_args.markdown.split('.')[0] + '.html'
    cmdline_args.output = os.path.basename(cmdline_args.output)
        
script_name = __file__
script_dir  = os.path.dirname(os.path.realpath(script_name))
local_dir   = os.getcwd()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Header read
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

logging.info("Working script directory "+script_dir)

fin_header = os.path.join(script_dir, "org", "header.html")
with open(fin_header) as FIN: header = FIN.read()

with open(cmdline_args.markdown) as FIN:
    raw = FIN.read()

markdown_parser = markdown_presentation()
slide_html = markdown_parser(raw)

reveal_init_val=''
for i,j in reveal_init.iteritems():
    reveal_init_val += '%s: %s, ' % (i,j)

# Give a bit more control over the initalize params
header_args = vars(cmdline_args)
header_args["reveal_init_args"] = reveal_init_val
header_args["html_content"]     = slide_html

f_css, link_html = src.markdown_slide.process_theme(theme)
header_args["theme_link"] = link_html

f_dependencies = os.path.join(script_dir, "org", "dependencies.js")
with open(f_dependencies) as FIN:
    header_args["reveal_dependencies"] = FIN.read()

# Determine the proper src for the latex files
if local_dir not in script_dir:
    logging.warning("Not running for a subdirectory, can mess up css")

target_dir = script_dir[len(local_dir):]
f_latex_css = os.path.join(target_dir, "css/md2reveal_style.css")
f_latex_css = f_latex_css.lstrip("/")
header_args["f_latex_css"] = f_latex_css

final_html = header.format(**header_args)

with open(cmdline_args.output, 'w') as FOUT:
    if not cmdline_args.prettify:
        FOUT.write(final_html)
    else:
        import bs4
        soup = bs4.BeautifulSoup(final_html)
        encoded_html = soup.prettify().encode('utf8')
        FOUT.write(encoded_html)

logging.info("{} created".format(cmdline_args.output))


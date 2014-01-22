import os, inspect
import bs4 as BS
import logging, shutil
import numpy as np

# Shorthand notation
import os_functions as osf
shell = osf.shell

scriptname = inspect.getfile(inspect.currentframe())
scriptpath = os.path.dirname(os.path.abspath(scriptname))
f_tex_src  = os.path.join(scriptpath, 'org', 'single_block.tex')

def sanitize_latex(text):
    ''' Removes all latex formatting from text input '''

    sub = dict()
    text = ''.join(x if not x=='\\' else r'\textbackslash' for x in text)

    sub['{'] = r'\{'
    sub['}'] = r'\}'

    for key in sub:
        if key in text:
            text = text.replace(key, sub[key])

    del sub['{']
    del sub['}']
    sub['^'] = r'\^{}'
    sub['$'] = r'\$'
    sub['&'] = r'\&'
    sub['#'] = r'\#'
    sub['_'] = r'\_'
    sub['%'] = r'\%'
    sub['~'] = r'\textasciitilde{}'
    sub['<'] = r'\textless{}'
    sub['>'] = r'\textgreater{}'
    sub['|'] = r'\textbar{}'
    sub['"'] = r'\textquotedbl{}'
    sub["'"] = r'\textquotesingle{}'
    sub["`"] = r'\textasciigrave{}'

    for key in sub:
        if key in text:
            text = text.replace(key, sub[key])
    return text


def filter_tex_errors(shell_results):
    return [x for x in shell_results.split('\n') if x and "!" == x[0]]

def build_tex_item(text, filename_only=False, debug=False):
    org_text = text
    original_text = text
           
    if not text.strip():
        logging.warning("Empty line found in textline render")
        return 2

    with osf.cache_result('.render_cache', render_text,ext='.svg') as C:
        logging.info("Rendering text [%s]"%org_text)
        svg_text = C(text,debug)
        if filename_only: return C.f_save       
        return svg_text

            

def render_text(text,debug):
    print "# Rendering", text
    f_tex_input = 'target.tex'
   
    with osf.temp_workspace() as W:
        f_tmp_tex = W.store(f_tex_src, 'block.tex')

        with open(f_tex_input,'w') as FOUT:
            encoded_text = text.encode('utf8')
            FOUT.write(encoded_text)

        # Compile the TeX with XeLaTex
        cmd  = "pdflatex -halt-on-error %s"
        args = (f_tmp_tex,)
        stdout, stderr = shell(cmd % args)
        tex_errors = filter_tex_errors(stdout)

        if tex_errors:
            logging.critical("TeX Error %s"%tex_errors)

        f_pdf = f_tmp_tex.replace('.tex','.pdf')

        # Convert to a SVG
        f_svg = f_pdf.replace('.pdf','.svg')
        cmd = "pdftocairo -cropbox -svg %s %s"
        args = (f_pdf, f_svg)
        stdout, stderr = shell(cmd % args)
        if stderr: raise RuntimeError(stderr)
        
        # Crop to the bounding box
        cmd  = "python %s/svg_crop.py %s %s"
        args = (scriptpath, f_svg, f_svg)

        if debug:
            os.system('bash')

        stdout, stderr = shell(cmd % args)             
        if stderr: raise RuntimeError(stderr)

        # Find the baseline
        # baseline = extract_baseline(f_svg)

        # Adjust the baseline
        # svg.svg['baseline']= baseline

        # Tag the svg as a latex one
        # svg.svg['class'] = "SVGlatex"

        with open(f_svg) as FIN:
            return FIN.read()


        '''
        # Convert SVG to PNG for testing
        if RENDER_PNG:
            f_png = f_pdf_crop.replace('.pdf','.png')
            cmd = "convert %s %s"
            args = (f_svg, f_png)
            stdout, stderr = shell(cmd % args)
            if stderr: raise RuntimeError(stderr)
            W.save(f_png, f_output.replace('.svg','.png'))
        '''
    
    # Should not get to this point
    assert(True)
    return 0


if __name__ == "__main__":

    #print build_tex_item('g h i')
    #s = r"B_2 = -\frac{1}{2}"
    s = r"Lateral packing $=\frac{\sqrt{(n \pi d)^2 + h^2}}{s}$"
    svg = build_tex_item(s,debug=True)
    with open("test.svg",'w') as FOUT:
        FOUT.write(svg)
    

    

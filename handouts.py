from src.latex_src.os_functions import temp_workspace
from src.extra_io import mkdir_p
import argparse
import bs4
import uuid, os, shutil

desc = '''
Converts the final md2reveal .html file into a pdf of slides'''.strip()

parser = argparse.ArgumentParser(description=desc)
parser.add_argument('md', help='markdown')
cmdline_args = parser.parse_args()

f_tex = "template.tex"
f_tex_content = "content.tex"
cmd_md2reveal = "python {} --keep_equations --prettify {} --output {}"
cmd_panddoc   = "pandoc -f html -t latex {} > {}"
cmd_latex     = "pdflatex {}"

cmd_convert_svg_to_png = "convert {f}.svg {f}.png"

basic_tex = r'''
\documentclass[a4paper, 10pt]{scrartcl}
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{fullpage}

\begin{document}
%s
\end{document}'''.strip()

with temp_workspace() as W:
    py_md2  = os.path.join(W.local_dir, "md2reveal.py")
    md_file = os.path.join(W.local_dir, cmdline_args.md)
    f_html = os.path.join(W.temp_dir, "target.html")

    os.chdir(W.local_dir)
    cmd = cmd_md2reveal.format(py_md2, md_file, f_html)
    os.system(cmd)
    os.chdir(W.temp_dir)

    with open(f_html) as FIN:
        raw = FIN.read()
        full_soup = bs4.BeautifulSoup(raw)
        soup = full_soup.find("div", {"class":"reveal"})


    # Copy all images locally and convert any svgs
    for img in soup.findAll("img"):
        f_org_img = os.path.join(W.local_dir, img["src"])
        f_img = os.path.join(W.temp_dir, img["src"])
        
        if not os.path.exists(os.path.dirname(f_img)):
            os.makedirs(os.path.dirname(f_img))

        shutil.copyfile(f_org_img, f_img)
        
        extension = f_img.split('.')[-1]
        if extension == "svg":
            f_name = '.'.join(f_img.split('.')[:-1])
            cmd = cmd_convert_svg_to_png.format(f = f_name)
            os.system(cmd)
            img["src"] = img["src"].replace('.svg','.png')

    with open(f_html, 'w') as FOUT:
        FOUT.write(soup.prettify())
    
    os.system(cmd_panddoc.format(f_html,f_tex_content))

    with open(f_tex_content) as FIN:
        tex = FIN.read()
    tex = tex.replace(r'\\',' ')
    
    with open(f_tex,'w') as FOUT:
        FOUT.write(basic_tex%tex)

    os.system(cmd_latex.format(f_tex))

    # Save the output!

    f_final_pdf = os.path.join(W.local_dir, cmdline_args.md.replace('.md','.pdf'))

    shutil.copyfile("template.pdf", f_final_pdf)

    print "{} created!".format(f_final_pdf)

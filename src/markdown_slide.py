from latex_src.render_string import build_tex_item
import json, logging, glob, os, cgi
from pyparsing import *

# Useful names
def boxExpr(DLIM_L, DLIM_R, name):
    return QuotedString(DLIM_L, endQuoteChar=DLIM_R)(name)

brackets = boxExpr('[',']','brackets')
paren    = boxExpr('(',')','paren')
angles   = boxExpr('<','>','angles')
double_angles   = boxExpr('<<','>>','double_angles')

_CODE_LANUAGE = "python"

local_themes    = (glob.glob("*.css") +
                   glob.glob("css/*.css") ) 
packaged_themes = glob.glob("reveal.js/css/theme/*.css")
packaged_themes = [os.path.basename(x) for x in packaged_themes]

# Only split on spaces, newlines are important
ParserElement.setDefaultWhitespaceChars(" ")

# Helper function, all quoted strings markers can be escaped with \
def QString(quoteChar, escChar='\\'):
    return QuotedString(quoteChar, escChar=escChar)

def process_inline_link(s,loc,tokens):
    return '<a href="%s">%s</a>' % (tokens.url, tokens.text)

def process_left_justify(s,loc,tokens):
    return "<div align='left'>{text}</div>"

def process_code_block(s, loc, tokens):
    html = '\n'.join(tokens['code_block']).rstrip()
    html = cgi.escape(html, quote=True)
    s    = '<pre><code class={}>{}</code></pre>'
    return s.format(_CODE_LANUAGE, html)

def option_iterator(option_string):
    option_key    = Word(alphanums+'_')("key")
    option_value  = Word(alphanums+'"_')("value")
    option_marker = Literal(":").suppress()
    option_keyval = Group(option_key + Optional(option_marker + option_value))
    option_grammar = delimitedList(option_keyval, delim=";")
    
    for opt in option_grammar.parseString(option_string):
        key = opt["key"]
        value = opt["value"] if "value" in opt else True
        yield key, value

def process_image(img):
    img_html = '''
    <a href="{src}">
    <img class="{classname}" src="{src}" {arguments}>
    </a>
    '''.strip()

    video_html = '''
    <video autoplay loop {arguments}>  
    <source src="{src}" type="video/mp4"> 
    </video>
    '''.strip()
    
    extension = os.path.splitext(img["src"])[1].split('.')[-1]

    if extension in ["mp4", "m4v"]:
        html = video_html
    else:
        html = img_html

    # Known img arguments
    recognized_opts = "width", "height"
    args, image_class_names = {}, []

    for key,val in option_iterator(img["options"][0]):
        key = key.lower()

        if key in recognized_opts:
            args[key] = val

        elif key == 'transparent':
            image_class_names.append("transparent_image")

        else:
            msg = "Unknown image option {}".format(key)
            logging.warning(msg)

    arg_text = ['{}="{}"'.format(key,val) for key,val in args.items()]
    arg_text = ' '.join(arg_text)
    
    cls  = ' '.join(image_class_names)
    html = html.format(src=img['src'], classname=cls, arguments=arg_text)

    print html

    if "link" in img:
        link_text = '<a href={link}>{html_img}</a>'
        html = link_text.format(link=img['link'],
                                html_img = html)

    return html

def process_latex(s,loc,tokens):
    latex_input = tokens['latex']
    eq = r"\begin{align*}%s\end{align*}"

    try:
        f_svg = build_tex_item(eq%latex_input, filename_only=True)
        with open(f_svg) as FIN:
            svg = FIN.read()
    except Exception as Ex:       
        logging.warning("Could not render {}".format(latex_input))
        svg = eq
    return svg

def process_quote_block(s,loc,tokens):
    s = ' '.join(tokens['quote_block'])
    return "<blockquote>%s</blockquote>" %s

def process_ulist_block(s,loc,tokens):
    items = tokens['ulist_block']
    items = map(_global_markdown_line, items)
    items = ["<li>{}</li>".format(x) for x in items]
    return "<ul>{}</ul>".format('\n'.join(items))

def process_olist_block(s,loc,tokens):
    items = tokens['olist_block']
    items = map(_global_markdown_line, items)
    items = ["<li>{}</li>".format(x) for x in items]
    return "<ol>{}</ol>".format('\n'.join(items))

class markdown_line(object):

    def process_tag(self, tag, recursive=False):
        def process_function(s,loc,tokens):
            val = tokens.pop()
            if recursive: val = self(val)
            return r"<{tag}>{result}</{tag}>".format(tag=tag, result=val)
        return process_function

    def __init__(self):

        strong = QString("*")('strong')
        emph   = QString("_")('emph')

        latex       = QuotedString("$")('latex')
        inline_link = (brackets('text')+paren('url'))('inline_link')
        inline_code = QuotedString("`")('inline_code')
        options = double_angles('options') 

        tokens = (strong | emph | latex | 
                  inline_code | inline_link | options)

        self.grammar = tokens("text")

        # Recursive tags
        emph.setParseAction(self.process_tag("em",recursive=True))
        strong.setParseAction(self.process_tag("strong",recursive=True))
        
        # Simple tags
        inline_code.setParseAction(self.process_tag("code"))
        inline_link.setParseAction(process_inline_link)

        # External calls
        latex.setParseAction(process_latex)


    def __call__(self, text):
        return (self.grammar).transformString(text)
    
    def grammar(self):
        return self.grammar

# Global object for functions to call
_global_markdown_line = markdown_line()
 
class markdown_multiline(object):

    def __init__(self):
        self.hn = [0,0]   # Keeps track of headers
        options     = Group(ZeroOrMore(double_angles))('options')

        empty_line = LineEnd()("empty")

        # White space marker, useful for when I leave whitespace in
        ws = Optional(Word(" "))

        # Rest of line ROL
        ROL   = SkipTo(LineEnd().suppress(),include=True) 
        code_marker = ((Literal(' ')*4)).suppress()
        code_line   = (code_marker + ROL).leaveWhitespace()
        code_block = Group(OneOrMore(code_line))('code_block')

        rule_marker = Literal('-').suppress()
        line_rule   = ((rule_marker*4) + ROL)('rule')

        image_marker = Literal("!").suppress()
        image_line   = (image_marker + paren('src') 
                        + Optional(brackets)('link') + ws
                        + ws + options + ROL).leaveWhitespace()

        option_block = (QuotedString(quoteChar='{', 
                                    endQuoteChar='}',
                                    multiline=True,
                                    unquoteResults=False)('options') 
                        + ROL.suppress())

        quote_box_marker = Literal(">").suppress()
        quote_box_line = quote_box_marker + ROL
        quote_box_block= Group(OneOrMore(quote_box_line))('quote_block')
        
        ulist_marker = Literal('+').suppress()
        ulist_line   = ulist_marker + ROL
        ulist_block  = Group(OneOrMore(ulist_line))('ulist_block')

        olist_marker = (Word(nums) + Literal('.')).suppress()
        olist_line   = olist_marker + ROL
        olist_block  = Group(OneOrMore(olist_line))('olist_block')

        prefix_marker = (image_marker | rule_marker | 
                         code_marker  | quote_box_marker |
                         ulist_marker | olist_marker)

        unicodePrintables = u''.join(unichr(c) for c in xrange(65536) 
                                     if not unichr(c).isspace())

        line_text    = Group(OneOrMore(Word(unicodePrintables)))
        regular_line = (~prefix_marker + ~option_block + ~code_line
                         + line_text + LineEnd().suppress())

        paragraph    = Group(OneOrMore(regular_line))("paragraph")  

        self.grammar = OneOrMore(empty_line      | 
                                 option_block    |
                                 image_line      |
                                 code_block      | 
                                 quote_box_block |
                                 ulist_block     |
                                 olist_block     |
                                 line_rule       |
                                 paragraph)

        paragraph.setParseAction(self.process_paragraph)
        empty_line.setParseAction(self.process_empty_line)
        line_text.setParseAction(self.process_line_text)
        image_line.setParseAction(process_image)

        option_block.setParseAction(self.process_option_block)

        code_block.setParseAction(process_code_block)
        quote_box_block.setParseAction(process_quote_block)
        ulist_block.setParseAction(process_ulist_block)
        olist_block.setParseAction(process_olist_block)

        line_rule.setParseAction(lambda x:'<hr>')
        regular_line.setParseAction(self.process_regular_line)

    def __call__(self, text):
        return '\n'.join((self.grammar).parseString(text))

    def process_regular_line(self, s,loc,tokens):

        # Reset the headers if there is a fragment
        for items in tokens:
            if '<div class="fragment">' in items:
                self.hn = [1,1]

        if self.hn[-1] == 0 and self.hn[-2]==0:
            tokens.insert(-1,r"<br>")

        return tokens
    
    def process_option_block(self, s,loc,tokens):
        text = '%s'%tokens[0]
        try:
            options = json.loads(text)
        except:
            logging.critical("Can't convert option to JSON %s"%text)
            return ""

        return self.handle_options(options)
    
    def handle_options(self, options):
        output_str = []

        if "include_code" in options:
            f_code = options['include_code']
            with open(f_code) as FIN:
                raw  = FIN.read()
                html = cgi.escape(raw, quote=True)
            v = "<pre><code>%s</code></pre>" % html
            output_str.append(v)

        if "theme" in options:
            f_css, theme_html = process_theme(options["theme"])
            output_str.append(theme_html)

        return "\n".join(output_str)


    def process_line_text(self,s,loc,tokens):

        header_marker = tokens[0][0]
        header_pop = False
        text = "{}"

        hn = 0
        if "#" in header_marker:
            hn = min(6, header_marker.count("#"))
            text = "<h{hn:d}>{text}</h{hn:d}>".format(text=text,hn=hn)
            header_pop = True
        self.hn.append(hn)

        if "|" in header_marker:
            text = r"<div display='inline' align='left'>{}</div>".format(text)
            header_pop = True

        if "&&" in header_marker:
            text = '<div class="reference_footnote">{}</div>'
            header_pop = True

        if header_pop: 
            tokens[0][0] = tokens[0][0].lstrip("#|&")
            if not tokens[0][0]: del tokens[0][0]
        s = _global_markdown_line(' '.join(tokens[0]))

        return text.format(s)

    def process_empty_line(self,s,loc,tokens):
        return "<br>"

    def process_paragraph(self, s,loc,tokens):
        # First tokens might be an extra <br> tag, remove if so
        while tokens.paragraph and tokens.paragraph[0] == "<br>":
            tokens.paragraph.pop(0)

        # Join the paragraph tokens together
        sval = ''.join(tokens.paragraph)
        return "<p>\n{}</p>".format(sval)




def get_theme_path(theme):
    f_css = ""
    local_list = [os.path.basename(x) for x in local_themes]

    if theme in local_list:
        index = local_list.index(theme)
        f_css = local_themes[index]
    elif theme in packaged_themes:
        index = packaged_themes.index(theme)
        rdest = "reveal.js/css/theme"
        f_css = os.path.join(rdest,packaged_themes[index])
    elif os.path.exists(theme):
        f_css = theme
    else:
        msg = ("Theme '{}' not found. "
               "Local themes {}. "
               "Packaged thems {}")
        msg = msg.format(theme,local_list, packaged_themes)
        logging.warning(msg)

    return f_css


def process_theme(theme):

    if not theme:
        return "", ""

    theme_string = r'''
    <link rel="stylesheet" href="%s" id="theme">'''.strip()

    f_css = get_theme_path(theme)

    return f_css, theme_string%f_css





if __name__ == "__main__":
    #A0 = "|# the [link text](www.google.com) big *cat (who is _fat_)* in $*a*^b$ the *hat* `*monkey` <<foobar>>  <<span>>"
    A0 = "The *cat* in _the_ *hat is _fat_*."

    A1 ='''_text_
    text2
    The *cat* in _the_ *hat is _fat_*.
    text3
    |# Main Idea
    Predict $B_{2}$ from structural information [link](http://www.google.com)

    against

    ## pH Dependence
    ## Concentration 
    ## Charge anisotropy

    !(https://www.google.com/images/srpr/logo11w.png) <<span>> <<foobar>>

        print x
        print y
    '''

    g = markdown_line()
    g = markdown_multiline()
    print g(A1)
    with open("test.html",'w') as FOUT: FOUT.write(g(A1))

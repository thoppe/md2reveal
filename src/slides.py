from pyparsing import *
import logging, json
from markdown_slide import markdown_multiline, option_iterator
from markdown_slide import brackets, paren, double_angles

def match_at_least_n(token,n):
    val = Literal(token)
    grammar = And([val]*n) + ZeroOrMore(val)
    return grammar

class markdown_presentation(object):

    def __init__(self):

        self.slide_id_name = ""
        sid = Optional(brackets)("slide_id") 
        sid.setParseAction(self.process_slide_id)

        self.background_img   = ""
        self.background_trans = ""
        self.background_size  = ""
        self.data_trans = ""

        img_g   = Literal("!").suppress() + paren
        backimg = Optional(img_g)("background")
        backimg.setParseAction(self.process_background)

        options = double_angles('options') 
        options.setParseAction(self.process_slide_options)

        mark_sep = match_at_least_n("=",4)
        marker_V = (Combine(mark_sep + match_at_least_n("*",1)) 
                    + sid + backimg + Optional(options))

        marker_P = Combine(mark_sep + match_at_least_n("+",1)) 
        marker_H = ((~(marker_V|marker_P) + mark_sep) 
                    + sid + backimg + Optional(options))

        h_block = Combine(OneOrMore(~marker_H + ~options +
                                     SkipTo(LineEnd(),include=True)))
        h_block.setParseAction(self.process_h_block)
        self.hg = delimitedList(h_block, delim=marker_H)

        v_block = Combine(OneOrMore(~marker_V + ~options +
                                     SkipTo(LineEnd(),include=True)))
        v_block.setParseAction(self.process_v_block)
        self.vg = delimitedList(v_block, delim=marker_V)

        p_block = Combine(OneOrMore(~marker_P + 
                                     SkipTo(LineEnd(),include=True)))
        p_block.setParseAction(self.process_p_block)
        self.pg = delimitedList(p_block, delim=marker_P)

        self.slide_grammar = markdown_multiline()
        self.grammar = self.hg      

    def process_slide_id(self, tokens):
        # If a slide_id is found, set this variable and 
        # pick it up on the next slide creation
        self.slide_id_name = ""

        if "slide_id" in tokens:
            self.slide_id_name = tokens["slide_id"]
        return None

    def process_background(self, tokens):
        # Example !(myimg.png 90% zoom)
        if "background" in tokens:
            vals = tokens["background"][0].split(' ')
            if len(vals)>0:
                self.background_img   = vals[0]
            if len(vals)>1:
                self.background_size  = vals[1]
            if len(vals)>2:
                self.background_trans = vals[2]
        else:
            self.background_img = ""
        return None

    def process_slide_options(self, tokens):
        if "options" in tokens:
            for key, val in option_iterator(tokens["options"]):
                if key == "transition":
                    self.data_trans = val
                else:
                    msg = "Unknown slide option {}/{}".format(key,val)
                    logging.warning(msg)

        return None

    def get_slide_background(self):
        s = []

        if self.data_trans:
            html = 'data-transition="%s"'%self.data_trans
            s.append(html)

        if self.background_size:
            s.append('data-background-size="%s"'
                     %self.background_size)

        if self.background_img:
            s.append('data-background="%s"'
                     %self.background_img)

        if self.background_trans:
            s.append('data-background-transition="%s"'
                     %self.background_trans)

        # Force none transistion if nothing selected      
        #else:
        #    s.append('data-background-transition="none"')

        return ' '.join(s)

    def get_slide_name(self):
        if self.slide_id_name:
            return 'id="{}"'.format(self.slide_id_name)
        return ""
        
    def process_h_block(self, tokens):
        # Take the first token a replace the tabs to four spaces
        val = tokens.pop().replace('\t','    ')

        # Format the inner vertical slide blocks
        val = self.vg.transformString(val)
        text = '<section class="vertical-stack">\n{}\n</section>'

        return text.format(val)

    def process_v_block(self, tokens):
        val = tokens.pop()

        # Handle the fragments
        self.fragment_stack = 0
        val = self.pg.transformString(val)

        # Apply the markdown grammar
        val = self.slide_grammar(val.strip())

        text = '<section {} class="vertical-slide">\n{}\n</section>'

        opts = ' '.join([self.get_slide_name(), 
                         self.get_slide_background()])

        return text.format(opts, val)

    def process_p_block(self, tokens):
        html = "{}"
        if self.fragment_stack:
            html = '\n<div class="fragment">\n{}\n</div>'

        self.fragment_stack += 1

        val = tokens.pop().strip('\n')
        
        return html.format(val)

    def __call__(self, text):

        # Preprocess any includes
        ROL   = SkipTo(LineEnd().suppress(),include=True)
        include_block = (QuotedString(quoteChar='{', 
                                      endQuoteChar='}',
                                      multiline=True,
                                      unquoteResults=False)
                         + ROL.suppress())
        comment_line = (Literal("%") + ROL).suppress()

        other_line = Combine(SkipTo(LineEnd(),include=True))
        include_grammar = OneOrMore(
            comment_line
            |include_block("include")
            |other_line).leaveWhitespace()
        include_grammar.setParseAction(process_include_block)
        text = include_grammar.transformString(text)
        #print text
        #exit()

        # Process the slide grammar
        return self.grammar.transformString(text)

def process_include_block(s,loc,tokens):
    output = []
    for line in tokens:
        if "include" in line:
            try:
                options = json.loads(line)
                with open(options["include"]) as FIN:
                    line = FIN.read()

            except Exception as Ex:
                msg = "Can't convert option to JSON {}, {}"
                logging.critical(msg.format(line, Ex))
        output.append(line)
    return ''.join(output)


if __name__ == "__main__":

    with open("../talks/lab2.markdown") as FIN:
        raw = FIN.read()

    P = markdown_presentation()
    print P(raw)

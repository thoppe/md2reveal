from pyparsing import *
from markdown_slide import markdown_multiline
from markdown_slide import brackets

def match_at_least_n(token,n):
    val = Literal(token)
    grammar = And([val]*n) + ZeroOrMore(val)
    return grammar

class markdown_presentation(object):

    def __init__(self):

        self.slide_id_name = ""
        sid = Optional(brackets)("slide_id") 
        sid.setParseAction(self.process_slide_id)

        mark_sep = match_at_least_n("=",4)
        marker_V = Combine(mark_sep + match_at_least_n("*",1)) + sid
        marker_P = Combine(mark_sep + match_at_least_n("+",1)) 
        marker_H = (~(marker_V|marker_P) + mark_sep) + sid

        h_block = Combine(OneOrMore(~marker_H + 
                                     SkipTo(LineEnd(),include=True)))
        h_block.setParseAction(self.process_h_block)
        self.hg = delimitedList(h_block, delim=marker_H)

        v_block = Combine(OneOrMore(~marker_V + 
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

        text = '<section class="vertical-slide" {}>\n{}\n</section>'
        opts = self.get_slide_name()
        return text.format(opts, val)

    def process_p_block(self, tokens):
        html = "{}"
        if self.fragment_stack:
            html = '\n<div class="fragment">\n{}\n</div>'
            #tokens[0] = tokens[0].lstrip('\n')

        self.fragment_stack += 1

        val = tokens.pop().strip('\n')
        
        return html.format(val)

    def __call__(self, text):
        return self.grammar.transformString(text)

if __name__ == "__main__":

    with open("../talks/lab2.markdown") as FIN:
        raw = FIN.read()

    P = markdown_presentation()
    print P(raw)

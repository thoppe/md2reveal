import bs4
import numpy as np
from svg2.parser import parse_path
import ast
import random, string


def random_id_gen(N=10):
    return ''.join([random.choice(string.ascii_uppercase) 
                    for x in range(5)])

_SVG_CONTROL_POINTS = 2000

class bounding_box(object):
    def __init__(self, input_points=None):
        self.x0,self.y0 =  np.inf, np.inf
        self.x1,self.y1 = -np.inf, -np.inf

        if input_points != None:
            self.update(input_points)
    

    def update(self, pts):
        self.x0 = min(pts[:,0].min(), self.x0)
        self.y0 = min(pts[:,1].min(), self.y0)
        self.x1 = max(pts[:,0].max(), self.x1)
        self.y1 = max(pts[:,1].max(), self.y1)

    def get_box(self):
        return  np.array([[self.x0, self.y0],
                          [self.x1, self.y1]])
    
    def update_from_box(self, rhs):
        self.update(rhs.get_box())

    def __repr__(self): return '\n'+str(self.get_box())

    def __add__(self, pt):
        b2 = bounding_box()
        b2.x0 = pt[0]+self.x0
        b2.x1 = pt[0]+self.x1
        b2.y0 = pt[1]+self.y0
        b2.y1 = pt[1]+self.y1
        return b2

    def width(self): return self.x1-self.x0
    def height(self): return self.y1-self.y0


def get_SVG_bounding_box(soup):

    # Load the symbols from the defs
    LPATH = np.linspace(0,1,_SVG_CONTROL_POINTS)
    BBOX  = {}

    # Loop over the defs and find all the paths
    # determine the bbox for each symbol
    for symbol in soup.svg.defs.findAll("symbol"):
        for path in symbol.findAll("path"):

            B = bounding_box()

            P = parse_path(path["d"])
            for curve in P:
                pts = curve.point(LPATH)
                x,y = pts.real, pts.imag
                b_box = bounding_box(np.array((x,y)).T)
                B.update_from_box(b_box)
            
            BBOX[symbol["id"]]= B

    IMG_BBOX = bounding_box()

    #for x in BBOX:
    #    print x, BBOX[x]

    for use_symbol in soup.svg.findAll("use"):
        x = float(use_symbol["x"])
        y = float(use_symbol["y"])
        iden = use_symbol["xlink:href"][1:]
        use_bbox = BBOX[iden]+(x,y)
        IMG_BBOX.update_from_box(use_bbox)

    return IMG_BBOX, BBOX


def clean_soup(soup):

    for symbol in soup.svg.defs.findAll("symbol"):
        for path in symbol.findAll("path"):
            if not path["d"]:
                # Empty path? DECOMPOSE!
                symbol.decompose()
    
    # Remove extra styles in use
    for use_symbol in soup.svg.findAll("use"):
        del use_symbol.parent["style"]
    
    # Find the simple transforms
    for path in soup.svg.findAll("path"):
        if "transform" in path.attrs:
            m_text = path["transform"]
            m_text = m_text.strip().split('matrix')[1]
            m_coord= ast.literal_eval(m_text)
            tx = m_coord[4]
            ty = m_coord[5]
            del path["transform"]

            # Only keep the thickness on the style
            style = path['style'].split(';')
            thickness = [x for x in style if "stroke-width" in x][0] + ';'
            path["style"] = thickness
            
            # Create a symbol
            sx = soup.new_tag("symbol", overflow="visible")
            random_id  = "MATRIXPATH_"+random_id_gen()
            sx.append(path)
            sx['id'] = random_id
            soup.svg.defs.g.append(sx)

            # Create a use symbol
            usex = soup.new_tag("use", x=tx, y=ty)
            usex['xlink:href'] = '#' + random_id
            g_usex = soup.new_tag('g')
            g_usex.append(usex)
            
            surface = soup.find("g", attrs={"id":"surface1"})
            surface.append(g_usex)
    
    # Remove extra styles in path
    #for path in soup.svg.findAll("path"):
    #    del path["style"]


    

def svg_crop(soup):
           
    clean_soup(soup)

    box,BBOX = get_SVG_bounding_box(soup)

    # pdfcrop cairo names this incorrectly
    del soup.svg["viewbox"]

    width  = box.width()
    height = box.height()

    # Adjust all the pos. of the symbols
    for use_symbol in soup.svg.findAll("use"):
        x,y = map(float, [use_symbol["x"], use_symbol["y"]])
        iden = use_symbol["xlink:href"][1:]

        use_symbol["x"] = x-box.x0
        use_symbol["y"] = y-box.y0

    view = ' '.join(map(str, (0,0, width, height)))
    soup.svg["viewBox"] = view
    soup.svg["height"] = "{:f}px".format(height)
    soup.svg["width"]  = "{:f}px".format(width)
    soup.svg["class"] = "latexSVG"

    # Relabel all the symbols to prevent conflicts
    random_id  = random_id_gen()

    # Find all the symbol names
    symbol_map = {}
    for symbol in soup.svg.findAll("symbol"):
        symbol_map[symbol["id"]] = None

    # Build a mapping
    for k,key in enumerate(symbol_map):
        symbol_map[key] = "equation_{}_{}".format(random_id, k)

    # Fix the symbols
    for symbol in soup.svg.findAll("symbol"):
        symbol["id"] = symbol_map[symbol["id"]]

    for use_symbol in soup.svg.findAll("use"):
        iden = use_symbol["xlink:href"][1:]
        use_symbol["xlink:href"] = "#" + symbol_map[iden]

    return soup.svg

def crop_svg_file(f_in, f_out, prettify=True):

    with open(f_in,'r') as FIN:
        soup = bs4.BeautifulSoup(FIN.read(),'xml')

    crop_soup = svg_crop(soup)

    with open(f_out,'w') as FOUT:
        if prettify:
            FOUT.write(crop_soup.prettify())
        else:
            FOUT.write(crop_soup)

if __name__ == "__main__":

    import sys
    if len(sys.argv) != 3:
        err = "Input error: [f_in] [f_out]"
        raise ValueError(err)

    f_in, f_out = sys.argv[1:]
    
    crop_svg_file(f_in, f_out)

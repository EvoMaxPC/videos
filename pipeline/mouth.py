from PIL import Image, ImageDraw, ImageFilter
import numpy as np

INK=(20,26,44)
def skin_at(img, cx, cy, r=26):
    a=np.array(img.crop((cx-r,cy+int(r*1.6),cx+r,cy+int(r*2.6)))).reshape(-1,3)
    return tuple(int(v) for v in np.median(a,axis=0))

def make_mouth_layer(w, h, open_amt, stretch=1.0):
    """returns (RGBA patch, RGBA mouth) sized (2*rx+2, 2*ry+2)"""
    rx=int(w*0.72); ry=int(max(h*1.15, w*0.30))
    W,H=rx*2, ry*2
    patch=Image.new('L',(W,H),0)
    ImageDraw.Draw(patch).ellipse([0,0,W,H], fill=255)
    patch=patch.filter(ImageFilter.GaussianBlur(max(2,w*0.06)))
    mouth=Image.new('RGBA',(W,H),(0,0,0,0))
    d=ImageDraw.Draw(mouth)
    cx,cy=rx,ry
    mw=w*0.46*stretch
    mh=max(2.0, h*0.30 + open_amt*w*0.42)
    lw=max(2,int(w*0.09))
    if open_amt<0.07:
        d.arc([cx-mw, cy-mh*2.2, cx+mw, cy+mh*1.6], 195, 345, fill=INK, width=lw)
    else:
        d.ellipse([cx-mw, cy-mh, cx+mw, cy+mh], fill=INK)
        d.ellipse([cx-mw*0.88, cy-mh*0.92, cx+mw*0.88, cy-mh*0.92+mh*0.62], fill=(252,250,246,255))
        d.ellipse([cx-mw*0.52, cy+mh*0.18, cx+mw*0.52, cy+mh*1.02], fill=(190,80,92,255))
    return patch, mouth

def draw_mouth(img, cx, cy, w, h, open_amt, skin, stretch=1.0):
    patch, mouth = make_mouth_layer(w,h,open_amt,stretch)
    PW,PH=patch.size
    box=(cx-PW//2, cy-PH//2)
    skin_img=Image.new('RGB',(PW,PH),skin)
    out=img.copy()
    out.paste(skin_img, box, patch)
    out.paste(mouth, box, mouth)
    return out

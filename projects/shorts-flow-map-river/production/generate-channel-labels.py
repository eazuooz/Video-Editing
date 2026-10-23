"""Deterministic vector text outlines for the two RG values, no font runtime dependency."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from audio_revision import P,R
out=R/'motion-canvas/src/projects'/P.name/'labels';out.mkdir(exist_ok=True)
font=TTFont('C:/Windows/Fonts/malgunbd.ttf');glyphs=font.getGlyphSet();cmap=font.getBestCmap()
for name,text,colour in [('r-half','R 0.5','#F27C70'),('r-full','R 1.0','#F27C70'),('g-half','G 0.5','#92DF9C')]:
 x=0;parts=[];bounds=[]
 for c in text:
  glyph=glyphs[cmap[ord(c)]];pen=SVGPathPen(glyphs);glyph.draw(pen)
  bp=BoundsPen(glyphs);glyph.draw(bp)
  if bp.bounds:bounds.append((x+bp.bounds[0],bp.bounds[1],x+bp.bounds[2],bp.bounds[3]))
  parts.append(f'<path transform="translate({x},0)" d="{pen.getCommands()}"/>');x+=glyph.width
 xmin=min(b[0] for b in bounds);ymin=min(b[1] for b in bounds);xmax=max(b[2] for b in bounds);ymax=max(b[3] for b in bounds)
 s=55/font['head'].unitsPerEm;w=(xmax-xmin)*s;h=(ymax-ymin)*s
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {xmax-xmin} {ymax-ymin}"><g fill="{colour}" transform="translate({-xmin},{ymax}) scale(1,-1)">'+''.join(parts)+'</g></svg>'
 (out/(name+'.svg')).write_text(svg,encoding='utf8')

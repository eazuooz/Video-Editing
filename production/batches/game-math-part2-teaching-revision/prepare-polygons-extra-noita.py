"""Compare further fresh intervals after rejecting shop/menu candidates."""
from pathlib import Path
B=Path(__file__).parent
s=(B/'prepare-polygons-extra-comparison.py').read_text(encoding='utf8')
s=s.replace("polygons-extra-comparison';O.mkdir", "polygons-extra-noita';O.mkdir")
start=s.index('plans=['); end=s.index('\nrows=[]',start)
s=s[:start]+"plans=[('noita-e',source,65,110),('noita-f',source,244,282),('noita-g',source,304,338)]"+s[end:]
s=s.replace("polygons-extra-comparison'\")", "polygons-extra-noita'\")")
exec(compile(s,str(B/'prepare-polygons-extra-comparison.py'),'exec'))

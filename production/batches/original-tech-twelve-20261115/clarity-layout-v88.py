"""Cached existing shorts grammar, with explicit beginner comparison diagrams."""
from pathlib import Path
import importlib.util
H=Path(__file__).resolve().parent
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
previous=load('clarity_cached_layout',H/'shorts-layout-v6.py')
diagrams=load('clarity_explanatory_models',H/'clarity-diagrams-v88.py')
NativeStreamReader=previous.NativeStreamReader
class Composer(previous.Composer):
 def diagram(self,key,seconds,caption=''):
  pixels,e=diagrams.render(key,seconds);im=self.base('해설용 비교 모형');im.paste(pixels,(0,396));self.captioned(im,caption)
  return im,dict(diagramEvidence=e,bodyRect=[0,396,984,984],caption=caption,finalFilm=False)

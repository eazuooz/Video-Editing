"""Cache static overlays only; preserve exact v3 RGB pixels and source timing."""
from pathlib import Path
import importlib.util
from PIL import Image
HERE=Path(__file__).resolve().parent
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
previous=module('ot12_previous_layout',HERE/'shorts-layout-v3.py')
previous.diagrams=module('ot12_source_ordered_diagrams_v3',HERE/'tech-diagrams-v3.py')
NativeStreamReader=previous.NativeStreamReader
class Composer(previous.Composer):
 def __init__(self,slug):
  super().__init__(slug);self._base_cache={};self._caption_cache={};self._small_cats={}
 def base(self,label):
  if label not in self._base_cache:self._base_cache[label]=super().base(label)
  return self._base_cache[label].copy()
 def captioned(self,im,text):
  if not text:return im
  if text not in self._caption_cache:
   sample=Image.new('RGB',(1080,1920),'black');super().captioned(sample,text);self._caption_cache[text]=sample.crop((0,1470,1080,1740))
  # This region is always black before captions: picture ends at1380 and
  # the approved reaction ends at1344. No source picture is covered.
  im.paste(self._caption_cache[text],(0,1470));return im
 def reaction(self,im,pose):
  if pose:
   assert pose in self.cats
   if pose not in self._small_cats:self._small_cats[pose]=self.cats[pose].resize((150,150),Image.Resampling.LANCZOS)
   cat=self._small_cats[pose];im.paste(cat,(35,1194),cat)
  return im

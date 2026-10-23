"""Use exactly the same font-run measurement as the encoded ASS caption writer."""
import re
def wrap_exact(text,font,bold,emphasis):
 def width(s,offset):
  if not emphasis:return font.getlength(s)
  a=max(0,emphasis['start']-offset);b=min(len(s),emphasis['end']-offset)
  if 0<=a<b<=len(s):return font.getlength(s[:a])+bold.getlength(s[a:b])+font.getlength(s[b:])
  return font.getlength(s)
 if width(text,0)<=1560:return [text]
 options=[]
 for word in list(re.finditer(r'\S+',text))[1:]:
  a=text[:word.start()].rstrip();b=text[word.start():];wa=width(a,0);wb=width(b,len(a)+1)
  if max(wa,wb)<=1560:options.append((abs(wa-wb),a,b))
 assert options,('Meaningful paired-clause split required',text)
 _,a,b=min(options);return [a,b]

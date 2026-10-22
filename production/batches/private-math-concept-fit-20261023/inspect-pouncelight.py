from common import *
import urllib.request
from html.parser import HTMLParser
url='https://pouncelight.games/tiny-glade/'
s=urllib.request.urlopen(url,timeout=30).read().decode()
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src'] and v:print(tag,k,v)
Links().feed(s)
o=R/'shared/output/private-math-concept-fit-20261023/research';o.mkdir(exist_ok=True)
(o/'pouncelight.html').write_text(s,encoding='utf8')

from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,urllib.request,urllib.parse,zipfile
P=Path(__file__).resolve().parents[1];R=P.parents[1]
read=lambda p:json.loads(p.read_text('utf-8'))
delivery=read(P/'production/delivery-output.json');D=R/delivery['directory']
base='http://127.0.0.1:9283/'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for name in ('href','src','poster'):
   if a.get(name):self.urls.append(a[name])
html=(D/'index.html').read_text('utf-8');links=Links();links.feed(html)
for f in delivery['files']:
 with (D/f['name']).open('rb') as s:assert hashlib.file_digest(s,'sha256').hexdigest()==f['sha256']
checked=[]
for url in sorted(set(links.urls)):
 if '://' in url:continue
 request=urllib.request.Request(base+urllib.parse.quote(url,safe='/#?='),method='HEAD')
 with urllib.request.urlopen(request) as response:
  assert response.status==200,(url,response.status)
  checked.append({'url':url,'status':response.status,'bytes':int(response.headers['Content-Length'])})
request=urllib.request.Request(base+P.name+'.captioned.mp4',headers={'Range':'bytes=0-1023'})
with urllib.request.urlopen(request) as response:
 body=response.read();assert response.status==206 and len(body)==1024
 byte_range=response.headers['Content-Range']
with zipfile.ZipFile(D/'ai-2d-demo-kit.zip') as z:
 assert z.testzip() is None
 names=z.namelist()
 assert not any(name.lower().endswith(('.safetensors','.pth','.wav','.mp3')) for name in names)
report={'reviewUrl':base,'masterSha256':next(f['sha256'] for f in delivery['files'] if f['name'].endswith('.captioned.mp4')),'fourDeliveryHashes':'match','localLinks':checked,'mp4Range':{'status':206,'bytes':1024,'contentRange':byte_range},'kitArchive':'pass','kitMembers':len(names),'browserHumanPlayback':'not inferred from HTTP checks'}
(P/'production/delivery-http-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'links':len(checked),'rangeStatus':206,'kitMembers':len(names),'sha256':report['masterSha256']}))

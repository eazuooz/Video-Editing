"""Download an explicitly selected, rights-reviewed Commons original."""
from pathlib import Path
import argparse,urllib.request,re,json,hashlib,html,time
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('url');a=p.parse_args()
out=ROOT/'shared/sources'/SLUG/'actual-footage-v2';out.mkdir(parents=True,exist_ok=True)
cache=out/(a.key+'.commons.html')
def request(u):return urllib.request.Request(u,headers={'User-Agent':'YamYamCodingVideoProduction/1.0'})
if cache.exists():page=cache.read_text(encoding='utf-8')
else:page=urllib.request.urlopen(request(a.url),timeout=60).read().decode();cache.write_text(page,encoding='utf-8')
url=html.unescape(re.search(r'class="fullMedia"[\s\S]{0,1000}?href="([^"]+)"',page).group(1))
assert url.startswith('https://upload.wikimedia.org/')
target=out/(a.key+'.webm');part=out/(a.key+'.part')
if not target.exists():
 with urllib.request.urlopen(request(url),timeout=60) as r,part.open('wb') as f:
  while chunk:=r.read(1024*1024):f.write(chunk)
 part.rename(target)
receipt={'pageUrl':a.url,'downloadUrl':url,'path':target.relative_to(ROOT).as_posix(),'sizeBytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'at':time.time()}
(out/(a.key+'.download.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(a.key,target.stat().st_size,flush=True)

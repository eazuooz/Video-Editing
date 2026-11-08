from pathlib import Path
import json,urllib.request,hashlib,zipfile
H=Path(__file__).resolve().parent;j=json.loads((H/'delivery.json').read_text('utf8'));base=j['reviewUrl'];rows=[]
with urllib.request.urlopen(base) as r:assert r.status==200 and b'<video' in r.read()
for f in j['files']:
 with urllib.request.urlopen(urllib.request.Request(base+f['name'],method='HEAD')) as r:
  assert r.status==200 and int(r.headers['Content-Length'])==f['bytes']
  rows.append({'name':f['name'],'status':r.status,'bytes':f['bytes'],'sha256':f['sha256']})
 assert hashlib.file_digest(Path(f['path']).open('rb'),'sha256').hexdigest()==f['sha256']
with urllib.request.urlopen(urllib.request.Request(base+'ai-2d-game-assets.captioned.mp4',headers={'Range':'bytes=0-1023'})) as r:
 assert r.status==206 and len(r.read())==1024;rangeValue=r.headers['Content-Range']
with zipfile.ZipFile(Path(j['directory'])/'room-process-kit.zip') as z:assert z.testzip() is None;entryCount=len(z.namelist())
(H/'delivery-http-qa.json').write_text(json.dumps({'url':base,'indexStatus':200,'files':rows,'rangeStatus':206,'contentRange':rangeValue,'processKitZip':'CRC passed','processKitEntries':entryCount,'browserFullPlayback':'not asserted','userReview':False},ensure_ascii=False,indent=2)+'\n','utf8')
print('Review index / four outputs / range seeking / process kit passed')

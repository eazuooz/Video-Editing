"""Reuse alive9250 helper; three same-inode local media links, no new server."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,psutil
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
RAW=ROOT/'shared/assets/presenting-game-scores/raw'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
helper=psutil.Process(27140);assert 'serve-native-review-v1.py' in ' '.join(helper.cmdline())
assert abs(helper.create_time()-1791509666.837781)<.01
sp=O/'current34-mixed-detailed-render-execution-v2.json';s=rd(sp);assert s['workerDead'] and s['actualOuterExitCode']==0
rows=[];markup=[]
for row in s['results']:
 sid=row['id'];source=ROOT/row['output'];assert sha(source)==row['outputSha256']
 link=RAW/f'orientation-mixed-detailed-{sid}-v1.mp4';assert not link.exists();link.hardlink_to(source)
 assert link.stat().st_ino==source.stat().st_ino and sha(link)==row['outputSha256']
 rows.append(dict(scene=sid,source=rel(source),link=rel(link),sha256=row['outputSha256'],sameInode=True,frames=row['frames']))
 markup.append(f'<section><h2>{sid} 상세 설명과 기존 게임 비교</h2><video id="v{sid}" controls muted preload="metadata" src="{link.name}"></video><p><button id="p{sid}" onclick="document.getElementById(\'v{sid}\').play()">재생 {sid}</button></p></section>')
html=RAW/'orientation-current34-mixed-detailed-review-v1.html';assert not html.exists()
html.write_text('<!doctype html><meta charset="utf-8"><title>Orientation mixed detailed V1 review</title><style>body{font:18px sans-serif;background:#eef2ef;color:#24303d}video{width:min(1200px,96vw)}section{margin:30px}button{font-size:22px;padding:12px}</style><h1>현재 상세 비교 03b / 07b / 10b</h1><p>정상 1× 무음 · 실제 게임 구간 재사용 / 설명 모형만 교체 · 최종244자막 승인 아님</p>'+''.join(markup),'utf-8')
out=O/'current34-mixed-detailed-browser-preparation-v1.json';assert not out.exists()
out.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),helperPid=helper.pid,helperCreateTime=helper.create_time(),helperCommandLine=helper.cmdline(),helperCwd=helper.cwd(),newServer=0,sourceMediaCopies=0,execution=rel(sp),executionSha256=sha(sp),rows=rows,html=rel(html),htmlSha256=sha(html),url='http://127.0.0.1:9250/'+html.name,newImageGit=0),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(helperAlive=True,newServer=0,hardlinks=3,url='http://127.0.0.1:9250/'+html.name)))

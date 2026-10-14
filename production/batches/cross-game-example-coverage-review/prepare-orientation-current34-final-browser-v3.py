"""Expose the closed detailed pair through the existing local9250 helper."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,psutil
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
RAW=ROOT/'shared/assets/presenting-game-scores/raw'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
helper=psutil.Process(27140)
assert abs(helper.create_time()-1791509666.837781)<.01 and 'serve-native-review-v1.py' in ' '.join(helper.cmdline())
sp=O/'current34-final-pair-execution-v3.json';s=read(sp)
assert s['actualOuterExitCode']==0 and s['workerDead'] and len(s['pair'])==2 and s['frames']==65917
rows=[]
for label,row in zip(['clean','captioned'],s['pair']):
 p=ROOT/row['path'];assert sha(p)==row['sha256']
 link=RAW/f'orientation-current34-final-{label}-v3.mp4';assert not link.exists();link.hardlink_to(p)
 assert link.stat().st_ino==p.stat().st_ino and sha(link)==row['sha256']
 rows.append(dict(kind=label,source=rel(p),link=rel(link),sha256=row['sha256'],sameInode=True))
hp=RAW/'orientation-current34-final-review-v3.html';assert not hp.exists()
hp.write_text('<!doctype html><meta charset="utf-8"><title>Orientation current34 detailed final reviewV3</title><style>body{font:18px sans-serif;background:#eef2ef;color:#24303d}video{width:min(1440px,96vw)}button{font-size:22px;padding:12px}</style><h1>현재 상세 설명·34음성·244고정 자막 최종 검수본</h1><p>1098.616667초 / 60fps · 정상1× 무음 / 전체 사람 청취 승인 대기</p><video id="vfinal" controls muted preload="metadata" src="orientation-current34-final-captioned-v3.mp4"></video><p><button id="playfinal" onclick="document.getElementById(\'vfinal\').play()">최종 자막본 정상 재생</button></p><p>기존 팔레트·원래 음성·고양이·회원 엔딩 유지 / 최종 표본 검수 전 승인 아님</p>','utf-8')
out=O/'current34-final-browser-preparation-v3.json';assert not out.exists()
out.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),helperPid=helper.pid,helperCreateTime=helper.create_time(),helperCommandLine=helper.cmdline(),helperCwd=helper.cwd(),execution=rel(sp),executionSha256=sha(sp),rows=rows,html=rel(hp),htmlSha256=sha(hp),url='http://127.0.0.1:9250/'+hp.name,newServer=0,sourceCopies=0,newImageGit=0),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(url='http://127.0.0.1:9250/'+hp.name,hardlinks=2,newServer=0)))

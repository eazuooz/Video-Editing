"""Seal the32 actual newly read samples, then expose their existing review media."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
RAW=ROOT/'shared/assets/presenting-game-scores/raw'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=O/'current34-06a-caption-clearance-execution-v1.json';s=rd(sp);assert s['workerDead'] and s['actualOuterExitCode']==0
x=s['scenes'][0];assert len(x['samples'])==32 and len(x['boards'])==8
for v in x['samples']+x['boards']:assert sha(ROOT/v['path'])==v['sha256']
out=O/'current34-06a-caption-clearance-sampled-direct-review-v1.json';assert not out.exists()
r=dict(recordedAt=datetime.now(timezone.utc).isoformat(),execution=sp.relative_to(ROOT).as_posix(),executionSha256=sha(sp),samples=x['samples'],boards=x['boards'],all32SamplesDirectlyRead=True,all8BoardsDirectlyRead=True,
    originalResolutionProof=x['samples'][0],observations='All32 current-caption samples directly read. Gray semantic legend and blue body-axis label are clearly separated above the actual widest two-line captions, including original held absolute14232. Detailed aircraft/cockpit/wings/tail/engines and red/green/blue axes remain visible. Narrated local(1,0,0) to world(0,1,0), followed by world-read matrix columns, retain their sequence. All three cue intervals, quiet last frame and1 EX rounding tail are preserved.',
    targetedCaptionClearanceApproved=True,allIntermediateFramesApproved=False,humanListeningApproved=False,all244FinalCuePixelsApproved=False)
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
p=psutil.Process(27140);assert abs(p.create_time()-1791509666.837781)<.01 and p.cwd()==str(ROOT) and 'serve-native-review-v1.py' in ' '.join(p.cmdline())
source=ROOT/x['output'];assert sha(source)==x['outputSha256'];target=RAW/'orientation-06a-current-caption-clearance-v1.mp4';assert not target.exists();os.link(source,target);assert os.path.samefile(source,target)
html=RAW/'orientation-06a-current-caption-clearance-review-v1.html';assert not html.exists()
html.write_text('''<!doctype html><meta charset="utf-8"><title>Orientation 06a caption clearance V1</title>
<style>body{font:18px sans-serif;background:#eef2ef}video{width:min(1100px,96vw)}button{font-size:22px;padding:12px}</style>
<h1>몸의 자를 바깥 기준으로 읽기 · 자막 여백</h1><p>정상1× 무음 · 문구 위치만 교정 · 최종 조립본 검수 별도</p>
<video id="v06a" controls muted preload="metadata" src="orientation-06a-current-caption-clearance-v1.mp4"></video>
<p><button id="p06a" onclick="document.getElementById('v06a').play()">재생06a</button></p>''','utf-8')
print(json.dumps(dict(review=out.relative_to(ROOT).as_posix(),sha256=sha(out),samples=32,boards=8,url='http://127.0.0.1:9250/'+html.name,samefile=True)))

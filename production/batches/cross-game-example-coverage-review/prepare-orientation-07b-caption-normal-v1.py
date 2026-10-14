"""Serve the already reviewed current-caption 07b through the existing helper."""
from pathlib import Path
import hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
RAW=ROOT/'shared/assets/presenting-game-scores/raw'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=psutil.Process(27140)
assert abs(p.create_time()-1791509666.837781)<.01
assert p.cwd()==str(ROOT) and 'serve-native-review-v1.py' in ' '.join(p.cmdline())
sp=O/'current34-clearance-caption-bindings-execution-v1.json';s=rd(sp)
assert s['workerDead'] and s['actualOuterExitCode']==0
r=rd(O/'current34-clearance-caption-pixels-partial-direct-review-v1.json')
assert r['allSelectedPixelsDirectlyRead'] and r['samplesDirectlyRead']==557
x=next(x for x in s['scenes'] if x['id']=='07b');source=ROOT/x['output']
assert sha(source)==x['outputSha256']
target=RAW/'orientation-07b-current-caption-clearance-v1.mp4'
assert not target.exists();os.link(source,target)
assert os.path.samefile(source,target)
html=RAW/'orientation-07b-current-caption-clearance-review-v1.html'
assert not html.exists()
html.write_text('''<!doctype html><meta charset="utf-8"><title>Orientation 07b current-caption clearance V1</title>
<style>body{font:18px sans-serif;background:#eef2ef}video{width:min(1100px,96vw)}button{font-size:22px;padding:12px}</style>
<h1>비행기 날개와 현재 고정 자막 여백</h1><p>정상 1× 무음 · 전체 날개와 조작 UI · 최종 조립본 검수 별도</p>
<video id="v07b" controls muted preload="metadata" src="orientation-07b-current-caption-clearance-v1.mp4"></video>
<p><button id="p07b" onclick="document.getElementById('v07b').play()">재생 07b</button></p>''','utf-8')
print(json.dumps(dict(url='http://127.0.0.1:9250/'+html.name,source=x['output'],sourceSha256=x['outputSha256'],samefile=True,helperPid=p.pid)))

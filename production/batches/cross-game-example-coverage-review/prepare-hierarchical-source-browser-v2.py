"""Add the new official stream once to the already-running native review helper."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import psutil

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
MEDIA=ROOT/'shared/assets/presenting-game-scores/raw'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
out=V/'source-browser-preparation-v2.json'
assert not out.exists(), 'Reuse the existing version2 browser preparation'
closed=read(V/'source-acquisition-execution-v2.session.json')
assert closed['actualOuterExitCode']==0 and closed['exactWorkerDead'] and closed['exactChildrenDead']
p=psutil.Process(27140)
assert abs(p.create_time()-1791509666.8377817)<.02
assert p.cmdline()[-1]=='production/batches/sakurai-planning-game-design/proof-presenting-game-scores/serve-native-review-v1.py'
assert p.cwd()==str(ROOT)
prior=read(V/'source-browser-preparation-v1.json');links=prior['sourceLinks']
for link in links:
    assert os.path.samefile(ROOT/link['source'],MEDIA/link['urlPath'])
    assert (ROOT/link['source']).stat().st_size==link['fileBytes']
state=read(V/'source-acquisition-execution-v2.json');assert len(state['results'])==1
source=state['results'][0];sid=source['videoId'];assert sid=='6TNjosDftog'
original=ROOT/source['localMediaPath'];link=MEDIA/('hierarchical-source-'+sid+'-v2.mp4')
assert not link.exists()
os.link(original,link)
assert os.path.samefile(original,link) and original.stat().st_size==source['fileBytes']
links=links+[dict(videoId=sid,source=source['localMediaPath'],urlPath=link.name,sameFile=True,
    sourceSha256=source['fileSha256'],fileBytes=source['fileBytes'])]
html=MEDIA/'hierarchical-candidate-native-review-v2.html';assert not html.exists()
html.write_text('''<!doctype html><meta charset="utf-8"><title>Hierarchy candidate native review v2</title>
<style>body{background:#181b21;color:#fff;font:15px sans-serif;margin:8px;overflow-x:hidden}h1{font-size:18px;margin:4px 0}p{margin:4px 0}input{width:82px}button,select,input{font:inherit;padding:4px;margin:2px}#status{font:12px monospace;padding:4px;background:#262c36;overflow-wrap:anywhere}video{display:block;width:100%;height:calc(100vh - 145px);object-fit:contain;background:#000}</style>
<h1>Hierarchy native source review v2</h1><p>Candidate research: source rate1/muted. Final narration, captions, rights and four-game teaching review pending.</p>
<select id="source">'''+''.join('<option value="'+x['urlPath']+'"'+(' selected' if x['videoId']==sid else '')+'>'+x['videoId']+'</option>' for x in links)+'''</select>
<label>Start seconds <input id="start" type="number" value="2306" step="0.01"></label>
<label>End seconds <input id="end" type="number" value="2330" step="0.01"></label>
<button id="load">Load interval</button><button id="play">Play normal1x</button><button id="pause">Pause</button>
<p id="status">No source loaded</p><video id="v" controls muted playsinline preload="metadata"></video>
<script>
const v=document.querySelector('#v'),s=document.querySelector('#source'),a=document.querySelector('#start'),b=document.querySelector('#end'),status=document.querySelector('#status');
let stop=2330;
const render=()=>status.textContent=JSON.stringify({source:s.value,currentTime:v.currentTime,duration:v.duration,intervalStart:Number(a.value),intervalEnd:stop,paused:v.paused,ended:v.ended,muted:v.muted,playbackRate:v.playbackRate,videoWidth:v.videoWidth,videoHeight:v.videoHeight});
document.querySelector('#load').onclick=()=>{v.pause();v.src=s.value;v.load();v.muted=true;v.playbackRate=1;stop=Number(b.value);v.onloadedmetadata=()=>{v.currentTime=Number(a.value);render()};};
document.querySelector('#play').onclick=()=>{v.muted=true;v.playbackRate=1;v.play();};
document.querySelector('#pause').onclick=()=>{v.pause();render();};
v.ontimeupdate=()=>{if(v.currentTime>=stop&&!v.paused)v.pause();render()};v.onpause=render;v.onplay=render;v.onseeked=render;
</script>''','utf-8')
proof=dict(recordedAt=datetime.now(timezone.utc).isoformat(),existingHelper=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd()),
    newServerStarted=False,oldLinksRecreated=0,newHardLinks=1,sourceLinks=links,url='http://127.0.0.1:9250/'+html.name,
    htmlPath=html.relative_to(ROOT).as_posix(),htmlSha256=hashlib.sha256(html.read_bytes()).hexdigest(),
    previousHtmlPreserved=True,candidatePlaybackApproved=False,newGitMedia=0)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(existingHelperPid=27140,newServer=False,previousLinksRecreated=0,newLinks=1,url=proof['url'])))

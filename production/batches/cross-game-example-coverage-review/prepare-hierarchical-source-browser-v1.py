"""Expose candidate sources through the existing loopback helper, with unique hard links."""
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
assert not (V/'source-browser-preparation-v1.json').exists()
p=psutil.Process(27140)
assert abs(p.create_time()-1791509666.8377817)<.02
assert p.cmdline()[-1]=='production/batches/sakurai-planning-game-design/proof-presenting-game-scores/serve-native-review-v1.py'
assert p.cwd()==str(ROOT)
state=read(V/'source-acquisition-execution-v1.json')
links=[]
for source in state['results']:
    sid=source['videoId']
    original=ROOT/source['localMediaPath']
    link=MEDIA/('hierarchical-source-'+sid+'-v1.mp4')
    assert not link.exists(), 'Do not replace an existing helper artifact'
    os.link(original,link)
    assert os.path.samefile(original,link) and original.stat().st_size==source['fileBytes']
    links.append(dict(videoId=sid,source=source['localMediaPath'],urlPath=link.name,
        sameFile=True,sourceSha256=source['fileSha256'],fileBytes=source['fileBytes']))
assert {x['videoId'] for x in links}>={'gVkhhrLARU8','Jsc7003gSu0'}
html=MEDIA/'hierarchical-candidate-native-review-v1.html'
assert not html.exists()
html.write_text('''<!doctype html><meta charset="utf-8"><title>Hierarchy candidate native review v1</title>
<style>body{background:#181b21;color:#fff;font:18px sans-serif;margin:20px}video{width:min(100%,1280px);background:#000}input{width:90px}button,select,input{font:inherit;padding:6px;margin:4px}#status{padding:10px;background:#262c36}</style>
<h1>Hierarchy candidate native review v1</h1>
<p>Original official source pixels, muted at rate1. Source-only research: final narration, captions, rights and four-game teaching approval remain pending.</p>
<select id="source">'''+''.join('<option value="'+x['urlPath']+'">'+x['videoId']+'</option>' for x in links)+'''</select>
<label>Start seconds <input id="start" type="number" value="23" step="0.01"></label>
<label>End seconds <input id="end" type="number" value="156" step="0.01"></label>
<button id="load">Load interval</button><button id="play">Play normal1x</button><button id="pause">Pause</button>
<p id="status">No source loaded</p><video id="v" controls muted playsinline preload="metadata"></video>
<script>
const v=document.querySelector('#v'),s=document.querySelector('#source'),a=document.querySelector('#start'),b=document.querySelector('#end'),status=document.querySelector('#status');
let stop=156;
const render=()=>status.textContent=JSON.stringify({source:s.value,currentTime:v.currentTime,duration:v.duration,intervalStart:Number(a.value),intervalEnd:stop,paused:v.paused,ended:v.ended,muted:v.muted,playbackRate:v.playbackRate,videoWidth:v.videoWidth,videoHeight:v.videoHeight});
document.querySelector('#load').onclick=()=>{v.pause();v.src=s.value;v.load();v.muted=true;v.playbackRate=1;stop=Number(b.value);v.onloadedmetadata=()=>{v.currentTime=Number(a.value);render()};};
document.querySelector('#play').onclick=()=>{v.muted=true;v.playbackRate=1;v.play();};
document.querySelector('#pause').onclick=()=>{v.pause();render();};
v.ontimeupdate=()=>{if(v.currentTime>=stop&&!v.paused)v.pause();render()};v.onpause=render;v.onplay=render;v.onseeked=render;
</script>''','utf-8')
proof=dict(recordedAt=datetime.now(timezone.utc).isoformat(),existingHelper=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd()),
    newServerStarted=False,sourceLinks=links,url='http://127.0.0.1:9250/'+html.name,
    htmlPath=html.relative_to(ROOT).as_posix(),htmlSha256=hashlib.sha256(html.read_bytes()).hexdigest(),
    candidatePlaybackApproved=False,newGitMedia=0)
(V/'source-browser-preparation-v1.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(existingHelperPid=27140,newServer=False,linkedSources=len(links),url=proof['url'])))

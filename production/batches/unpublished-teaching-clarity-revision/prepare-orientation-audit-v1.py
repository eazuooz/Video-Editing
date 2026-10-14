"""Preserve current orientation baseline; create local read-only playback audit."""
from pathlib import Path
import json,hashlib,os,subprocess,datetime
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'production/batches/unpublished-teaching-clarity-revision'
P=ROOT/'projects/game-math-orientation-matrices'
R=P/'revision-teaching-clarity-v1'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for buf in iter(lambda:f.read(4*1024*1024),b''): h.update(buf)
 return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not (R/'baseline-preservation-v1.json').exists(),'Existing audit must be resumed, not overwritten'
R.mkdir(exist_ok=True)
cp=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|ffmpeg|node)' -and ($_.CommandLine -match 'serve-native-review|9253|train_multiview|phase1_train|queue|gpu-handoff|unpublished-teaching') } | Select-Object ProcessId,ParentProcessId,CreationDate,Name,CommandLine | ConvertTo-Json -Depth 3"],capture_output=True,text=True,encoding='utf8',check=True)
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
write(R/'audit-resource-v1.json',{'observedAt':now,'cim':json.loads(cp.stdout),'gpu':gpu.stdout.strip(),'ownHeavyCpuJobs':0,'ownGpuJobs':0,'foreignProcessesModified':0})
protected=[P/'project.json',P/'script/narration.ko.json',P/'script/narration.en.json',P/'script/final.ko.srt',P/'script/final.en.srt',P/'sources/gameplay-cuts.json',P/'production/timeline.json',P/'production/qa.json',ROOT/'production/batches/game-math-part2-full-series/lessons/game-math-orientation-matrices.json',ROOT/'manim/projects/game-math-part2-full-series/lesson.py']
timeline=json.loads((P/'production/timeline.json').read_text(encoding='utf-8-sig'))
protected.extend(ROOT/s['voice'] for s in timeline['scenes'])
manifest=json.loads((P/'project.json').read_text(encoding='utf-8-sig'))
protected.extend(ROOT/manifest['paths'][k] for k in ['narration','audioMix','videoClean','videoBurnedCaptions'])
entries=[]
for p in protected:
 assert p.is_file(),p
 entries.append({'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size})
snap=R/'baseline-snapshot-v1';snap.mkdir(exist_ok=True)
for p in protected[:10]:
 q=snap/rel(p).replace('/','__');assert not q.exists();q.write_bytes(p.read_bytes())
write(R/'baseline-preservation-v1.json',{'observedAt':now,'baselineVideoId':'6-kP65hrZcI','baselineFinalFrames':54145,'bodyActualFrames':21370,'bodyExplanationFrames':32055,'originalOverviewSeconds':20.16,'originalSceneCount':24,'originalKoLines':140,'originalEnLines':140,'protectedFiles':entries,'baselineAndSourceBytesModified':0,'oldScheduledUploadPreserved':True,'newFinalMediaApproved':False,'replacementVideoId':None})
raw=ROOT/'shared/assets/presenting-game-scores/raw'
links=[]
for name,path in [('orientation-original-ncr-v1.mp4',ROOT/'shared/output/game-math-part2-full-series/sources/-Hpr1dqRzIk.mp4'),('orientation-alternative-superflight-v1.mp4',ROOT/'shared/output/game-math-part2-full-series/sources/FvSgGn941U0.mp4'),('orientation-baseline-captioned-v1.mp4',ROOT/manifest['paths']['videoBurnedCaptions'])]:
 dest=raw/name
 if dest.exists():assert os.path.samefile(path,dest)
 else:os.link(path,dest)
 links.append({'path':rel(dest),'source':rel(path),'sameFile':os.path.samefile(path,dest),'bytes':path.stat().st_size,'sha256':sha(path),'mediaCopiedOrEncoded':False})
write(R/'playback-hardlinks-v1.json',links)
scenes=[{'id':s['id'],'start':s['start'],'title':s['title']} for s in timeline['scenes']]
html='''<!doctype html><meta charset="utf-8"><title>Orientation source clarity audit</title><style>body{background:#111;color:#fff;font:16px sans-serif;margin:12px}video{width:min(1280px,100%)}button,input,select{padding:8px;margin:4px}pre{white-space:pre-wrap}</style>
<h1>방향·회전 행렬 · 실제 원본/대안/기존 영상 읽기</h1><p>정상 1배속·음소거 검토. 화면의 기울기는 월드 회전값이나 내부 엔진 데이터가 아닙니다.</p><label>자료 <select id="src"><option value="orientation-original-ncr-v1.mp4">NCR 원본</option><option value="orientation-alternative-superflight-v1.mp4">Superflight 대안</option><option value="orientation-baseline-captioned-v1.mp4">현재 자막 완성본</option></select></label><video id="v" controls muted preload="metadata" src="orientation-original-ncr-v1.mp4"></video>
<div><label>시작 초<input id="a" type="number" value="22" step="0.0166666667"></label><label>끝 초<input id="b" type="number" value="61" step="0.0166666667"></label><button id="seek">시작으로 이동</button><button id="play">현재 구간 1배속 재생</button><button id="pause">일시정지</button></div><div id="scenes"></div><pre id="status"></pre><pre id="events"></pre>
<script>const scenes=SCENES,v=document.getElementById('v'),records=[];let end=61;function update(){document.getElementById('status').textContent=JSON.stringify({src:v.getAttribute('src'),currentTime:v.currentTime,duration:v.duration,paused:v.paused,ended:v.ended,rate:v.playbackRate,muted:v.muted},null,2);document.getElementById('events').textContent=JSON.stringify(records,null,2)}
document.getElementById('src').onchange=e=>{v.pause();v.src=e.target.value;v.load();update()};document.getElementById('seek').onclick=()=>{v.pause();v.currentTime=Number(document.getElementById('a').value);update()};document.getElementById('play').onclick=()=>{end=Number(document.getElementById('b').value);v.currentTime=Number(document.getElementById('a').value);v.muted=true;v.playbackRate=1;v.play();update()};document.getElementById('pause').onclick=()=>v.pause();v.addEventListener('timeupdate',()=>{if(!v.paused&&v.currentTime>=end)v.pause();update()});['loadedmetadata','seeked','play','pause','ended'].forEach(e=>v.addEventListener(e,()=>{records.push({event:e,t:v.currentTime,src:v.getAttribute('src'),observedAt:new Date().toISOString()});update()}));
scenes.forEach(s=>{let b=document.createElement('button');b.textContent=s.id+' '+s.title;b.onclick=()=>{document.getElementById('src').value='orientation-baseline-captioned-v1.mp4';v.pause();v.src='orientation-baseline-captioned-v1.mp4';document.getElementById('a').value=s.start;document.getElementById('b').value=s.start+12;v.currentTime=s.start;update()};document.getElementById('scenes').appendChild(b)});</script>'''.replace('SCENES',json.dumps(scenes,ensure_ascii=False))
helper=raw/'orientation-source-clarity-audit-v1.html';assert not helper.exists();helper.write_text(html,encoding='utf8')
write(R/'latest-checkpoint.json',{'observedAt':now,'stage':'baseline-preserved-source-and-gameplay-audit','baseline':rel(R/'baseline-preservation-v1.json'),'resource':rel(R/'audit-resource-v1.json'),'sourceSectionsRead':['8.1','8.2.1','8.2.2 correction','8.2.3','8.2.4','8.2.5'],'currentKoEnFullScriptsRead':True,'originalOverviewRetainRecommended':True,'actualGameplayComparisonApproved':False,'dependentNewScriptPrepared':False,'newTtsStarted':False,'newFinalMediaApproved':False,'privateReplacementSaved':False,'replacementVideoId':None,'next':'Directly compare actual source playback and existing annotated pixels; write retained/inserted causal map before dependent narration.'})
q=json.loads((B/'queue.json').read_text(encoding='utf-8-sig'))
entry=next(x for x in q['items'] if x['slug']=='game-math-orientation-matrices') if 'items' in q else None
if entry:
 entry['status']='content-and-gameplay-clarity-audit-in-progress';entry['auditCheckpoint']=rel(R/'latest-checkpoint.json')
 q['updatedAt']=now;write(B/'queue.json',q)
print(json.dumps({'protectedFiles':len(entries),'links':len(links),'helper':rel(helper),'replacementId':None,'ownGpuJobs':0}))

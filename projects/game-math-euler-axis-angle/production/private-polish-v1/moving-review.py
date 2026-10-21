"""Finite new-pixel samples and local playback controls, never production inputs."""
import json,sys
from PIL import Image
import common as c
import preview as p

def main():
 paths=[]
 for sid in ['16','21','24']:
  for i,t in enumerate(c.SCENES[sid]['lineStarts']):
   q=p.still(sid,min(t+2.7,c.SCENES[sid]['seconds']-.1),f'updated-{sid}-cue-{i+1:02}')
   if q:paths.append(q)
 for j in range(0,len(paths),6):p.board(paths[j:j+6],f'updated-board-{j//6+1:02}')
 actual=[]
 for w in c.read(c.P/'sources/annotation-plan-v2.json')['windows']:
  sid=w['scene'];files=[]
  if not(c.O/'clips'/f'{sid}.mp4').exists():continue
  for i in range(6):
   t=w['baselineSceneWindow'][0]+.15+i*(w['baselineSceneWindow'][1]-w['baselineSceneWindow'][0]-.3)/5
   q=p.still(sid,t,f'guide-{sid}-{i:02}')
   if q:files.append(q);actual.append(c.rel(q))
  p.board(files,f'guide-board-{sid}',columns=3,width=640)
 rows=[{'id':s['id'],'start':s['start'],'window':next((w['baselineSceneWindow'][0] for w in c.read(c.P/'sources/annotation-plan-v2.json')['windows'] if w['scene']==s['id']),0)} for s in c.T['scenes']]
 page='''<!doctype html><meta charset="utf-8"><title>기존 강의 보강 · 움직임 검수</title><style>body{background:#222;color:white;font:18px system-ui}video{width:min(100%,1280px);display:block}button{font:inherit;margin:5px;padding:8px}#state{margin:10px}</style><video id="v" controls muted></video><div id="state"></div><button id="pause">일시정지</button><button id="small">375px</button><button id="large">1080p 화면</button><div id="buttons"></div><script>const rows=ROWS;let limit=0;rows.forEach(r=>{let b=document.createElement('button');b.textContent='장면 '+r.id;b.onclick=()=>{v.src='clips/'+r.id+'.mp4';v.onloadedmetadata=()=>{v.currentTime=Math.max(0,r.window-.25);limit=v.currentTime+8;v.play()}};buttons.appendChild(b)});v.ontimeupdate=()=>{state.textContent=v.currentTime.toFixed(2)+' / '+v.duration.toFixed(2);if(v.currentTime>=limit)v.pause()};pause.onclick=()=>v.pause();small.onclick=()=>v.style.width='375px';large.onclick=()=>v.style.width='min(100%,1280px)';</script>'''.replace('ROWS',json.dumps(rows))
 (c.O/'moving-review.html').write_text(page,encoding='utf8')
 c.save(c.O/'qa/additional-samples.json',{'updatedExplanations':[c.rel(x) for x in paths],'gameplayGuideFrames':actual})
 print('Changed explanatory and actual-guide frames ready.',flush=True)

if __name__=='__main__':main()

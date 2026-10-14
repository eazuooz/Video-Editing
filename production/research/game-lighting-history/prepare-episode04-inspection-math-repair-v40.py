"""Two numeric geometry fixes; retain all other pixels and approved PCM."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, wave
R=Path(__file__).resolve().parents[3]
S=R/'motion-canvas/src/projects/game-lighting-history-04/spatial'
P=R/'projects/game-lighting-history-04/production'
D=R/'production/research/game-lighting-history/local/episode04-inspection-math-repair-v40'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
def write(p,j):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
assert not D.exists();(D/'renders').mkdir(parents=True);(D/'audio').mkdir()
model=(S/'frame-inspection-model-v1.tsx').read_text('utf-8')
old="e.add(es.box(x-55,0,20,60,110,()=>8+170*dep*(1-p()),P.teal));\n  e.add(es.box(x+55,0,20,60,110,()=>8+170*(1-dep)*p(),P.orange));"
new="e.add(new Node({opacity:()=>.25+.75*(1-p()),children:[es.box(x-55,0,20,60,110,170*dep,P.teal)]}));\n  e.add(new Node({opacity:p,children:[es.box(x+55,0,20,60,110,170*(1-dep),P.orange)]}));"
assert old in model;model=model.replace(old,new)
old="n.add(ns.box(x,0,20,100,170,()=>30+samples[q]*12*p(),P.teal));"
new="n.add(new Node({opacity:()=>Math.max(0,Math.min(1,p()*6-q)),children:[ns.box(x,0,20,100,170,samples[q]*12,P.teal)]}));"
assert old in model;model=model.replace(old,new)
model=model.replace("n.add(text('예시 N=6 · 평균 9.33 ms · 범위 8~11 ms',0,-230,33,P.yellow));","n.add(text('예시 N=6 · 평균 9.33 ms · 범위 8~11 ms',0,-230,33,P.yellow));\n n.add(text('같은 높이 단위 · 0 ms 기준에서 비교',0,-185,25,P.muted));")
mp=S/'frame-inspection-model-v2.tsx';assert not mp.exists();mp.write_text(model,'utf-8')
rt=(S/'narrated-runtime-v2.tsx').read_text('utf-8').replace("'./frame-inspection-model-v1'","'./frame-inspection-model-v2'")
rp=S/'narrated-inspection-math-runtime-v7.tsx';assert not rp.exists();rp.write_text(rt,'utf-8')
oldPlan=read(R/'production/research/game-lighting-history/local/episode04-clean-model-inputs-v5/plan.json')
scenes=[s for s in oldPlan['scenes'] if s['id'] in ['original-22r-5','original-22rb-6']]
assert [s['frames'] for s in scenes]==[832,804]
chunks=[];mapping=[];at=0
with wave.open(str(R/oldPlan['currentAudio']['path']),'rb') as w:
 assert(w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
 for s in scenes:
  w.setpos(s['sourceSamples'][0]);buf=w.readframes(s['sourceSamples'][1]-s['sourceSamples'][0]);assert hashlib.sha256(buf).hexdigest()==s['originalPcmSha256']
  chunks.extend([buf,bytes(s['silentPaddingSamples']*2)])
  wrapper=S/f"clean-inspection-math-{s['id']}-v40.tsx"
  assert not wrapper.exists();wrapper.write_text((R/s['wrapper']).read_text('utf-8').replace("'./narrated-runtime-v2'","'./narrated-inspection-math-runtime-v7'"),'utf-8')
  mapping.append({'id':s['id'],'fromFrame':at,'toFrame':at+s['frames'],'frames':s['frames'],'wrapper':rel(wrapper),'wrapperSha256':sha(wrapper),'originalPcmSha256':s['originalPcmSha256']});at+=s['frames']
audio=D/'audio/episode04-inspection-math-repair-v40.wav'
with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b''.join(chunks))
assert sum(len(b) for b in chunks)//2==at*400
name='episode04-inspection-math-repair-v40';pr=S/(name+'.ts');assert not pr.exists()
pr.write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(f"import p{i} from './{Path(m['wrapper']).stem}?scene';" for i,m in enumerate(mapping))+"\nexport default makeProject({scenes:[p0,p1],audio:"+json.dumps('/@fs/'+audio.as_posix())+"});\n",'utf-8')
write(pr.with_suffix('.meta'),{'version':0,'shared':{'background':None,'range':[0,(at-1)/60],'size':{'x':1920,'y':1080},'audioOffset':0},'preview':{'fps':30,'resolutionScale':1},'rendering':{'fps':60,'resolutionScale':1,'colorSpace':'srgb','exporter':{'name':'@motion-canvas/ffmpeg','options':{'fastStart':True,'includeAudio':True}}}})
job={'name':name,'project':rel(pr),'frames':at,'scenes':mapping,'audio':{'path':rel(audio),'sha256':sha(audio),'samples':at*400},'output':rel(D/'renders'/f'{name}.mp4'),'execution':rel(D/'renders'/f'{name}.execution.json')}
write(D/'plan.json',{'preparedAt':stamp(),'runtime':{'path':rel(rp),'sha256':sha(rp)},'model':{'path':rel(mp),'sha256':sha(mp)},'jobs':[job],'scenes':scenes,'newTts':0,'allFinalPixelsReviewed':False,'uploaded':False})
write(P/'inspection-numeric-math-rejection-v40.json',{'reviewedAt':stamp(),'basis':'Direct clean boards012 and019-020; mathematical source audit','historicalPlan':'projects/game-lighting-history-04/production/inspection-chapter-review-plan-v38.json','rejectedScenes':['original-22r-5','original-22rb-6'],'findings':['22r5 depth labels were fixed while d height multiplied by 1-p and reverse height by p; intermediate geometry did not encode labelled values.','22rb6 fixed 8/10/9/11/8/10 ms labels accompanied heights30+12*value*p; intermediate and final heights were not zero-baseline proportional values.'],'repair':['Fixed d and 1-d geometry, reveal by opacity only.','Fixed 12px/ms heights from0, reveal six measurements in sequence by opacity.'],'preserved':['PCM','paragraphs','captions','frames','24 other review cuts'],'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'uploaded':False})
cfg=R/'motion-canvas/vite.game-lighting-history04.inspection-math-repair-v40.config.ts'
assert not cfg.exists()
t=(R/'motion-canvas/vite.game-lighting-history04.postprocess-math-repair-v36.config.ts').read_text('utf-8')
t=t.replace('episode04-postprocess-math-repair-v36','episode04-inspection-math-repair-v40').replace('game-lighting-history04-postprocess-math-repair-v36','game-lighting-history04-inspection-math-repair-v40').replace('port:9268','port:9269')
cfg.write_text(t,'utf-8')
write(R/'motion-canvas/tsconfig.game-lighting-history04-inspection-math-repair-v40.json',{'extends':'./tsconfig.json','include':['src/env.d.ts',rel(pr).replace('motion-canvas/',''),*[m['wrapper'].replace('motion-canvas/','') for m in mapping]]})
cp=R/'production/research/game-lighting-history/checkpoint.json';j=read(cp);j['episode04InspectionMathRepairV40']={'plan':rel(D/'plan.json'),'frames':at,'rendered':False,'newTts':0,'finalApproved':False};j['updatedAt']=stamp();tmp=cp.with_suffix('.inspection-math-v40.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
print(json.dumps({'preparedFrames':at,'scenes':2,'newTts':0,'newGitImages':0}))

"""Versioned two-scene repair; preserve original audio, all other chapter cuts."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, wave, psutil

R=Path(__file__).resolve().parents[3]
P=R/'projects/game-lighting-history-04/production'
S=R/'motion-canvas/src/projects/game-lighting-history-04/spatial'
D=R/'production/research/game-lighting-history/local/episode04-postprocess-math-repair-v36'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,j):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
sessions=[]
for folder,ep,sid in [('episode04-postprocess-chapter-v34',P/'postprocess-chapter-review-execution-v34.json',94568),('episode04-postprocess-encoded-v34',R/'production/research/game-lighting-history/local/episode04-postprocess-encoded-v34/execution.json',10944),('episode04-renderdoc-native-v35',R/'production/research/game-lighting-history/local/episode04-renderdoc-native-v35/execution.json',61055)]:
 s=read(ep);w=s['worker'];assert s['active'] is None and all(c['exitCode']==0 for c in s['commands'])
 try:assert abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01,'Original worker remains alive'
 except psutil.NoSuchProcess:pass
 dst=R/'production/research/game-lighting-history/local'/folder/'session.json'
 write(dst,{'sessionId':sid,'worker':w,'terminalCompletionObserved':True,'exitCode':0,'endedAt':s['endedAt'],'verifiedAt':now(),'execution':{'path':rel(ep),'sha256':sha(ep)},'originalWorkerAlive':False})
 sessions.append({'path':rel(dst),'sha256':sha(dst)})
write(P/'postprocess-encoded-math-rejection-v34.json',{'reviewedAt':now(),'scope':'All24 clean boards directly read across previous/current contexts. Captioned325-sample review still incomplete; no final approval.','cleanBoardsRead':list(range(1,25)),'captionedBoardsRead':[],'sessions':sessions,'rejectedScenes':['original-22p-1','original-22p-2'],'findings':['22p1 displayed progress*y as y=x/(1+x), so intermediate labels did not equal the displayed fixed-input function.','22p2 interpolated identity x to x/(1+x) while presenting the tone function as fixed: sample1.27 exceeds its range0..1. Left exposure output and right input were not explicitly distinguished.','22p3-6 and three native exposures/focus cuts show projected shapes and control/result labels; continuous/caption clearance remain separate.'],'repair':'Keep tone output fixed at the mathematically calculated value; reveal geometry by opacity. Label original shared inputs and exposure multiplier explicitly. Preserve original narration/timing and all nine other clean cuts.','allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'wholeEpisode60to40Approved':False,'uploaded':False})

assert not D.exists();(D/'renders').mkdir(parents=True);(D/'audio').mkdir()
model=(S/'postprocess-model-v3.tsx').read_text('utf-8')
model=model.replace("a.add(s.box(x,30,20,70,100,()=>220*(output?y*p():values[i]/16),output?P.teal:P.orange));","a.add(new Node({opacity:()=>output?p():1,children:[s.box(x,30,20,70,100,220*(output?y:values[i]/16),output?P.teal:P.orange)]}));")
model=model.replace("a.add(text(()=>output?('y = '+(y*p()).toFixed(3)):('x = '+values[i]),x,255,28));","a.add(text(output?('y = '+y.toFixed(3)):('x = '+values[i]),x,255,28));")
model=model.replace("b.add(bs.box(base,25,0,630,320,20,P.surfaceTop));b.add(text(kind,base,-235,34,P.yellow));","b.add(bs.box(base,25,0,630,320,20,P.surfaceTop));b.add(text(base<0?()=>('노출 × '+(1+p()).toFixed(2)):kind,base,-235,34,P.yellow));")
model=model.replace("b.add(bs.box(x,25,20,70,110,()=>30*((1-p())*input[i]+p()*out),base<0?P.orange:P.teal));","b.add(new Node({opacity:()=>base<0?1:Math.max(0,Math.min(1,(p()-.2)/.65)),children:[bs.box(x,25,20,70,110,()=>30*(base<0?input[i]*(1+p()):out),base<0?P.orange:P.teal)]}));")
model=model.replace("b.add(text(()=>((1-p())*input[i]+p()*out).toFixed(2),x,260,27));","b.add(text('입력 x='+input[i],x,210,22,P.muted));\n   b.add(text(()=>('y='+(base<0?input[i]*(1+p()):out).toFixed(2)),x,270,27));")
model=model.replace('왼쪽은 비례 · 오른쪽은 비선형 압축 · 비교할 때 노출·카메라·조명 조건을 통제','같은 원래 입력 x에 두 변환을 각각 적용 · 순차 적용 아님 · 비교 조건 통제')
assert 'y*p()).toFixed' not in model and '(1-p())*input' not in model
mp=S/'postprocess-model-v4.tsx';assert not mp.exists();mp.write_text(model,'utf-8')
runtime=(S/'narrated-runtime-v2.tsx').read_text('utf-8').replace("'./postprocess-model-v3'","'./postprocess-model-v4'")
rp=S/'narrated-postprocess-math-runtime-v6.tsx';assert not rp.exists();rp.write_text(runtime,'utf-8')
old=read(R/'production/research/game-lighting-history/local/episode04-clean-model-inputs-v5/plan.json')
scenes=[s for s in old['scenes'] if s['id'] in ['original-22p-1','original-22p-2']]
assert [s['frames'] for s in scenes]==[727,890]
pcm=[];mapping=[];at=0
with wave.open(str(R/old['currentAudio']['path']),'rb') as w:
 assert(w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
 for s in scenes:
  w.setpos(s['sourceSamples'][0]);buf=w.readframes(s['sourceSamples'][1]-s['sourceSamples'][0]);assert hashlib.sha256(buf).hexdigest()==s['originalPcmSha256'];pcm.extend([buf,bytes(s['silentPaddingSamples']*2)])
  wrapper=S/f"clean-postprocess-math-{s['id']}-v36.tsx";text=(R/s['wrapper']).read_text('utf-8').replace("'./narrated-runtime-v2'","'./narrated-postprocess-math-runtime-v6'");assert not wrapper.exists();wrapper.write_text(text,'utf-8')
  mapping.append({'id':s['id'],'fromFrame':at,'toFrame':at+s['frames'],'frames':s['frames'],'wrapper':rel(wrapper),'wrapperSha256':sha(wrapper),'originalPcmSha256':s['originalPcmSha256']});at+=s['frames']
audio=D/'audio/episode04-postprocess-math-repair-v36.wav'
with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b''.join(pcm))
assert sum(len(b) for b in pcm)//2==at*400
name='episode04-postprocess-math-repair-v36';pr=S/(name+'.ts')
pr.write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(f"import p{i} from './{Path(m['wrapper']).stem}?scene';" for i,m in enumerate(mapping))+"\nexport default makeProject({scenes:[p0,p1],audio:"+json.dumps('/@fs/'+audio.as_posix())+"});\n",'utf-8')
write(pr.with_suffix('.meta'),{'version':0,'shared':{'background':None,'range':[0,(at-1)/60],'size':{'x':1920,'y':1080},'audioOffset':0},'preview':{'fps':30,'resolutionScale':1},'rendering':{'fps':60,'resolutionScale':1,'colorSpace':'srgb','exporter':{'name':'@motion-canvas/ffmpeg','options':{'fastStart':True,'includeAudio':True}}}})
job={'name':name,'project':rel(pr),'frames':at,'scenes':mapping,'audio':{'path':rel(audio),'sha256':sha(audio),'samples':at*400},'output':rel(D/'renders'/f'{name}.mp4'),'execution':rel(D/'renders'/f'{name}.execution.json')}
write(D/'plan.json',{'preparedAt':now(),'runtime':{'path':rel(rp),'sha256':sha(rp)},'model':{'path':rel(mp),'sha256':sha(mp)},'jobs':[job],'scenes':scenes,'newTts':0,'allFinalPixelsReviewed':False,'uploaded':False})
config=(R/'motion-canvas/vite.game-lighting-history04.clean-inputs-v5.config.ts').read_text('utf-8').replace('episode04-clean-model-inputs-v5','episode04-postprocess-math-repair-v36').replace('game-lighting-history04-clean-inputs-v5','game-lighting-history04-postprocess-math-repair-v36').replace('port:9265','port:9268')
cfg=R/'motion-canvas/vite.game-lighting-history04.postprocess-math-repair-v36.config.ts';assert not cfg.exists();cfg.write_text(config,'utf-8')
ts=R/'motion-canvas/tsconfig.game-lighting-history04-postprocess-math-repair-v36.json'
write(ts,{'extends':'./tsconfig.json','include':['src/env.d.ts',rel(pr).replace('motion-canvas/',''),*[m['wrapper'].replace('motion-canvas/','') for m in mapping]]})
cp=R/'production/research/game-lighting-history/checkpoint.json';j=read(cp);j['episode04PostprocessMathRepairV36']={'plan':rel(D/'plan.json'),'preparedFrames':at,'newTts':0,'rendered':False,'finalApproved':False};j['ownedActiveWork']={'status':'no-active-owned-media-worker','next':'One CPU2 scoped two-scene math repair; then reuse9 old clean cuts and review changed samples.'};j['updatedAt']=now();tmp=cp.with_suffix('.math-v36.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
print(json.dumps({'preparedFrames':at,'scenes':2,'newTts':0,'newGitImages':0,'config':rel(cfg)}))

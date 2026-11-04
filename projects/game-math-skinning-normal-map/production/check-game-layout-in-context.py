"""Actual M22 game frames, source-timed clauses and production overlay geometry."""
from pathlib import Path
import hashlib,importlib.util,json,math,subprocess,sys,shutil
from PIL import Image,ImageDraw

P=Path(__file__).resolve().parents[1];R=P.parents[1];B=R/'production/batches/game-math-remaining-20261104'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def module(name,p):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
bindings=read(P/'planning/scene-bindings.json')
revision=3 if any(s.get('actualGamePart',{}).get('nativeDetailInset') for s in bindings['scenes'] if s.get('actualGamePart')) else 1
if revision==3 and bindings['scenes'][0]['actualGamePart']['nativeDetailInset']['displayAt'][1]>=300:revision=4
D=P/f'production/local/game-layout-in-context-v{revision}';D.mkdir(exist_ok=True)
sys.argv=['align','--project',P.name,'--audio-revision','audio-v2']
A=module('speech_basis',B/'align-module-speech.py')
sys.argv=['compose','--queue',str(P/'production/unity-staging/local-preflight-v5/queue.json')]
M=module('production_layout',B/'compose-module.py')
source={x['id']:x for x in read(P/'planning/footage-audit.json')['sources']}
proof=[];pics=[]
for s in bindings['scenes']:
 g=s.get('actualGamePart')
 if not g:continue
 sid=s['id'];seg=P/f'production/local/audio-v2/review/paragraphs/{sid}-01.json';rec=read(seg);e=rec['entry']
 raw=sid+'-01-scene.wav';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 assert sha(P/'production/local/audio-v2/chunks'/raw)==sha(P/'production/local/audio-v3/chunks'/raw)
 assert s['speech']==e['text'] and s['speech'].startswith(g['speechTarget']['prefixKo'])
 _,_,mapping,owners,_=A.map_chars(e['text'],rec['chunks']);cursor=0;cues=[]
 for clause in A.chunks(e['text']):
  at=e['text'].find(clause,cursor);cursor=at+len(clause)
  t,_=A.phrase_time(e['text'],clause,mapping,owners,at);cues.append(dict(id=len(cues)+1,start=max(0,t-e['start']),end=e['end']-e['start'],text=A.display_span(e['text'],e['display_text'],at,cursor)))
 for l,n in zip(cues,cues[1:]):l['end']=n['start']
 native=g['sourceIn'];length=g['sourceOut']-native
 if g['speechTarget'].get('endBeforeKo'):
  phrase=g['speechTarget']['endBeforeKo'];t,_=A.phrase_time(e['text'],phrase,mapping,owners,s['speech'].index(phrase));length=min(length,t-e['start'])
 assert native+length+1/60>=g.get('minimumObservedResultOut',g['sourceOut'])
 cut=dict(scene=sid,frames=round(length*60),sourceId=g['sourceId'],sourceIn=native,sourceOut=native+length)
 if g.get('nativeDetailInset'):cut['nativeDetailInset']=g['nativeDetailInset']
 src=source[g['sourceId']];track=M.annotation_ass(cut,src,D/(sid+'.game.ass'));layout=M.C.caption_ass(D/(sid+'.caption.ass'),cues,0,{})
 assert all(len(x['lines'])==1 for x in layout)
 for w in track['tracks']:
  d=read(R/w['trackFile']);start=max(native,d['start']);end=min(native+length,d['end'])
  sample_frames=[round((start-native+(end-start)*f)*60) for f in (.2,.5,.8)]
  names=[D/f'{sid}-{j}.png' for j in range(3)]
  if revision==4 and sid!='000' and not any(p.exists() for p in names):
   # The sole v4 visual change is the location of Mario's magnified inset.
   prior=P/'production/local/game-layout-in-context-v3'
   assert (prior/(sid+'.game.ass')).read_bytes()==(D/(sid+'.game.ass')).read_bytes() and (prior/(sid+'.caption.ass')).read_bytes()==(D/(sid+'.caption.ass')).read_bytes()
   for dest in names:shutil.copy2(prior/dest.name,dest)
  if not all(p.is_file() for p in names):
   assert not any(p.exists() for p in names),'Preserve partial samples'
   choose='+'.join(f'eq(n,{n})' for n in sample_frames);vf=M.game_filters(cut,sid+'.game.ass')+f",ass={sid}.caption.ass,select='{choose}'"
   # Start at the actual cut so both the main frame and the same-instant zoom
   # pass through their real frame-synchronization path before sampling.
   subprocess.run([str(M.FF),'-v','error','-nostdin','-n','-threads','1','-filter_threads','2','-ss',str(native),'-t',str((sample_frames[-1]+4)/60),'-i',str(R/src['file']),'-vf',vf,'-frames:v','3','-threads','1','-fps_mode','vfr','-start_number','0',str(D/(sid+'-%d.png'))],cwd=D,check=True,creationflags=M.CREATE)
  for j,f in enumerate([.2,.5,.8]):
   loc=sample_frames[j]/60;png=names[j];assert png.is_file()
   clause=next((c['text'] for c in cues if c['start']<=loc<c['end']),None);assert clause
   proof.append(dict(scene=sid,source=src['id'],nativeSeconds=native+loc,relativeAudioSeconds=loc,caption=clause,still=png.name,unchangedRawTake=sha(P/'production/local/audio-v3/chunks'/raw),annotation=w['id'],seen=False))
   pics.append((sid,loc,png))
sheet=Image.new('RGB',(3*375,3*239),'#101111');draw=ImageDraw.Draw(sheet)
for i,(sid,loc,png) in enumerate(pics):
 im=Image.open(png).convert('RGB');assert im.size==(1920,1080);im.thumbnail((375,211),Image.Resampling.LANCZOS);x=i%3*375;y=i//3*239;sheet.paste(im,(x,y));draw.text((x+7,y+214),f'{sid} +{loc:.2f}s',fill='white')
sheet.save(D/'mobile.jpg',quality=96)
(D/'samples.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(pics),'actual native frames with unchanged voice timing and final caption geometry;',D/'mobile.jpg')

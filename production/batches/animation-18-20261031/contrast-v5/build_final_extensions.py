"""Merge inspected gameplay, speech and explanation edits on one old clock.

Positive speech deltas preserve native pictures, then add explicitly labelled
still-pose analysis. They never slow or loop gameplay or stretch speech.
Planning/import is cheap; encoding requires the explicit --render-speech flag.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,subprocess

H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local/final-extensions'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,j):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def path(p):return R/Path(p)
def rel(p):return Path(p).absolute().relative_to(R).as_posix()
def hit(a,b,c,d):return max(a,c)<min(b,d)
def subtract(a,b,ranges):
 spans=[(a,b)]
 for c,d in sorted(ranges):
  spans=[q for x,y in spans for q in ([(x,y)]if not hit(x,y,c,d)else([(x,c)]if x<c else[])+([(d,y)]if d<y else[]))]
 return spans
def load_module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
assembly=load_module('contrast_assembly',H/'assemble_explanations.py')

def context(ep):
 control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert ep in control['episodes']and ep!='A03'and control['fullLocalProductionAuthorized']
 gameManifest=H/'game-plates-caption-safe.json'
 if not gameManifest.exists():gameManifest=H/'game-plates-manifest.json'
 p=next(e for e in read(gameManifest)['episodes']if e['id']==ep);assert p['ready'],'Gameplay plates not complete'
 correction=H/'visual-corrections'/(ep+'.json')
 if correction.exists():
  patch=read(correction);assert patch['episode']==ep and patch['readyForAssembly']
  p=copy.deepcopy(p)
  for q in patch['pictureEdits']:
   x,y=q['startFrame'],q['endFrame'];assert q['newFrames']==y-x and q['sourceVerified']
   assert sha(path(q['picture']))==q['pictureSha256']
   keep=[]
   for r in p['pictureEdits']:
    for j,(a,b)in enumerate(subtract(r['startFrame'],r['endFrame'],[(x,y)])):
     s=copy.deepcopy(r);s.update(id=r['id']+f'-visual-fragment{j}',startFrame=a,endFrame=b,newFrames=b-a,sourceStartFrame=r.get('sourceStartFrame',0)+a-r['startFrame']);keep.append(s)
   p['pictureEdits']=keep+[q]
  p['visualCorrectionSha256']=sha(correction)
 i=next(e for e in read(assembly.INTEGRATION)['episodes']if e['id']==ep)
 b=next(e for e in read(H/'baseline-review-manifest.json')['records']if e['id']==ep)
 a=next(e for e in read(H/'local/final-audio/audio-preparation.json')['episodes']if e['id']==ep)
 assert all(g['status']!='waiting-for-takes'for g in a['groups']),'Unfinished speech must not be silently omitted'
 assert a['sourceRevisionsSha256']==sha(H/'narration/source-verified-revisions.json')
 return p,i,b,a

def visual_timeline(p,i,b):
 overlays=[{'id':r['id'],'startFrame':r['relationFrameStart'],'endFrame':r['relationFrameEnd'],'newFrames':r['newFrames'],'picture':r['output'],'sourceStartFrame':0,'sourceVerified':True}for r in i['rows']if r['newFrames']==r['relationFrameEnd']-r['relationFrameStart']]
 baseline=next(x['path']for x in b['files']if x['kind']=='clean.mp4')
 rows=assembly.core.picture_edl(b['frames'],baseline,overlays,p['pictureEdits'])
 byid={r['id']:r for r in overlays+p['pictureEdits']}
 for r in rows:
  if r['id']!='baseline':
   owner=byid[r['id']];r['sourceStartFrame']+=owner.get('sourceStartFrame',0);r['sourceClassification']=owner.get('sourceClassification','explanation')
  else:r['sourceClassification']='preserved-picture'
 return rows

def composite(ep,g,rows,render=False):
 a,b=g['baselineStartFrame'],g['baselineEndFrame'];delta=g['deltaFrames'];assert delta>0
 folder=assembly.L/ep/'speech-pictures'/g['id'];out=folder/'picture.mp4'
 clips=[]
 for r in rows:
  x,y=max(a,r['oldStartFrame']),min(b,r['oldEndFrame'])
  if x<y:clips.append({'source':r['source'],'sourceStartFrame':r['sourceStartFrame']+x-r['oldStartFrame'],'frames':y-x,'id':r['id'],'oldRange':[x,y],'sourceClassification':r['sourceClassification']})
 assert sum(r['frames']for r in clips)==b-a
 # A caption edge can fall a handful of frames into the following picture.
 # Never freeze that incidental next shot for the whole new explanation.
 holdIndex=max((n for n,r in enumerate(clips)if r['frames']>=30),default=len(clips)-1)
 holdClip=clips[holdIndex];kept=clips[:holdIndex+1];nativeFrames=sum(r['frames']for r in kept);stillFrames=b-a+delta-nativeFrames
 sig={'clips':[dict(r,sha256=sha(path(r['source'])))for r in clips],'deltaFrames':delta,'fps':60,'method':'unscaled-meaningful-picture-then-labelled-still-analysis','heldClipIndex':holdIndex,'nativeFrames':nativeFrames,'stillFrames':stillFrames,'codeSha256':sha(__file__)}
 prior=read(folder/'signature.json')if(folder/'signature.json').exists()else{}
 if render and(not out.is_file()or sig!=prior):
  folder.mkdir(parents=True,exist_ok=True);(folder/'segments').mkdir(exist_ok=True);parts=[]
  for n,c in enumerate(kept):
   row={'source':c['source'],'sourceStartFrame':c['sourceStartFrame'],'frames':c['frames'],'sourceSha256':sig['clips'][n]['sha256']}
   parts.append(assembly.segment(row,folder/'segments'))
  concat=folder/'concat.txt';concat.write_text('\n'.join("file '"+str(x).replace('\\','/').replace("'","'\\''")+"'"for x in parts)+'\n','utf8')
  native=folder/'native.mp4';assembly.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',concat,'-map','0:v:0','-an','-c','copy',native])
  font='C\\:/Windows/Fonts/malgunbd.ttf';start=nativeFrames/60
  # Replace only the existing current-picture chip, not the separate source
  # line or the title. Game imagery starts at80px; own panels start lower.
  gameHeader=holdClip['sourceClassification']in('game','analysis')
  boxX,boxH,labelX,labelY=(1410,79,1510,24)if gameHeader else(1618,110,1630,57)
  vf=f"tpad=stop_mode=clone:stop_duration={stillFrames/60:.9f},drawbox=x={boxX}:y=0:w={1920-boxX}:h={boxH}:color=0x080d0a:t=fill:enable='gte(t,{start:.9f})',drawtext=fontfile='{font}':text='정지 분석':x={labelX}:y={labelY}:fontsize=32:fontcolor=0xf2d787:enable='gte(t,{start:.9f})'"
  log=folder/'render.log'
  with log.open('wb')as f:subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-threads','4','-filter_threads','1','-i',str(native),'-an','-vf',vf,'-frames:v',str(b-a+delta),*assembly.ENC,str(out)],stdout=f,stderr=f,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  save(folder/'signature.json',sig)
 if not out.is_file():return None,{'id':g['id'],'stage':'picture-render-pending','deltaFrames':delta,'clips':clips}
 assert read(folder/'signature.json')==sig,'Changed source must be rerendered'
 v=next(s for s in assembly.probe(out)if s['codec_type']=='video');assert int(v['nb_frames'])==b-a+delta
 return {'id':g['id']+'-picture','kind':'authored-explanation','startFrame':a,'endFrame':b,'newFrames':b-a+delta,'picture':rel(out),'pictureSha256':sha(out),'sourceStartFrame':0,'sourceVerified':True,'mediaComposition':{'originalUnscaledFrames':nativeFrames,'labelledStillAnalysisFrames':stillFrames,'incidentalTailFramesReplaced':b-a-nativeFrames,'heldClipIndex':holdIndex,'clips':clips}},None

def build(ep,render=False):
 p,i,b,audio=context(ep);groups=audio['groups'];positive=[g for g in groups if g.get('deltaFrames',0)>0];ranges=[(g['baselineStartFrame'],g['baselineEndFrame'])for g in positive]
 rows=visual_timeline(p,i,b);pictures=[];pending=[]
 for q in p['pictureEdits']:
  for n,(x,y)in enumerate(subtract(q['startFrame'],q['endFrame'],ranges)):
   r=copy.deepcopy(q);r.update(id=q['id']+f'-fragment{n}',startFrame=x,endFrame=y,newFrames=y-x,sourceStartFrame=q.get('sourceStartFrame',0)+x-q['startFrame']);pictures.append(r)
 for g in positive:
  q,wait=composite(ep,g,rows,render)
  if wait:pending.append(wait)
  else:pictures.append(q)
 timing=next(x for x in read(H/'baseline-sentence-timing.json')['records']if x['id']==ep)
 for q in pictures:
  hits=[r['id']for r in i['rows']if hit(q['startFrame'],q['endFrame'],r['relationFrameStart'],r['relationFrameEnd'])]
  q['expectedUnderlyingExplanationIds']=hits
  if hits:
   ids=[s['id']for s in timing['sentences']if hit(q['startFrame'],q['endFrame'],s['startSeconds']*60,s['endSeconds']*60)]
   assert ids; q['narrationEvidence']={'path':rel(H/'narration/source-verified-revisions.json'),'sha256':sha(H/'narration/source-verified-revisions.json'),'sentenceIds':ids}
 sounds=[];unverified=[]
 for g in groups:
  if not g.get('technicalMixVerified',False):unverified.append(g['id'])
  q={k:g[k]for k in ['startSample','endSample','newSamples','source','sourceSha256','sourceStartSample','audioKind']}
  q.update(id=g['id']+'-audio',sourceVerified=g.get('technicalMixVerified',False),verification=g.get('technicalMixVerification'),inputChecks=g.get('inputChecks',[]))
  if g.get('deltaFrames',0)>0:q['pictureEditId']=g['id']+'-picture'
  sounds.append(q)
 if ep=='A01':
  stem=read(H/'local/final-audio/A01/stems/stem-remap.json');assert sha(path(stem['source']))==stem['sourceSha256']
  for r in stem['ranges']:
   for n,(x,y)in enumerate(subtract(r['startSample'],r['endSample'],[(g['startSample'],g['endSample'])for g in groups])):
    sounds.append({'id':r['id']+f'-clean{n}','audioKind':'complete-mix','startSample':x,'endSample':y,'newSamples':y-x,'source':stem['source'],'sourceSha256':stem['sourceSha256'],'sourceStartSample':x,'sourceVerified':True,'verification':'Exact processed voice+sidechained original music stem ancestry; original incompatible game stem removed only in authorized replaced-source ranges. Human listening pending.'})
 visual=H/'visual-corrections'/(ep+'.json')
 visualProof={'path':rel(visual),'sha256':sha(visual)}if visual.exists()else None
 out={'schemaVersion':1,'clock':'relations-v4','baselineReviewSHA256':sha(H.parent/'relations-v4/review-manifest.json'),'episodes':[{'id':ep,'pictureEdits':sorted(pictures,key=lambda q:q['startFrame']),'audioEdits':sorted(sounds,key=lambda q:q['startSample']),'visualCorrection':visualProof}],'sourceMetadata':'footage/final-audio-adoption.json','pendingPicture':pending,'pendingTechnicalMix':unverified,'humanReviewed':False,'readyForAssembly':not pending and not unverified}
 save(L/ep/'extensions.json',out);print(json.dumps({'episode':ep,'pictureEdits':len(pictures),'pendingPicture':len(pending),'pendingTechnicalMix':len(unverified),'readyForAssembly':out['readyForAssembly']}))
 return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--episode',required=True);ap.add_argument('--render-speech',action='store_true');v=ap.parse_args();build(v.episode,v.render_speech)

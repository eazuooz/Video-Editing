"""Preserve the rejected/preventive v1 sources before a project-local caption-safe revision.
No media, captions, narration, shared geometry, uploads or Git are rewritten.
"""
from pathlib import Path
import json,hashlib,datetime,re
ROOT=Path(__file__).resolve().parents[3]
changes={
 'motion-sickness-games':('[0,170],.9','[0,70],.76',[365,370,375],[305]),
 'hierarchical-game-outlines':('[0,145],.86','[0,75],.70',[360,365,375,380],[305,320]),
 'game-reward-planning':('[0,150],.86','[0,65],.74',[360,365,375,390],[305,315,325,335]),
 'avoid-game-comparisons':('[0,150],.86','[0,90],.76',[360,365,370],[]),
 'making-game-sequels':('[0,155],.86','[0,65],.76',[365,375],[305,310]),
 'familiar-game-rules':('[0,155],.86','[0,65],.76',[365,370],[305]),
}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
for slug,(old,new,footers,upper) in changes.items():
 folder=ROOT/'projects'/slug/'production/visual-depth-v1'
 source=ROOT/'motion-canvas/src/projects'/slug/'depth-explanations-v1.tsx'
 record=folder/'caption-safe-repair-request.json'
 if record.exists():raise RuntimeError('Inspect existing correction, do not repeat '+slug)
 original=source.read_text('utf-8-sig')
 if original.count(old)!=1:raise RuntimeError('Exact project-local projection expected '+slug)
 preserved=folder/'depth-explanations-pre-caption-safe.tsx'
 if preserved.exists():raise RuntimeError('Preserve earlier source '+slug)
 preserved.write_bytes(source.read_bytes())
 revised=original.replace(old,new)
 counts={}
 for y in upper+footers:
  target=265 if y in upper else 315
  pattern=rf',{y},(P\.|[\'\"])'
  revised,n=re.subn(pattern,rf',{target},\1',revised)
  counts[str(y)]=dict(newY=target,occurrences=n)
  if not n:raise RuntimeError('Expected fixed text position absent '+slug+' '+str(y))
 # Spatial placement only: quoted narration/diagram text and timeline stays byte-identical.
 literals=lambda s:re.findall(r"'[^'\n]*'|\"[^\"\n]*\"",s)
 if literals(original)!=literals(revised):raise RuntimeError('Diagram wording changed')
 source.write_text(revised,'utf-8')
 retained=[]
 for name in ['white-preflight-direct-review.json','white-direct-review.json','assembly-inputs.json','white-technical-qa.json','pair-technical-qa.json','pair-execution.json','encoded-pixel-direct-progress.json']:
  p=folder/name
  if p.exists():retained.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
 write(record,dict(slug=slug,preparedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='Observed caption collision in exact motion encoded pair; source-level risk in remaining five warrants direct captioned preflight before rendering.',observedEncodedRejection=slug=='motion-sickness-games',originalSource=preserved.relative_to(ROOT).as_posix(),originalSourceSha256=sha(preserved),source=source.relative_to(ROOT).as_posix(),sourceSha256=sha(source),projection=dict(old=old,new=new),fixedTextChanges=counts,diagramWordingPreserved=True,sharedGeometryChanged=False,narrationChanged=False,captionsMoved=False,timingChanged=False,retainedV1Records=retained,revision='v2',preflightPixelsApproved=False,allFinalPixelsReviewed=False))
 qpath=ROOT/'production/batches/visual-depth-revision/queue.json';q=json.loads(qpath.read_text('utf-8-sig'));item=next(i for i in q['items'] if i['slug']==slug);item.update(stage='caption-safe-v2-preparation',allPixelsReviewed=False,captionSafeRepair=record.relative_to(ROOT).as_posix(),pid=None,activePid=None);q['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(qpath,q)
 print(slug+' source preserved; caption-safe geometry prepared; approval remains false')

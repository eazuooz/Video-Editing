"""Record inspected temporal targets; final subtitle/layout/motion QA stays open."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parents[1];src=P/'production/local/annotation-tracking-v1';dst=P/'production/local/annotation-reviewed-v1';dst.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
notes={
'raised-roof':'Eight temporal samples: new roof stays inside tracked extent during camera rotation; no mesh or GPU internals inferred.',
'near-cube':'Ten temporal samples: foreground cube covers changing distant platform; contour follows the cube and does not assign numeric game depth.',
'glass-frame':'Six temporal samples: opaque support and adjacent transparent pane are distinguishable; hide guide when tracked extent exceeds visibility bounds.',
'submerged-body':'Four temporal samples: body crosses the visible water surface; hide at jump/out-of-frame. Label covers both states, not a claim the emerged body remains underwater.'}
windows=[]
for name,note in notes.items():
 d=read(src/(name+'.json'))
 if name=='submerged-body':d['label']='물속과 물 밖의 몸'
 d['visualQa']=dict(status='temporal-samples-reviewed-final-encoded-pending',at=datetime.now(timezone.utc).isoformat(),evidence=str((src/(name+'-1.jpg')).relative_to(R)),note=note,humanFinalReview=False,movingFinalComposite=False)
 path=dst/(name+'.json');assert not path.exists(),'Keep previous reviewed evidence'
 path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 windows.append({**{k:v for k,v in d.items() if k!='keyframes'},'trackFile':str(path.relative_to(R)),'trackSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'compositeShape':'hollow ellipse following the reviewed extent'})
(P/'planning/game-annotation-tracks.json').write_text(json.dumps(dict(status='sampled-source-tracks-reviewed-final-composite-pending',windows=windows,finalCompositeViewed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

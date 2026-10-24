"""Reuse only existing measured source-frame targets in the same source interval."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent
for ep in sys.argv[1:]:
 path=V/(ep+'-plan.json');d=json.loads(path.read_text('utf8'))
 c=json.loads((R/'projects'/d['slug']/'production/concept-fit-v2/composition.json').read_text('utf-8-sig'))
 for p in d['patches']:
  src=d['sources'][p['source']]['path'];st=p['segments'][0]['in'];dur=p['duration'];tracks=[]
  for s in c['scenes']:
   games=s.get('game') or []
   if isinstance(games,dict):games=[games]
   for g in games:
    if c['sources'][g['source']]['path']!=src:continue
    for name in ['track','track2']:
     pts=[[round(t+g['start']-st,4),x,y,r] for t,x,y,r in g.get(name,[]) if 0<=t+g['start']-st<=dur]
     if len(pts)>=2:tracks.append({'points':pts,'provenance':f'concept-fit-v2/composition.json#{s["id"]}.{name}'})
  if tracks:p['tracks']=tracks
 d['sourceReview']['annotationDecision']='Reuse source-frame targets only where source identity and time overlap; clear before later motion. New targets require visual checking.'
 path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(ep,'tracked intervals',sum(len(p.get('tracks',[])) for p in d['patches']))

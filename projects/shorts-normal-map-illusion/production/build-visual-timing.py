"""Build visual cues from the actual final voice alignment; no guessed runtime."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1];L=P/'production/local'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 control=read(P.parents[1]/'shared/publishing/video-production-control.json');assert control.get('shortsDirectSelection',{}).get('selectedRevision')=='normal-map-v1','V1 builder is historical; use build-visual-timing-v2.py for selected revision'
 c=read(P/'script/captions.json');q={x['id']:x for x in c['cues']}
 # id, first cue, native mode, normal strength, light from/to, camera yaw from/to, shader output.
 specs=[
 ('hero','c01','wall',1,25,40,0,0,0),
 ('flat-reveal','c02','wall-edge',1,40,40,0,82,0),
 ('shared-normal','c03','wall-flatnormals',0,40,40,35,35,0),
 ('normal-definition','c05','wall-flatnormals',0,40,40,35,35,0),
 ('pixel-normal','c07','wall-normals',1,40,40,35,35,0),
 ('normal-data','c09','wall',1,40,40,0,0,1),
 ('neutral-purple','c11','wall',1,40,40,0,0,1),
 ('light-facing','c13','wall-normals',1,-40,-40,35,35,0),
 ('light-sideways','c14','wall-normals',1,-40,40,35,35,0),
 ('moving-light','c15','wall',1,40,-40,0,0,0),
 ('knight-source','c17','knight-source',1,40,40,0,0,0),
 ('knight-bake','c18','knight-pipeline',1,40,40,0,0,0),
 ('knight-light','c19','knight-lit',1,-55,55,0,0,0),
 ('wall-detail','c20','wall',1,-35,35,0,0,0),
 ('same-mesh','c23','wall-ab',1,40,40,0,0,0),
 ('silhouette','c25','wall-edge',1,40,40,65,88,0),
 ('closing','c26','wall-ab',1,40,40,0,0,0)]
 sections=[]
 for i,s in enumerate(specs):
  name,cue,kind,strength,lf,lt,af,at,mode=s
  start=0 if i==0 else q[cue]['start'];end=q[specs[i+1][1]]['start'] if i+1<len(specs) else c['durationSeconds']
  sections.append(dict(id=name,cue=cue,kind=kind,start=start,end=end,normalStrength=strength,lightFrom=lf,lightTo=lt,angleFrom=af,angleTo=at,mode=mode))
 reactions=[
  dict(start=q['c02']['start']+.1,end=min(q['c03']['start'],q['c02']['start']+1.6),kind='realize'),
  dict(start=q['c10']['start']+.1,end=min(q['c11']['start'],q['c10']['start']+1.4),kind='puzzled'),
  dict(start=max(q['c27']['start'],c['durationSeconds']-1.5),end=c['durationSeconds']-.15,kind='understood')]
 out=dict(schemaVersion=1,project=P.name,revision='normal-map-v1',fps=60,frames=c['frames'],durationSeconds=c['durationSeconds'],voiceDurationSeconds=c['voiceDurationSeconds'],voiceOffsetSeconds=c['voiceOffsetSeconds'],sources={},sections=sections,reactions=reactions,captionsSha256=hashlib.sha256((P/'script/captions.json').read_bytes()).hexdigest(),classification='All executable Unity explanation, native game audio absent; measured share100% explanation. No fixed gameplay quota for this technical Short.',voiceSpeed=1)
 save(P/'production/visual-timing.json',out)
 save(L/'visual-timing.json',out)
 print(json.dumps(dict(frames=out['frames'],durationSeconds=out['durationSeconds'],sections=len(sections))))
if __name__=='__main__':main()

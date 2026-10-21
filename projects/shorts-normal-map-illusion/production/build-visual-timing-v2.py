"""V2 visual cues from the one final aligned40-clause voice, never guessed time."""
from pathlib import Path
import argparse,json,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local'
REVISION='normal-map-v2-grid-rgb-deadcells'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--captions',type=Path,default=L/'audio-v2/captions.json');a=ap.parse_args()
 control=read(R/'shared/publishing/video-production-control.json');assert control.get('selectedShortVideo')==P.name and control.get('shortsDirectSelection',{}).get('selectedRevision')==REVISION
 c=read(a.captions);q={x['id']:x for x in c['cues']};assert len(q)==40 and 'c40'in q,'Actual aligned v2 voice/captions required'
 def cueframe(id):return int(q[id].get('startFrame',round(q[id]['start']*60)))
 def event(id):return dict(cue=id,start=cueframe(id)/60,startFrame=cueframe(id))
 specs=[
 ('hero','c01','wall',1,25,40,0,0,0),
 ('flat-reveal','c02','wall-edge',1,40,40,0,82,0),
 ('shared-normal','c03','wall-flatnormals',0,40,40,35,35,0),
 ('normal-definition','c05','wall-flatnormals',0,40,40,35,35,0),
 ('grid-flat','c07','wall-flatnormals',0,40,40,35,35,0),
 ('pixel-normal','c08','wall-normals',1,40,40,35,35,0),
 ('normal-data','c10','wall',1,40,40,0,0,1),
 ('rgb-signed','c12','wall',1,40,40,0,0,1),
 ('rgb-encoding','c15','wall',1,40,40,0,0,1),
 ('neutral-purple','c18','wall',1,40,40,0,0,1),
 ('light-facing','c24','wall-normals',1,-40,-40,35,35,0),
 ('light-sideways','c25','wall-normals',1,-40,40,35,35,0),
 ('moving-light','c26','wall',1,40,-40,0,0,0),
 ('dead-cells','c28','game',0,40,40,0,0,0),
 ('knight-source','c31','knight-source',1,40,40,0,0,0),
 ('knight-light','c32','knight-lit',1,-55,55,0,0,0),
 ('wall-detail','c33','wall',1,-35,35,0,0,0),
 ('same-mesh','c36','wall-ab',1,40,40,0,0,0),
 ('silhouette','c38','wall-edge',1,40,40,65,88,0),
 ('closing','c39','wall-ab',1,40,40,0,0,0)]
 sections=[]
 for i,s in enumerate(specs):
  id,cue,kind,strength,lf,lt,af,at,mode=s;start=0 if i==0 else cueframe(cue);end=cueframe(specs[i+1][1])if i+1<len(specs)else c['frames']
  sections.append(dict(id=id,cue=cue,kind=kind,startFrame=start,endFrame=end,start=start/60,end=end/60,normalStrength=strength,lightFrom=lf,lightTo=lt,angleFrom=af,angleTo=at,mode=mode))
 byid={s['id']:s for s in sections};byid['pixel-normal'].update(animateNormals=True,normalFrom=0,normalTo=1)
 for name,ids in [('rgb-signed',['c12','c13','c14']),('rgb-encoding',['c15','c16','c17']),('neutral-purple',['c18','c19','c20','c21','c22','c23'])]:byid[name]['events']=[event(id)for id in ids]
 evidence=read(P/'sources/deadcells-v2.json');game=byid['dead-cells'];gameEnd=min(game['endFrame'],game['startFrame']+396);game.update(endFrame=gameEnd,end=gameEnd/60,source='deadCells',sourceStart=30.0,sourceEnd=30+(gameEnd-game['startFrame'])/60,rate=1,nativeAudioAdopted=False)
 if gameEnd<cueframe('c31'):
  bridge=dict(byid['knight-source']);bridge.update(id='knight-bake-bridge',kind='knight-pipeline',startFrame=gameEnd,start=gameEnd/60,endFrame=cueframe('c31'),end=cueframe('c31')/60);sections.append(bridge)
  byid['knight-source']['kind']='knight-pipeline'
 split=(cueframe('c31')+cueframe('c32'))//2;assert split>cueframe('c31')
 bake=dict(byid['knight-source']);bake.update(id='knight-bake',kind='knight-pipeline',startFrame=split,start=split/60)
 byid['knight-source'].update(endFrame=split,end=split/60);sections.append(bake);sections.sort(key=lambda s:s['startFrame'])
 assert all(a['endFrame']==b['startFrame']for a,b in zip(sections,sections[1:]));assert sections[-1]['endFrame']==c['frames']
 reactions=[dict(start=q['c02']['start']+.1,end=min(q['c03']['start'],q['c02']['start']+1.5),kind='realize'),dict(start=q['c26']['start']+.1,end=min(q['c28']['start'],q['c26']['start']+1.4),kind='realize'),dict(start=max(q['c40']['start'],c['durationSeconds']-1.5),end=c['durationSeconds']-.15,kind='understood')]
 sources={'deadCells':dict(path=evidence['source']['file'],originalOffsetSeconds=0,nativeAudioAdopted=False,sourceAudioAdopted=False,sourceSHA256=evidence['source']['sha256'])}
 out=dict(schemaVersion=2,project=P.name,revision=REVISION,fps=60,frames=c['frames'],durationSeconds=c['frames']/60,voiceDurationSeconds=c['voiceDurationSeconds'],voiceOffsetSeconds=c['voiceOffsetSeconds'],sources=sources,sections=sections,reactions=reactions,captionsPath=str(a.captions.resolve().relative_to(P.resolve())).replace('\\','/'),captionsSha256=hashlib.sha256(a.captions.read_bytes()).hexdigest(),classification='Measured actual independent gameplay plus executable Unity explanation. No fixed gameplay quota for this technical Short. Source soundtrack excluded by documented rights decision.',voiceSpeed=1)
 save(P/'production/visual-timing.json',out);save(L/'visual-timing.json',out)
 meta=R/'motion-canvas/src/projects/shorts-normal-map-illusion/project.meta';settings=read(meta);settings['shared']['range']=[0,out['durationSeconds']];settings['shared']['size']=dict(x=1080,y=1920);settings['preview']['fps']=60;save(meta,settings)
 print(json.dumps(dict(frames=out['frames'],durationSeconds=out['durationSeconds'],sections=len(sections),nativeGameFrames=gameEnd-game['startFrame'],nativeGameSeconds=(gameEnd-game['startFrame'])/60)))
if __name__=='__main__':main()

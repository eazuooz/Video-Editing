"""Lock one integer-frame edit from reviewed assets and measured guide speech."""
import pathlib,json,hashlib,datetime,math,collections
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-01';O=P/'production/local/final-edit-v1'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 import soundfile as sf
 assert not (O/'plan.json').exists(),'Do not replace a locked edit.'
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 review=rd(P/'production/native-guides-direct-review-v1.json')
 assert review['all36WholeTextsDirectlyCompared'] and review['contentCoverageApproved']
 recipe=rd(O/'recipe.json');assets=rd(P/'production/local/explanation-assets-v1/plan.json')
 design=rd(P/review['designPath'])
 guides={g['packetIndex']:g for g in design['rows']}
 # Resolve the measured0.1s overrun in g07 by transferring a unique preceding
 # Quake range from a slot with spare nonspoken action. Total is unchanged.
 recipe['packets'][4]['intervals'][-1]['endFrame']-=24
 recipe['packets'][7]['intervals'][0]['startFrame']-=24
 # g17's measured8.96s needs0.61s beyond its former speech slot.
 # Transfer0.8s of the immediately preceding mask view from g18's spare action.
 recipe['packets'][18]['intervals'][-1]['endFrame']-=48
 recipe['packets'][17]['intervals'].insert(0,dict(startFrame=2153*60+12,endFrame=2154*60))
 # Preserve all59s, but place the actual Shadow Frustums menu with p8;
 # the count4/0/1/3 operation belongs to p9, before its distance/distribution tail.
 recipe['packets'][36]['intervals']=[dict(startFrame=2174*60,endFrame=2196*60)]
 recipe['packets'][37]['intervals']=[dict(startFrame=2100*60,endFrame=2112*60),dict(startFrame=2121*60,endFrame=2131*60),dict(startFrame=2196*60,endFrame=2211*60)]
 native_by_anchor=collections.defaultdict(list)
 for i,p in enumerate(recipe['packets']):
  p['index']=i;p['frames']=sum(x['endFrame']-x['startFrame'] for x in p['intervals'])
  native_by_anchor[(p['anchor'],p['where'])].append(p)
 source_ranges=collections.defaultdict(list)
 for p in recipe['packets']:
  for z in p['intervals']:source_ranges[p['sourceId']].append((z['startFrame'],z['endFrame']))
 for sid,z in source_ranges.items():
  z.sort();assert all(a[1]<=b[0] for a,b in zip(z,z[1:])),('source-overlap',sid)
 for i,g in guides.items():
  f=R/review['audioPaths'][g['id']];info=sf.info(f)
  assert info.samplerate==24000 and sh(f)==review['audioHashes'][g['id']]
  g.update(audio=f.relative_to(R).as_posix(),samples=info.frames,audioFrames=math.ceil(info.frames/400),sha256=sh(f))
 nodes=[];voice=[];chapters=[];paragraphs=[];cursor=120
 def push(role,path,start,frames,**meta):
  nonlocal cursor
  node=dict(id=f's{len(nodes):03}',role=role,path=path,sourceStartFrame=start,frames=frames,startFrame=cursor,endFrame=cursor+frames,**meta)
  nodes.append(node);cursor+=frames;return node
 nodes.append(dict(id='branding',role='branding',path='projects/game-reward-planning/production/final-v1/white-segments/branding.mp4',sourceStartFrame=0,frames=120,startFrame=0,endFrame=120,sha256='706a0738dcd160b80ace24e54e16c09604c0173aba095fcd221a227c541fffb2'))
 pcm=rd(P/'project.json')['paths']['narration'];originalSamples=sf.info(R/pcm).frames
 def native(packet,key,originalPart=None):
  first=cursor;source=recipe['sourceRegistry'][packet['sourceId']];g=guides.get(packet['index'])
  for shot in packet['intervals']:
   push('actual',source['localFile'],shot['startFrame'],shot['endFrame']-shot['startFrame'],sourceId=source['id'],sourceSha256=source['sha256'],packetIndex=packet['index'],anchor=key,focusKo=packet['focusKo'],focusEn=packet['focusEn'])
  used=0
  if originalPart:
   a,z,b=originalPart
   pre=packet['frames']-(z-a) if key=='09b-p3' else 0
   target=first+pre;sourceframe=b['pcmStartFrame']+a
   count=min((z-a)*400,originalSamples-sourceframe*400)
   voice.append(dict(kind='original',key=key,path=pcm,sourceStartSample=sourceframe*400,samples=count,targetStartSample=target*400,startFrame=target,frames=z-a))
   used=z-a
  if g:
   target=first+8 if not originalPart or key=='09b-p3' else first+used+8
   limit=first+packet['frames']-(used if key=='09b-p3' else 0)
   assert target+g['audioFrames']<=limit,('guide-overflow',g['id'],(target+g['audioFrames']-limit)/60)
   voice.append(dict(kind='guide',key=g['id'],path=g['audio'],sourceStartSample=0,samples=g['samples'],targetStartSample=target*400,startFrame=target,frames=g['audioFrames'],audioSha256=g['sha256'],packetIndex=packet['index']))
  return first
 for ch in assets['chapters']:
  chapters.append(dict(id=ch['id'],title=ch['title'],startFrame=cursor))
  for b in ch['blocks']:
   key=b['paragraphKey'];placements=[]
   for a,z,role in recipe['sourceRoleParts'][key]:
    if role=='actual':
     packets=native_by_anchor[(key,'at')];assert len(packets)==1
     native(packets[0],key,(a,z,b));v=voice[-2] if voice[-1]['kind']=='guide' else voice[-1]
     placements.append(dict(sourceStartFrame=b['pcmStartFrame']+a,sourceEndFrame=b['pcmStartFrame']+z,targetStartFrame=v['startFrame']))
    else:
     first=cursor
     if key=='09b-p3':
      src=recipe['sourceRegistry']['epic-material-baking-2017']
      push('explanation',src['localFile'],1910*60,z-a,sourceId=src['id'],sourceSha256=src['sha256'],anchor=key,actualExportGraph=True,focusKo='표면 데이터 내보내기 · 조명 베이킹과 구별',focusEn='Exporting surface data is distinct from baking lighting.')
     else:
      push('explanation',ch['output'],b['pcmStartFrame']-ch['pcmStartFrame']+a,z-a,anchor=key,retainedExplanationAsset=True)
     sf0=(b['pcmStartFrame']+a)*400;count=min((z-a)*400,originalSamples-sf0)
     voice.append(dict(kind='original',key=key,path=pcm,sourceStartSample=sf0,samples=count,targetStartSample=first*400,startFrame=first,frames=z-a))
     placements.append(dict(sourceStartFrame=b['pcmStartFrame']+a,sourceEndFrame=b['pcmStartFrame']+z,targetStartFrame=first))
   for p in native_by_anchor[(key,'after')]:native(p,key)
   offsets={q['targetStartFrame']-q['sourceStartFrame'] for q in placements}
   assert len(offsets)==1,('uninterrupted-paragraph',key,placements)
   paragraphs.append(dict(key=key,sourceStartFrame=b['pcmStartFrame'],sourceEndFrame=b['pcmEndFrame'],timelineOffsetFrames=offsets.pop(),placements=placements))
 bodyEnd=cursor
 push('membership','projects/game-reward-planning/production/final-v1/white-segments/membership.mp4',0,600,sha256='181e5c5dd37672349542aa590629fe2f2d00a83f4cd3c811a29a21c029612123')
 # Coalesce adjacent retained ranges from the same already-rendered asset.
 # Paragraph/voice mappings remain independent and exact; no repeated rendering.
 merged=[]
 for n in nodes:
  if merged and n.get('retainedExplanationAsset') and merged[-1].get('retainedExplanationAsset') and merged[-1]['path']==n['path'] and merged[-1]['sourceStartFrame']+merged[-1]['frames']==n['sourceStartFrame'] and merged[-1]['endFrame']==n['startFrame']:
   prev=merged[-1];prev['frames']+=n['frames'];prev['endFrame']=n['endFrame'];prev.setdefault('anchors',[prev['anchor']]).append(n['anchor'])
  else:merged.append(n)
 nodes=merged
 for i,n in enumerate(nodes):
  if n['role'] not in ['branding','membership']:n['id']=f's{i:03}'
 actual=sum(n['frames'] for n in nodes if n['role']=='actual');ex=sum(n['frames'] for n in nodes if n['role']=='explanation')
 assert abs(actual-(actual+ex)*.6)<=1 and actual+ex==bodyEnd-120
 originals=sorted((v for v in voice if v['kind']=='original'),key=lambda v:v['sourceStartSample'])
 assert originals[0]['sourceStartSample']==0
 assert all(a['sourceStartSample']+a['samples']==b['sourceStartSample'] for a,b in zip(originals,originals[1:]))
 assert sum(v['samples'] for v in originals)==originalSamples
 ranges=sorted(voice,key=lambda v:v['targetStartSample']);assert all(a['targetStartSample']+a['samples']<=b['targetStartSample'] for a,b in zip(ranges,ranges[1:]))
 result=dict(schemaVersion=1,createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='measured-edit-awaiting-framing-and-current-pixels',fps=60,timeBase=90000,frames=cursor,seconds=cursor/60,actualFrames=actual,explanationFrames=ex,bodyFrames=actual+ex,bodyRatioApproved=True,nodes=nodes,voice=voice,chapters=chapters,paragraphs=paragraphs,original108SamplesPreserved=originalSamples,guideCount=len(guides),inputHashes={str(f.relative_to(R)).replace('\\','/'):sh(f) for f in [O/'recipe.json',P/review['designPath'],P/'production/native-guides-direct-review-v1.json',P/'production/local/explanation-assets-v1/plan.json']},finalTimingApproved=True,allFinalPixelsApproved=False,finalMixAsrApproved=False,finalPairComplete=False)
 wr(O/'plan.json',result);print(json.dumps({k:result[k] for k in ['frames','seconds','actualFrames','explanationFrames','original108SamplesPreserved','guideCount']}))
if __name__=='__main__':main()

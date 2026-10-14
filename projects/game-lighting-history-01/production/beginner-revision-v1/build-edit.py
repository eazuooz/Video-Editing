"""One revised timeline: retain native/voice assets, replace only selected speech/scenes."""
import pathlib,json,math,hashlib,datetime,copy,collections
import soundfile as sf
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/beginner-revision-v1'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 base=rd(P/'production/local/threejs-revision-v1/pair-caption-decoder-v3/plan.json');changes={r['key']:r for r in rd(H/'changes.json')['rows']};scenes={r['key']:r for r in rd(H/'measured-scene-plan.json')['scenes']}
 additions=rd(H/'native-additions.json');by_packet={r['packetIndex']:r for r in additions['rows'] if r['packetIndex'] is not None};new_guides={r['id']:r for r in additions['guideRows']}
 allvoice=collections.defaultdict(list)
 for v in base['voice']:allvoice[v['key']].append(v)
 def voice(key,start,sourceOffset=0,samples=None):
  if key in new_guides:path=f'shared/output/narration/game-lighting-history-01/beginner-native-additions/chunks/{key}-scene.wav';offset=0;count=sf.info(R/path).frames;kind='added-guide'
  elif key in changes:
   r=changes[key];path=r.get('replacementAudioPath') or f"shared/output/narration/game-lighting-history-01/beginner-revision-v1/chunks/{r['ttsSceneId']}-scene.wav";offset=0;count=sf.info(R/path).frames;kind='replacement'
  else:
   vs=allvoice[key];path=vs[0]['path'];offset=min(v['sourceStartSample'] for v in vs);count=sum(v['samples'] for v in vs);kind=vs[0]['kind']
  count=count-sourceOffset if samples is None else samples
  assert count>0 and offset+sourceOffset+count<=sf.info(R/path).frames,key
  return dict(key=key,kind=kind,path=path,sourceStartSample=offset+sourceOffset,utteranceStartSample=sourceOffset,samples=count,startFrame=start,targetStartSample=start*400,frames=math.ceil(count/400),audioSha256=sha(R/path))
 nodes=[];voices=[];cursor=0;old_starts={};groups=[]
 def push(n):
  nonlocal cursor
  n=copy.deepcopy(n);n['startFrame']=cursor;n['endFrame']=cursor+n['frames'];nodes.append(n);cursor=n['endFrame'];return n
 def extra(a):
  for j,r in enumerate(a['intervals']):
   push(dict(id=f"{a['id']}-{j}",role='actual',path=a['path'],sourceStartFrame=r['startFrame'],frames=r['endFrame']-r['startFrame'],sourceId=a['sourceId'],sourceSha256=a['sourceSha256'],packetIndex=a['packetIndex'],anchor=a['anchor'],focusKo=a['focusKo'],newNative=True,additionId=a['id']))
 def native_asset(n):
  # Already caption-free framed clips, previously checked at native rate.
  for suffix in ['repair-v2','segments']:
   f=P/f"production/local/final-edit-v1/{suffix}/{n['id']}.mp4"
   if f.exists():return f.relative_to(R).as_posix()
  raise RuntimeError(('missing-retained-native',n['id']))
 def old_native(n):
  return {**n,'baselineNodeId':n['id'],'retainedAssetPath':native_asset(n),'retainedAssetStartFrame':0}
 i=0
 while i<len(base['nodes']):
  n=base['nodes'][i];old_starts.setdefault(n['startFrame'],cursor)
  if n['role'] in ['branding','membership']:
   push(n);i+=1;continue
  if n['role']=='actual':
   packet=n['packetIndex'];group=[]
   while i<len(base['nodes']) and base['nodes'][i].get('packetIndex')==packet and base['nodes'][i]['role']=='actual':group.append(base['nodes'][i]);i+=1
   start=cursor;a=by_packet.get(packet);base_frames=sum(x['frames'] for x in group)
   if a and a['where']=='before':extra(a)
   for g in group:
    old_starts[g['startFrame']]=start if g==group[0] else cursor
    if packet==9:
     # First see the wall, then UV address inspection at the spoken definition.
     left=old_native(g);left['frames']=420;left['id']+='-a';push(left);extra(a)
     right=old_native(g);right.update(id=g['id']+'-b',sourceStartFrame=g['sourceStartFrame']+420,retainedAssetStartFrame=420,frames=g['frames']-420);push(right)
    else:push(old_native(g))
   if a and a['where']=='after' and packet!=9:extra(a)
   end=cursor;existing=[v for v in base['voice'] if group[0]['startFrame']<=v['startFrame']<group[-1]['endFrame']]
   keys=list(dict.fromkeys(v['key'] for v in sorted(existing,key=lambda v:v['startFrame'])))
   if packet==0:keys=['g00','02-p1']
   if packet==40:keys=[k for k in keys if k!='g40']
   if packet==41:keys=['g40',*keys]
   at=start+(8 if keys and keys[0].startswith('g') else 0)
   for key in keys:
    if key=='09b-p3':v=voice(key,end-862,samples=862*400)
    elif key=='03-p6':v=voice(key,at,samples=sum(v['samples'] for v in existing if v['key']==key))
    elif key=='09a-p6':
     vv=next(v for v in existing if v['key']==key);v=voice(key,at,sourceOffset=vv['sourceStartSample']-allvoice[key][0]['sourceStartSample'],samples=vv['samples'])
    else:v=voice(key,at)
    voices.append(v);at=v['startFrame']+v['frames']+8
   if a and a['id'] in new_guides:
    v=voice(a['id'],max(at,start+base_frames+8));voices.append(v);at=v['startFrame']+v['frames']
   last_end=max(v['startFrame']+v['frames'] for v in voices if start<=v['startFrame']<end)
   assert last_end<=end,('packet-voice-overflow',packet,(last_end-end)/60)
   groups.append(dict(packetIndex=packet,startFrame=start,endFrame=end,voiceKeys=keys,addedGuide=a['id'] if a and a['id'] in new_guides else None))
   continue
  # Explanation nodes split into semantic voice ranges; preserve exact retained
  # visual ranges and their speech instead of rebuilding whole chapters.
  matches=sorted([v for v in base['voice'] if n['startFrame']<=v['startFrame']<n['endFrame']],key=lambda v:v['startFrame'])
  assert matches and matches[0]['startFrame']==n['startFrame'],n['id']
  consumed=0
  for j,bv in enumerate(matches):
   key=bv['key'];oldframes=(matches[j+1]['startFrame'] if j+1<len(matches) else n['endFrame'])-bv['startFrame'];start=cursor
   if key in changes and key!='09b-p3':
    b=scenes[key];sub='manim/videos/1080p60' if b['renderer']=='Manim' else 'scenes';file=O/f'{sub}/{key}.mp4';assert file.exists(),file
    visual=dict(id='e-'+key,role='explanation',path=file.relative_to(R).as_posix(),sourceStartFrame=0,frames=b['frames'],anchor=key,newExplanation=True)
    v=voice(key,start)
   else:
    # The reviewed composite includes the caption-safe inset. Reuse that
    # composite, rather than returning to an uninset raw Three.js asset.
    visual=dict(id='e-'+key,role='explanation',path=n['path'],sourceStartFrame=n['sourceStartFrame']+consumed,frames=oldframes,anchor=key,retained=True,baselineNodeId=n['id'])
    if key=='09b-p3':
     # Keep actual material-export graph while the new last sentence explains
     # why object textures differ from screen-space G-buffers.
     v=voice(key,start,sourceOffset=862*400)
     visual.update(actualExportGraph=True,sourceId=n['sourceId'],focusKo=n['focusKo'],retainedAssetPath=native_asset(n),retainedAssetStartFrame=0)
    else:
     offset=bv['sourceStartSample']-min(q['sourceStartSample'] for q in allvoice[key]);v=voice(key,start,sourceOffset=offset,samples=bv['samples'])
   push(visual);voices.append(v);assert v['startFrame']+v['frames']<=cursor,key
   if key=='09-p2':
    a=next(r for r in additions['rows'] if r['id']=='xsh');s=cursor;extra(a)
    # Natural sentence gaps synchronize whole-light disable, restore, and
    # cast-shadow settings. Every original source sample stays present once.
    for lo,hi,at in [(0,74880,8),(74880,162720,300),(162720,229920,720),(229920,366720,1200)]:
     v=voice('xsh',s+at,sourceOffset=lo,samples=hi-lo);voices.append(v);assert v['startFrame']+v['frames']<=cursor
   consumed+=oldframes
  assert consumed==n['frames'],n['id'];i+=1
 # One unique utterance exists for every retained/replaced/additional key.
 expected=set(allvoice)|set(new_guides);assert {v['key'] for v in voices}==expected
 for key in expected:
  vs=sorted((v for v in voices if v['key']==key),key=lambda v:v['utteranceStartSample']);assert vs[0]['utteranceStartSample']==0,key
  assert all(a['utteranceStartSample']+a['samples']==b['utteranceStartSample'] for a,b in zip(vs,vs[1:])),key
  assert sum(v['samples'] for v in vs)==voice(key,0)['samples'],key
 ordered=sorted(voices,key=lambda v:v['targetStartSample']);assert all(a['targetStartSample']+a['samples']<=b['targetStartSample'] for a,b in zip(ordered,ordered[1:])), 'speech overlap'
 actual=sum(n['frames'] for n in nodes if n['role']=='actual');ex=sum(n['frames'] for n in nodes if n['role']=='explanation');error=actual-.6*(actual+ex);assert abs(error)<=1,(actual,ex,error)
 chapters=[{**c,'startFrame':old_starts[c['startFrame']]} for c in base['chapters']]
 out=dict(schemaVersion=1,createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),fps=60,timeBase=90000,frames=cursor,seconds=cursor/60,nodes=nodes,voice=voices,chapters=chapters,nativeGroups=groups,actualFrames=actual,explanationFrames=ex,bodyFrames=actual+ex,ratioRoundingErrorFrames=error,bodyRatioApproved=True,allFinalPixelsApproved=False,finalMixAsrApproved=False,finalPairComplete=False,finalTimingApproved=False,inputHashes={f.relative_to(R).as_posix():sha(f) for f in [H/'native-additions.json',H/'changes.json',H/'measured-scene-plan.json']},retainedVoiceKeys=92,replacedVoiceKeys=52,additionalGuides=6,baselineId='uT5FTLJx5_c',baselineModified=False)
 wr(O/'edit-plan-proposal.json',out);print(json.dumps({k:out[k] for k in ['frames','seconds','actualFrames','explanationFrames','ratioRoundingErrorFrames']}))
if __name__=='__main__':main()

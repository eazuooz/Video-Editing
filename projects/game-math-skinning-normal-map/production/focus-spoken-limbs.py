"""Retarget M22's body markers to the actual words and observed native motion."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
work=P/'production/local/game-layout-in-context-v1';out=P/'production/local/annotation-reviewed-v3';assert not out.exists()
assert read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['productionAllowedNow']
spec=[('000','mario-pose','같은 순간 확대 · 팔과 다리','mario',714.8,
 [(216,80,37,52),(213,93,38,49),(202,96,41,41),(204,96,34,40),(202,96,33,40),(201,135,40,37),(200,136,37,39),(198,139,38,39),(202,138,35,41),(203,134,32,52),(198,133,35,53),(199,142,32,35),(198,135,36,55),(192,135,41,53),(190,96,37,54),(186,70,43,56)]),
 ('002','rider-pose','착지 뒤 구부린 팔과 무릎','rider',743.4,
 [(132,104,65,80),(145,102,67,83),(150,111,71,78),(149,116,64,80),(145,115,68,82),(148,114,67,84),(143,113,60,86),(144,115,63,85),(146,116,73,78),(143,117,79,73),(150,117,88,67),(157,117,87,64),(154,116,86,66)])]
tracks=P/'planning/game-annotation-tracks.json';old=read(tracks);bindings=read(P/'planning/scene-bindings.json');plan=read(P/'planning/production-plan.json')
for sid,id,label,board,t0,boxes in spec:
 window=next(w for w in old['windows'] if w['id']==id);prior=R/window['trackFile'];d=read(prior);s=next(s for s in bindings['scenes'] if s['id']==sid)
 times=[t0+j/8 for j in range(len(boxes))];keys=[]
 for t,(cx,cy,w,h) in zip(times,boxes):
  keys.append(dict(time=t,bbox=[round(v*4.8,2) for v in [cx-w/2,cy-h/2,w,h]],visible=True))
 d.update(start=times[0],end=times[-1],bbox=keys[0]['bbox'],label=label,keyframes=keys,shape='hollow-ellipse',method='Individually placed on inspected native frames at 8 fps; interpolate visible extent only. Not measured skeletal joints.',priorTrack=prior.relative_to(R).as_posix(),failedSamples=0)
 boardfile=work/(board+'-spoken-focus.jpg');assert boardfile.is_file()
 d['visualQa']=dict(status='temporal-samples-reviewed-final-encoded-pending',at=datetime.now(timezone.utc).isoformat(),evidence=boardfile.relative_to(R).as_posix(),sha256=sha(boardfile),note='Inspected native 8-fps sequence against unchanged actual paragraph ASR. Mario: airborne, tucked, crouched landing, straightening, jump. Rider: body absorbs landing and banks into turn. No inferred game internals.',movingFinalComposite=False,humanListening=False)
 new=out/(id+'.json');save(new,d)
 window.update(start=d['start'],end=d['end'],bbox=d['bbox'],label=label,shape=d['shape'],trackFile=new.relative_to(R).as_posix(),sourceTrackSha256=sha(new),visualQa=d['visualQa'],compositeShape='tracked hollow perimeter; current body-part words')
 if sid=='000':
  inset=dict(kind='same-instant-native-crop',start=times[0],end=times[-1],cropSize=[272,224],displaySize=[544,448],displayAt=[1160,314],
   centers=[[t,round(x*4.8,2),round(y*4.8,2)] for t,(x,y,_,_) in zip(times,boxes)],
   basis='Native source pixels only. Same time as main picture, during the words about limbs. Right wall is clear of the live character, native HUD and fixed captions.',sourceFrames=boardfile.relative_to(R).as_posix(),finalQa=False)
  s['actualGamePart']['nativeDetailInset']=inset
  next(g for g in plan['nativeGameCueBindings'] if g['sceneId']==sid)['nativeDetailInset']=copy.deepcopy(inset)
save(tracks,old);bp=P/'planning/scene-bindings.json';save(bp,bindings);plan['sceneBindingsSha256']=sha(bp)
plan['spokenLimbFocus']=dict(sourceSpeech='Unchanged raw takes 000 and 002, audio-v2 and audio-v3',evidence=work.relative_to(R).as_posix(),scope='Retimed native frame guides, same-instant Mario enlargement. Source/audio windows unchanged.',finalEncodedQa=False);save(P/'planning/production-plan.json',plan)
print('Two speech-specific body guides and one same-instant native detail inset selected.')

"""Reuse decoded original narration; replace only the 46 authorized complete paragraphs."""
from common import *
import copy,math
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
P=R/'projects/game-math-quaternion-foundations-v3';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';A=O/'audio';rate=48000
authorized('M05');plan=read(H/'voice-plan.json');takes=read(A/'paragraph-takes.json')
assert takes['identitySha256']==plan['identitySha256'] and takes['takeCount']==len(plan['jobs'])
for inp in plan['inputs'].values():assert sha(R/inp['file'])==inp['sha256']
byid={x['id']:x for x in takes['takes']};edits=read(B/'m05-narration-edits.json')['edits']
baseline=O/'baseline-audio.m4a';pcm=A/'baseline-decoded-48k.wav'
if not pcm.exists():run(['ffmpeg','-v','error','-i',baseline,'-ar',rate,'-ac','2','-c:a','pcm_f32le',pcm])
x,sr=sf.read(pcm,dtype='float32',always_2d=True);assert sr==rate
old=read(P/'production/timeline.json');script=read(P/'script/concept-fit-v2/narration.ko.json');by_script={s['id']:s for s in script['scenes']}
out=copy.deepcopy(old);out['scenes']=[];out.pop('koCaptions',None);out.pop('enCaptions',None)
out.update(revision='concept-fit-v2',sourceTimelineSha256=sha(P/'production/timeline.json'),sourceAudioSha256=sha(baseline),newTtsParagraphs=46,unchangedParagraphs=125)
chunks=[x[:2*rate]];cursor=120;mapping=[];(A/'scenes').mkdir(exist_ok=True)
def level(v):
 m=v.mean(axis=1) if v.ndim==2 else v;n=2400;frames=m[:len(m)//n*n].reshape(-1,n);db=20*np.log10(np.maximum(np.sqrt(np.mean(frames.astype(np.float64)**2,axis=1)),1e-12));return float(np.median(db[db>=db.max()-30]))
for original in old['scenes']:
 sid=original['id'];scene=copy.deepcopy(original);scene['start']=cursor/60;scene['title']=by_script[sid]['title'];scene['audioOrigins']=[]
 start=round(original['start']*rate);size=original['frames']*800;raw=x[start:start+size];assert len(raw)==size
 if sid not in edits:
  y=raw.copy();scene['audioPreservation']='Exact decoded baseline scene samples; no new synthesis or time adjustment'
 else:
  parts=[];local=0;newcues=[];starts=[]
  for j,cue in enumerate(original['cues'],1):
   a=max(0.,cue['start']-.08);b=min(original['seconds'],cue['end']+.16)
   if j<len(original['cues']):b=min(b,original['cues'][j]['start']-.02)
   boundaries=[];acc=0
   for pause in original.get('observationPauses',[]):
    pa=pause['rawAt']+acc;pb=pa+pause['seconds'];acc+=pause['seconds'];boundaries.append((pa,pb))
   intervals=[];at=a
   for pa,pb in boundaries:
    if pb<=at or pa>=b:continue
    if pa>at:intervals.append((at,min(pa,b)))
    at=max(at,pb)
   if at<b:intervals.append((at,b))
   source=np.concatenate([raw[round(u*rate):round(v*rate)] for u,v in intervals])
   key=f'{sid}.L{j:02}';changed=str(j) in edits[sid]
   if changed:
    take=byid[key];assert sha(R/take['file'])==take['sha256'];v,rr=sf.read(R/take['file'],dtype='float32');assert rr==24000
    requested_gain=float(np.clip(level(source)-level(v),-12,12));v=resample_poly(v,2,1).astype('float32')
    gain=min(requested_gain,float(20*np.log10(.90/max(float(abs(v).max()),1e-9))))
    v=v*np.float32(10**(gain/20));v=np.column_stack([v,v])
    origin=dict(kind='changed-complete-paragraph',take=take['file'],takeSha256=take['sha256'],gainDb=gain,requestedGainDb=requested_gain,headroomLimited=gain<requested_gain-.001,sourceIntervals=intervals)
    speech_a=0.;speech_b=len(v)/rate
   else:
    v=source;origin=dict(kind='original-decoded-paragraph',baseline=rel(baseline),globalIntervals=[[original['start']+u,original['start']+w] for u,w in intervals],sampleCount=len(v))
    def mapped(t):return sum(max(0,min(t,w)-u) for u,w in intervals)
    speech_a=mapped(cue['start']);speech_b=mapped(cue['end'])
   if j>1:parts.append(np.zeros((round(.18*rate),2),dtype='float32'));local+=len(parts[-1])
   begin=local/rate;starts.append(begin+speech_a)
   newcues.append(dict(start=begin+speech_a,end=begin+speech_b,text=by_script[sid]['lines'][j-1],line=j))
   origin.update(line=j,outputStart=begin,outputSamples=len(v),speechStart=begin+speech_a,speechEnd=begin+speech_b);scene['audioOrigins'].append(origin)
   parts.append(v);local+=len(v)
  y=np.concatenate(parts);frames=math.ceil((len(y)/rate+.20)*60);y=np.pad(y,((0,frames*800-len(y)),(0,0)))
  scene.update(frames=frames,seconds=frames/60,cues=newcues,lineStarts=starts,voiceSeconds=len(y)/rate,observationPauses=[],observationReview={'status':'legacy automatic observation silence removed only in changed game passages','newAutomaticHolds':0})
  scene['audioPreservation']='Unchanged complete paragraphs decoded from original AAC; only game-specific changed paragraphs use new Qwen takes. No time-stretch or fades.'
  for key in ['cuts','cut','rawOrigin','narrationWindowSeconds','voiceSha256']:scene.pop(key,None)
 path=A/'scenes'/f'{sid}-scene.wav';sf.write(path,y,rate,subtype='FLOAT');scene['voice']=rel(path);scene['voiceSha256']=sha(path);scene['voiceSampleRate']=rate
 scene['baselineStart']=original['start'];scene['baselineSeconds']=original['seconds'];scene['gameWindowSeconds']={'02':18.,'GA01':11.,'QF30':9.}.get(sid,0.)
 if original['classification']=='actual':scene['classification']='mixed' if scene['gameWindowSeconds'] else 'explanation-implementation'
 out['scenes'].append(scene);chunks.append(y);cursor+=scene['frames'];mapping.append(dict(scene=sid,newStart=scene['start'],oldStart=original['start'],newSeconds=scene['seconds'],oldSeconds=original['seconds'],changedParagraphs=len(edits.get(sid,{})),audioOrigins=scene['audioOrigins']))
old_outro=round((old['seconds']-10)*rate);chunks.append(x[old_outro:old_outro+10*rate]);cursor+=600
full=np.concatenate(chunks);assert len(full)==cursor*800
sf.write(A/'narration-full.wav',full,rate,subtype='FLOAT')
out.update(frames=cursor,seconds=cursor/60,bodyFrames=cursor-720,bodySeconds=(cursor-720)/60,actualFrames=round(sum(s['gameWindowSeconds'] for s in out['scenes'])*60));out['actualShare']=out['actualFrames']/out['bodyFrames'];out['explanationFrames']=out['bodyFrames']-out['actualFrames'];out['explanationShare']=1-out['actualShare']
save(H/'timeline.json',out);save(H/'audio-restoration-map.json',dict(sourceAudioSha256=sha(baseline),decodedBaselineSha256=sha(pcm),output=rel(A/'narration-full.wav'),outputSha256=sha(A/'narration-full.wav'),sampleRate=rate,seconds=len(full)/rate,floatPeak=float(abs(full).max()),scenes=mapping,review='Source ASR, phrase seams and final moving review pending. Decoded AAC reuse is not original uncompressed PCM recovery.'))
print(json.dumps(dict(seconds=out['seconds'],frames=cursor,changed=46,unchanged=125,peak=float(abs(full).max())),ensure_ascii=False))

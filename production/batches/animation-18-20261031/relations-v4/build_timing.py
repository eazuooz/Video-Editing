from pathlib import Path
import json,re,difflib,math,hashlib,subprocess,sys
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local';plan=json.loads((H/'planning/relations-plan.json').read_text('utf-8'))
def norm(s):return ''.join(c.lower() for c in s if c.isalnum())
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args):return subprocess.run([str(x) for x in args],capture_output=True,check=True,encoding='utf-8',errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
episodes=[];reviews=[];prior_reviews={x['id']:x for x in json.loads((L/'text-review.json').read_text('utf-8'))} if (L/'text-review.json').exists() else {}
selected={x for x in sys.argv[1:] if re.fullmatch(r'A\d\d',x)}
prior_timing={x['id']:x for x in json.loads((L/'timing.json').read_text('utf-8'))['episodes']} if (L/'timing.json').exists() else {}
available='--available' in sys.argv
level_corrections=json.loads((H/'audio-level-corrections.json').read_text('utf-8')) if (H/'audio-level-corrections.json').exists() else {}
for ep in plan['episodes']:
 if selected and ep['id'] not in selected:
  assert ep['id'] in prior_timing and ep['id'] in prior_reviews,(ep['id'],'Selective update requires preserved timing and review')
  episodes.append(prior_timing[ep['id']]);reviews.append(prior_reviews[ep['id']]);continue
 if available and not (L/'asr'/(ep['id']+'.json')).exists():continue
 id=ep['id'];audio=L/'voice/chunks'/(id+'-scene.wav');asr=json.loads((L/'asr'/(id+'.json')).read_text('utf-8'));assert asr['audio_sha256']==sha(audio)
 text='';times=[]
 for w in asr['chunks']:
  a,b=w['timestamp']
  if a is None or b is None:continue
  word=norm(w['text']);text+=word
  times +=[(a+(b-a)*i/max(1,len(word)),a+(b-a)*(i+1)/max(1,len(word))) for i in range(len(word))]
 spoken=[norm(s.get('spokenKo',s['ko'])) for s in ep['sentences']];expected=''.join(spoken);matcher=difflib.SequenceMatcher(None,expected,text,autojunk=False);mapping={}
 for a,b,n in matcher.get_matching_blocks():
  for k in range(n):mapping[a+k]=times[b+k]
 cursor=0;sentences=[];bad=[]
 for s,normalized in zip(ep['sentences'],spoken):
  found=[mapping[i] for i in range(cursor,cursor+len(normalized)) if i in mapping];score=len(found)/max(1,len(normalized))
  if score<.62 or len(found)<4:bad.append({'id':s['id'],'matchRatio':score,'expected':s.get('spokenKo',s['ko'])})
  assert found,(id,s['id'],'Sentence absent from independent ASR')
  sentences.append({'id':s['id'],'beat':s['beat'],'start':found[0][0],'end':found[-1][1],'ko':s['ko'],'en':s['en'],'matchRatio':score})
  cursor+=len(normalized)
 boundary_repairs=[]
 for left,right in zip(sentences,sentences[1:]):
  if left['end']>right['start']:
   overlap=left['end']-right['start'];assert overlap<=.25,(id,'Large ASR sentence overlap needs contextual review',left,right)
   boundary=(left['end']+right['start'])/2;boundary_repairs.append({'left':left['id'],'right':right['id'],'overlapSeconds':overlap,'sharedBoundary':boundary,'reason':'Whisper word timestamps overlap at long-form chunk boundary; midpoint joins caption timing only, PCM unchanged.'});left['end']=right['start']=boundary
 review={'id':id,'audioSha256':sha(audio),'expected':' '.join(s.get('spokenKo',s['ko']) for s in ep['sentences']),'actual':asr['text'],'sequenceMatchRatio':matcher.ratio(),'flaggedSentences':bad,'directReview':'pending'}
 prev=prior_reviews.get(id,{})
 if all(prev.get(k)==review[k] for k in ['audioSha256','expected','actual']):review.update({k:v for k,v in prev.items() if k in ['directReview','reviewNotes','reviewedAt']})
 reviews.append(review)
 if bad:continue
 info=sf.info(audio);frames=math.ceil((info.duration+.16)*60);out=R/'projects'/ep['slug']/'production/local/relations-v4';out.mkdir(exist_ok=True)
 processing_audio=audio;correction=level_corrections.get(id)
 if correction:
  assert correction['sourceSha256']==sha(audio)
  samples,samplerate=sf.read(audio,dtype='float64',always_2d=True);clock=np.arange(len(samples))/samplerate
  gain_envelope=np.clip((clock-correction['rampStart'])/(correction['rampEnd']-correction['rampStart']),0,1)*correction['gainDb']
  samples*=10**(gain_envelope[:,None]/20);assert float(abs(samples).max())<1
  processing_audio=out/'level-corrected-source.wav';sf.write(processing_audio,samples,samplerate,subtype='PCM_24')
  correction=dict(correction,processedSourceSha256=sha(processing_audio),rawSourcePreserved=True)
 # Explicit mono→stereo occurs before measurement, so channel conversion does not create a3dB surprise.
 meter=run(['ffmpeg','-hide_banner','-i',processing_audio,'-af','pan=stereo|c0=c0|c1=c0,loudnorm=I=-16:TP=-1.7:LRA=11:print_format=json','-f','null','-']).stderr
 metrics=json.loads(meter[meter.rfind('{'):meter.rfind('}')+1]);gain=-16-float(metrics['input_i'])
 wav=out/'addition-voice.wav';peak=10**(-1.8/20)
 run(['ffmpeg','-v','error','-y','-i',processing_audio,'-af',f'pan=stereo|c0=c0|c1=c0,volume={gain}dB,alimiter=limit={peak}:attack=5:release=80:level=false:latency=true,apad','-t',frames/60,'-ar','48000','-ac','2','-c:a','pcm_s24le',wav])
 # Continue the same approved bed through the added explanation. Existing body PCM is untouched.
 p=R/'projects'/ep['slug'];oldplan=json.loads((p/'production/pacing-v3/edit-plan.json').read_text('utf-8-sig'))
 oldproof=json.loads((p/'production/local/pacing-v3/audio-proof.json').read_text('utf-8-sig'))
 if oldplan.get('audioMode')=='preserve-final-mix':
  musicpath=R/oldplan['music'];musicgain=(oldproof.get('insertedMusicBridges') or [{}])[0].get('musicGain',1)
 else:
  musicpath=p/'production/local/pacing-v3/music.wav';musicgain=oldproof['gain']
 v,vs=sf.read(wav,dtype='float64',always_2d=True);music,ms=sf.read(musicpath,dtype='float64',always_2d=True);assert vs==ms==48000
 oldat=round(ep['insertion']['atSeconds']*48000);n=len(v);at=oldat%len(music)
 idx=np.arange(n);w=np.clip((idx/max(1,n-1)-.35)/.30,0,1)[:,None]
 bed=(music[(at+idx)%len(music)]*(1-w)+music[(at-n+idx)%len(music)]*w)*musicgain
 edge=min(1920,n//4);fade=np.ones(n);fade[:edge]=np.linspace(0,1,edge);fade[-edge:]=np.linspace(1,0,edge);bed*=fade[:,None]
 mixed=v+bed;attenuation=min(1,10**(-1.7/20)/max(1e-12,float(np.max(abs(mixed)))));mixed*=attenuation
 final=out/'addition.wav';sf.write(final,mixed,48000,subtype='PCM_24')
 episodes.append({'id':id,'slug':ep['slug'],'duration':frames/60,'frames':frames,'rawDuration':info.duration,'sentences':sentences,'asrBoundaryRepairs':boundary_repairs,'audio':str(final),'audioSha256':sha(final),'voice':str(wav),'voiceSha256':sha(wav),'rawAudioSha256':sha(audio),'sourceLoudness':metrics,'constantGainDb':gain,'music':{'path':str(musicpath),'sha256':sha(musicpath),'gain':musicgain,'phaseReturnBridge':True,'edgeFadeSeconds':.04},'newMixAttenuation':attenuation,'endBreathingSeconds':frames/60-info.duration})
 if correction:episodes[-1]['voiceLevelCorrection']=correction
(L/'text-review.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n','utf-8')
(L/'timing.json').write_text(json.dumps({'fps':60,'episodes':episodes},ensure_ascii=False,indent=2)+'\n','utf-8')
assert len(episodes)==len(reviews) and (available or len(episodes)==18),('ASR mismatches require review before proceeding',[r['id'] for r in reviews if r['flaggedSentences']])
print(str(len(episodes))+' diagrams timed to actual complete speech; direct transcript review still required')

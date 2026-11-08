"""Insert one adjacent passage; retain every sample of the existing final PCM."""
from pathlib import Path
import json,math,hashlib,subprocess,difflib,importlib.util
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/room-v4-video';OLD=P/'production/local/room-v3';O=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v4-video/video');OLDOUT=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v3/video')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd):return subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf8',errors='replace',check=True,creationflags=subprocess.CREATE_NO_WINDOW)
base=read(OLD/'timeline.json');source=L/'voice/chunks/W36-scene.wav';info=sf.info(source);frames=math.ceil((info.duration+.28)*60);duration=frames/60;insert=next(s['start'] for s in base['scenes'] if s['id']=='R30')
scene={'id':'W36','title':'기록을 남기는 작은 작업실','start':insert,'speechEnd':insert+info.duration,'duration':duration,'frames':frames,'source':str(source),'sourceSha256':sha(source),'sourceDuration':info.duration,'originalPcmPreserved':False}
rows=[]
for r in base['scenes']:
 r=dict(r)
 if r['id']=='R30':rows.append(scene);r['start']+=duration;r['speechEnd']+=duration
 rows.append(r)
tm={**base,'scenes':rows,'duration':base['duration']+duration,'frames':base['frames']+frames};save(L/'timeline.json',tm)
new,sr=sf.read(source,dtype='float32');assert sr==24000
if new.ndim>1:new=new.mean(axis=1)
n=round(sr*.05);rms=np.array([np.sqrt(np.mean(new[k:k+n]**2)+1e-12) for k in range(0,len(new)-n,n)]);db=20*np.log10(np.maximum(rms,1e-8));median=float(np.median(db[db>db.max()-25]));gain=float(np.clip(-22-median,-12,12));fade=round(sr*.006);new*=10**(gain/20);new[:fade]*=np.linspace(0,1,fade);new[-fade:]*=np.linspace(1,0,fade)
new=np.pad(new,(0,round(duration*sr)-len(new)));sf.write(O/'new-aligned.wav',new,sr,subtype='FLOAT')
oldqa=read(H.parent/'room-v3/audio-qa.json');common=oldqa['globalGainDb'];limiter=oldqa['peakProtection']['filter'];run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',O/'new-aligned.wav','-af',f'pan=stereo|c0=c0|c1=c0,volume={common}dB,{limiter}','-ar','48000','-ac','2','-c:a','pcm_s24le',O/'new-final.wav'])
oldpcm,oldsr=sf.read(OLDOUT/'final-mix.wav',dtype='int32');newpcm,newsr=sf.read(O/'new-final.wav',dtype='int32');assert oldsr==newsr==48000;cut=round(insert*oldsr);expected=round(duration*oldsr)
if len(newpcm)<expected:newpcm=np.pad(newpcm,((0,expected-len(newpcm)),(0,0)))
newpcm=newpcm[:expected];mixed=np.concatenate([oldpcm[:cut],newpcm,oldpcm[cut:]]);sf.write(O/'final-mix.wav',mixed,oldsr,subtype='PCM_24');check,_=sf.read(O/'final-mix.wav',dtype='int32');assert np.array_equal(check[:cut],oldpcm[:cut]);assert np.array_equal(check[cut+expected:],oldpcm[cut:]);run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',O/'final-mix.wav','-c:a','aac','-b:a','192k',O/'final-mix.m4a'])
measure=run(['ffmpeg','-hide_banner','-i',O/'final-mix.m4a','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);meter=json.loads(measure.stderr[measure.stderr.rfind('{'):measure.stderr.rfind('}')+1]);assert float(meter['input_tp'])<=-1.4,meter;assert abs(float(meter['input_i'])+16)<.6,meter
save(H/'audio-qa.json',{'duration':tm['duration'],'oldPcmSha256':sha(OLDOUT/'final-mix.wav'),'newSourceSha256':sha(source),'oldSampleRangesIdentical':True,'oldSampleCount':len(oldpcm),'insertAtSeconds':insert,'newDurationSeconds':duration,'newActiveMedianDbfs':median,'newGainDb':gain,'reusedGlobalGainDb':common,'mixSha256':sha(O/'final-mix.wav'),'encodedMixSha256':sha(O/'final-mix.m4a'),'measuredEncoded':meter,'wholeActualListening':False,'newPassageAsr':'asr/W36.json','unchanged51AsrReuse':'room-v3 current-mix baseline and added semantic review; identical PCM ranges'})
spec=importlib.util.spec_from_file_location('previous_caption_helpers',P/'production/build_captions.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
script=next(s for s in read(H/'revision-plan.json')['scenes'] if s['id']=='W36');parts=read(H/'caption-clauses.json')['scenes'][0]['parts'];asr=read(L/'asr/W36.json');assert asr['audio_sha256']==sha(source)
for lang in ['ko','en']:assert ''.join(''.join(v[lang].split()) for v in parts)==''.join(script[lang].split()),lang
expectedtext=helper.norm(script['ko']);recognized='';at=[]
for w in asr['chunks']:
 a,b=w['timestamp'];n=helper.norm(helper.asr_spelling(w['text']))
 if a is None or b is None:continue
 recognized+=n;at.extend(np.linspace(a,b,max(1,len(n)),endpoint=False).tolist()[:len(n)])
match=difflib.SequenceMatcher(None,expectedtext,recognized,autojunk=False);anchors={}
for a,b,n in match.get_matching_blocks():
 for k in range(n):anchors[a+k]=at[b+k]
xs=np.array(sorted(anchors));ys=np.array([anchors[x] for x in xs]);mapped=np.maximum.accumulate(np.interp(np.arange(len(expectedtext)),xs,ys));offset=0;added=[]
for part in parts:
 n=len(helper.norm(part['ko']));a=float(mapped[min(offset,len(mapped)-1)]);offset+=n;b=float(mapped[offset]) if offset<len(mapped) else info.duration
 added.append({'scene':'W36','start':insert+a,'end':insert+b,'ko':part['ko'].replace('오백 자','500자'),'spoken':part['ko'],'en':part['en']})
cues=[]
for c in read(OLD/'captions.json'):
 c=dict(c)
 if c['scene']=='R30':c['start']+=duration;c['end']+=duration
 cues.append(c)
cues+=added;cues.sort(key=lambda v:v['start'])
for i,c in enumerate(cues):c['index']=i+1;assert c['end']>c['start']
save(L/'captions.json',cues)
for lang in ['ko','en']:(L/f'captions.{lang}.srt').write_text('\n\n'.join(f"{c['index']}\n{helper.stamp(c['start'])} --> {helper.stamp(c['end'])}\n{c[lang]}" for c in cues)+'\n','utf8')
save(H/'alignment-review.json',{'id':'W36','expected':script['ko'],'recognized':asr['text'],'ratio':match.ratio(),'matchedCharacters':len(anchors),'original51CuesPreservedExceptR30TimeShift':True,'humanListening':False})
print('Integrated',tm['duration'],'seconds',tm['frames'],'frames',len(cues),'cues; ASR',match.ratio(),meter)

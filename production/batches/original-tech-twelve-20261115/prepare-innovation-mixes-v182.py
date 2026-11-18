"""Add reviewed opening PCM to each byte-preserved original body mix on CPU."""
from pathlib import Path
import hashlib,importlib.util,json,math
import av,numpy as np,soundfile as sf
from scipy.ndimage import minimum_filter1d
from scipy.signal import resample_poly
H=Path(__file__).resolve().parent;ROOT=H.parents[2];M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');BASE=M/'innovation-openings-v181'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def rms(x):return float(np.sqrt(np.mean(x.astype(np.float64)**2)))
def db(x):return 20*math.log10(max(1e-12,rms(x)))
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def stamp(s):
 n=round(s*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def parse_stamp(s):
 a,b,c=s.replace(',','.').split(':');return int(a)*3600+int(b)*60+float(c)
def main():
 plan=read(H/'innovation-opening-plan-v181.json');v=read(BASE/'voice/voice-generation-complete-proof.json');qa=read(BASE/'voice/technical-voice-review-v182.json');sources=read(H/'innovation-opening-source-review-v181.json');assert qa['approvedForConstantGainMix']and not qa['issues'];assert qa['voice']==pin(BASE/'voice/voice-generation-complete-proof.json')
 primitive=module('intro177_existing_level',ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py')
 music=ROOT/'shared/assets/music/incompetech/Wholesome.mp3';resampler=av.AudioResampler(format='fltp',layout='stereo',rate=24000);parts=[]
 with av.open(str(music))as c:
  for f in c.decode(audio=0):
   parts.extend(x.to_ndarray().T.copy()for x in resampler.resample(f))
   if sum(len(x)for x in parts)>30*24000:break
 music_pcm=np.concatenate(parts).astype(np.float32);built=[]
 rawcanonical,rate=sf.read(v['canonical']['path'],dtype='float32');assert rate==24000
 unit_times=read(v['unitTiming']['path'])['entries'];narration=read(H/'innovation-opening-narration-v181.json')
 for row,review,sr in zip(plan['rows'],qa['rows'],sources['rows']):
  order=row['order'];out=BASE/row['slug'];proofpath=out/'audio-build-v182.json'
  if proofpath.exists():
   old=read(proofpath);assert old['sourceVoiceReview']==pin(BASE/'voice/technical-voice-review-v182.json');assert pin(old['mix']['path'])==old['mix'];built.append(pin(proofpath));continue
  oldmix=read(row['baselineMix']['path']);body,br=sf.read(oldmix['mix']['path'],dtype='float32',always_2d=True);oldvoice,vr=sf.read(oldmix['voice']['path'],dtype='float32');assert br==vr==24000 and body.shape==(oldmix['frames'],2)and len(oldvoice)==len(body)
  oldvoice=np.asarray(oldvoice).reshape(-1)*oldmix['masterConstantGain'];bodyLevelTarget=primitive.levels(oldvoice,24000)['bodyDbfs'];oldWordLevels=[primitive.levels(oldvoice[w['startSample']:w['endSample']],24000)['bodyDbfs']for w in oldmix['wordWindows']if w['endSample']>w['startSample']];target=float(np.median(oldWordLevels));a,b=review['canonicalStartSample'],review['canonicalEndSample'];raw=rawcanonical[a:b].copy();voice=raw.copy();gainrows=[]
  for u,e,chunk in zip(narration['units'],unit_times,v['rawChunks']):
   if u['order']!=order:continue
   x,y=round(e['start']*24000)-a,round(e['end']*24000)-a;assert 0<=x<y<=len(raw)
   before=primitive.levels(raw[x:y],24000);unitWords=[w for w in review['words']if x<=(w['start']+w['end'])*12000<y];wordMedian=float(np.median([primitive.levels(raw[math.floor(w['start']*24000):math.ceil(w['end']*24000)],24000)['bodyDbfs']for w in unitWords]));gainDb=target-wordMedian;assert abs(gainDb)<=12
   gain=10**(gainDb/20);voice[x:y]*=gain;gainrows.append(dict(unit=u['id'],rawChunk=chunk,startSample=x,endSample=y,gainDb=gainDb,gain=gain,referenceWordBodyMedianDbfs=target,rawWholeWordBodyMedianDbfs=wordMedian,rawLevels=before,afterConstantGainLevels=primitive.levels(voice[x:y],24000)))
  # Only sub-frame alignment silence, after the complete natural utterance.
  alignment=(-len(voice))%400;voice=np.pad(voice,(0,alignment));introFrames=len(voice)//400;introSeconds=introFrames/60
  assert introSeconds<=sum(w['availableSeconds']for w in sr['selectedWindows'])
  bg=music_pcm[:len(voice)].copy()*oldmix['musicSourceGain']*oldmix['masterConstantGain'];fade=min(2400,len(bg)//4);bg[:fade]*=np.linspace(0,1,fade,dtype=np.float32)[:,None];bg[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
  targetenv=np.ones(len(bg),dtype=np.float32)
  for word in review['words']:
   x,y=math.floor(word['start']*24000),math.ceil(word['end']*24000);limit=min(1,rms(voice[x:y])/max(1e-12,rms(bg[x:y]))*10**(-14/20));x=max(0,x-480);y=min(len(bg),y+480);targetenv[x:y]=np.minimum(targetenv[x:y],limit)
  envelope=minimum_filter1d(targetenv,size=961,mode='nearest');release=math.exp(-1/(.28*24000))
  for j in range(1,len(bg)):envelope[j]=min(envelope[j],release*envelope[j-1]+1-release)
  bg*=envelope[:,None];intro=voice[:,None]+bg;tp=float(np.max(np.abs(resample_poly(intro,4,1,axis=0))));introBus=min(1,10**(-3.5/20)/max(tp,1e-12));intro*=introBus;voice*=introBus;bg*=introBus
  for g in gainrows:assert abs(primitive.levels(voice[g['startSample']:g['endSample']],24000)['bodyDbfs']-bodyLevelTarget)<=4
  wordrows=[];words_for_trend=[]
  for w in review['words']:
   x,y=math.floor(w['start']*24000),math.ceil(w['end']*24000);lev=primitive.levels(voice[x:y],24000);delta=db(bg[x:y])-db(voice[x:y]);assert delta<=-12+.001;wordrows.append(dict(text=w['text'],startSample=x,endSample=y,musicMinusVoiceDb=delta,voiceLevels=lev));words_for_trend.append(dict(text=w['text'],startSeconds=w['start'],endSeconds=w['end'],durationSeconds=w['end']-w['start'],levels=dict(processed=lev)))
  trend=primitive.trend(words_for_trend,'processed');assert not trend['suspect'],(order,trend)
  median=float(np.median([w['musicMinusVoiceDb']for w in wordrows]));assert median>-22
  full=np.concatenate([intro,body]);fullvoice=np.concatenate([voice,oldvoice]);assert np.array_equal(full[len(intro):],body)
  out.mkdir(parents=True,exist_ok=True);mixpath=out/'final-mix-v182.wav';vp=out/'narration-stem-v182.wav';bgp=out/'intro-music-v182.wav';sf.write(mixpath,full,24000,subtype='FLOAT');sf.write(vp,fullvoice,24000,subtype='FLOAT');sf.write(bgp,bg,24000,subtype='FLOAT')
  check,cr=sf.read(mixpath,dtype='float32',always_2d=True);assert cr==24000 and np.array_equal(check[len(intro):],body)
  cues=[]
  for c in review['cues']:cues.append(dict(c))
  cues[-1]['end']=introSeconds
  for lang,key in [('ko','subtitlesKo'),('en','subtitlesEn')]:
   oldtext=Path(row['baseline']['artifacts'][key]['path']).read_text('utf8').strip();blocks=oldtext.split('\n\n');text=[]
   for i,c in enumerate(cues):text.append(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c[lang]}')
   for j,block in enumerate(blocks):
    lines=block.splitlines();x,y=lines[1].split(' --> ');text.append(f'{len(cues)+j+1}\n{stamp(parse_stamp(x)+introSeconds)} --> {stamp(parse_stamp(y)+introSeconds)}\n'+ '\n'.join(lines[2:]))
   (out/f'captions-v182.{lang}.srt').write_text('\n\n'.join(text)+'\n','utf8')
  proof=dict(order=order,slug=row['slug'],mix=pin(mixpath),narrationStem=pin(vp),introMusic=pin(bgp),sourceVoiceReview=pin(BASE/'voice/technical-voice-review-v182.json'),baselineMix=row['baselineMix'],baselineBodyPcmSha256=hashlib.sha256(body.tobytes()).hexdigest(),bodyFloatPcmByteExact=True,bodyVoiceMusicAndGameAudioUnmodified=True,introVoiceCanonicalStartSample=a,introVoiceCanonicalEndSample=b,introSamples=len(intro),introVideoFrames=introFrames,introSeconds=introSeconds,alignmentSilenceSamples=alignment,frames=len(full),durationSeconds=len(full)/24000,rate=24000,channels=2,newUnitConstantGain=gainrows,constantGainMethod='One scalar per complete utterance; actual whole-word-body median matched to current accepted body; no within-utterance envelope change',bodyWordBodyMedianTargetDbfs=target,bodyFullTakeLevelDbfs=bodyLevelTarget,introOnlyBusGain=introBus,withinUtteranceEnvelopeChanged=False,sourceMusic=pin(music),musicLicense=pin(music.with_suffix('.LICENSE.md')),medianIntroMusicMinusVoiceDb=median,newWordLevels=wordrows,processedParagraphTrend=trend,captionCues=cues,selectedSourceWindows=sr['selectedWindows'],source=row['introSource'],bodyCaptionTimingShiftSeconds=introSeconds,actualFullListening=False,humanApproval=False)
  save(proofpath,proof);built.append(pin(proofpath));print(json.dumps(dict(order=order,introSeconds=introSeconds,totalSeconds=proof['durationSeconds'],bodyPcmByteExact=True,musicVsVoiceDb=median)),flush=True)
 save(BASE/'all-mixes-v182.json',dict(mixes=built,sourcePlan=pin(H/'innovation-opening-plan-v181.json'),sourceVoiceReview=pin(BASE/'voice/technical-voice-review-v182.json'),count=12,independentFinalMixedAsrRequired=True,actualListening=False,humanApproval=False))
if __name__=='__main__':main()

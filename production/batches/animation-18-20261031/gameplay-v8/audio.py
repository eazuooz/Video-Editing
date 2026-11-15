"""Natural-duration surgical speech replacement; original PCM survives outside edits."""
from common import *
import math,shutil,os
os.environ.setdefault('OMP_NUM_THREADS','4');os.environ.setdefault('MKL_NUM_THREADS','4')
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

RATE=48000
def ts(t):
 n=round(t*1000);h,n=divmod(n,3600000);m,n=divmod(n,60000);s,n=divmod(n,1000)
 return f'{h:02}:{m:02}:{s:02},{n:03}'
def write_srt(p,rows):
 Path(p).write_text(''.join(f"{i}\n{ts(r['start'])} --> {ts(r['end'])}\n{r['text']}\n\n" for i,r in enumerate(rows,1)),encoding='utf-8')
def map_frame(n,changes):return n+sum(c['deltaFrames'] for c in changes if n>=c['oldEndFrame'])
def old_frame(n,changes):
 delta=0
 for r in changes:
  at=r['oldEndFrame']+delta
  if at<=n<at+r['deltaFrames']:return r['oldEndFrame']-1
  if n>=at+r['deltaFrames']:delta+=r['deltaFrames']
 return n-delta

def source_mix(ep):
 p=Path('C:/Users/1/Videos/YamyamProduction/animation-native-clips-v6')/ep/'assembly/final-mix.wav'
 assert p.is_file(),p
 return p
def music_path(ep):
 if ep=='A03':return ROOT/'projects/animation-breaking-down-attack-animations/production/local/grid-v1/music-stem.wav'
 # The v6 receipt retains the original project slug.
 p=read(BATCH/'native-clips-v6/plan.json');e=next(e for e in p['episodes'] if e['id']==ep)
 return ROOT/'projects'/e['baseline']['slug']/'production/local/series-v1/music.wav'
def prepare_episode(e):
 ep=e['id'];folder=WORK/ep;folder.mkdir(parents=True,exist_ok=True)
 prior={r['kind']:Path(r['path']) for r in e['baselineFiles']}
 patches=[dict(r,audioFile=str(HERE/'local/voice/chunks'/(r['id']+'-scene.wav'))) for r in read(HERE/'narration-changes.json')['records'] if r['episode']==ep]
 if (HERE/'guidance-changes.json').exists():patches += [r for r in read(HERE/'guidance-changes.json')['records'] if r['episode']==ep]
 for r in patches:
  if r.get('kind')=='music-only-observation-guidance':
   assert not any(c['start']<r['end'] and c['end']>r['start'] for c in e['bodyNarrationCues']),(ep,'guidance overlaps original speech')
 out=folder/'audio.json'
 signature=dict(algorithm='exact-sample-splice-guided-observations-v3',original=sha(source_mix(ep)),patches=[dict(id=r['id'],start=r['start'],end=r['end'],sha256=sha(r['audioFile']),ko=r['ko'],en=r['en'],units=r.get('units'),**({'postNormalizeGainDb':r['postNormalizeGainDb']} if 'postNormalizeGainDb' in r else {})) for r in patches])
 if out.exists() and read(out).get('signature')==signature and (folder/'final-mix.wav').exists():return read(out)
 original,rate=sf.read(source_mix(ep),dtype='float32',always_2d=True);assert rate==RATE
 assert abs(len(original)/RATE-e['baselineFrames']/60)<.04,(ep,len(original)/RATE)
 records=[]
 for r in patches:
  r=dict(r);p=Path(r['audioFile']);norm=folder/(r['id']+'-normalized.wav')
  filters='loudnorm=I=-18:TP=-3:LRA=7,aresample=48000'
  if r.get('postNormalizeGainDb'):filters+=f",volume={r['postNormalizeGainDb']}dB"
  if r.get('postNormalizeGainDb',0)>0:filters+=',alimiter=limit=0.70:level=false:attack=5:release=50'
  ff('-i',p,'-af',filters,'-ar',48000,'-ac',1,'-c:a','pcm_f32le',norm)
  samples,sr=sf.read(norm,dtype='float32');assert sr==RATE
  a=round(r['start']*60);b=round(r['end']*60);delta=max(0,math.ceil((len(samples)/RATE+.04-(r['end']-r['start']))*60))
  r.update(oldStartFrame=a,oldEndFrame=b,oldStartSample=round(r['start']*RATE),oldEndSample=round(r['end']*RATE),
           deltaFrames=delta,voiceSamples=len(samples),normalized=str(norm),audioSha256=sha(p),naturalDuration=len(samples)/RATE)
  records.append(r)
 records.sort(key=lambda r:r['oldStartFrame']);assert all(r['oldEndFrame']<=q['oldStartFrame'] for r,q in zip(records,records[1:]))
 if records:music,mr=sf.read(music_path(ep),dtype='float32',always_2d=True)
 else:music,mr=np.zeros((1,2),dtype='float32'),RATE
 if mr!=RATE:
  g=math.gcd(mr,RATE);music=resample_poly(music,RATE//g,mr//g,axis=0).astype('float32')
 if music.shape[1]==1:music=np.repeat(music,2,axis=1)
 parts=[];cursor=0;identical=[];delta=0
 for r in records:
  a=r['oldStartSample'];b=r['oldEndSample']
  parts.append(original[cursor:a]);identical.append(dict(oldStartSample=cursor,oldEndSample=a,newStartSample=cursor+delta*800))
  voice,_=sf.read(r['normalized'],dtype='float32');length=b-a+r['deltaFrames']*800
  edge=min(288,len(voice)//2);ramp=np.linspace(0,1,edge,dtype='float32');voice[:edge]*=ramp;voice[-edge:]*=ramp[::-1]
  bed=music[np.arange(a,a+length)%len(music)].copy();bed[:len(voice)]+=voice[:,None]
  assert float(np.max(np.abs(bed)))<1,(ep,r['id'],'clipping')
  fade=240;mix=np.linspace(0,1,fade)[:,None];bed[:fade]=original[a:a+fade]*(1-mix)+bed[:fade]*mix
  # The trailing edge blends to the same original next-sample context.
  bed[-fade:]=bed[-fade:]*(1-mix)+original[b-fade:b]*mix
  r.update(newStartFrame=r['oldStartFrame']+delta,newEndFrame=r['oldEndFrame']+delta+r['deltaFrames'],newStartSeconds=r['start']+delta/60)
  delta+=r['deltaFrames'];parts.append(bed);cursor=b
 parts.append(original[cursor:]);identical.append(dict(oldStartSample=cursor,oldEndSample=len(original),newStartSample=cursor+delta*800))
 mixed=np.concatenate(parts,axis=0);want=(e['baselineFrames']+delta)*800
 if abs(len(mixed)-want)<=1600:
  if len(mixed)<want:mixed=np.pad(mixed,((0,want-len(mixed)),(0,0)))
  else:mixed=mixed[:want]
 assert len(mixed)==want
 for proof in identical:
  a,b,c=proof.values();assert np.array_equal(original[a:b],mixed[c:c+b-a]),(ep,'unchanged PCM altered')
 sf.write(folder/'final-mix.wav',mixed,RATE,subtype='FLOAT')
 for lang in ['ko','en']:
  cues=srt(prior[lang+'.srt']);lookup={r['captionIndex']:r for r in records if r['captionIndex'] is not None};new=[]
  for i,c in enumerate(cues):
   if i in lookup:
    r=lookup[i];new.append(dict(start=r['newStartSeconds'],end=r['newStartSeconds']+r['naturalDuration'],text=wrap_caption(r[lang])))
   else:new.append(dict(start=c['start']+(map_frame(round(c['start']*60),records)-round(c['start']*60))/60,
                        end=c['end']+(map_frame(round(c['end']*60),records)-round(c['end']*60))/60,text=c['text']))
  for r in records:
   if r['captionIndex'] is not None:continue
   units=r['units'];weights=[len(u['ko'].replace(' ','')) for u in units];cursor=r['newStartSeconds']
   for unit,weight in zip(units,weights):
    end=cursor+r['naturalDuration']*weight/sum(weights);new.append(dict(start=cursor,end=end,text=wrap_caption(unit[lang])));cursor=end
  new.sort(key=lambda c:c['start'])
  assert all(a['end']<=b['start']+.022 for a,b in zip(new,new[1:])),(ep,lang,'overlapping captions')
  write_srt(folder/(lang+'.srt'),new)
 record=dict(signature=signature,episode=ep,changes=records,originalFrames=e['baselineFrames'],frames=e['baselineFrames']+delta,
  addedNaturalSpeechFrames=delta,audio=str(folder/'final-mix.wav'),audioSha256=sha(folder/'final-mix.wav'),
  unchangedPcmRanges=identical,unchangedPcmRangeCount=len(identical),originalPcmUnchangedOutsideReplacements=True,
  overviewSpeechPreserved=True,recapSpeechPreserved=True,speechTimeCompression=False,bgmRetained=True,fullListening='pending-human-review',
  guidanceCount=sum(r['captionIndex'] is None for r in records),captionAlignmentPending=any(r['captionIndex'] is None for r in records))
 save(out,record);print(ep,'natural-duration audio ready, added frames',delta,flush=True);return record

if __name__=='__main__':
 for e in read(HERE/'plan.json')['episodes']:
  if e['id'] in SCOPE:prepare_episode(e)

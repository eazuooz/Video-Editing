"""Build the A03 clock, fixed bilingual captions and house music from sealed takes."""
from pathlib import Path
import hashlib,json,math,subprocess
import numpy as np,soundfile as sf
import caption_pipeline as captions
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/grid-v1'
read=lambda f:json.loads(f.read_text(encoding='utf-8-sig'))
def save(f,x):f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(f):return f.relative_to(R).as_posix()
def sha(f):
 with f.open('rb') as b:return hashlib.file_digest(b,'sha256').hexdigest()
def ff(*args,log='ffmpeg'):
 with (L/(log+'.log')).open('wb') as record:
  cmd=['ffmpeg','-hide_banner','-nostdin','-y',*map(str,args)]
  if subprocess.call(cmd,stdout=record,stderr=record):raise RuntimeError((L/(log+'.log')).read_text(encoding='utf-8',errors='replace')[-2400:])
def timeline():
 units=read(H/'units-final.json');voice=L/'voice';assembly=read(voice/'narration.timing.json')
 originals={r['ko']:r for pars in read(P/'script/grid-v1/caption-units.json')['byScene'].values() for group in pars.values() for r in group}
 assert len(assembly['entries'])==len(units['groups'])
 paragraphs=[];scenes=[];rows=[]
 aliases={'마흔여덟':'48','마흔여덟번째':'48번째','서른여섯':'36','예순':'60','영 점 팔':'08','영 점 육':'06','영 점 이':'02','영점팔':'08','영점육':'06','영점이':'02','제로점이':'02','히트스탑':'히트스톱','hit stop':'히트스톱','hitstop':'히트스톱','cancel':'캔슬'}
 for group,item,row in zip(units['groups'],units['paragraphs'],assembly['entries'],strict=True):
  sid=item['id'];assert sid==row['scene_id']
  wav=voice/'chunks'/(sid+'-scene.wav');q=voice/'asr'/(sid+'.json');r=read(q);assert r['audio_sha256']==sha(wav)
  duration=sf.info(wav).duration;origin=2+row['start'];end=2+row['end']
  assert abs(duration-(end-origin))<.00015
  spans=[]
  for k,e in group:
   unit=originals.get(k,{'ko':k,'en':e,'twoLineReason':'Keep the complete observed action and its result within the same cue.'})
   assert unit['en']==e;spans.append(unit)
  para=dict(id=sid,scene=item['chapter'],line=item['paragraph'],start=origin,duration=duration,ko=' '.join(k for k,e in group),en=' '.join(e for k,e in group),asrFile=rel(q),audioFile=rel(wav),captionUnits=spans)
  # Whisper can attach trailing punctuation to an overlapping second token. Keep
  # source ASR immutable, trim only timestamp overlap in the alignment input.
  safe=[];last=0
  for word in r['words']:
   a,b=word['timestamp']
   a=last if a is None else max(last,a);b=duration if b is None else min(duration,b)
   if b>a+.0001:
    safe.append({'text':word['text'],'timestamp':[a,b]});last=b
  cache=L/'alignment-words'/f'{sid}.json';cache.parent.mkdir(exist_ok=True)
  save(cache,{'words':safe,'audio_sha256':r['audio_sha256'],'rawAsrSha256':sha(q)});para['asrFile']=rel(cache);paragraphs.append(para)
  rows.append(dict(id=sid,chapter=item['chapter'],paragraph=item['paragraph'],start=origin,end=end,pcmSha256=sha(wav)))
 total=math.ceil((2+assembly['duration_seconds'])*60)+600
 for i,row in enumerate(rows):
  row['f0']=round(row['start']*60);row['f1']=round(rows[i+1]['start']*60) if i<len(rows)-1 else total-600
 data={'fps':60,'bodyEndFrame':total-600,'aliases':aliases,'paragraphs':paragraphs}
 save(L/'caption-input.json',data);captions.build(data,L)
 for n in range(1,7):
  group=[r for r in rows if r['chapter']==f'{n:02}']
  scenes.append({'id':f'{n:02}','title':next(r['title'] for r in units['paragraphs'] if r['chapter']==f'{n:02}'),'f0':group[0]['f0'],'f1':group[-1]['f1']})
 plan={'totalFrames':total,'bodyFrames':total-720,'framesPerSecond':60,'paragraphs':rows,'scenes':scenes}
 save(L/'timeline.json',plan);print(total,'frames',flush=True)
def mix():
 p=read(L/'timeline.json');sr=24000;n=round(p['totalFrames']/60*sr);a=np.zeros(n,np.float32);levels=[]
 for r in p['paragraphs']:
  wav=L/'voice/chunks'/(r['id']+'-scene.wav');x,rate=sf.read(wav,dtype='float32');assert rate==sr and sha(wav)==r['pcmSha256']
  levels1=[]
  for i in range(0,max(1,len(x)-sr//5),sr//8):
   block=x[i:i+sr//5];power=np.mean(block**2)
   if power>10**-4:levels1.append(10*np.log10(power))
  gain=-20-float(np.median(levels1));start=round(r['start']*sr);ramp=min(round(.006*sr),len(x)//2)
  x[:ramp]*=np.linspace(0,1,ramp);x[-ramp:]*=np.linspace(1,0,ramp)
  a[start:start+len(x)]=x*10**(gain/20);levels.append({'id':r['id'],'gainDb':gain})
 sf.write(L/'source-stem.wav',a,sr,subtype='FLOAT')
 ff('-i',L/'source-stem.wav','-af','acompressor=threshold=0.2:ratio=4:attack=2:release=80:makeup=1,pan=stereo|c0=c0|c1=c0,loudnorm=I=-16:TP=-2.5:LRA=9','-ar','48000','-c:a','pcm_s24le',L/'narration-stem.wav',log='normalize')
 music=R/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'
 assert sha(music)=='06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08' and music.with_suffix('.LICENSE.md').exists()
 duration=p['totalFrames']/60
 md=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(music)]))
 repeats=math.ceil(duration/(md-1));inputs=[];filters=[];last='0:a'
 for i in range(repeats):
  inputs+=['-i',music]
  if i:filters.append(f'[{last}][{i}:a]acrossfade=d=1[m{i}]');last=f'm{i}'
 filters.append(f'[{last}]atrim=duration={duration},loudnorm=I=-28:TP=-4:LRA=7,afade=t=in:d=0.4,afade=t=out:st={duration-.6}:d=.6[music]')
 ff(*inputs,'-filter_complex',';'.join(filters).replace('d=.6','d=0.6'),'-map','[music]','-ar','48000','-ac','2','-c:a','pcm_s24le',L/'music-stem.wav',log='music')
 graph='[0:a]asplit=2[v][side];[1:a][side]sidechaincompress=threshold=0.025:ratio=3:attack=35:release=400[m];[v][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.794:level=false:latency=true[out]'
 ff('-i',L/'narration-stem.wav','-i',L/'music-stem.wav','-filter_complex',graph,'-map','[out]','-c:a','pcm_s24le',L/'final-mix.wav',log='mix')
 ff('-i',L/'final-mix.wav','-t',duration,'-c:a','aac','-b:a','192k',L/'audio.m4a',log='encode-audio')
 save(L/'mix.json',{'stems':levels,'musicSha256':sha(music),'aacSha256':sha(L/'audio.m4a'),'sourceAudio':'Two CC recordings have music or guide audio, muted. Channel music and own voice.'})
if __name__=='__main__':timeline();mix()

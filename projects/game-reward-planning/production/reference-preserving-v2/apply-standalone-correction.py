"""Four complete-sentence edits; retain other approved PCM, source video and timing."""
from pathlib import Path
import json,sys,hashlib,subprocess
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';D=P/'production/reference-preserving-v2';B=P/'production/local/reference-preserving-v2/edit';O=B/'standalone-v3';N=R/'shared/output/narration/game-reward-planning/reference-preserving-v2';T=N/'standalone-patches'
sys.path.insert(0,str(R/'qwen3-tts'))
from align_project_subtitles import align_characters,normalized,partition_fixed
from build_translated_srt import split_caption,wrapped_lines,timestamp
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args,name):
 r=subprocess.run(['ffmpeg','-hide_banner','-y',*args],cwd=R,capture_output=True);(O/(name+'.log')).write_bytes(r.stderr)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-1800:])
spec=load(D/'standalone-patches.json')['patches'];timing=load(N/'game-reward-planning-reference-v2.timing.json');rows=load(B/'caption-tracks.json');base,sr=sf.read(B/'narration-stem.wav',dtype='float32',always_2d=True);voice=base.copy();mask=np.zeros(len(base),bool);report=[];replacementRows={}
def level(a):
 a=a.mean(axis=1) if a.ndim==2 else a;w=round(sr*.4);h=round(sr*.1)
 d=[20*np.log10(max(float(np.sqrt(np.mean(a[i:i+w]**2))),1e-9)) for i in range(0,len(a)-w+1,h)]
 return float(np.percentile(d,70))
for x in spec:
 src=T/'chunks'/f"{x['id']}-scene.wav";raw=load(T/'asr'/f"{x['id']}.json");assert raw['audio_sha256']==sha(src);info=sf.info(src);duration=info.duration
 assert duration<=x['slot'][1]-x['slot'][0],(x['id'],duration,'does not fit; do not time-stretch')
 # Split extra silence across both sentence joins, retaining the scene timeline.
 x['start']=round((x['slot'][0]+x['slot'][1]-duration)/2,4)
 origin=2+next(y['start'] for y in timing['entries'] if y['scene_id']==x['scene']);l,r=[round((origin+v)*sr) for v in x['slot']];start=round((origin+x['start'])*sr)
 # Same voice compressor as the approved stem, then one constant local gain.
 temp=O/f"{x['id']}-processed.wav";run(['-i',str(src),'-af','acompressor=threshold=0.1:ratio=2:attack=20:release=250:makeup=1','-ar',str(sr),'-ac','2','-c:a','pcm_f32le',str(temp)],x['id']+'-process');a,rate=sf.read(temp,dtype='float32',always_2d=True);assert rate==sr
 target=level(base[l:r]);gain=target-level(a);a*=10**(gain/20)
 sf.write(O/f"{x['id']}-gain.wav",a,sr,subtype='FLOAT')
 run(['-i',str(O/f"{x['id']}-gain.wav"),'-af','alimiter=limit=0.794:level=false:latency=true','-c:a','pcm_f32le',str(O/f"{x['id']}-limited.wav")],x['id']+'-peak')
 a,rate=sf.read(O/f"{x['id']}-limited.wav",dtype='float32',always_2d=True);assert float(np.max(np.abs(a)))<.8
 voice[l:r]=0;voice[start:start+len(a)]=a;mask[l:r]=True
 end=start+len(a);report.append(dict(x,origin=origin,absoluteSlot=[l/sr,r/sr],absoluteStart=start/sr,absoluteSpeechEnd=end/sr,duration=duration,sourceSha256=sha(src),recognized=raw['text'],gainDb=gain,oldSpeechP70Dbfs=target,newSpeechP70Dbfs=level(a),humanListening='pending'))
 aa,bb,_=align_characters(x['ko'],raw['words'],duration);aa[1:]=np.maximum(aa[1:],bb[:-1]);bb=np.maximum(aa,bb);count=max(len(split_caption(x['ko'],32)),len(split_caption(x['en'],46)));kk=partition_fixed(x['ko'],32,count);ee=partition_fixed(x['en'],46,count);offset=0;new=[]
 for ko,en in zip(kk,ee):
  n=len(normalized(ko));new.append(dict(scene=x['scene'],line=x['line'],start=origin+x['start']+float(aa[offset]),end=origin+x['start']+float(bb[offset+n-1]),ko='\n'.join(wrapped_lines(ko,32)),en='\n'.join(wrapped_lines(en,46))));offset+=n
 replacementRows[(x['scene'],x['line'])]=new
assert np.array_equal(voice[~mask],base[~mask]);sf.write(O/'narration-stem.wav',voice,sr,subtype='PCM_24');readback,_=sf.read(O/'narration-stem.wav',dtype='float32',always_2d=True);assert np.array_equal(readback[~mask],base[~mask])
outrows=[];emitted=set()
for row in rows:
 key=(row['scene'],row['line'])
 if key in replacementRows:
  if key not in emitted:outrows.extend(replacementRows[key]);emitted.add(key)
 else:outrows.append(row)
for lang in ['ko','en']:
 blocks=[];previous=0
 for i,row in enumerate(outrows,1):
  assert row['start']>=previous-.002 and row['end']>row['start'],(i,row);previous=row['end'];blocks.append(f"{i}\n{timestamp(row['start'])} --> {timestamp(row['end'])}\n{row[lang]}")
 (O/f'captions.{lang}.srt').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')
save(O/'caption-tracks.json',outrows)
graph='[0:a]asplit=3[voice][side1][side2];[1:a][side1]sidechaincompress=threshold=0.025:ratio=3:attack=35:release=400[bg];[2:a][side2]sidechaincompress=threshold=0.035:ratio=2:attack=15:release=250[game];[voice][bg][game]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.794:level=false:latency=true[out]'
run(['-i',str(O/'narration-stem.wav'),'-i',str(B/'music-stem.wav'),'-i',str(B/'game-stem.wav'),'-filter_complex',graph,'-map','[out]','-t',str(len(base)/sr),'-ar',str(sr),'-c:a','pcm_s24le',str(O/'remixed.wav')],'remix')
oldmix,rs=sf.read(B/'final-mix.wav',dtype='float32',always_2d=True);newmix,rs2=sf.read(O/'remixed.wav',dtype='float32',always_2d=True);assert len(oldmix)==len(newmix) and rs==rs2==sr
final=oldmix.copy();mixmask=np.zeros(len(final),bool)
for x in report:
 l=max(0,round((x['absoluteSlot'][0]-2)*sr));r=min(len(final),round((x['absoluteSlot'][1]+4)*sr));w=np.ones(r-l,dtype=np.float32);f=round(.1*sr);w[:f]=np.linspace(0,1,f);w[-f:]=np.linspace(1,0,f);final[l:r]=newmix[l:r]*w[:,None]+oldmix[l:r]*(1-w[:,None]);mixmask[l:r]=True;x['mixAffectedRange']=[l/sr,r/sr]
assert np.array_equal(final[~mixmask],oldmix[~mixmask]);sf.write(O/'final-mix.wav',final,sr,subtype='PCM_24');readback,_=sf.read(O/'final-mix.wav',dtype='float32',always_2d=True);assert np.array_equal(readback[~mixmask],oldmix[~mixmask])
save(O/'patch-evidence.json',{'patches':report,'unaffectedNarrationSamplesIdentical':True,'unaffectedMixSamplesIdentical':True,'originalNarrationSha256':sha(B/'narration-stem.wav'),'newNarrationSha256':sha(O/'narration-stem.wav'),'originalMixSha256':sha(B/'final-mix.wav'),'newMixSha256':sha(O/'final-mix.wav'),'duration':len(final)/sr,'speedChanges':False,'unchangedCaptions':len(rows)-sum(1 for r in rows if (r['scene'],r['line']) in replacementRows),'changedCueCount':sum(map(len,replacementRows.values())),'footageAndTimingChanged':False})
# Reuse the established caption renderer at the new output path.
source=(D/'build-caption-layout.py').read_text(encoding='utf8');source=source.replace("P/'production/local/reference-preserving-v2/edit'","P/'production/local/reference-preserving-v2/edit/standalone-v3'");exec(compile(source,str(D/'build-caption-layout.py'),'exec'),{'__file__':str(D/'build-caption-layout.py')})
print('Localized narration/mix and paired captions ready; unaffected PCM verified identical')

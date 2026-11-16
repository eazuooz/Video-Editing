"""CPU-only decoded video/audio and actual word-window QA; never infer listening."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math
import av,numpy as np,soundfile as sf
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
CONFIG={x['slug']:('revision-ninja-turns-20261116/film-v78'if x['slug']=='shorts-oot-ninja-show-z-targeting'else'film-v7'if x['slug']=='shorts-mario64-lakitu-camera'else'film-v10')for x in json.loads((HERE/'batch.json').read_text(encoding='utf-8-sig'))['projects']}

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',choices=CONFIG,required=True);p.add_argument('--mode',choices=['pilot','clean'],default='pilot');a=p.parse_args();slug=a.project;version=CONFIG[slug];base=MEDIA/slug/version;pp=base/('pilot-proof.json'if a.mode=='pilot'else'clean-proof.json');proof=read(pp);video=Path(proof['video']['path']);assert pin(video)==proof['video'];caption_path=Path(next(x['path']for x in proof['identity']['inputs']if Path(x['path']).name.startswith('caption-timing-')));captions=read(caption_path);voice=read(captions['voice']['path']);mix=read(next(x['path']for x in proof['identity']['inputs']if Path(x['path']).name=='audio-build.json'));out=base/(a.mode+'-encoded-qa-v1');assert not out.exists();out.mkdir()
 s=importlib.util.spec_from_file_location('unchanged_encoded_level_primitive',ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
 samples={};chosen={min(proof['actualVideoFrames']-1,math.floor((c['start']+c['spokenEnd'])/2*60)):i for i,c in enumerate(captions['cues'])};minimum_body_variance=1e9;count=0;last_pts=-1
 with av.open(str(video))as c:
  st=c.streams.video[0];assert(st.width,st.height)==(1080,1920)and st.average_rate==60
  for i,f in enumerate(c.decode(st)):
   assert f.time is not None and abs(f.time-i/60)<=1/15360+.00001 and f.time>last_pts;last_pts=f.time;count+=1
   if i in chosen:
    im=f.to_image();body=np.asarray(im.crop((0,396,984,1380)),dtype=np.float32);variance=float(body.var());minimum_body_variance=min(minimum_body_variance,variance);assert variance>1,'Blank sampled source body'
    image=out/('cue-'+str(chosen[i]).zfill(3)+'-375.jpg');im.resize((375,667),Image.Resampling.LANCZOS).save(image,quality=94);samples[chosen[i]]=pin(image)
 assert count==proof['actualVideoFrames']==math.ceil(mix['durationSeconds']*60)
 frames=[];audio_pts=[];resample=av.AudioResampler(format='fltp',layout='stereo',rate=24000)
 with av.open(str(video))as c:
  st=c.streams.audio[0];duration=float(st.duration*st.time_base);assert abs(duration-mix['frames']/24000)<=1/24000+.000001,('Audio track body duration',duration,mix['frames']/24000)
  for f in c.decode(st):
   audio_pts.append(float(f.time));frames.extend(x.to_ndarray().T.copy()for x in resample.resample(f))
 decoded=np.concatenate(frames,axis=0);assert abs(audio_pts[0])<=1/24000 and len(decoded)>=mix['frames'];reference,rate=sf.read(mix['mix']['path'],dtype='float32',always_2d=True);assert rate==24000 and len(reference)==mix['frames'];alignment=q.estimate_alignment(reference,decoded,24000);assert alignment['supported'],alignment
 offset=alignment['decodedMinusReferenceSamples'];assert isinstance(offset,int)
 # Include every actual unit ASR word, not only displayed caption endpoints.
 reviewpaths={x['source']['review']['path']for c in captions['cues']for x in [c['startWord'],c['endWord']]};reviews=[read(p)for p in reviewpaths];timing=read(voice['unitTiming']['path'])['entries'];word_windows=[]
 for e,raw in zip(timing,voice['rawChunks']):
  records=[r for d in reviews for r in d['results']if r['task'].get('unit')==e['scene_id']or r['task']['key']=='unit-'+e['scene_id']];records=[r for r in records if r['task']['sha256']==raw['sha256']]
  if records:
   r=records[0]
   for w in r['rawRecognition']['chunks']:
    x,y=w['timestamp'];assert x is not None and y is not None and 0<=x<y<=raw['duration'];word_windows.append((e['start']+x,e['start']+y,w['text']))
  else:
   # A whole-paragraph recognition may be the independently accepted source.
   para=next(u['paragraph']for u in voice['identity']['unitGroups']if u['id']==e['scene_id']);cs=[c for c in captions['cues']if c['paragraph']==para];rp=read(cs[0]['startWord']['source']['review']['path']);key=cs[0]['startWord']['source']['taskKey'];r=next(x for x in rp['results']if x['task']['key']==key);offset_seconds=r['task']['offsetSample']/24000
   for w in r['rawRecognition']['chunks']:
    x,y=w['timestamp'];assert x is not None and y is not None and x<y;word_windows.append((offset_seconds+x,offset_seconds+y,w['text']))
 rows=[];seen=set()
 for x,y,text in word_windows:
  start,end=q.sample_window(x,y,24000)
  if (start,end)in seen:continue
  seen.add((start,end));assert 0<=start<end<=len(reference)and 0<=start+offset<end+offset<=len(decoded);before=q.levels(reference[start:end],24000);after=q.levels(decoded[start+offset:end+offset],24000);delta=after['bodyDbfs']-before['bodyDbfs'];assert abs(delta)<=q.POLICY['encodedWordLevelDeltaWarningDb'],(text,delta);rows.append(dict(text=text,startSample=start,endSample=end,encodedBodyDeltaDb=delta))
 contacts=[];ordered=sorted(samples.items())
 for k in range(0,len(ordered),8):
  group=ordered[k:k+8];im=Image.new('RGB',(4*375,2*697),'#15221d');d=ImageDraw.Draw(im)
  for j,(i,r)in enumerate(group):
   x=j%4*375;y=j//4*697;d.text((x+5,y+5),str(i)+' '+captions['cues'][i]['paragraph'],fill='white');im.paste(Image.open(r['path']),(x,y+30))
  path=out/f'contact-{k//8:02}.jpg';im.save(path,quality=94);contacts.append(pin(path))
 report=dict(video=pin(video),renderProof=pin(pp),mixProof=next(x for x in proof['identity']['inputs']if Path(x['path']).name=='audio-build.json'),captionTiming=pin(caption_path),decodedVideoFrames=count,sourceSize=[1080,1920],fps=60,bodyMixFrames=mix['frames'],audioTrackSeconds=duration,codecDecodedFrames=len(decoded),codecTrailingSamples=len(decoded)-mix['frames'],audioContentAlignment=alignment,wordLevelWindows=rows,minimumSampledBodyVariance=minimum_body_variance,captionSamples=[samples[i]for i in sorted(samples)],contactSheets=contacts,allAutomaticChecksPassed=True,actualListening=False,actualRealtimePlayback=False,humanApproval=False,visualReviewStillRequired=True)
 save(base/(a.mode+'-encoded-qa.json'),report);print(json.dumps(dict(report=pin(base/(a.mode+'-encoded-qa.json')),contacts=contacts)))
if __name__=='__main__':main()

"""CPU-only decoded video/audio and actual word-window QA; never infer listening."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math
import av,numpy as np,soundfile as sf
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
CONFIG={'shorts-mario64-lakitu-camera':'camera-paired-v164/film-v171'}

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
  st=c.streams.video[0];st.thread_count=2;assert(st.width,st.height)==(1080,1920)and st.average_rate==60
  for i,f in enumerate(c.decode(st)):
   assert f.time is not None and abs(f.time-i/60)<=1/15360+.00001 and f.time>last_pts;last_pts=f.time;count+=1
   if i in chosen:
    im=f.to_image();body=np.asarray(im.crop((0,396,984,1380)),dtype=np.float32);variance=float(body.var());minimum_body_variance=min(minimum_body_variance,variance);assert variance>1,'Blank sampled source body'
    image=out/('cue-'+str(chosen[i]).zfill(3)+'-375.jpg');im.resize((375,667),Image.Resampling.LANCZOS).save(image,quality=94);samples[chosen[i]]=pin(image)
 assert count==proof['actualVideoFrames']==math.ceil(mix['durationSeconds']*60)
 # The selected change is visual only. Exact AAC packet bytes and timing
 # bind the previously decoded full audio/whole-word/true-peak result.
 baseline=MEDIA/slug/'camera-music-v139/local-review-v5/captioned-v154.mp4';oldqa_path=MEDIA/slug/'camera-music-v139/film-v154/pilot-encoded-qa.json';oldqa=read(oldqa_path)
 def audio_packets(path):
  with av.open(str(path))as c:
   st=c.streams.audio[0];return [(p.pts,p.dts,p.duration,str(st.time_base),bytes(p))for p in c.demux(st)if p.size]
 assert audio_packets(video)==audio_packets(baseline),'Audio bytes/timing changed unexpectedly'
 with av.open(str(video))as c:
  st=c.streams.audio[0];duration=float(st.duration*st.time_base);assert abs(duration-mix['frames']/24000)<=1/24000+.000001;assert abs(next(c.decode(st)).time)<=1/24000
 rows=oldqa['wordLevelWindows'];alignment=oldqa['audioContentAlignment'];truepeakDbtp=oldqa['truePeakDbtp'];wordsource=Path(oldqa['wholeWordSource']['path'])
 contacts=[];ordered=sorted(samples.items())
 for k in range(0,len(ordered),8):
  group=ordered[k:k+8];im=Image.new('RGB',(4*375,2*697),'#15221d');d=ImageDraw.Draw(im)
  for j,(i,r)in enumerate(group):
   x=j%4*375;y=j//4*697;d.text((x+5,y+5),str(i)+' '+captions['cues'][i]['paragraph'],fill='white');im.paste(Image.open(r['path']),(x,y+30))
  path=out/f'contact-{k//8:02}.jpg';im.save(path,quality=94);contacts.append(pin(path))
 report=dict(video=pin(video),renderProof=pin(pp),mixProof=next(x for x in proof['identity']['inputs']if Path(x['path']).name=='audio-build.json'),captionTiming=pin(caption_path),decodedVideoFrames=count,sourceSize=[1080,1920],fps=60,bodyMixFrames=mix['frames'],audioTrackSeconds=duration,codecDecodedFrames=oldqa['codecDecodedFrames'],codecTrailingSamples=oldqa['codecTrailingSamples'],unchangedAudioQaReusedByExactPacketAndTimingEquality=True,referenceAudioQa=pin(oldqa_path),audioContentAlignment=alignment,wordLevelWindows=rows,wholeWordSource=pin(wordsource),truePeakDbtp=truepeakDbtp,minimumSampledBodyVariance=minimum_body_variance,captionSamples=[samples[i]for i in sorted(samples)],contactSheets=contacts,allAutomaticChecksPassed=True,encodedAudioPacketsByteExact=True,actualListening=False,actualRealtimePlayback=False,humanApproval=False,visualReviewStillRequired=True)
 save(base/(a.mode+'-encoded-qa.json'),report);print(json.dumps(dict(report=pin(base/(a.mode+'-encoded-qa.json')),contacts=contacts)))
if __name__=='__main__':main()

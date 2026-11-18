"""Full decode/PTS/AAC checks plus retained-body coded-picture and RGB equivalence."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,re
import av,numpy as np,soundfile as sf
from scipy.signal import resample_poly
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;ROOT=H.parents[2];C=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/innovation-openings-v181')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def stamp(s):
 a,b,c=s.replace(',','.').split(':');return int(a)*3600+int(b)*60+float(c)
def packets(path):
 with av.open(str(path))as c:
  s=c.streams.audio[0];return [(p.pts,p.dts,p.duration,str(s.time_base),bytes(p))for p in c.demux(s)if p.size]
def vcl(path):
 rows=[]
 with av.open(str(path))as c:
  s=c.streams.video[0];assert s.codec_context.name=='h264';extra=s.codec_context.extradata;assert extra[0]==1;length=(extra[4]&3)+1
  for packet in c.demux(s):
   data=bytes(packet);at=0
   while at<len(data):
    size=int.from_bytes(data[at:at+length],'big');at+=length;nal=data[at:at+size];assert len(nal)==size and size>0;at+=size
    if nal[0]&31 in [1,5]:rows.append(hashlib.sha256(nal).hexdigest())
   assert at==len(data)
 return rows
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--order',type=int,required=True);a=ap.parse_args();assert 1<=a.order<=12;plan=read(H/'innovation-opening-plan-v181.json');row=plan['rows'][a.order-1];out=C/row['slug'];rp=out/'render-proof-v183.json';proof=read(rp);mix=read(out/'audio-build-v182.json');target=out/'encoded-qa-v184.json';assert not target.exists();qaout=out/'encoded-qa-v184';assert not qaout.exists();qaout.mkdir()
 sp=importlib.util.spec_from_file_location('innovation184_old_level',ROOT/'production/batches/architectural-111-20261106/first-level-continuity-review.py');q=importlib.util.module_from_spec(sp);sp.loader.exec_module(q)
 oldtext=Path(row['baseline']['artifacts']['subtitlesKo']['path']).read_text('utf8');body_samples={0,1,proof['baselineVideoFrames']-1}
 for block in oldtext.strip().split('\n\n'):
  x,y=block.splitlines()[1].split(' --> ');body_samples.add(min(proof['baselineVideoFrames']-1,math.floor((stamp(x)+stamp(y))*30)))
 for beat in read(row['baselineFilm']['path'])['identity']['beats']:
  body_samples.add(min(proof['baselineVideoFrames']-1,math.floor(beat['start']*60)));body_samples.add(min(proof['baselineVideoFrames']-1,math.ceil(beat['end']*60)-1))
 intro_samples={min(proof['introVideoFrames']-1,math.floor((c['start']+c['spokenEnd'])*30)):i for i,c in enumerate(mix['captionCues'])};contacts=[];modes=[]
 for mode in ['captioned','clean']:
  video=Path(proof['masters'][mode]['path']);oldvideo=Path(row['baseline']['artifacts'][mode]['path']);assert pin(video)==proof['masters'][mode]
  oldcoded=vcl(oldvideo);newcoded=vcl(video);assert newcoded[-len(oldcoded):]==oldcoded,'Retained body coded-picture bytes changed'
  expected={}
  with av.open(str(oldvideo))as c:
   st=c.streams.video[0];st.thread_count=2
   for i,f in enumerate(c.decode(st)):
    if i in body_samples:expected[i]=hashlib.sha256(f.to_ndarray(format='rgb24').tobytes()).hexdigest()
  assert len(expected)==len(body_samples);count=0;matched=0;captured=[]
  with av.open(str(video))as c:
   st=c.streams.video[0];st.thread_count=2;assert (st.width,st.height)==(1080,1920)and st.average_rate==60
   for i,f in enumerate(c.decode(st)):
    assert f.time is not None and abs(f.time-i/60)<=1/15360+.000001;count+=1;bodyIndex=i-proof['introVideoFrames']
    if bodyIndex in expected:assert hashlib.sha256(f.to_ndarray(format='rgb24').tobytes()).hexdigest()==expected[bodyIndex],(mode,bodyIndex);matched+=1
    if i in intro_samples:
     im=f.to_image()
     if mode=='clean':assert float(np.quantile(np.asarray(im.crop((0,1470,1080,1740))),.999))<=8
     else:
      p=qaout/f'cue-{intro_samples[i]:02}-375.jpg';im.resize((375,667),Image.Resampling.LANCZOS).save(p,quality=94);captured.append(pin(p))
  assert count==proof['expectedTotalVideoFrames']and matched==len(expected)
  assert packets(video)==packets(proof['audio']['path'])
  with av.open(str(video))as c:
   st=c.streams.audio[0];duration=float(st.duration*st.time_base);assert abs(duration-mix['durationSeconds'])<=1/24000+.000001
  modes.append(dict(mode=mode,video=pin(video),decodedFrames=count,bodyRgbSamplesExact=matched,allBodyVclNalPayloadsByteExact=True,sourceBodyVclNalCount=len(oldcoded),aacPacketsAndTimingExactToSharedEncode=True,actualAudioTrackSeconds=duration,captionSamples=captured))
  if captured:
   im=Image.new('RGB',(1500,1394),'#14221c');dr=ImageDraw.Draw(im)
   for j,p in enumerate(captured):
    x=j%4*375;y=j//4*697;dr.text((x+5,y+5),f'{a.order:02} cue{j}',fill='white');im.paste(Image.open(p['path']),(x,y+30))
   p=qaout/'contact.jpg';im.save(p,quality=94);contacts.append(pin(p))
 ref,rate=sf.read(mix['mix']['path'],dtype='float32',always_2d=True);assert rate==24000;parts=[];resampler=av.AudioResampler(format='fltp',layout='stereo',rate=24000)
 with av.open(proof['masters']['captioned']['path'])as c:
  for f in c.decode(audio=0):parts.extend(z.to_ndarray().T.copy()for z in resampler.resample(f))
  parts.extend(z.to_ndarray().T.copy()for z in resampler.resample(None))
 decoded=np.concatenate(parts);assert len(decoded)>=len(ref);alignment=q.estimate_alignment(ref,decoded,24000);assert alignment['supported']and abs(alignment['decodedMinusReferenceSamples'])<=2;lag=alignment['decodedMinusReferenceSamples'];aligned=decoded[max(0,lag):max(0,lag)+len(ref)];assert len(aligned)==len(ref)
 peak=float(np.max(np.abs(resample_poly(aligned,4,1,axis=0))));truepeak=20*math.log10(max(peak,1e-12));assert truepeak<=-1
 words=[]
 for w in mix['newWordLevels']:
  x,y=w['startSample'],w['endSample'];before=q.levels(ref[x:y],24000);after=q.levels(aligned[x:y],24000);delta=after['bodyDbfs']-before['bodyDbfs'];assert abs(delta)<=2;words.append(dict(text=w['text'],startSample=x,endSample=y,reference=before,decoded=after,bodyDifferenceDb=delta))
 report=dict(order=a.order,slug=row['slug'],renderProof=pin(rp),audioMixProof=pin(out/'audio-build-v182.json'),modes=modes,fullVideoDecodeAndPtsPassed=True,retainedBodyVclAndDecodedSamplesExact=True,audioPacketsIdenticalForCleanAndCaptioned=True,audioAlignment=alignment,truePeakDbtp=truepeak,newEncodedWordWindows=words,codecDecodedSamples=len(decoded),codecTrailingSamples=len(decoded)-len(ref),contactSheets=contacts,automaticChecksPassed=True,allowedForUserReview=True,actualEncodedVisualInspectionStillRequired=True,actualFullListening=False,actualRealtimePlayback=False,humanApproval=False)
 target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(report=pin(target),order=a.order,frames=proof['expectedTotalVideoFrames'],bodyRgbAndVclExact=True,truePeakDbtp=truepeak,contacts=contacts)))
if __name__=='__main__':main()

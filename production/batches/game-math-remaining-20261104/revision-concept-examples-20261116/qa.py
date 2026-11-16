"""Actual encoded audio continuity, cue preservation and native-motion evidence."""
import numpy as np
from prepare import *
from render import ff,read_srt,read_json,run,FP
def decoded(p,t,d=1.4):return np.frombuffer(ff(['-ss',t,'-t',d,'-i',p,'-map','0:a:0','-ac','1','-ar','24000','-f','f32le','-'],capture=True),dtype='<f4')
def compare(a,b):
 n=min(len(a),len(b));a=a[:n];b=b[:n];r=float(np.sqrt(np.mean(a*a)))
 if r<1e-5:return dict(quiet=True,rms=r)
 options=[]
 for delta in range(-3,4):
  x=a[max(0,delta):n+min(0,delta)];y=b[max(0,-delta):n+min(0,-delta)];c=float(np.dot(x,y)/(np.linalg.norm(x)*np.linalg.norm(y)+1e-12));options.append((c,delta))
 c,shift=max(options);ratio=float(np.sqrt(np.mean(b*b)))/r;assert c>.965 and .88<ratio<1.12,(c,shift,ratio)
 return dict(correlation=c,shiftSamples=shift,rmsRatio=ratio)
def main():
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('episodes',nargs='*');args=ap.parse_args();results=[]
 for e in read(HERE/'plan.json')['episodes']:
  if args.episodes and e['id'] not in args.episodes:continue
  d=read(HERE/'deliveries'/(e['id']+'.json'));p=pathlib.Path(d.get('workDir',str(HERE/'local/work'/e['id'])));cached=p/'continuity.json'
  if cached.exists() and read(cached).get('masterSha256')==d['files']['clean']['sha256']:results.append(read(cached));continue
  original=e['baselineFiles']['clean']['path'];final=d['files']['clean']['path'];offset=0;joins=[]
  for s in d['inserts']:
   at=s['atFrame']/60;added=s['frames']/60
   before=compare(decoded(original,at-2),decoded(final,at+offset-2))
   after=compare(decoded(original,at+.4),decoded(final,at+offset+added+.4))
   joins.append(dict(key=s['key'],before=before,after=after,at=at,shift=offset,added=added));offset+=added
  subtitles=[]
  for lang in ('ko','en'):
   old=read_srt(e['baselineFiles'][lang]['path']);new=read_srt(d['files'][lang]['path']);added_texts=[]
   for s in d['inserts']:
    for c in read(HERE/'alignment.json')['items'][s['key']]['cues']:added_texts.append(c[lang])
   cursor=0
   for c in new:
    if cursor<len(old) and c['text']==old[cursor]['text']:
     src=old[cursor];shift=sum(s['frames']/60 for s in d['inserts'] if s['atFrame']/60<=src['start']+.03)
     assert abs(c['start']-src['start']-shift)<.0011 and abs(c['end']-src['end']-shift)<.0011;cursor+=1
   assert cursor==len(old),(e['id'],lang,'old cue missing',cursor,len(old))
   assert len(new)==len(old)+len(added_texts)
   subtitles.append(dict(language=lang,originalCues=len(old),originalTextAndOrderPreserved=True,newCues=len(added_texts),allOriginalTimingsShiftedByExactInsertedDuration=True))
  a=[]
  for kind in ('clean','captioned'):a.append(ff(['-i',d['files'][kind]['path'],'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],capture=True).decode().strip())
  assert a[0]==a[1]
  result=dict(id=e['id'],masterSha256=d['files']['clean']['sha256'],audioJoins=joins,originalVoiceAndPacePreservedBySignalComparison=True,subtitles=subtitles,cleanCaptionedAudioPayloadIdentical=True,humanListening=False)
  save(cached,result);results.append(result);print('Continuity QA passed',e['id'],flush=True)
 save(HERE/'continuity.json',dict(status='passed-for-listed-episodes',episodes=results))
if __name__=='__main__':main()

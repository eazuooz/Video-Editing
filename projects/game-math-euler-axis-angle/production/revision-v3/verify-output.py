"""One hash-cached current-output integrity, audio and complete pixel contact pass."""
from pathlib import Path
import json,math,hashlib,subprocess,sys
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v3';Q=O/'qa';Q.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):
 p=Path(p)
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def run(cmd):return subprocess.run(cmd,cwd=R,capture_output=True,check=True).stdout
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def mapped(t,pauses):return t+sum(p['seconds'] for p in pauses if t>=p['rawAt'])
def db(v):return float(20*np.log10(max(float(v),1e-10)))
def measure(path):
 c=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],cwd=R,capture_output=True,check=True).stderr.decode(errors='replace')
 return json.loads(c[c.rfind('{'):c.rfind('}')+1])
def integrity(plan):
 results=[];pair=read(O/'pair-source.json');assert pair['inputs']['timelineSha256']==sha(P/'production/revision-v3/timeline.json'),'Final pair timeline mismatch'
 for kind in ['clean','captioned']:
  f=O/f'euler-{kind}.mp4';digest=sha(f);receipt=Q/(kind+'-integrity.json')
  assert pair['outputs'][kind]['sha256']==digest,'Final video differs from current pair receipt'
  if receipt.exists() and read(receipt).get('sha256')==digest:
   cached=read(receipt);assert cached['frames']==plan['totalFrames'] and cached['fps']==60 and cached['width']==1920 and cached['height']==1080 and int(cached['sampleRate'])==48000 and cached.get('channels')==2
   results.append(cached);continue
  info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
  assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',plan['totalFrames'])
  assert int(a['sample_rate'])==48000 and int(a['channels'])==2,'Final audio must be48kHzstereo'
  assert abs(float(a.get('duration',info['format']['duration']))-plan['totalFrames']/60)<.1,'Audio/video duration differs'
  run(['ffmpeg','-v','error','-xerror','-i',str(f),'-f','null','-'])
  pts=run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',str(f)]).decode().splitlines();times=[float(s.split(',')[0]) for s in pts if s.strip() and s.split(',')[0].strip()]
  assert len(times)==plan['totalFrames'] and abs(times[0])<1e-6 and all(abs(b-a-1/60)<.00004 for a,b in zip(times,times[1:]))
  adts=run(['ffmpeg','-v','error','-i',str(f),'-map','0:a','-c:a','copy','-f','adts','-'])
  r=dict(kind=kind,sha256=digest,bytes=f.stat().st_size,frames=len(times),width=1920,height=1080,fps=60,fullDecodePassed=True,ptsMonotonicAndUniform=True,aacSha256=hashlib.sha256(adts).hexdigest(),sampleRate=a['sample_rate'],channels=int(a['channels']),duration=float(info['format']['duration']));save(receipt,r);results.append(r)
 assert results[0]['aacSha256']==results[1]['aacSha256'];assert plan['actualFrames']*3==plan['explanationFrames']*2
 save(Q/'integrity.json',dict(outputs=results,bodyFrames=plan['bodyFrames'],actualFrames=plan['actualFrames'],explanationFrames=plan['explanationFrames'],ratioErrorFrames=0,sourceIntervalsUnique=plan['sourceIntervalsUnique'],sourceSpeed=plan['sourceSpeed'],noGameplayFreezeOrLoop=not plan['sourceFreezeOrLoop'],humanWholeListening='pending',actualMovingPixelsReview='pending'))
 return results
def audio(plan):
 inputs=dict(timelineSha256=sha(P/'production/revision-v3/timeline.json'),stemSha256=sha(O/'narration-stem.wav'),encodedSha256=sha(O/'euler-captioned.mp4'),audioBuildSha256=sha(O/'audio-build.json'))
 source_signatures=[]
 for s in plan['scenes']:
  voice_hash,asr_hash=sha(R/s['voice']),sha(R/s['asr']);assert voice_hash==s['voiceSha256'] and asr_hash==s['asrSha256'],'Source voice/ASR changed after measured mix'
  source_signatures.append(dict(scene=s['id'],voiceSha256=voice_hash,asrSha256=asr_hash))
 inputs['sourceScenes']=source_signatures
 previous=Q/'audio-continuity.json'
 if previous.exists() and (Q/'encoded-loudness.json').exists() and read(previous).get('inputs')==inputs:return
 for name,src in [('stem',O/'narration-stem.wav'),('encoded',O/'euler-captioned.mp4')]:
  dest=Q/(name+'-mono.wav');receipt=Q/(name+'-mono-source.json');sig=dict(sourceSha256=sha(src),rate=24000,channels=1,format='pcm_f32le')
  if not(dest.exists() and receipt.exists() and read(receipt)==sig):run(['ffmpeg','-v','error','-y','-i',str(src),'-vn','-ac','1','-ar','24000','-c:a','pcm_f32le',str(dest)]);save(receipt,sig)
 stem,sr=sf.read(Q/'stem-mono.wav',dtype='float32');encoded,_=sf.read(Q/'encoded-mono.wav',dtype='float32');windows=[];summaries=[]
 for s in plan['scenes']:
  raw,rate=sf.read(R/s['voice'],dtype='float32');assert rate==sr;mask=np.zeros(len(raw),dtype=bool);words=read(R/s['asr'])['words']
  for w in words:
   a,b=w['timestamp']
   if a is not None and b is not None:mask[max(0,round(a*sr)):min(len(raw),round(b*sr))]=True
  local=[];pauses=s['observationPauses']
  for a in range(0,len(raw)-round(sr*.4),round(sr*.1)):
   b=a+round(sr*.4);m=mask[a:b]
   if m.mean()<.3:continue
   # A raw window spanning an intentionally inserted observation pause is
   # not contiguous in the mix; analyze both adjacent sides separately.
   if any(a/sr<p['rawAt']<b/sr for p in pauses):continue
   time=s['voiceStart']+mapped(a/sr,pauses);origin=round(time*sr);x=raw[a:b][m];y=stem[origin:origin+b-a][m];z=encoded[origin:origin+b-a][m]
   xr=np.sqrt(np.mean(x*x));yr=np.sqrt(np.mean(y*y));zr=np.sqrt(np.mean(z*z))
   if db(yr)<-46:continue
   projection=float(np.sum(y*z)/max(np.sum(y*y),1e-10));row=dict(scene=s['id'],time=time,rawTime=a/sr,sourceDbfs=db(xr),stemDbfs=db(yr),finalMixDbfs=db(zr),stemMinusSourceDb=db(yr/xr),estimatedVoiceTransferDb=db(projection));windows.append(row);local.append(row)
  assert local,s['id'];summaries.append(dict(scene=s['id'],speechWindows=len(local),sourceMedianDbfs=float(np.median([r['sourceDbfs'] for r in local])),stemMedianDbfs=float(np.median([r['stemDbfs'] for r in local])),minimumEstimatedVoiceTransferDb=min(r['estimatedVoiceTransferDb'] for r in local)))
 flags=[r for r in windows if r['estimatedVoiceTransferDb']<-2.5];low=[]
 for r in windows:
  neighbors=[q['stemDbfs'] for q in windows if q['scene']==r['scene'] and .5<abs(q['time']-r['time'])<=3]
  if neighbors and r['stemDbfs']<float(np.median(neighbors))-6:low.append(dict(**r,neighborMedianDbfs=float(np.median(neighbors))))
 groups=[]
 for r in low:
  if groups and r['scene']==groups[-1][-1]['scene'] and r['time']-groups[-1][-1]['time']<.151:groups[-1].append(r)
  else:groups.append([r])
 sustained=[dict(scene=g[0]['scene'],start=g[0]['time'],end=g[-1]['time']+.4,samples=len(g),maximumDifferenceDb=max(r['neighborMedianDbfs']-r['stemDbfs'] for r in g),status='needs contextual review; may be natural prosody') for g in groups if len(g)>=5]
 joins=[dict(before=a['scene'],after=b['scene'],speechMedianDifferenceDb=b['stemMedianDbfs']-a['stemMedianDbfs']) for a,b in zip(summaries,summaries[1:])]
 stats=measure(O/'euler-captioned.mp4');save(Q/'encoded-loudness.json',stats);assert float(stats['input_tp'])<=-1.5,stats
 save(Q/'audio-continuity.json',dict(inputs=inputs,windowSeconds=.4,hopSeconds=.1,speechMask='current word timestamps mapped around intentional sentence-seam pauses',scenes=summaries,windows=windows,flaggedVoiceTransferWindows=flags,sustainedLocalDropCandidates=sustained,sceneJoins=joins,humanListening='pending; not inferred from ASR or loudness'))
def pixels(plan):
 layout=read(O/'caption-layout.json');sig=dict(videoSha256=sha(O/'euler-captioned.mp4'),layoutSha256=sha(O/'caption-layout.json'),timelineSha256=sha(P/'production/revision-v3/timeline.json'),placementSha256=sha(P/'production/local/revision-v2/unity-spatial-placement.json'),extractorSha256=sha(__file__))
 receipt=Q/'pixel-extraction.json'
 if receipt.exists() and read(receipt).get('inputs')==sig:return
 samples={12:['branding early'],108:['branding exit'],plan['totalFrames']-580:['membership enter'],plan['totalFrames']-300:['membership names'],plan['totalFrames']-18:['membership exit']}
 for c in layout['rows']:
  scene=next(s for s in plan['scenes'] if s['start']<=c['start']<s['start']+s['seconds'])
  if not scene.get('retainedRender'):samples.setdefault(round((c['start']+c['end'])*30),[]).append('cue'+str(c['cue']))
 for s in plan['scenes']:
  for f,label in [(s['startFrame']+8,'in'),(s['endFrame']-8,'out')]:samples.setdefault(f,[]).append(s['id']+label)
  if s['kind']=='explanation' and not s.get('retainedRender'):
   for i,t in enumerate(s['lineStarts']):samples.setdefault(min(s['endFrame']-1,s['startFrame']+round((t+.5)*60)),[]).append(s['id']+' visual'+str(i+1))
 for c in plan['cuts']:
  for f,label in [(c['globalStartFrame']+min(8,c['frames']//3),'in'),(c['globalStartFrame']+c['frames']-min(8,c['frames']//3),'out')]:samples.setdefault(f,[]).append(c['id']+label)
  if c.get('annotationWindowIndex') is not None:
   s=next(s for s in plan['scenes'] if s['id']==c['scene']);n=s['annotationWindow']['endFrame']
   for f in [1,n//2,n-1]:samples.setdefault(c['globalStartFrame']+f,[]).append(c['id']+' guide')
 # Retained17 source clips, local caption text/timing and renderer settings
 # are hash-checked; prior moving explanation evidence is reused. Current
 # source cuts, changed captions and all inter-scene joins are sampled here.
 annotations=read(P/'sources/annotation-plan-v3.json')
 for c in plan['cuts']:
  for w in annotations['windows']:
   if w['scene']!=c['scene'] or w['sourceId']!=c['sourceId']:continue
   a=max(w['sourceIn'],c['sourceStart']);b=min(w['sourceOutExclusive'],c['sourceEnd'])
   if b<=a:continue
   for t in [a+.1,(a+b)/2,b-.1]:
    if not a<=t<b:continue
    frame=c['globalStartFrame']+round((t-c['sourceStart'])*60)
    samples.setdefault(frame,[]).append(w['id']+' guide')
 rows=[dict(frame=f,time=f/60,labels=ls) for f,ls in sorted(samples.items())];save(Q/'pixel-sample-index.json',rows)
 def balanced(terms):
  if len(terms)==1:return terms[0]
  m=len(terms)//2;return '('+balanced(terms[:m])+'+'+balanced(terms[m:])+')'
 expression=balanced(['eq(n,'+str(r['frame'])+')' for r in rows]);run(['ffmpeg','-v','error','-i',str(O/'euler-captioned.mp4'),'-an','-vf',"select='"+expression+"'",'-fps_mode','vfr','-c:v','mjpeg','-threads','1','-q:v','3','-y',str(Q/'frame-%04d.jpg')])
 for page in range(math.ceil(len(rows)/8)):
  chunk=rows[page*8:(page+1)*8];sheet=Image.new('RGB',(1920,580*math.ceil(len(chunk)/2)),(22,22,22));draw=ImageDraw.Draw(sheet)
  for k,row in enumerate(chunk):
   im=Image.open(Q/f'frame-{page*8+k+1:04}.jpg').resize((960,540),Image.Resampling.LANCZOS);x=k%2*960;y=k//2*580;sheet.paste(im,(x,y));draw.text((x+5,y+544),f"{row['time']:.2f}s | "+' / '.join(row['labels'])[:100],fill='white')
  sheet.save(Q/f'contact-{page:02}.jpg')
 # Mobile inspection sheets preserve the actual375px video width, with the
 # final encoded captions. They are QA rasters and excluded from Git.
 mobile=[]
 for s in plan['scenes']:
  candidate=min(rows,key=lambda r:abs(r['time']-(s['start']+s['seconds']*.48)));index=rows.index(candidate)+1;mobile.append((s['id'],index))
 sheet=Image.new('RGB',(1500,240*math.ceil(len(mobile)/4)),(22,22,22));draw=ImageDraw.Draw(sheet)
 for i,(sid,n) in enumerate(mobile):
  im=Image.open(Q/f'frame-{n:04}.jpg').resize((375,211),Image.Resampling.LANCZOS);x=i%4*375;y=i//4*240;sheet.paste(im,(x,y));draw.text((x+5,y+214),sid,fill='white')
 sheet.save(Q/'mobile-all-scenes.jpg');save(receipt,dict(inputs=sig,samples=len(rows),sheets=math.ceil(len(rows)/8),nativeSampleSize=[1920,1080],contactSampleSize=[960,540],mobileVideoWidth=375,review='pending direct whole contact/movement review'))
def main():
 assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 plan=read(P/'production/revision-v3/timeline.json');stage=sys.argv[1] if len(sys.argv)>1 else 'all'
 for path,digest in plan['inputHashes'].items():assert sha(R/path)==digest,('Stale measured input',path)
 if stage in ['integrity','all']:integrity(plan)
 if stage in ['audio','all']:audio(plan)
 if stage in ['pixels','all']:pixels(plan)
 print('Current output checks prepared:',stage,'; direct pixel/listening statuses remain explicit')
if __name__=='__main__':main()

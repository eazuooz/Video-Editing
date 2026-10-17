"""One current-output integrity pass; direct pixel/listening review stays explicit."""
from pathlib import Path
import subprocess,json,hashlib,math
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4];P=R/'projects/avoid-game-comparisons';V=P/'production/reference-preserving-v2';O=P/'production/local/reference-preserving-v2/edit';Q=O/'qa';Q.mkdir(exist_ok=True)
def run(cmd):return subprocess.run(cmd,cwd=R,capture_output=True,check=True).stdout
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((V/'edit-plan.json').read_text(encoding='utf8'));layout=json.loads((O/'caption-layout.json').read_text(encoding='utf8'))
results=[]
for kind in ['clean','captioned']:
 f=O/f'avoid-game-comparisons-v2-{kind}.mp4';digest=sha(f);receipt=Q/(kind+'-integrity.json')
 if receipt.exists() and json.loads(receipt.read_text()).get('sha256')==digest:results.append(json.loads(receipt.read_text()));continue
 info=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));video=next(s for s in info['streams'] if s['codec_type']=='video');audio=next(s for s in info['streams'] if s['codec_type']=='audio')
 assert (video['width'],video['height'],video['r_frame_rate'],int(video['nb_frames']))==(1920,1080,'60/1',plan['totalFrames'])
 decoded=run(['ffmpeg','-v','error','-xerror','-i',str(f),'-f','null','-'])
 pts=run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',str(f)]).decode().splitlines();times=[float(s.split(',')[0]) for s in pts if s.strip() and s.split(',')[0].strip()]
 assert len(times)==plan['totalFrames'] and all(abs(b-a-1/60)<.00004 for a,b in zip(times,times[1:]))
 adts=run(['ffmpeg','-v','error','-i',str(f),'-map','0:a','-c:a','copy','-f','adts','-'])
 result={'kind':kind,'sha256':digest,'bytes':f.stat().st_size,'frames':len(times),'width':1920,'height':1080,'fps':60,'fullDecodePassed':True,'ptsMonotonicAndUniform':True,'aacSha256':hashlib.sha256(adts).hexdigest(),'sampleRate':audio['sample_rate'],'duration':float(info['format']['duration'])};receipt.write_text(json.dumps(result,indent=2)+'\n');results.append(result)
assert results[0]['aacSha256']==results[1]['aacSha256']
actual=sum(c['frames'] for c in plan['cuts'] if c['kind']=='independent-gameplay');assert abs(actual-plan['bodyFrames']*.6)<=1
# Voice continuity: compare the same speech-active interval across source,
# processed stem and final encoded mixture. Whole-file LUFS is not this check.
for name,src in [('stem',O/'narration-stem.wav'),('encoded',O/'avoid-game-comparisons-v2-captioned.mp4')]:
 dest=Q/(name+'-mono.wav')
 if not dest.exists():run(['ffmpeg','-v','error','-i',str(src),'-vn','-ac','1','-ar','24000','-c:a','pcm_f32le',str(dest)])
stem,sr=sf.read(Q/'stem-mono.wav',dtype='float32');encoded,_=sf.read(Q/'encoded-mono.wav',dtype='float32');N=R/'shared/output/narration/avoid-game-comparisons/reference-preserving-v2';windows=[];summaries=[]
db=lambda x:float(20*np.log10(max(float(x),1e-10)))
for scene in plan['scenes']:
 sid=scene['id'];raw,_=sf.read(N/'chunks'/f'{sid}-scene.wav',dtype='float32');words=json.loads((N/'asr'/f'{sid}.json').read_text(encoding='utf8'))['words'];mask=np.zeros(len(raw),dtype=bool)
 for w in words:
  a,b=w['timestamp']
  if a is not None and b is not None:mask[max(0,round(a*sr)):min(len(raw),round(b*sr))]=True
 origin=round(scene['voiceStart']*sr);local=[]
 for a in range(0,len(raw)-round(sr*.4),round(sr*.1)):
  b=a+round(sr*.4);m=mask[a:b]
  if m.mean()<.3:continue
  x=raw[a:b][m];y=stem[origin+a:origin+b][m];z=encoded[origin+a:origin+b][m]
  xr=float(np.sqrt(np.mean(x*x)));yr=float(np.sqrt(np.mean(y*y)));zr=float(np.sqrt(np.mean(z*z)))
  if db(yr)<-46:continue
  projection=float(np.dot(y,z)/max(np.dot(y,y),1e-10));row={'scene':sid,'time':scene['voiceStart']+a/sr,'sourceDbfs':db(xr),'stemDbfs':db(yr),'finalMixDbfs':db(zr),'stemMinusSourceDb':db(yr/xr),'estimatedVoiceTransferDb':db(projection)};windows.append(row);local.append(row)
 summaries.append({'scene':sid,'speechWindows':len(local),'sourceMedianDbfs':float(np.median([r['sourceDbfs'] for r in local])),'stemMedianDbfs':float(np.median([r['stemDbfs'] for r in local])),'minimumEstimatedVoiceTransferDb':min(r['estimatedVoiceTransferDb'] for r in local)})
flags=[r for r in windows if r['estimatedVoiceTransferDb']<-2.5]
audio={'windowSeconds':.4,'hopSeconds':.1,'speechMask':'current recognized word timestamps, not whole-file amplitude gate','scenes':summaries,'windows':windows,'flaggedVoiceTransferWindows':flags,'humanListening':'pending complete user review; not inferred from ASR or loudness'};(Q/'audio-continuity.json').write_text(json.dumps(audio,indent=2)+'\n')
# Every caption and every source/diagram cut receives a decoded final-frame
# contact view. Additional start/mid/end marker frames cover tracked highlights.
samples={}
for c in layout['rows']:
 f=round((c['start']+c['end'])/2*60);samples.setdefault(f,[]).append(f"KO/EN cue {c['cue']}")
for c in plan['cuts']:
 for f,label in [(c['startFrame']+min(15,c['frames']//3),'in'),(c['endFrame']-min(15,c['frames']//3),'out')]:samples.setdefault(f,[]).append(c['id']+' '+label)
 for m in c.get('marks',[]):
  for sourceTime in [m['from']+.08,(m['from']+m['to'])/2,m['to']-.08]:
   f=c['startFrame']+round((sourceTime-c['sourceStart'])*60)
   if c['startFrame']<=f<c['endFrame']:samples.setdefault(f,[]).append(c['id']+' '+m['label'])
rows=[{'frame':f,'time':f/60,'labels':labels} for f,labels in sorted(samples.items())];(Q/'pixel-sample-index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
selection='+'.join('eq(n,'+str(r['frame'])+')' for r in rows);vf="select='"+selection+"',scale=480:270:flags=lanczos"
run(['ffmpeg','-v','error','-i',str(O/'avoid-game-comparisons-v2-captioned.mp4'),'-vf',vf,'-fps_mode','vfr','-y',str(Q/'frame-%04d.jpg')])
for page in range(math.ceil(len(rows)/12)):
 chunk=rows[page*12:(page+1)*12];sheet=Image.new('RGB',(1440,310*math.ceil(len(chunk)/3)),(22,22,22));draw=ImageDraw.Draw(sheet)
 for k,row in enumerate(chunk):
  image=Image.open(Q/f'frame-{page*12+k+1:04}.jpg');x=k%3*480;y=k//3*310;sheet.paste(image,(x,y));draw.text((x+5,y+274),f"{row['time']:.2f}s | "+' / '.join(row['labels'])[:65],fill='white')
 sheet.save(Q/f'contact-{page:02}.jpg')
report={'outputs':results,'bodyFrames':plan['bodyFrames'],'actualFrames':actual,'explanationFrames':plan['bodyFrames']-actual,'ratioRoundingErrorFrames':actual-plan['bodyFrames']*.6,'noSourceLoopsOrSpeedChanges':all(c.get('playbackSpeed',1)==1 and not c.get('loop') for c in plan['cuts']),'captionPairs':len(layout['rows']),'pixelSamples':len(rows),'contactSheets':math.ceil(len(rows)/12),'actualPixelsReview':'pending direct review','fullAsrReview':'pending','humanWholeListening':'pending','platformMutation':False};(Q/'integrity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='outputs'}))

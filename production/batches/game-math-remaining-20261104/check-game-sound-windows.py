"""Verify the synchronized original game sound at each selected native window.

Lightweight CPU-only input inspection, not a listening or rights approval.
Silence, missing timestamps and insufficient native audio must remain visible.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,array,hashlib,json,math,shutil,subprocess

B=Path(__file__).resolve().parent;R=B.parents[2]
FF=shutil.which('ffmpeg');assert FF
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow']
sr=12000;cached={};allrows=[]
ap=argparse.ArgumentParser();ap.add_argument('--episode');args=ap.parse_args()
if args.episode:assert args.episode in c['itemIds'][1:]
for ep in read(B/'batch.json')['items'][1:]:
 if args.episode and ep['id']!=args.episode:continue
 p=R/'projects'/ep['slug'];assert p.name in c['projectSlugs']
 sources={s['id']:s for s in read(p/'planning/footage-audit.json')['sources']}
 cuts=[s['actualGamePart'] for s in read(p/'planning/scene-bindings.json')['scenes'] if s.get('actualGamePart')]
 rows=[]
 for g in cuts:
  s=sources[g['sourceId']];a=s.get('audio',{});sep=a.get('separateFullOriginalAudio') or a.get('separateOriginalAudio') or a.get('recoveredOriginalAudio')
  src=(R/(sep or s['file'])).resolve();assert src.is_relative_to(R) and src.is_file()
  start=g.get('fullOriginalAudioIn',g['sourceIn']) if sep else g['sourceIn'];duration=g['sourceOut']-g['sourceIn'];key=(str(src),start,duration)
  if key not in cached:
   raw=subprocess.check_output([FF,'-v','error','-nostdin','-threads','1','-ss',str(start),'-i',str(src),'-t',str(duration),'-map','0:a:0','-vn','-af','aresample=12000','-ac','1','-c:a','pcm_f32le','-f','f32le','pipe:1'],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   pcm=array.array('f');pcm.frombytes(raw);assert pcm
   peak=max(map(abs,pcm));rms=(sum(v*v for v in pcm)/len(pcm))**.5;w=sr//4
   win=[(sum(x*x for x in pcm[i:i+w])/len(pcm[i:i+w]))**.5 for i in range(0,len(pcm),w)]
   db=lambda x:round(20*math.log10(x),2) if x>0 else None
   cached[key]=dict(samples=len(pcm),sampleRate=sr,seconds=len(pcm)/sr,decodedWindowPcmSha256=hashlib.sha256(raw).hexdigest(),downmixedPeakDbfs=db(peak),downmixedRmsDbfs=db(rms),subMinus60DbWindows=sum(x<.001 for x in win),totalQuarterSecondWindows=len(win),decodeExit=0)
  v=cached[key]
  flags=[]
  if abs(v['seconds']-duration)>1/60:flags+=['audio-extent-needs-review']
  if v['downmixedRmsDbfs'] is None or v['downmixedRmsDbfs']< -55:flags+=['near-silent-window-needs-listening']
  rec=dict(episode=ep['id'],scene=g.get('sceneId',g.get('beat')),sourceId=s['id'],game=s['game'],soundFile=str(src.relative_to(R)),nativeVideoStart=g['sourceIn'],audioStart=start,seconds=duration,separateOriginalSound=bool(sep),flags=flags,**{'measurement':v})
  rows.append(rec);allrows.append(rec)
 report=dict(episode=ep['id'],checkedAt=datetime.now(timezone.utc).isoformat(),method='Actual original PCM from selected video or its recorded synchronized sidecar; 12kHz mono is for signal/extent QA only. The edit retains original sound.',windows=rows,actualListening=False,contentOrRightsInferred=False,addedMusic=False)
 (p/'planning/game-sound-window-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(allrows),'selected windows;',len(cached),'distinct sound intervals;',[(r['episode'],r['scene'],r['flags']) for r in allrows if r['flags']])

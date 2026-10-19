"""Build the voice-led edit and exact source-frame caches for this Short only."""
from pathlib import Path
import json, subprocess, hashlib, sys
P=Path(__file__).resolve().parents[1]; R=P.parents[1]; L=P/'production/local'
FF=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
def read(p): return json.loads(p.read_text(encoding='utf8'))
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 c=read(R/'shared/publishing/video-production-control.json')['shortsRecurringAuthorization']
 assert c['selectedShort']==P.name and c['latestSelection']['selectedRevision']=='zombie-quiet-v1'
 captions=read(P/'script/captions.json'); cues=captions['cues']; end=captions['durationSeconds']
 starts={i:min(x['start'] for x in cues if x['lineIndex']==i) for i in range(11)}
 # All source times below are relative to the downloaded, decoded FHD60 clip.
 game=lambda id,a,b,source,s:dict(id=id,start=a,end=b,kind='game',source=source,sourceStart=s,sourceEnd=round(s+b-a,8),rate=1)
 sections=[game('opening-combat',0,1.7,'l4d',20),game('opening-quiet',1.7,starts[2],'l4d',33),
  game('intensity-events',starts[2],starts[3],'l4d',22),
  dict(id='pacing',start=starts[3],end=starts[5],kind='diagram'),
  game('remaining-threats',starts[5],starts[6],'l4d',26.8),
  game('pz-quiet',starts[6],starts[7],'pz',3),
  dict(id='sound-migration',start=starts[7],end=starts[9],kind='diagram'),
  game('l4d-return',starts[9],cues[22]['start'],'l4d',39),
  game('pz-return',cues[22]['start'],end,'pz',7)]
 for a,b in zip(sections,sections[1:]): assert abs(a['end']-b['start'])<1e-7
 phases=[dict(id='baseline',start=starts[3],end=starts[3]+.6),
  dict(id='compare',start=starts[3]+.6,end=cues[7]['start']),
  dict(id='gap',start=cues[7]['start'],end=starts[4]),
  dict(id='result',start=starts[4],end=starts[5])]
 sound=[dict(id='before',start=starts[7],end=starts[7]+.55),
  dict(id='sound',start=starts[7]+.55,end=cues[17]['start']),
  dict(id='move',start=cues[17]['start'],end=starts[8]+.7),
  dict(id='result',start=starts[8]+.7,end=starts[9])]
 reactions=[dict(start=1.75,end=3.1,kind='puzzled'),dict(start=4.6,end=6.1,kind='relief'),
  dict(start=starts[6]+.2,end=starts[6]+1.8,kind='puzzled'),
  dict(start=starts[10]+.1,end=end-.1,kind='realize')]
 timing=dict(fps=60,frames=captions['frames'],durationSeconds=end,voiceOffsetSeconds=.2,
  sourceTimeBasis='clip-relative',sections=sections,pacingPhases=phases,soundPhases=sound,reactions=reactions,
  sourceFiles={'l4d':'l4d1-church-65-120.mp4','pz':'pz-neighborhood-175-210.mp4'},
  actualFrames=sum(round((s['end']-s['start'])*60) for s in sections if s['kind']=='game'),
  note='Shorts content-led duration/ratio; no slow motion, loops or fake internal game telemetry')
 target=L/'visual-timing.json'
 if target.exists(): assert read(target)==timing,'Preserve previous timing until reviewed'
 else: save(target,timing)
 canonical=P/'production/visual-timing.json'
 if canonical.exists(): assert read(canonical)==timing,'Canonical timing differs'
 else: save(canonical,timing)
 if '--frames' not in sys.argv: print(json.dumps(timing,ensure_ascii=False));return
 for s in sections:
  if s['kind']!='game':continue
  dest=L/'frames'/s['id'];dest.mkdir(parents=True,exist_ok=True);n=round((s['end']-s['start'])*60)
  existing=list(dest.glob('frame-*.jpg'))
  if len(existing)==n:continue
  assert not existing,'Inspect incomplete frame cache before restarting '+s['id']
  subprocess.run([str(FF),'-v','error','-n','-ss',str(s['sourceStart']),'-i',str(L/'footage'/timing['sourceFiles'][s['source']]),
   '-an','-vf','crop=1280:960:320:60,scale=1000:750','-frames:v',str(n),'-fps_mode','passthrough','-q:v','2','-start_number','0',str(dest/'frame-%04d.jpg')],check=True)
  assert len(list(dest.glob('frame-*.jpg')))==n
  print(s['id'],n,flush=True)
if __name__=='__main__':main()

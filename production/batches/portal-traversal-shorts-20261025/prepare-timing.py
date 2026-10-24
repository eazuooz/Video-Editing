from pathlib import Path
import json,subprocess,sys,hashlib
R=Path(__file__).resolve().parents[3]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for slug in sys.argv[1:]:
 p=R/'projects'/slug;c=read(p/'script/captions.json');q={a['id']:a for a in c['cues']};plan=read(p/'production/section-plan.json');starts=[0]+[q[s['firstCue']]['startFrame'] for s in plan[1:]]+[c['frames']];sections=[];foot=read(p/'sources/selected-footage.json')
 for i,s in enumerate(plan):
  d=dict(s,kind='game' if s['id'].startswith('game') else 'implementation',startFrame=starts[i],endFrame=starts[i+1],start=starts[i]/60,end=starts[i+1]/60,hold=0)
  if d['kind']=='game':
   d.update(source='gameplay',sourceStart=foot['plannedIntroStart'] if d['id']=='game' else foot['plannedConfirmationStart'],rate=1,nativeAudioAdopted=False);d['sourceEnd']=d['sourceStart']+d['end']-d['start']
  sections.append(d)
 reactions=[{'start':sections[1]['start']+.4,'end':sections[1]['start']+2.2,'kind':'realize'},{'start':sections[-1]['end']-1.8,'end':sections[-1]['end']-.1,'kind':'understood'}]
 t={'revision':'portal-traversal-v1','frames':c['frames'],'durationSeconds':c['durationSeconds'],'voiceDurationSeconds':c['voiceDurationSeconds'],'sections':sections,'sources':{'gameplay':{'path':foot['localPath'],'sourceSHA256':foot['sha256'],'originalOffsetSeconds':450,'nativeAudioAdopted':False}},'reactions':reactions,'cueStarts':{k:v['start'] for k,v in q.items()},'captureMode':'full-v1'}
 for dest in [p/'production/visual-timing.json',p/'production/local/visual-timing.json',p/'production/local/audio-v1/visual-timing.json']:save(dest,t)
 project=read(p/'project.json');project['durationSeconds']=c['durationSeconds'];project['video']['durationSeconds']=c['durationSeconds'];save(p/'project.json',project)
 for s in sections:
  if s['kind']!='game':continue
  out=p/'production/local/game-frames'/s['id'];out.mkdir(parents=True,exist_ok=True)
  if not (out/'00000.jpg').exists():subprocess.run(['ffmpeg','-v','error','-n','-ss',str(s['sourceStart']),'-i',str(R/foot['localPath']),'-frames:v',str(s['endFrame']-s['startFrame']),'-vf','fps=60','-q:v','3','-threads','2','-start_number','0',str(out/'%05d.jpg')],check=True)
 print(slug,c['durationSeconds'])

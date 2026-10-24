"""Build cue-led finite timelines after separately reviewed ASR spelling variants."""
import json,hashlib,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
slugs=read(B/'batch.json')['authorization']['slugs']
starts={slugs[0]:222,slugs[1]:38,slugs[2]:10,slugs[3]:34,slugs[4]:92}
ALIASES={slugs[0]:{'타이탄폴2':'타이탄폴투','10m':'십미터','맵사이에높이':'맵사이의높이'}}
def prepare(slug):
 p=R/'projects'/slug;L=p/('production/local/audio-v2' if (p/'production/local/audio-v2/voice/narration.wav').exists() else 'production/local/audio-v1');voice=L/'voice/narration.wav';asr=next(L.glob('asr-voice-*.json'))
 if slug in ALIASES:
  save(L/'asr-reconciliation.json',{'voiceSha256':sha(voice),'asrSha256':sha(asr),'aliases':ALIASES[slug], 'basis':'Number/name orthography and Korean 의/에 contextual homophone normalization only; no words added or removed. Raw ASR retained. Human pronunciation review pending.'})
 clauses=read(p/'script/clauses.json')
 if not (p/'script/captions.json').exists():
  for c in clauses['clauses']:
   c['ko']=c['ko'].replace('타이탄폴 투','타이탄폴 2').replace('기어스 오브 워 포','기어스 오브 워 4').replace('십 미터','10m').replace('두 미터','2m').replace('여섯 미터','6m')
   for word,role in [('위아래','result'),('순간이동','term'),('강제 원근','term'),('상승기류','term'),('관성화','term'),('스텐실 버퍼','term'),('재귀 렌더링','term'),('세 배','result')]:
    if c['ko'].count(word)==1:c['emphasis']={'text':word,'role':role};break
  save(p/'script/clauses.json',clauses)
 subprocess.run([str(R/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(p/'production/time-captions.py')],check=True)
 c=read(p/'script/captions.json');q={x['id']:x for x in c['cues']};plan=read(p/'production/section-plan.json')
 frames=[0]+[q[s['firstCue']]['startFrame'] for s in plan[1:]]+[c['frames']]
 sections=[]
 for i,s in enumerate(plan):
  d=dict(s,kind='game' if s['id'].startswith('game') else 'implementation',startFrame=frames[i],endFrame=frames[i+1],start=frames[i]/60,end=frames[i+1]/60,hold=0)
  if d['kind']=='game':d.update(source='gameplay',sourceStart=starts[slug] if s['id']=='game' else 229 if slug==slugs[0] else 78.5,rate=1,nativeAudioAdopted=False);d['sourceEnd']=d['sourceStart']+d['end']-d['start']
  sections.append(d)
 source=p/'production/local/gameplay.mp4';info=read(p/'sources/selected-footage.json')
 reactions=[{'start':sections[1]['start']+.5,'end':min(sections[1]['end'],sections[1]['start']+2.3),'kind':'realize'},{'start':sections[-1]['end']-2.0,'end':sections[-1]['end']-.1,'kind':'understood'}]
 d={'revision':'distinctive-v1','frames':c['frames'],'durationSeconds':c['durationSeconds'],'voiceDurationSeconds':c['voiceDurationSeconds'],'sections':sections,'sources':{'gameplay':{'path':source.relative_to(R).as_posix(),'sourceSHA256':sha(source),'originalOffsetSeconds':0,'nativeAudioAdopted':False}},'reactions':reactions,'cueStarts':{k:v['start'] for k,v in q.items()},'captureMode':'full-v1'}
 for dest in [p/'production/visual-timing.json',p/'production/local/visual-timing.json',L/'visual-timing.json']:save(dest,d)
 project=read(p/'project.json');project['durationSeconds']=c['durationSeconds'];project['video']['durationSeconds']=c['durationSeconds'];save(p/'project.json',project)
 for s in sections:
  if s['kind']!='game':continue
  out=p/'production/local/game-frames'/s['id'];out.mkdir(parents=True,exist_ok=True)
  if not (out/'00000.jpg').exists():
   subprocess.run(['ffmpeg','-v','error','-n','-ss',str(s['sourceStart']),'-i',str(source),'-frames:v',str(s['endFrame']-s['startFrame']),'-vf','fps=60','-q:v','3','-threads','2','-start_number','0',str(out/'%05d.jpg')],check=True)
 print(slug,c['durationSeconds'],'seconds',flush=True)
if __name__=='__main__':
 for slug in sys.argv[1:]:prepare(slug)

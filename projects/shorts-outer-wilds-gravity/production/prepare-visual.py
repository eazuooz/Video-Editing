"""Compile narration-aligned visual sections; never invent speech timings."""
from pathlib import Path
import json,subprocess,hashlib,sys
P=Path(__file__).resolve().parents[1]
# The script itself remains in D:; only local media resolves through the C: junction.
R=P.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def run(a):subprocess.run(a,check=True)
def main():
 auth=read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations']['explicit-ten-distinctive-shorts-20261025']
 assert auth['status']=='active' and P.name in auth['slugs'] and auth['fullProductionAuthorized']
 c=read(P/'script/captions.json');assert c['timingInputs']['voiceSha256'],'Actual voice timing required'
 starts=[0]+[min(q['startFrame'] for q in c['cues'] if q['lineIndex']==i) for i in range(1,7)]+[c['frames']]
 topic='viewfinder' if 'viewfinder' in P.name else 'gravity'
 sections=[]
 for i in range(7):
  a,b=starts[i],starts[i+1]
  if i==0:
   span=min(b-a,324 if topic=='viewfinder' else 330)
   sections.append({'id':'open','paragraph':i,'kind':'game','startFrame':a,'endFrame':a+span,'sourceStart':9.0 if topic=='viewfinder' else 41.5})
   if a+span<b:sections.append({'id':'opening-question','paragraph':i,'kind':'implementation','startFrame':a+span,'endFrame':b})
  elif i==6:
   span=min(b-a,216 if topic=='viewfinder' else 270)
   sections.append({'id':'confirm','paragraph':i,'kind':'game','startFrame':a,'endFrame':a+span,'sourceStart':33.2 if topic=='viewfinder' else 37.0})
   if a+span<b:sections.append({'id':'close','paragraph':i,'kind':'implementation','startFrame':a+span,'endFrame':b})
  else:sections.append({'id':'p'+str(i+1),'paragraph':i,'kind':'diagram' if topic=='gravity' and i in [1,2,3] else 'implementation','startFrame':a,'endFrame':b})
 for s in sections:
  s.update(start=s['startFrame']/60,end=s['endFrame']/60)
  if s['kind']=='game':s.update(source='official-gameplay',nativeAudioAdopted=False,sourceEnd=s['sourceStart']+(s['endFrame']-s['startFrame'])/60,rate=1)
 phases=[]
 for frame in range(c['frames']):
  i=next(i for i in range(7) if starts[i]<=frame<starts[i+1]);u=(frame-starts[i])/(starts[i+1]-starts[i])
  phase=[0,.08,.15+.30*u,.45+.15*u,.60+.30*u,.90,.95][i] if topic=='viewfinder' else (u if i==4 else 0 if i<4 else 1)
  phases.append(phase)
 save(P/'production/local/native-phase-plan.json',{'phases':phases,'voiceSha256':c['timingInputs']['voiceSha256']})
 if '--plan-only' in sys.argv:
  print(json.dumps({'slug':P.name,'frames':len(phases),'next':'CPU/WARP capture using -lessonPhaseFile and -lessonFrames'}));return
 media=P/'production/local'/('viewfinder-gameplay-4k.mp4' if topic=='viewfinder' else 'outer-wilds-reveal.mp4')
 for s in sections:
  if s['kind']!='game':continue
  folder=P/'production/local/game-frames-final'/s['id'];folder.mkdir(parents=True,exist_ok=True)
  if not (folder/'00000.jpg').exists():run(['ffmpeg','-v','error','-n','-ss',str(s['sourceStart']),'-i',str(media),'-an','-vf','fps=60,scale=1920:1080:flags=lanczos','-frames:v',str(s['endFrame']-s['startFrame']),'-q:v','2','-threads','2','-start_number','0',str(folder/'%05d.jpg')])
  assert len(list(folder.glob('*.jpg')))==s['endFrame']-s['startFrame']
 native=read(P/'production/local/unity-capture/success.json');assert native['frames']==c['frames'],'Native capture must use the narration phase plan'
 d={'revision':'distinctive-ten-v1','status':'voice-aligned','frames':c['frames'],'durationSeconds':c['durationSeconds'],'sections':sections,'paragraphStarts':starts,'nativeFrames':native['frames'],'nativeFolder':'unity-capture','nativeTimelineAligned':True,'voiceSha256':c['timingInputs']['voiceSha256'],'topic':topic,'sourceAudioAdopted':False,'nativeAudioAdopted':False,'sources':{'official-gameplay':{'path':str(media.relative_to(R)).replace('\\','/'),'sourceSHA256':read(P/'sources/selected-footage.json')['sources'][0]['sha256'],'nativeAudioAdopted':False}},'gameFramesFolder':'game-frames-final'}
 save(P/'production/visual-timing.json',d);save(P/'production/local/visual-timing.json',d)
 print(json.dumps({'slug':P.name,'frames':c['frames'],'sections':len(sections)}))
if __name__=='__main__':main()

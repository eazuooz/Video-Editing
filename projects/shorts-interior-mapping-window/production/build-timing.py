"""Current speech cues drive every explanatory change, without time compression."""
from audio_revision import P,R,L,REVISION,read,guard
import json,hashlib,subprocess
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
guard();c=read(P/'script/captions.json');q={x['id']:x for x in c['cues']}
starts=[('game',0),('hero',q['p2-1']['start']),('plane',q['p3-1']['start']),('hero',q['p3-3']['start']),('pixelIntro',q['p4-0']['start']),('ray',q['p4-1']['start']),('room',q['p4-3']['start']),('sample',q['p5-1']['start']),('move',q['p6-1']['start']),('compare',q['p6-3']['start']),('pixels',q['p7-1']['start']),('close',q['p8-1']['start'])]
frames=[round(t*60) for _,t in starts]+[c['frames']]
sections=[{'id':id,'kind':'game' if id=='game' else 'implementation','startFrame':frames[i],'endFrame':frames[i+1],'start':frames[i]/60,'end':frames[i+1]/60,'hold':0} for i,(id,t) in enumerate(starts)]
source=P/'production/local/research/simcity-city.mp4'
# A continuous inspected source interval, at native speed, no source soundtrack.
game=sections[0];assert game['end']<=8,'Review a longer source interval before adoption'
game.update(source='simcity',sourceStart=70,sourceEnd=70+game['end'],rate=1,nativeAudioAdopted=False)
d={'revision':REVISION,'frames':c['frames'],'durationSeconds':c['durationSeconds'],'voiceDurationSeconds':c['voiceDurationSeconds'],'sections':sections,'sources':{'simcity':{'path':source.relative_to(R).as_posix(),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'originalOffsetSeconds':0,'nativeAudioAdopted':False}},'reactions':[{'start':q['p2-3']['start'],'end':min(q['p2-3']['end'],q['p2-3']['start']+1.8),'kind':'realize'},{'start':q['p8-5']['start'],'end':c['durationSeconds'],'kind':'understood'}],'cueStarts':{k:v['start'] for k,v in q.items()}}
for p in [P/'production/visual-timing.json',P/'production/local/visual-timing.json',L/'visual-timing.json']:save(p,d)
project=read(P/'project.json');project['durationSeconds']=c['durationSeconds'];project['video']['durationSeconds']=c['durationSeconds'];save(P/'project.json',project)
out=P/'production/local/game-frames';out.mkdir(exist_ok=True)
if not (out/'00000.jpg').exists():
 subprocess.run(['ffmpeg','-v','error','-n','-ss','70','-i',str(source),'-t',str(game['end']),'-vf','crop=1920:810:0:134,fps=60','-q:v','3','-threads','2','-start_number','0',str(out/'%05d.jpg')],check=True)
print('Timeline',c['durationSeconds'],'seconds; actual game',game['end'],'seconds')

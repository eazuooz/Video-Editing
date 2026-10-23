from pathlib import Path
import json,math,hashlib
from audio_revision import P,R,L,REVISION,read,guard
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
guard();c=read(P/'script/captions.json');print('caption keys',list(c))
q={x['id']:x for x in c['cues']}
starts=[('hero',0),('uniform',q['p2-1']['start']),('arrows',q['p2-3']['start']),('map',q['p3-1']['start']),('decode',q['p3-4']['start']),('flow',q['p4-1']['start']),('stretch',q['p5-1']['start']),('reset',q['p5-2']['start']),('blend',q['p5-3']['start']),('move',q['p6-1']['start']),('update',q['p6-2']['start']),('close',q['p6-3']['start'])]
frames=[round(t*60) for _,t in starts]+[c['frames']]
sections=[{'id':id,'kind':'implementation','startFrame':frames[i],'endFrame':frames[i+1],'start':frames[i]/60,'end':frames[i+1]/60,'hold':0} for i,(id,_) in enumerate(starts)]
d={'revision':REVISION,'frames':c['frames'],'durationSeconds':c['durationSeconds'],'voiceDurationSeconds':c['voiceDurationSeconds'],'sections':sections,'sources':{},'reactions':[{'start':q['p1-3']['start'],'end':min(q['p1-3']['end'],q['p1-3']['start']+1.5),'kind':'realize'},{'start':q['p6-4']['start'],'end':c['durationSeconds'],'kind':'understood'}],'cueStarts':{k:v['start'] for k,v in q.items()}}
save(P/'production/visual-timing.json',d);save(P/'production/local/visual-timing.json',d)
out=P/'production/local/audio/visual-timing.json';save(out,d)
print('Timeline',c['frames'],c['durationSeconds'])

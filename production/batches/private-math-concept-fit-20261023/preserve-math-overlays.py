"""Retain prior header/spacing repairs only on byte-reused mathematical scenes."""
from common import *
def seconds(value):
 h,m,s=value.split(':');return int(h)*3600+int(m)*60+float(s)
def stamp(t):
 n=round(t*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
def prepare(project):
 p=R/'projects'/project;h=p/'production/concept-fit-v2';o=p/'production/local/concept-fit-v2'
 old=read(p/'production/timeline.json');new=read(h/'timeline.json');render=read(h/'render-progress.json');assembly=read(p/'production/private-polish-v1/assembly.json')
 kept={s['id']:s for s in new['scenes'] if render['scenes'][s['id']]['origin']=='unchanged approved math clip'}
 old_byid={s['id']:s for s in old['scenes']};records=[];filters=[]
 for key,field,hashfield in [('compositionPolish','globalAss','globalAssSha256'),('supplementSpacing','ass','assSha256')]:
  info=assembly.get(key)
  if not info:continue
  source=R/info[field];assert sha(source)==info[hashfield]
  lines=[];events=[]
  for line in source.read_text(encoding='utf-8-sig').splitlines():
   if not line.startswith('Dialogue:'):lines.append(line);continue
   parts=line.split(',',9);a,b=seconds(parts[1]),seconds(parts[2])
   candidates=[sid for sid in kept if a>=old_byid[sid]['start']-.011 and b<=old_byid[sid]['start']+old_byid[sid]['seconds']+.011]
   if not candidates:continue
   assert len(candidates)==1
   sid=candidates[0];prior=old_byid[sid];current=kept[sid];assert prior['frames']==current['frames']
   delta=current['start']-prior['start'];parts[1]=stamp(a+delta);parts[2]=stamp(b+delta)
   lines.append(','.join(parts));events.append(dict(scene=sid,before=[a,b],after=[a+delta,b+delta]))
  if events:
   target=o/f'preserved-{key}.ass';target.write_text('\n'.join(lines)+'\n',encoding='utf8')
   filters.append('ass='+target.name);records.append(dict(source=rel(source),sourceSha256=info[hashfield],output=rel(target),sha256=sha(target),events=events))
 save(h/'preserved-math-overlays.json',dict(checkedAt=now(),policy='Only original mathematical scene repairs retimed; replaced game guides excluded',records=records))
 return ','.join(filters)

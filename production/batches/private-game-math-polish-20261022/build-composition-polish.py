"""Apply inspected overlay/header repairs in one final encode, preserving clips."""
import sys
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();assert e.id in ['M05','M06']
polish=read(e.H/'annotation-polish.json');events=[];inputs={};header=None
def sec(t):
 h,m,s=t.split(':');return int(h)*3600+int(m)*60+float(s)
def stamp(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'
for s in e.T['scenes']:
 sid=s['id'];a=s['start'];z=a+s['seconds']
 if sid in polish['scenes']:
  p=polish['scenes'][sid];ass=R/p['ass'];assert sha(ass)==p['sha256']
  source=ass.read_text(encoding='utf8');head,body=source.split('[Events]',1)
  if header is None:header=head
  else:assert header==head,'Overlay styles must be identical before merging'
  for line in body.splitlines():
   if not line.startswith('Dialogue:'):continue
   fields=line.split(',',9);fields[1]=stamp(a+sec(fields[1]));fields[2]=stamp(min(z,a+sec(fields[2])))
   events.append(','.join(fields))
  raw=e.O/f'gameplay/{sid}-raw.mp4';e.verify(raw,s['frames'])
  inputs[sid]={'path':rel(raw),'sha256':sha(raw),'reason':'Use original clean game cut; revised guide is composed once at final encode','overlaySha256':p['sha256']}
 if s['classification']=='explanation' and sid.isdigit():
  # The native original divider crosses the convention subtitle. Redraw only
  # that static header strip, keeping the exact wording and diagram untouched.
  shape=r'{\an7\pos(0,0)\p1}m 70 155 l 1850 155 1850 225 70 225{\p0}'
  events.append(f'Dialogue: 5,{stamp(a)},{stamp(z)},RepairShape,,0,0,0,,{shape}')
  text=r'{\an7\pos(80,165)}게임수학 Part 2 / 3D 회전 3편 · 오른손 / 열벡터 / Hamilton / wxyz'
  events.append(f'Dialogue: 6,{stamp(a)},{stamp(z)},RepairText,,0,0,0,,{text}')
  line=r'{\an7\pos(0,0)\c&HDDDDDD&\p1}m 80 230 l 1837 230 1837 232 80 232{\p0}'
  events.append(f'Dialogue: 6,{stamp(a)},{stamp(z)},RepairShape,,0,0,0,,{line}')
assert header
if (e.H/'ui-clearance.json').exists():
 clearance=read(e.H/'ui-clearance.json')
 for sid,p in clearance['inputs'].items():
  assert sid not in inputs and sha(R/p['path'])==p['sha256']
  inputs[sid]=p
header+='Style: RepairShape,Malgun Gothic,40,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1\nStyle: RepairText,Malgun Gothic,40,&H00777777,&H00777777,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1\n'
target=e.O/'composition-polish.ass';target.write_text(header+'\n[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n'+'\n'.join(events)+'\n',encoding='utf8')
save(e.H/'composition-polish.json',{'timelineSha256':sha(e.P/'production/timeline.json'),'globalAss':rel(target),'globalAssSha256':sha(target),'inputs':inputs,'headerRepair':'Only numeric quaternion scenes: preserve exact convention subtitle, move crossing divider below subtitle','changes':'Current observed guide placement, larger labels, unchanged underlying action and all speech/cue timing','internalVisualQa':'pending'})
print(e.id,'one-pass composition repair prepared; final pixels pending',flush=True)

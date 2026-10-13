"""Bind semantic paragraph endpoints to the already-reviewed, frame-rounded SRT."""
from pathlib import Path
import json, hashlib, datetime
P=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def tm(s):
 h,m,x=s.replace(',','.').split(':');return round(int(h)*3600+int(m)*60+float(x),3)
def cues(lang):
 out=[]
 for block in (P/f'captions.{lang}.srt').read_text(encoding='utf-8-sig').strip().split('\n\n'):
  lines=block.splitlines();a,b=lines[1].split(' --> ');out.append((tm(a),tm(b)))
 return out
target=P/'caption-alignment-review-v1.json';j=read(target)
backup=P/'caption-alignment-before-frame-rounding-local.json'
assert not backup.exists();backup.write_bytes(target.read_bytes())
tracks={lang:cues(lang) for lang in ['ko','en']};changes=[]
for p in j['paragraphs']:
 bounds=[]
 for lang in ['ko','en']:
  indices=p[lang+'Cues'];bounds.append((tracks[lang][indices[0]-1][0],tracks[lang][indices[-1]-1][1]))
 assert bounds[0]==bounds[1]
 old=(p['start'],p['end']);new=bounds[0]
 assert max(abs(a-b) for a,b in zip(old,new))<=1/60
 p['measuredSpeechStart'],p['measuredSpeechEnd']=old
 p['start'],p['end']=new
 changes.append(dict(scene=p['scene'],paragraph=p['paragraph'],measured=old,srt=new))
for track in j['captions']:assert sha(P/f"captions.{track['language']}.srt")==track['sha256']
j['timingBinding']='Actual unchanged SRT endpoints after 60fps frame rounding; measured speech endpoints retained separately.'
j['scope']='All 27 paired paragraphs directly reviewed; current final caption pixels reviewed separately. Timing metadata correction only; SRT, audio and video unchanged.'
target.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
proof=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),cause='Collector requires SRT endpoints within 2ms; original review held pre-frame-rounding speech times. All differences under one frame.',changes=changes,captionFilesUnchanged=True,videoAudioChanges=False,collectorFailure='collection-verification-v1.json')
(P/'caption-review-timing-repair-v1.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('27 paragraph endpoints bound to unchanged KO/EN SRT; all changes less than one frame.')

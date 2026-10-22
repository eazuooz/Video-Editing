"""Prove cached ASR differs only by WAV PEAK write timestamp, not audio."""
from common import *
import datetime,struct
P=R/'projects/game-math-quaternion-foundations-v3';H=P/'production/concept-fit-v2';A=P/'production/local/concept-fit-v2/audio'
report=read(H/'changed-scene-asr-review.json');T=read(H/'timeline.json');by={s['id']:s for s in T['scenes']}
stamp=int(datetime.datetime.fromisoformat(read(A/'asr-execution.json')['startedAt']).timestamp());proof=[]
for row in report['scenes']:
 s=by[row['scene']];p=A/'asr'/f'{s["id"]}.json';c=read(p);data=bytearray((R/s['voice']).read_bytes());old=c['audioSha256'];current=sha(R/s['voice'])
 assert current==s['voiceSha256']
 if current==old:continue
 assert data[:4]==b'RIFF' and data[8:12]==b'WAVE';at=12;peak=None
 while at+8<=len(data):
  tag=bytes(data[at:at+4]);n=struct.unpack_from('<I',data,at+4)[0]
  if tag==b'PEAK':peak=at+12;break
  at+=8+n+(n%2)
 assert peak is not None
 matched=None;new_time=struct.unpack_from('<I',data,peak)[0]
 for candidate in range(stamp,stamp-61,-1):
  struct.pack_into('<I',data,peak,candidate)
  if hashlib.sha256(data).hexdigest()==old:matched=candidate;break
 assert matched is not None,f'Cannot prove header-only difference for {s["id"]}'
 evidence=dict(scene=s['id'],oldSha256=old,newSha256=current,onlyChangedBytes=[peak,peak+4],field='RIFF PEAK timestamp',oldTimestamp=matched,newTimestamp=new_time,proof='Restoring only these4 header bytes reproduces the exact ASR input SHA256; all remaining bytes including PCM are identical')
 c['headerOnlyRebinding']=evidence;c['audioSha256']=current;save(p,c);row['audioSha256']=current;row['headerOnlyRebinding']=evidence;proof.append(evidence)
save(H/'changed-scene-asr-review.json',report);save(H/'asr-header-rebinding.json',dict(checkedAt=now(),changes=proof,audioSamplesChanged=False))
print('ASR input identity verified:',len(proof),'timestamp-only differences')

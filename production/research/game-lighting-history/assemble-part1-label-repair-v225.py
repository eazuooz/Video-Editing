"""Byte-identical selected speech excerpts plus incomplete-frame silence."""
from pathlib import Path
import hashlib,json,wave,datetime
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'production/research/game-lighting-history/local/part1-label-repair-v225'
plan=json.loads((BASE/'plan.json').read_text('utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
target=ROOT/plan['jobs'][0]['audio']['path']
if target.exists():raise RuntimeError('Preserve completed assembly')
parts=[];ranges=[];offset=0
for s in plan['scenes']:
 p=ROOT/s['source']['path']
 if sha(p)!=s['source']['sha256']:raise RuntimeError('Changed take')
 a,z=s['sourceSampleRange']
 with wave.open(str(p),'rb') as w:
  if (w.getnchannels(),w.getsampwidth(),w.getframerate())!=(1,2,24000):raise RuntimeError('Unexpected PCM')
  w.setpos(a);raw=w.readframes(z-a)
 if len(raw)!=s['sourceSamples']*2 or s['silentPaddingSamples']>=400:raise RuntimeError('Bad excerpt or padding')
 parts += [raw,bytes(s['silentPaddingSamples']*2)]
 ranges.append(dict(id=s['id'],startSample=offset,endSample=offset+s['sourceSamples'],source=s['source'],sourceSampleRange=[a,z],pcm16Sha256=hashlib.sha256(raw).hexdigest(),silentPaddingSamples=s['silentPaddingSamples']))
 offset+=s['frames']*400
target.parent.mkdir(parents=True,exist_ok=True)
with wave.open(str(target),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b''.join(parts))
with wave.open(str(target),'rb') as w:
 data=w.readframes(w.getnframes())
 if w.getnframes()!=offset:raise RuntimeError('Wrong total')
for r in ranges:
 if hashlib.sha256(data[r['startSample']*2:r['endSample']*2]).hexdigest()!=r['pcm16Sha256']:raise RuntimeError('PCM changed')
r=dict(assembledAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),path=target.relative_to(ROOT).as_posix(),sha256=sha(target),samples=offset,frames=offset//400,ranges=ranges,allSelectedPcm16ByteIdentical=True,sourceAudio=0,bgm=0,finalMix=False,rendered=False)
(BASE/'audio-assembly-v225.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(frames=offset//400,excerpts=len(ranges),pcmByteIdentical=True)))

"""Copy three selected PCM16 takes losslessly; pad only incomplete video frames."""
from pathlib import Path
import hashlib,json,os,wave,datetime
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'production/research/game-lighting-history/local/guided-focus-label-v140'
plan=json.loads((BASE/'plan.json').read_text('utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
target=ROOT/plan['jobs'][0]['audio']['path']
if target.exists():raise RuntimeError('Preserve completed assembly')
parts=[];ranges=[];offset=0
for s in plan['scenes']:
 p=ROOT/s['source']['path']
 if sha(p)!=s['source']['sha256']:raise RuntimeError('Selected take changed')
 with wave.open(str(p),'rb') as w:
  if (w.getnchannels(),w.getsampwidth(),w.getframerate())!=(1,2,24000):raise RuntimeError('Unexpected PCM format')
  raw=w.readframes(w.getnframes())
 if len(raw)!=s['sourceSamples']*2:raise RuntimeError('Truncated take')
 parts.append(raw);parts.append(bytes(s['silentPaddingSamples']*2))
 ranges.append(dict(id=s['id'],startSample=offset,endSample=offset+s['sourceSamples'],source=s['source'],pcm16Sha256=hashlib.sha256(raw).hexdigest(),silentPaddingSamples=s['silentPaddingSamples']))
 offset+=s['frames']*400
target.parent.mkdir(parents=True,exist_ok=True)
with wave.open(str(target),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b''.join(parts))
with wave.open(str(target),'rb') as w:
 all_pcm=w.readframes(w.getnframes())
 if w.getnframes()!=offset:raise RuntimeError('Assembly sample count differs')
for r in ranges:
 piece=all_pcm[r['startSample']*2:r['endSample']*2]
 if hashlib.sha256(piece).hexdigest()!=r['pcm16Sha256']:raise RuntimeError('Original PCM altered')
record=dict(schemaVersion=1,assembledAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),path=target.relative_to(ROOT).as_posix(),sha256=sha(target),samples=offset,sampleRate=24000,frames=offset//400,ranges=ranges,allSelectedPcm16ByteIdentical=True,sourceAudio=0,bgm=0,finalMix=False)
(BASE/'audio-assembly.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(samples=offset,frames=offset//400,sha256=record['sha256'],allSelectedPcm16ByteIdentical=True)))

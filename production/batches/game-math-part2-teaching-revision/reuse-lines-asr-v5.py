"""Reuse recognition only when the complete scene PCM file is byte identical."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
old=ROOT/'shared/output/narration/game-math-lines-opening-retake-v4/qwen3-1.7b-balanced-v1'
new=ROOT/'shared/output/narration/game-math-lines-numeric-retakes-v5/qwen3-1.7b-balanced-v1'
provenance=json.loads((B/'lines-line-provenance-v5.json').read_text(encoding='utf8'))
assert provenance['unchangedEndingGatesPassed']
(new/'asr').mkdir(exist_ok=True);copied=[];pending=[]
for row in provenance['records']:
 ident=row['scene'];a=old/'chunks'/f'{ident}-scene.wav';z=new/'chunks'/f'{ident}-scene.wav';cache=old/'asr'/f'{ident}.json'
 current=hashlib.sha256(z.read_bytes()).hexdigest();assert current==row['currentSceneSha256']
 if a.exists() and cache.exists() and hashlib.sha256(a.read_bytes()).hexdigest()==current:
  raw=json.loads(cache.read_text(encoding='utf8'))
  if raw['audio_sha256']==current:
   (new/'asr'/f'{ident}.json').write_bytes(cache.read_bytes());copied.append({'scene':ident,'sha256':current});continue
 pending.append(ident)
assert len(copied)==18 and pending==['12','19']
(B/'lines-v5-asr-byte-reuse.json').write_text(json.dumps({'copied':copied,'currentHashRecognitionRequired':pending,'humanListeningComplete':False},indent=2)+'\n',encoding='utf8')
print(json.dumps({'byteIdenticalCachesReused':len(copied),'recognitionRequired':pending}))

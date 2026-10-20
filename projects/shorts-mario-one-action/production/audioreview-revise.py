"""Preserve the task-owned first mix then apply one justified peak-preparation correction."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local';A=L/'audio-first-mix-preserved'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c=read(R/'shared/publishing/video-production-control.json');assert c.get('selectedShortVideo')==P.name and c['shortsDirectSelection']['selectedRevision']=='one-action-v1'
 assert not A.exists(),'Never repeat/version over the preserved first mix'
 b=read(L/'audio-build.json');r=read(L/'audio-continuity.json');assert b['fingerprint']==r['fingerprint'];assert b['recipe']['settings']['audioRevision']=='one-action-v1'
 names=list(b['artifacts'])+['audio-build.json','audio-continuity.json']
 assert set(names)==set(['narration-source-timeline.wav','narration-prepared-stem.wav','narration-stem.wav','game-stem.wav','music-stem.wav','background-stem.wav','final-mix.wav','final-mix.m4a','audio-build.json','audio-continuity.json'])
 entries=[]
 for n in names:
  p=L/n;assert p.resolve().parent==L.resolve() and p.is_file() and not p.is_symlink()
  h=sha(p)
  if n in b['artifacts']:assert b['artifacts'][n]['sha256']==h
  entries.append(dict(name=n,sha256=h))
 A.mkdir()
 for e in entries:(L/e['name']).rename(A/e['name']);assert sha(A/e['name'])==e['sha256']
 (A/'finish-audio-first-recipe.py').write_bytes((P/'production/finish-audio.py').read_bytes())
 (A/'preservation-receipt.json').write_text(json.dumps(dict(reason='Peak-limited first voice measured-21.45LUFS and masking candidates; correct only prepared voice peaks, keep sourcePCM/timing/native/BGMrecipe.',oldFingerprint=b['fingerprint'],files=entries,newTtsRuns=0,fullMixAsrRunsBeforeCorrection=0,humanListening='pending'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 p=P/'production/finish-audio.py';s=p.read_text(encoding='utf8');s=s.replace("'audioRevision': 'one-action-v1'", "'audioRevision': 'one-action-v1-voice-peak-correction'");s=s.replace("acompressor=threshold=0.12:ratio=3:attack=5:release=140:makeup=1'", "acompressor=threshold=0.12:ratio=3:attack=5:release=140:makeup=1,alimiter=limit=0.14:attack=5:release=80:level=false:latency=true'")
 p.write_text(s,encoding='utf8');print('Exact10first-mixproducts preserved; sourcePCM/captions unchanged. Recipe corrected once.')
if __name__=='__main__':main()

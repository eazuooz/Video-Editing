"""Reuse word evidence only for byte-identical decoded paragraph PCM.

A retake shifts subsequent paragraphs in the assembled track. Verify those
samples exactly, then shift existing word times by the measured start delta.
Changed samples are never accepted from text equality or similar duration.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--source',required=True);ap.add_argument('--target',required=True);a=ap.parse_args()
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow'] and a.project in c['projectSlugs']
assert all(re.fullmatch(r'audio-v\d+',v) for v in [a.source,a.target]) and a.source!=a.target
P=R/'projects'/a.project/'production/local';src=P/a.source;dst=P/a.target
old=read(src/'narration.timing.json');new=read(dst/'narration.timing.json');oldhash=sha(src/'narration.wav');newhash=sha(dst/'narration.wav')
x,sx=sf.read(src/'narration.wav',dtype='float32');y,sy=sf.read(dst/'narration.wav',dtype='float32');assert sx==sy
lookup={(e['scene_id'],e['paragraph']):e for e in old['entries']};proof=[];folder=dst/'review/paragraphs';folder.mkdir(parents=True,exist_ok=True)
for e in new['entries']:
 k=(e['scene_id'],e['paragraph']);o=lookup[k];name=f'{k[0]}-{k[1]:02}.json';previous=src/'review/paragraphs'/name
 if not previous.exists():continue
 if e['text']!=o['text'] or e['display_text']!=o['display_text']:continue
 xp=x[round(o['start']*sx):round(o['end']*sx)];yp=y[round(e['start']*sy):round(e['end']*sy)]
 if not np.array_equal(xp,yp):continue
 d=read(previous);assert d['audio_sha256']==oldhash and d['entry']==o
 delta=e['start']-o['start'];d.update(audio_sha256=newhash,entry=e,reusedUnchangedParagraph=dict(source=str(previous.relative_to(R)),sourceRecordSha256=sha(previous),decodedPcmSha256=hashlib.sha256(xp.tobytes()).hexdigest(),samples=len(xp),timeShiftSeconds=delta,method='Exact float32 decoded PCM equality; word times shifted only',at=datetime.now(timezone.utc).isoformat()))
 for w in d['chunks']:w['timestamp']=[None if t is None else t+delta for t in w['timestamp']]
 target=folder/name
 if target.exists():
  kept=read(target)
  assert kept['audio_sha256']==newhash and kept['entry']==e and kept['chunks']==d['chunks'],'An earlier result differs; preserve and inspect it'
  for field in ['sourceRecordSha256','decodedPcmSha256','samples','timeShiftSeconds']:
   assert kept['reusedUnchangedParagraph'][field]==d['reusedUnchangedParagraph'][field],field
 else:target.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 proof.append(dict(scene=k[0],paragraph=k[1],samples=len(xp),shift=delta))
(dst/'review/reused-pcm-evidence.json').write_text(json.dumps(dict(sourceAudioSha256=oldhash,targetAudioSha256=newhash,reused=proof,humanListening=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(proof)} exactly unchanged paragraph transcripts reused; changed paragraphs still need actual ASR')

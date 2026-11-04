"""Preserve 34 raw takes; clarify the two edge identities in two paragraphs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, subprocess

P=Path(__file__).resolve().parents[1]; R=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=P/'production/local/audio-v2'; new=P/'production/local/audio-v3'
assert not new.exists(), 'Preserve existing revisions'
assert read(old/'finite-worker.json')['status']=='voice-generated-review-pending'
changes={
 '나머지 두 정점으로 가는 변을 큐 일과 큐 이라고 하죠.':
 '나머지 두 정점으로 가는 변을 첫 번째 변 큐 일, 두 번째 변 큐 이라고 하죠.',
 '접선은 티 이 큐 일에서 티 일 큐 이를 뺀 값을 이 행렬식으로 나누고, 비탄젠트는 마이너스 에스 이 큐 일에 에스 일 큐 이를 더해 같은 값으로 나눕니다.':
 '접선은 티 이 곱하기 첫 번째 변에서 티 일 곱하기 두 번째 변을 뺀 뒤 이 행렬식으로 나눕니다. 비탄젠트는 마이너스 에스 이 곱하기 첫 번째 변에 에스 일 곱하기 두 번째 변을 더해 같은 값으로 나눕니다.',
 'define the two geometric edges q1 and q2.':
 'call the first geometric edge q1 and the second edge q2.'
}
proof=[]
for name in ['script/narration.ko.json','script/narration.en.json','script/draft-narration.ko.json','script/draft-narration.en.json','planning/scene-bindings.json','planning/production-plan.json']:
 p=P/name; text=p.read_text(encoding='utf-8'); before=sha(p)
 for a,b in changes.items():text=text.replace(a,b)
 p.write_text(text,encoding='utf-8')
 proof.append(dict(file=name,beforeSha256=before,afterSha256=sha(p)))
digest={l:sha(P/f'script/narration.{l}.json') for l in ('ko','en')}
binding=read(P/'planning/scene-bindings.json')
for s in binding['scenes']:
 if s['id'] not in ('025','027'):continue
 for a in s['speechPhaseAnchors']:
  if a['phrase']=='큐 일과 큐 이':a['phrase']='첫 번째 변 큐 일'
  a['character']=s['speech'].index(a['phrase'])
binding['sourceNarrationSha256']=digest['ko']; save(P/'planning/scene-bindings.json',binding)
integration=read(P/'planning/script-integration.json')
for l in digest:integration['readThrough'][l+'Sha256']=digest[l]
integration.setdefault('preVoiceCorrections',[]).append(dict(
 at=datetime.now(timezone.utc).isoformat(),scenes=['025','027'],files=proof,
 reason='Two independent actual ASR decodes cannot distinguish q1/q2 in the spoken formulas. This is ambiguity evidence, not proof of a pronunciation fault. Explicit first/second-edge names make the same formula easier to follow.',
 canonicalFormula='T=(t2*q1-t1*q2)/D; B=(-s2*q1+s1*q2)/D; D=s1*t2-s2*t1',
 sourceOrderAndMathPreserved=True,humanListening=False,oldMediaPreserved=True))
save(P/'planning/script-integration.json',integration)
plan=read(P/'planning/production-plan.json')
for l in digest:plan['scriptReadthrough'][l+'Sha256']=digest[l]
save(P/'planning/production-plan.json',plan)
# The tangent and bitangent remain in one English semantic sentence but are now
# two separate Korean sentences to remove a long, easily confused spoken clause.
mapfile=P/'production/build-bilingual-map.py'
text=mapfile.read_text(encoding='utf-8');assert '27:[O]*4' in text
mapfile.write_text(text.replace('27:[O]*4','27:[O,O,(2,1),O]'),encoding='utf-8')
subprocess.run(['python','-X','utf8',str(mapfile)],check=True,cwd=R)
new.mkdir();(new/'chunks').mkdir();copied=[]
for f in sorted((old/'chunks').glob('*.wav')):
 if f.name in ('025-01-scene.wav','027-01-scene.wav'):continue
 target=new/'chunks'/f.name;shutil.copy2(f,target);assert sha(f)==sha(target)
 copied.append(dict(file=f.name,sha256=sha(f)))
assert len(copied)==34
m=read(P/'production/tts-manifest-audio-v2.json')
m['tts']['outputDir']=new.relative_to(R).as_posix()
m['retake']=dict(scenes=['025','027'],reason='Explicit first/second-edge identities; same mathematical explanation and approved voice.',preservedOriginal=old.relative_to(R).as_posix())
save(P/'production/tts-manifest-audio-v3.json',m)
save(new/'retake-plan.json',dict(at=datetime.now(timezone.utc).isoformat(),copiedUnchangedRawTakes=copied,retakeScenes=['025','027'],humanListening=False,sourceAudioPreserved=True))
print('34 raw takes preserved; two explicitly indexed paragraphs ready for retake')

"""M25 V2: say products, half, and the log's argument in operating order."""
from datetime import datetime,timezone
import json,hashlib,shutil,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];local=P/'production/local';old=local/'audio-v1';new=local/'audio-v2'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert P.name in read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['projectSlugs']
assert read(old/'finite-word-review.json')['status']=='word-evidence-ready-content-review-pending' and not new.exists()
report=read(local/'edit-v1/word-aligned-timeline.json');assert any(x['scene']=='018' for x in report['flags'])
assert any(x['scene']=='023' for x in report['identicalOverlappingAsrTimeSpans'])
changes={
 '009':('일반적인 시간 티에서는 높이가 에이 티이므로 변위는 이분의 일 에이 티 제곱입니다.',
        '일반적인 시간 티에서 삼각형의 높이는 가속도에 시간을 곱한 값이므로, 변위는 가속도에 시간의 제곱을 곱한 값의 절반입니다.'),
 '018':('출발점을 원점으로 두면 수평 위치는 브이 영 엑스 티, 높이는 브이 영 와이 티 빼기 이분의 일 지 티 제곱이 됩니다.',
        '출발점을 원점으로 두면 수평 위치는 처음 수평 속도에 시간을 곱한 값이고, 높이는 처음 수직 속도에 시간을 곱한 값에서 중력 때문에 떨어진 몫, 즉 중력의 크기에 시간의 제곱을 곱한 값의 절반을 빼면 됩니다.'),
 '031':('티의 역수는 영이 아닌 구간에서 로그 티의 절댓값을 원시함수로 갖습니다.',
        '영을 포함하지 않는 구간에서 티의 역수를 적분할 때는, 먼저 티의 절댓값을 구하고 그 값에 자연로그를 취하면 원시함수 하나가 됩니다.'),
}
files=['script/narration.ko.json','script/draft-narration.ko.json','planning/scene-bindings.json','planning/production-plan.json','planning/bilingual-caption-map.json','planning/script-integration.json','planning/caption-reading-adjustments.json']
backup=local/'operations-v1-inputs';assert not backup.exists()
src=read(P/files[0]);rows={s['id']:s for s in src['scenes']}
for sid,(before,after) in changes.items():
 assert rows[sid]['lines'][0].count(before)==1 and before in rows[sid]['displayLines'][0]
 assert before.count('.')==after.count('.')
backup.mkdir()
for n in files:
 dst=backup/n;dst.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(P/n,dst)
for n in files[:4]:
 f=P/n;s=f.read_text(encoding='utf8')
 for before,after in changes.values():s=s.replace(before,after)
 s=s.replace('"로그 티의 절댓값"','"먼저 티의 절댓값"');f.write_text(s,encoding='utf8')
ko=read(P/files[0]);before=read(backup/files[0])
assert {s['id'] for s,v in zip(ko['scenes'],before['scenes']) if s['lines']!=v['lines']}==set(changes)
d=read(P/files[2]);digest=sha(P/files[0])
for row,s in zip(d['scenes'],ko['scenes']):
 assert row['id']==s['id'] and row['speech']==s['lines'][0]
 for anchor in row['speechPhaseAnchors']:
  if not row['speech'][anchor['character']:].startswith(anchor['phrase']):
   assert row['speech'].count(anchor['phrase'])==1,(row['id'],anchor)
   anchor['character']=row['speech'].index(anchor['phrase'])
d['sourceNarrationSha256']=digest;save(P/files[2],d);d=read(P/files[3])
d['scriptReadthrough']['koSha256']=digest;d['sceneBindingsSha256']=sha(P/files[2]);save(P/files[3],d)
d=read(P/files[5]);d['readThrough']['koSha256']=digest
d.setdefault('preVoiceCorrections',[]).append(dict(at=datetime.now(timezone.utc).isoformat(),changes=changes,source='Δx = ½at² from rest; y = v₀ᵧt − ½gt²; ∫dt/t = ln|t| + C on an interval excluding zero.',reason='Say the arithmetic in the correct order without overloading the listener with letter names. Same examples, sections, formula cards and meaning groups. The M25-023 duplicate over identical timestamps was transcription-window overlap, not a reason to alter that raw take.',backup=backup.relative_to(R).as_posix(),humanListening=False))
save(P/files[5],d);subprocess.run(['python','-X','utf8',str(P/'production/build-bilingual-map.py')],cwd=R,check=True)
d=read(P/files[6]);d['koPrintedForms'].pop('로그 티의 절댓값',None);save(P/files[6],d)
new.mkdir();(new/'chunks').mkdir();copied=[]
for f in sorted((old/'chunks').glob('*.wav')):
 if f.name[:3] in changes:continue
 dest=new/'chunks'/f.name;shutil.copy2(f,dest);assert sha(f)==sha(dest);copied.append(dict(file=f.name,sha256=sha(f)))
assert len(copied)==36
m=read(P/'production/tts-manifest.json');m['tts']['outputDir']=new.relative_to(R).as_posix();m['retake']=dict(scenes=sorted(changes),reason='Clarify three spoken mathematical operations',preservedOriginal=old.relative_to(R).as_posix())
save(P/'production/tts-manifest-audio-v2.json',m);save(new/'retake-plan.json',dict(retakeScenes=sorted(changes),copiedUnchangedRawTakes=copied,originalPreserved=True,humanListening=False))
print('Three targeted operations; thirty-six identical original takes retained.')

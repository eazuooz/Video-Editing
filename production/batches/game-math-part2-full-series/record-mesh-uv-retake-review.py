"""Seal exact changed-wave provenance only after the complete direct raw review."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[3];P=R/'projects/game-math-mesh-uv/production';W=R/'shared/output/game-math-mesh-uv'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'shared/output/GPU_HANDOFF.json').exists()
review=read(P/'narration-review-in-progress.json');rows={s['scene']:s for s in review['scenes']}
assert not review['pendingScenes'] and set(rows)=={f'{x:02d}' for x in range(1,17)}
recordfile=P/'narration-number-correction.json';record=read(recordfile);current=[]
for original in record['originalAudio']:
 sid=original['scene'];provenance=read(W/f'line-repair-{sid}/provenance.json')
 row=rows[sid];raw=R/f'shared/output/narration/game-math-mesh-uv/qwen3-1.7b-balanced-v1/asr/{sid}.json'
 assert row['agentMeaningNumberReview']=='passed' and row['matchingCharacterCoverage']>=.93
 assert row['wavSha256']==provenance['sha256']==sha(R/provenance['currentWave'])==read(raw)['audio_sha256']
 assert original['originalWaveSha256']!=row['wavSha256'] and sha(R/original['originalWave'])==original['originalWaveSha256']
 current.append({'scene':sid,'originalWaveSha256':original['originalWaveSha256'],'currentWaveSha256':row['wavSha256'],'rawAsrSha256':sha(raw),'meaningNumberReview':'passed-full-current-direct-review','lineProvenance':(W/f'line-repair-{sid}/provenance.json').relative_to(R).as_posix()})
old=read(W/'before-hard-edge-clarification/provenance.json');new=read(W/'line-repair-13/provenance.json')
assert all(a['sha256']==b['sha256'] for a,b in zip(old['lines'],new['lines']) if a['line']!=4)
record.update(status='passed-current-agent-meaning-number-review-human-listening-pending',reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),audioReplacements={'status':'passed-current-agent-meaning-number-review','scenes':current},humanListening='pending')
record['secondRetake'].update(otherSixLineWavsByteIdentical=True,currentWholeRawReview='Both distinct directional clauses,all values and all original useful claims retained;no unrequested ending phrase.',currentWaveSha256=new['sha256'])
write(recordfile,record)
print('04/13 changed-wave provenance and other six13 lines verified; human listening remains pending.')

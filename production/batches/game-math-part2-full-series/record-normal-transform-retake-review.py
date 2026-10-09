"""Seal replaced waves only after all current full raw readbacks were reviewed."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[3];slug='game-math-normal-transform-uv';P=R/f'projects/{slug}/production'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
review=read(P/'narration-review-in-progress.json');assert not review['pendingScenes']
rows={s['scene']:s for s in review['scenes']};required=read(P/'narration-retake-required.json')
replacements=[]
for old in required['scenes']:
    sid=old['scene'];row=rows[sid]
    assert row['agentMeaningNumberReview']=='passed' and row['matchingCharacterCoverage']>=.93
    assert old['originalWaveSha256']!=row['wavSha256']
    prov=read(R/f'shared/output/{slug}/line-repair-{sid}/provenance.json')
    assert prov['sha256']==row['wavSha256']
    replacements.append({'scene':sid,'originalWaveSha256':old['originalWaveSha256'],'currentWaveSha256':row['wavSha256'],'currentRawAsrSha256':row['rawAsrSha256'],'notes':row['notes']})
required.update(status='passed-current-agent-meaning-number-review-human-listening-pending',replacements=replacements,reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),humanListening='pending')
write(P/'narration-retake-required.json',required)
correction=read(P/'narration-number-correction.json')
correction['status']='passed-current-agent-meaning-number-review-human-listening-pending'
correction['audioReplacements']={'status':'passed-current-agent-meaning-number-review','scenes':[r for r in replacements if r['scene'] in correction['retakeScenes']]}
correction['zeroDurationReadbackTailDiagnostic']='projects/'+slug+'/production/asr-zero-duration-tail-review.json'
correction['humanListening']='pending';write(P/'narration-number-correction.json',correction)
print({'replacedAndReviewed':[r['scene'] for r in replacements],'numericScenes':correction['retakeScenes'],'humanListening':'pending'})

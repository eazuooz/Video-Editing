"""Prepare a versioned, exact-36 revision. Never treat drafts as finished media."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BATCH = HERE.parent
ROOT = BATCH.parents[2]
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/elden-ring-development-36')

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    if path.exists() and path.read_bytes() == payload:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_bytes(payload)
    temp.replace(path)

def main():
    prior = read(BATCH / 'causal-review-20261128/review.json')
    scripts = read(HERE / 'narration-ko.json')
    expected = [f'{i:02}' for i in range(1, 37)]
    assert list(scripts) == expected
    assert all(len(v) == 4 and all(isinstance(t, str) and t.strip() for t in v) for v in scripts.values())
    baseline = read(BATCH / 'review-receipt-v10.json')
    assert sha(MEDIA / 'pc-review-v10/index.html') == baseline['reviewPageSha256']
    assert sha(MEDIA / 'pc-review-v10/manifest.json') == baseline['manifestSha256']
    pins = {}
    for path in [BATCH / 'causal-review-20261128/review.json', HERE / 'narration-ko.json',
                 BATCH / 'format-contract-v6.json', BATCH / 'asset-plan-v4.json',
                 BATCH / 'review-receipt-v10.json',
                 ROOT / 'projects/shorts-mario-one-action/production/local/tts-execution.json']:
        pins[path.relative_to(ROOT).as_posix()] = sha(path)
    original = {e['id']: e for e in read(BATCH / 'episodes-v1.json')}
    proposals = {e['id']: e for e in prior['episodes']}
    rows = []
    for key in expected:
        rows.append(dict(id=key, title=original[key]['title'], topic=original[key]['topic'],
                         narrationKo=scripts[key], acceptedProposal=proposals[key],
                         status='script-draft-source-and-shot-verification-pending',
                         evidenceLocked=False, voiceComplete=False, unityComplete=False,
                         renderComplete=False, humanReview='pending'))
    plan = dict(version='causal-v11', dateKst='2026-11-28', scope=expected,
                authorized=True, userInstruction='이 개선안대로 36편 전부 다시 만들어줘. 원래 목소리랑 쇼츠 양식 유지해서 중간에 묻지 말고 완성되면 PC 검수표 하나로 모아줘.',
                finalReviewTarget=(MEDIA / 'pc-review-v11/index.html').as_posix(),
                targetExistsIsNotCompletion=True, preserveBaseline='pc-review-v10',
                actualGameplayShare=.5, genuineUnityShare=.5, equalPairedFrames=True,
                allowPlatformChanges=False, allowOtherBatches=False,
                approvalsRequiredDuringProduction=False, sourcePins=pins, episodes=rows)
    write(HERE / 'plan.json', plan)
    status = HERE / 'checkpoint.json'
    if not status.exists():
        write(status, dict(version='causal-v11', scope=expected, state='preparing-causal-scenes-and-evidence',
                           planSha256=sha(HERE / 'plan.json'),
                           newCompletedEpisodes=[], newVoiceTakes=0, newUnityCuts=0,
                           finalReviewDelivered=False, baselinePreserved=True))
    print(json.dumps(dict(episodes=len(rows), newKoParagraphs=sum(len(r['narrationKo']) for r in rows),
                          planSha256=sha(HERE / 'plan.json'), baselinePreserved=True), ensure_ascii=False))

if __name__ == '__main__':
    main()

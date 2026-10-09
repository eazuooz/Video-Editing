"""Seal the directly read new normal/UV lecture and mesh delivery changes."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / 'production/batches/sakurai-planning-game-design/proof-similar-game-design'
REPORT = ROOT / 'production/batches/sakurai-planning-game-design/preflight/similar-game-design.json'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()
def save(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n', 'utf-8')

current = read(REPORT)
old = read(B / 'inventory-prior-v17.json')
old_map = {x['path']: x['sha256'] for x in old['inputFiles']}
changed = [x for x in current['inputFiles'] if old_map.get(x['path']) != x['sha256']]
expected = {
 'projects/game-math-mesh-uv/project.json':'0bd80039f35a8c5154777998056ab71a9ca6c131ade3a7cdeca6182135159766',
 'projects/game-math-mesh-uv/README.md':'f93b662464793e339bee32d149538b8a24f651d7770fc63e9fb6bf5e7b1f6ae0',
 'projects/game-math-mesh-uv/publishing/youtube-upload.json':'3a220fdb362e62ef0e7a6f278255fce7062e23cf3e6d6e79f09816d8af04fabb',
 'projects/game-math-normal-transform-uv/project.json':'bfa6480003ca28da71767da7fb0095616af3eeafe868c43503ac3eb396dee92d',
 'projects/game-math-normal-transform-uv/script/narration.ko.json':'344d3e27847c5a2d74d667bc3368f70c341382c707da0431f573078d47828d79',
 'projects/game-math-normal-transform-uv/script/narration.en.json':'1c0cba43f092315070fe5c833273f3212da93c0201fc1736c7ee7541e7ef873c',
 'projects/game-math-normal-transform-uv/planning/outline.md':'6a6575db16659b1ad98a08249ae9102318a20e5b7229bfebf741e8a11d259b73',
 'projects/game-math-normal-transform-uv/sources/SOURCES.md':'ac7d2a7a298f4c9312297c42fe70f24e4442c90fd22629ec5d3ba963ce032fb4',
 'projects/game-math-normal-transform-uv/README.md':'5ca04d99d31b08dc0ae26af0e21b31386376430b95d002b3b3a56fc6d5cb8b68',
}
assert current['inputsDigest'] == '216c67d1e37ed78dc528fe83a58b907d3944f5d45f4c16edc4f4d0095527c32a'
assert len(current['existingProjects']) == 51 and len(current['inputFiles']) == 358
assert {x['path']:x['sha256'] for x in changed} == expected
assert not set(old_map) - {x['path'] for x in current['inputFiles']}
for x in current['inputFiles']:
    assert sha(ROOT / x['path']) == x['sha256'], x['path']
counts = {}
for lang in ['ko','en']:
    script = read(ROOT / f'projects/game-math-normal-transform-uv/script/narration.{lang}.json')
    counts[lang] = dict(scenes=len(script['scenes']), paragraphs=sum(len(x['lines']) for x in script['scenes']))
    assert counts[lang] == dict(scenes=13, paragraphs=81)
receipt = read(ROOT / 'projects/game-math-mesh-uv/publishing/youtube-upload.json')
assert receipt['videoId'] == 'xnIA0EAJtiA' and receipt['privateVisibilitySaveVerified'] and receipt['fullSettingsVerified']
sp = ROOT / 'shared/output/similar-game-design/preflight/studio-current-v18.ax.txt'
studio = sp.read_text('utf-8')
assert 'xnIA0EAJtiA' in studio and '메시·법선 만들기' in studio and '비공개' in studio
comparison = '새 법선/UV 강의13장81문단씩 KOEN 전체를 직접 읽었다. 열벡터 접선-법선 수직, 비균일 확대의 역전치/정규화, 특이/반사 조건, UV 대응·회전·반전, 보간 뒤 repeat floor/clamp/mirror와 필터링 구분 및 정점에서 먼저 wrapping하는 오류를 계산한다. 렌더 픽셀에서 내부 토폴로지·UV를 추정하지 않는다. 친숙한 장르 행동에 목적·공간·협력 조합을 더해 새 작품을 선택할 이유를 만드는 현재 영상의 질문/장별 주장과 다르다. mesh의 변경 manifest/README/실제 saved-private receipt 전체를 읽었고, 이전 전체 mesh 대본의 독립 내용 판단을 유지했다.'
proof = dict(schemaVersion=1, reviewedAt=now(), candidate='similar-game-design', inventoryProjects=51,
 inputFiles=358, inputsDigest=current['inputsDigest'], changedFilesCount=9,
 previousReview=dict(path=(B / 'content-review-v17.json').relative_to(ROOT).as_posix(),sha256=sha(B / 'content-review-v17.json')),
 changedFiles=[dict(**x,previousSha256=old_map.get(x['path']),entireCurrentContentDirectlyRead=True,comparison=comparison,foreignFileModified=False) for x in changed],
 newWholeBilingualScriptReview=counts,
 currentStudio=dict(path=sp.relative_to(ROOT).as_posix(),sha256=sha(sp),uiOnly=True,visibleRows=30,
  meshActualId='xnIA0EAJtiA',meshPrivateListRowDirectlyRead=True,
  meshReceiptFullSettingsVerified=True,meshReceiptActual720p60Playback=True,mesh1080PlaybackNotClaimed=True,
  newNormalUvLocalProjectOnly=True,priorRelatedFullContentAndStudioReviewsPreserved=True,
  clippedListDescriptionsNotFullMetadata=True,existingPublishedAndScheduledRowsPreserved=True,uiWrites=0),
 decision='distinct',emptyExactMatchesUsedAsDecision=False,mathematical40_60AndNoBgmExceptionCopied=False,
 blackPaletteCopiedToAlreadyStartedSimilar=False,foreignFilesModified=0)
save(B / 'current-normal-uv-mesh-change-review-v18.json',proof)
review = copy.deepcopy(read(B / 'content-review-v17.json'))
review.update(reviewedAt=now(),previousReview=proof['previousReview'],addedWholeScriptReview=(B/'current-normal-uv-mesh-change-review-v18.json').relative_to(ROOT).as_posix(),currentForeignChangeReview=proof['changedFiles'],gateStatus='awaiting-current-check')
review['inventory'].update(projectCount=51,inputsDigest=current['inputsDigest'])
review['currentStudio']['currentList']=proof['currentStudio']
review['scope'] += ' v18: nine changed/new inputs fully directly read; new13-scene81-paragraph KOEN normal/UV lecture and saved mesh delivery compared. Previous full content/Studio review preserved; not a claim of fresh reread of all51 scripts.'
review.pop('gate',None)
save(B/'content-review-v18.json',review)
subprocess.run(['node','scripts/review-video-duplicates.cjs','similar-game-design','--decision','distinct','--reason',comparison+' 근거: '+(B/'content-review-v18.json').relative_to(ROOT).as_posix(),'--studio-evidence',(B/'content-review-v18.json').relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
subprocess.run(['node','scripts/review-video-duplicates.cjs','similar-game-design','--check'],cwd=ROOT,check=True)
checked=read(REPORT)
assert checked['inputsDigest']==current['inputsDigest']
review.update(gateStatus='current-distinct-check-passed',gate=dict(command='node scripts/review-video-duplicates.cjs similar-game-design --check',exitCode=0,checkedAt=now(),inputsDigest=checked['inputsDigest']))
save(B/'content-review-v18.json',review)
save(B/'inventory-prior-v18.json',checked)
cp_path=ROOT/'projects/similar-game-design/production/latest-checkpoint.json'
cp=read(cp_path)
cp.update(currentDuplicateReview=(B/'content-review-v18.json').relative_to(ROOT).as_posix(),duplicateInputsDigest=checked['inputsDigest'],updatedAt=now())
save(cp_path,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
queue=read(qp)
item=next(x for x in queue['items'] if x['slug']=='similar-game-design')
item.update(currentDuplicateReview=cp['currentDuplicateReview'],duplicateInputsDigest=checked['inputsDigest'])
queue['updatedAt']=now()
save(qp,queue)
print(json.dumps(dict(currentDistinctPassed=True,projects=51,changedWholeContentFiles=9,newWholeScriptCounts=counts,foreignFilesModified=0)))

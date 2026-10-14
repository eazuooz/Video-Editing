"""Seal reviewed changes and current Studio evidence before the strict topic gate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
REPORT=ROOT/'production/batches/sakurai-planning-game-design/preflight/hierarchical-game-outlines.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,o:p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
pending=read(V/'duplicate-refresh-pending-v1.json')
assert not (V/'duplicate-content-and-studio-direct-review-v1.json').exists()
assert sha(REPORT)==pending['currentReportSha256']
inventory=read(REPORT)
assert not inventory['exactMatches']
for item in inventory['inputFiles']:
    assert sha(ROOT/item['path'])==item['sha256'],item['path']
historic_path=ROOT/'production/batches/sakurai-planning-game-design/proof-hierarchical-game-outlines/content-review.json'
historic=read(historic_path)
inherited=[]
for item in historic['inventory']['relatedFullScriptComparisons']:
    for binding in item['activeScriptHashes']:
        assert sha(ROOT/binding['path'])==binding['sha256'],binding['path']
    inherited.append(item)
ui=V/'ui-proof-v1'
studio_files=[
    ('current-baseline-details-v1.ax.txt','jBRt3xatdPk','게임 기획서 정리: 계층형 아웃라인으로 생각을 묶는 법','scheduled'),
    ('current-lighting-04-1-duplicate-read-v1.ax.txt','YOsG939kaBw','부족한 픽셀과 메모리로 게임 화면을 만드는 법 | 그림자·TSR·모바일 렌더링','private'),
    ('current-game-reward-duplicate-read-v1.ax.txt','Njz_o1YJh8Q','게임 보상 기획: 기능·획득 조건·제작 범위를 먼저 정하는 법','scheduled'),
    ('current-avoid-comparisons-duplicate-read-v1.ax.txt','cQE7_ygx_XM','게임 기획 설명법: 작품명 대신 목표·행동·조건을 전달하기','scheduled')]
studio=[]
for f,sid,title,visibility in studio_files:
    ax=(ui/f).read_text('utf8')
    assert sid in ax and title in ax and 'button (disabled) 저장' in ax
    assert '고화질 완료' in ax and '표준 화질 완료' in ax
    assert ('text 비공개' if visibility=='private' else 'text 예약됨') in ax
    studio.append(dict(videoId=sid,title=title,actualVisibility=visibility,wholeTitleAndDescriptionRead=True,
        saveDisabled=True,sdHdComplete=True,path=(ui/f).relative_to(ROOT).as_posix(),sha256=sha(ui/f),settingsChanged=False))
lighting=ROOT/'projects/game-lighting-history-04-1'
ko=read(lighting/'script/narration.ko.json')
en=read(lighting/'script/narration.en.json')
assert len(ko['scenes'])==len(en['scenes'])==77
assert [s['id'] for s in ko['scenes']]==[s['id'] for s in en['scenes']]
lighting_receipt=read(lighting/'publishing/youtube-upload.json')
assert lighting_receipt['descriptionKo'] in (ui/'current-lighting-04-1-duplicate-read-v1.ax.txt').read_text('utf8')
for slug,fname in [('game-reward-planning','current-game-reward-duplicate-read-v1.ax.txt'),
                   ('avoid-game-comparisons','current-avoid-comparisons-duplicate-read-v1.ax.txt')]:
    main=read(ROOT/'projects'/slug/'project.json')
    k=read(ROOT/main['paths']['script'])
    e=read(ROOT/main['paths']['scriptEn'])
    assert [s['id'] for s in k['scenes']]==[s['id'] for s in e['scenes']]
owned_bindings=[]
for f in ['current34-mixed-complete-direct-review-v1.json','current34-caption-timing-direct-review-v1.json',
          'current34-final-technical-and-pixel-direct-review-v5.json','current34-main-promotion-v1.json',
          'current34-main-schedule-update-v1.json','publishing/private-settings-direct-review-v2.json',
          'publishing/schedule-direct-review-v1.json','publishing/production-git-verification-v1.json',
          'publishing/schedule-git-verification-v1.json']:
    p=O/f
    owned_bindings.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
current_o=read(ROOT/'projects/game-math-orientation-matrices/project.json')
assert sha(ROOT/'projects/game-math-orientation-matrices/project.json')==read(O/'current34-main-schedule-update-v1.json')['afterSha256']
assert current_o['paths']['script'].endswith('current34-combined-v1.ko.json')
assert read(O/'current34-mixed-complete-direct-review-v1.json')['all180ContextsDirectlyCompared']
now=datetime.now(timezone.utc).isoformat()
review=dict(schemaVersion=1,reviewedAt=now,candidate=dict(slug='hierarchical-game-outlines',
    baselineVideoId='jBRt3xatdPk',viewerQuestion='How can written game-design ideas be grouped at matching question scales, folded, moved with their children, and cross-referenced without losing conditions?',
    scope='Authorized additive revision of this existing upload; preserve original12PCM/60KOEN paragraphs and baseline until reviewed replacement.'),
    inventoryDigest=inventory['inputsDigest'],inventoryProjectCount=len(inventory['existingProjects']),
    inventoryInputCount=len(inventory['inputFiles']),allCurrentTitlesAndProjectIdentitiesRead=True,
    latestChanges=pending['changesSinceLatestOrientationInventory'],
    unchangedLatestInputCount=pending['unchangedLatestInputCount'],
    unchangedWholeReviewsReused=pending['previousWholeReview'],
    historicalLikelyOverlapReviews=historic_path.relative_to(ROOT).as_posix(),historicalLikelyOverlapSha256=sha(historic_path),
    inheritedExactRelatedFullScripts=inherited,
    addedDirectWholeScriptReads=[dict(slug='game-lighting-history-04-1',koScenes=77,enScenes=77,
        directReadChunks=['3aec30/truncated-first-read','6210bd/KO-first-and-final','27a3d6/KO30..48-recovered','104f07/EN1..39','ba7c24/EN40..77'],
        manifestAndReadmeRead=True,fullReceiptFieldsRead=True,receiptTruncationRecovered=['ae62ea','2e39ff','05acd1']),
        dict(slug='game-reward-planning',koScenes=13,enScenes=13,actualWholeReads=['bfaba0','0d653b']),
        dict(slug='avoid-game-comparisons',koScenes=15,enScenes=15,actualWholeReads=['56755f','43d603'])],
    ownedOrientationCompletedWholeReviewsReused=owned_bindings,
    findings=[
        'The current hierarchy baseline teaches heading levels, sibling question scale, folding without deleting, moving an entire text branch and side references. Its original12scenes/60independent KOEN paragraphs were fully read; only the opening/four-game additions are required. This is the same authorized project, not another new video on the source topic.',
        'The unchanged four closest historical topics remain SHA-identical to their full bilingual review: behavior analysis/tests, blank-project coding recall, story state/knowledge, and development roles differ from organizing a design document through heading levels and fold/reorder operations.',
        'All current77 KO/EN lighting04-1 paragraphs and its root/README/receipt were read. Shadow pages/texture storage, temporal image reconstruction, visibility/material and mobile policies concern image computation and memory. A material graph or resource group is not an outline-editing lesson. CUA123 whole current description exactly matches the receipt; private SD/HD complete and Save disabled. No foreign production/settings approval.',
        'The current13 paired reward-planning scenes organize a reward catalogue by behavior, acquisition conditions, combinations and asset work. The current15 paired comparison-explanation scenes communicate goal/actions/conditions in three sentences and test a listener restatement. Those content decisions can supply text to an outline, but neither teaches heading levels, folded branch review, whole-branch relocation or inclusion versus cross-reference. CUA125/126 full current descriptions read unchanged, scheduled and Save disabled.',
        'Orientation has already been directly reviewed as current34 scenes/180 paragraphs and244 cues through actual private/save-reopen/Git/Oct13 replacement. Its retained local-to-world bases, transpose, physical nested rotations, orthogonality and storage conventions concern object posture and numeric matrices. The shared word parent/child does not make that physical composition the same operation as moving written proposal headings. Exact owned completed proofs are reused; no completed narration/pixel/playback rerun.',
        'CUA119 current full title/description and exact Oct14 09:00 GMT+0900 modal were read. The baseline remains scheduled with no edits. No new actual upload exists. The latest channel reservation ledger/actual future list remains authoritative; this gate is not final footage or human/public-rights approval.'
    ],studioWholeReads=studio,verdict='distinct-authorized-additive-revision',allNewContentsCompared=True,
    currentStrictCheckPassed=False,foreignQualityOrRightsApproved=False,foreignFilesOrSettingsChanged=False,
    newNarrationCreated=False,newTtsStarted=False,newSceneCreated=False,humanListeningApproved=False,publicRightsApproved=False)
save(V/'duplicate-content-and-studio-direct-review-v1.json',review)
reason='Authorized additive replacement of current hierarchy upload jBRt3xatdPk: preserve12PCM/60KOEN and teach matching heading levels, folded branch review, whole-branch relocation and cross-references through four games. Current89-project516-input inventory reviewed:501 exact unchanged inputs inherited from prior whole reviews; new lighting77KOEN/root/receipt/currentStudio and owned orientation34/180 completed proofs compared. Full current reward13KOEN and comparison15KOEN/Studio are adjacent catalogue/communication tasks, not outline operations. See projects/hierarchical-game-outlines/revision-teaching-clarity-v1/duplicate-content-and-studio-direct-review-v1.json.'
evidence='CUA119 jBR full currentdescription and Oct14 09:00 GMT+0900 modal; CUA123 YOsG939kaBw private fullmatchingdescription/SDHD/Save disabled; CUA125 Njz_o1YJh8Q and CUA126 cQE7_ygx_XM scheduled full descriptions/SDHD/Save disabled. Exact unchanged Studio/history proof reused; no external edits. Evidence in projects/hierarchical-game-outlines/revision-teaching-clarity-v1/ui-proof-v1/.'
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
decision=subprocess.run([node,'scripts/review-video-duplicates.cjs','hierarchical-game-outlines','--decision','distinct','--reason',reason,'--studio-evidence',evidence],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
assert decision.returncode==0,decision.stderr
check=subprocess.run([node,'scripts/review-video-duplicates.cjs','hierarchical-game-outlines','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
save(V/'duplicate-current-check-verification-v1.json',dict(recordedAt=now,actualDecisionExitCode=decision.returncode,
    actualCheckExitCode=check.returncode,actualCheckStdout=check.stdout,actualCheckStderr=check.stderr,
    currentInventorySha256=sha(REPORT),currentDigest=read(REPORT)['inputsDigest'],reviewSha256=sha(V/'duplicate-content-and-studio-direct-review-v1.json')))
assert check.returncode==0,check.stderr
cp_path=V/'latest-checkpoint.json'
cp=read(cp_path)
cp.update(recordedAt=now,duplicateCurrentCheckPassed=True,duplicateReview=(V/'duplicate-content-and-studio-direct-review-v1.json').relative_to(ROOT).as_posix())
save(cp_path,cp)
print(json.dumps(dict(decisionExitCode=decision.returncode,checkExitCode=check.returncode,projects=89,inputs=516,
    inheritedInputs=501,studioWholeReads=len(studio),narrationStarted=False)))

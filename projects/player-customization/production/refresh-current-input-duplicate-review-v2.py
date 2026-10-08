"""Record directly read changed foreign inputs; never alter their production."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, os, time

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):
    t=p.with_name(p.name+f'.{os.getpid()}.writing')
    t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
    for n in range(40):
        try: os.replace(t,p); return
        except OSError:
            if n==39: raise
            time.sleep(.15)

report=ROOT/'production/batches/sakurai-planning-game-design/preflight/player-customization.json'
before=read(report)
files=[
 'projects/game-lighting-history-01/project.json',
 'projects/game-lighting-history-01/planning/outline.md',
 'projects/game-lighting-history-01/README.md',
 'projects/game-lighting-history-01/sources/SOURCES.md',
 'projects/game-lighting-history-01/script/narration-draft.ko.json',
 'projects/game-lighting-history-01/script/narration-draft.en.json',
 'projects/game-math-planes-barycentric/project.json',
 'projects/game-math-planes-barycentric/script/narration.ko.json',
 'projects/game-math-planes-barycentric/script/narration.en.json',
 'projects/game-math-planes-barycentric/publishing/youtube-upload.json',
]
ax=ROOT/'shared/output/player-customization/research/studio-current-change-v2.ax.txt'
assert ax.exists()
e=dict(schemaVersion=1,slug='player-customization',reviewedAt=now(),
 priorEvidence='projects/player-customization/production/current-lighting-project-duplicate-rereview-v1.json',
 originalFullSourceAndPrior15LikelyOverlapPairedReviewPreserved=True,
 changedForeignInputsWholeTextDirectlyRead=True,
 foreignFiles=[dict(path=f,sha256=sha(ROOT/f)) for f in files],
 completeScripts=[], comparisons=[
  dict(project='game-math-planes-barycentric',question='Distance to a plane, normal convention, triangle area/barycentric weights, independent coplanarity validation and attribute interpolation.',
       distinction='All22 chapters and both complete narration texts were read. Heights, target location and color here are geometric quantities. Player customization instead asks how a chosen function changes an action, how to preview and try it, and how appearance expresses a player. No calculation or lecture argument is imported; the foreign40:60/noBGM exception is not applied.'),
  dict(project='game-lighting-history-01',question='Stored versus updated light, visibility, lightmaps/filtering/TBDR, normal maps/shadow volumes/RNM, shadow maps/CSM, Forward/Deferred and SSAO.',
       distinction='The entire changed manifest, new outline/README/sources and both89-paragraph drafts were read. Stored surface light and renderer evaluation order are distinct from player function choice and trial. The drafts are not accepted narration and have no completed upload; this review does not approve foreign footage or production.')
 ],
 studio=dict(path=ax.relative_to(ROOT).as_posix(),sha256=sha(ax),observedAt='2026-10-08T04:08:24.686Z',
     scope='Current first30 rows directly read, about480 total; not a claim to reread all480. Original source/full prior overlap review remains preserved.',
     newVideo=dict(videoId='wsxSYEEj8aQ',title='게임수학 Part 2 · 기하 기본 요소 ② 평면과 무게중심 좌표',observedState='uploading38%; waiting; automatic checks pending',
                  productionReceipt='projects/game-math-planes-barycentric/publishing/youtube-upload.json',
                  completePrivateSettingsInferred=False),
     otherUserPublicAndScheduledStatusesPreserved=True,settingsChanged=False),
 foreignFilesModified=False,foreignCommitsCreated=False,
 currentDistinctCheckPassed=False,finalAllocationApproved=False,finalMixedAsrApproved=False,uploaded=False)
for slug,stem in [('game-math-planes-barycentric','narration'),('game-lighting-history-01','narration-draft')]:
    for lang in ['ko','en']:
        f=ROOT/f'projects/{slug}/script/{stem}.{lang}.json';j=read(f)
        e['completeScripts'].append(dict(path=f.relative_to(ROOT).as_posix(),scenes=len(j['scenes']),paragraphs=sum(len(s['lines']) for s in j['scenes']),sha256=sha(f),directlyRead=True))
target=BASE/'current-planes-lighting-input-duplicate-rereview-v2.json'
save(target,e)
reason='Preserve full source and prior15 complete KO/EN overlap comparisons. Directly reread all22 current plane/barycentric chapters130KOEN paragraphs per language and lighting13chapter89KOEN drafts plus whole changed/new manifests, outline, sources, README and actual transfer receipt. Geometry validation/interpolation and stored/updated rendering light differ from customization function choice, preview, trial and personal expression. Actual Studio first30 observed new wsxSYEEj8aQ transfer pending; no settings or foreign files changed. See projects/player-customization/production/current-planes-lighting-input-duplicate-rereview-v2.json.'
cmd=[NODE,'scripts/review-video-duplicates.cjs','player-customization','--decision','distinct','--reason',reason,'--studio-evidence',target.relative_to(ROOT).as_posix()]
r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8');e['recordCommand']=cmd;e['recordExitCode']=r.returncode;e['recordOutput']=r.stdout+r.stderr
if r.returncode==0:
    cmd=[NODE,'scripts/review-video-duplicates.cjs','player-customization','--check']
    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8');e['checkCommand']=cmd;e['checkExitCode']=r.returncode;e['checkOutput']=r.stdout+r.stderr
    e['currentDistinctCheckPassed']=r.returncode==0
    e['currentPreflightSha256']=sha(report)
    e['existingProjects']=len(read(report)['existingProjects'])
e['foreignHashChangesDuringReview']=[f for f in e['foreignFiles'] if sha(ROOT/f['path'])!=f['sha256']]
if e['foreignHashChangesDuringReview']:e['currentDistinctCheckPassed']=False
save(target,e)
cp=read(BASE/'latest-checkpoint.json');cp.update(currentDistinctCheckPassed=e['currentDistinctCheckPassed'],currentDuplicateRereview=target.relative_to(ROOT).as_posix());save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization');i.update(currentDistinctCheckPassed=e['currentDistinctCheckPassed'],currentDuplicateRereview=target.relative_to(ROOT).as_posix());q['updatedAt']=now();save(qp,q)
print(json.dumps({k:e.get(k) for k in ['currentDistinctCheckPassed','existingProjects','completeScripts','foreignHashChangesDuringReview','checkOutput']},ensure_ascii=False,indent=2))
assert e['currentDistinctCheckPassed'],'Read new changed input; do not bypass the current review gate.'

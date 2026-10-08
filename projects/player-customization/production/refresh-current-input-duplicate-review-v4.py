"""Refresh only the directly reread manifest/receipt delta; preserve foreign work."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, os, time
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing')
 t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
prior=read(BASE/'current-lighting108-and-polygon-upload-duplicate-rereview-v5.json')
changed={
 'projects/game-lighting-history-01/project.json':'013fbe28b3f00dfc3b1eec1445464023e4500ea3f1cdff8b79f2220c8fd0c295',
 'projects/game-math-polygons-triangulation/project.json':'7b16462f5ddb3883018c99c0c792ffb01a9ee8b9d04fc3089b6943927d75d3f5',
 'projects/game-math-polygons-triangulation/publishing/youtube-upload.json':'67d8e6a229d8c76d86a842e5b0de6a984a2257b08824a6e221856a497402fdbe',
}
expected={f['path']:changed.get(f['path'],f['sha256']) for f in prior['foreignFiles']}
assert all(sha(ROOT/f)==h for f,h in expected.items()),'Read any new foreign delta first.'
ax=ROOT/'shared/output/player-customization/research/studio-current-change-v6.ax.txt'
assert ax.exists()
e=dict(schemaVersion=1,slug='player-customization',reviewedAt=now(),
 priorEvidence='projects/player-customization/production/current-lighting108-and-polygon-upload-duplicate-rereview-v5.json',
 originalFullSourceAndPriorFullPairedReviewPreserved=True,
 changedForeignInputsWholeTextDirectlyRead=True,
 foreignFiles=[dict(path=f,sha256=h,changedSincePrior=f in changed) for f,h in expected.items()],
 completeScripts=prior['completeScripts'],
 comparisons=[
  dict(project='game-lighting-history-01',distinction='Whole current manifest reread: scoped voice repair and visual QA;13scenes108KOEN paragraphs unchanged from the prior complete read. Stored light, lightmaps, geometry/normal maps, CSM and deferred material/buffer questions differ from choosing a player function, previewing, trying its action and expression. Foreign scoped08/09b voice repairs and false final gates are preserved.'),
  dict(project='game-math-polygons-triangulation',distinction='Whole current59015frame manifest and saved-private receipt reread. All128KOEN paragraphs unchanged from the prior complete paired reading. Triangle centers, polygon boundary ordering, convexity and fan/ear clipping are geometric algorithm questions, distinct from player function choice, trial and expression. Foreign40:60/noBGM exception is preserved separately.'),
  dict(project='game-math-planes-barycentric',distinction='All130KOEN paragraphs and manifest/receipt hashes remain unchanged from prior full reading. Plane distance, coplanarity, area weights and attribute interpolation differ from player choice/preview/trial/expression.')],
 studio=dict(path=ax.relative_to(ROOT).as_posix(),sha256=sha(ax),
  scope='Current first30 of482 content rows read after reload; no claim that every row was newly reread. Original whole inventory and earlier full-content comparisons preserved.',
  newPolygon=dict(videoId='L7SXFwn4i2k',rowVideoIdLinkObserved=True,observedState='16:24;private;uploaded2026.10.8;1view;no current alert',privateSavedObserved=True),
  plane=dict(videoId='wsxSYEEj8aQ',observedState='17:18;private;2views;no current alert'),
  userStateChangesPreserved=[dict(videoId='6-kP65hrZcI',observed='Scheduled2026.10.11'),dict(videoId='ZLOewk8JHXA',observed='Scheduled2026.10.10'),dict(videoId='xtUVcAHtQzg',observed='Scheduled2026.10.10'),dict(videoId='gSN8tbGkJ5E',observed='Scheduled2026.10.9'),dict(videoId='PcxaKEvbzjg',observed='Public2026.10.8')],
  unknownUploadingRow='To do....2% uploading, title/concept not established; untouched',settingsChanged=False),
 foreignFilesModified=False,currentDistinctCheckPassed=False,finalAllocationApproved=False,finalMixedAsrApproved=False,uploaded=False)
target=BASE/'current-lighting-repair-and-polygon-private-duplicate-rereview-v6.json';assert not target.exists()
save(target,e)
reason='Preserve the original whole source and all prior complete paired overlap comparisons. Reread whole changed lighting scoped-repair manifest, polygon59015frame manifest and saved-private L7SXFwn4i2k receipt. Current Studio exact ID polygon16:24private and plane wsxSYEEj8aQ17:18private verified; user public/scheduled states preserved. All lighting108KOEN, polygon128KOEN and plane130KOEN paragraph contents are byte-identical to earlier direct full readings. Rendering storage/evaluation, geometric polygon algorithms and plane interpolation differ from player function choice, preview, trial and personal expression. Foreign40:60/noBGM and repair gates are not imported. See '+target.relative_to(ROOT).as_posix()+'.'
cmd=[NODE,'scripts/review-video-duplicates.cjs','player-customization','--decision','distinct','--reason',reason,'--studio-evidence',target.relative_to(ROOT).as_posix()]
r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8');e.update(recordCommand=cmd,recordExitCode=r.returncode,recordOutput=r.stdout+r.stderr)
if r.returncode==0:
 cmd=[NODE,'scripts/review-video-duplicates.cjs','player-customization','--check'];r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
 e.update(checkCommand=cmd,checkExitCode=r.returncode,checkOutput=r.stdout+r.stderr,currentDistinctCheckPassed=r.returncode==0)
e['foreignHashChangesDuringReview']=[f for f,h in expected.items() if sha(ROOT/f)!=h]
if e['foreignHashChangesDuringReview']:e['currentDistinctCheckPassed']=False
save(target,e)
cp=read(BASE/'latest-checkpoint.json');cp.update(currentDistinctCheckPassed=e['currentDistinctCheckPassed'],currentDuplicateCheckPassed=e['currentDistinctCheckPassed'],currentDuplicateRereview=target.relative_to(ROOT).as_posix());save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization');i.update(currentDistinctCheckPassed=e['currentDistinctCheckPassed'],currentDuplicateRereview=target.relative_to(ROOT).as_posix());q['updatedAt']=now();save(qp,q)
print(json.dumps({k:e.get(k) for k in ['currentDistinctCheckPassed','foreignHashChangesDuringReview','checkOutput']},ensure_ascii=False))
assert e['currentDistinctCheckPassed'],'Read the new changed input before proceeding.'

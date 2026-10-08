"""Seal the directly read current-input delta without modifying foreign work."""
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

expected={
 'projects/game-lighting-history-01/project.json':'b336523aa55845ac6595cec3357549b92396335a52873a8e0ec15fd627ecddba',
 'projects/game-lighting-history-01/planning/outline.md':'d6e231f1b0ace9362c803edf492d5008b267aa6364c2e5a15c5de3a4ca5555f0',
 'projects/game-lighting-history-01/sources/SOURCES.md':'fa22ed2eaf7f8808cf5ece71f2505ec967dc2b26f0a0cb7caddc885f6879bf54',
 'projects/game-lighting-history-01/README.md':'cfbe3eb7b420dcdf1da2f3256a766a063fdf15a66b6405bd670f3760f7c219a3',
 'projects/game-lighting-history-01/script/narration-draft.ko.json':'cc43a3ca98efc2e9f026c575d898898bbfe486678500d047500900523fc29c2f',
 'projects/game-lighting-history-01/script/narration-draft.en.json':'d79e40db8e3f991d008a650ce367642bac0f596ffc9551e7d05ce2eaf63b13db',
 'projects/game-lighting-history-01/script/narration.ko.json':'34117f98a165a1344fd665e3ca99f9426228e94ff4248e4835d5e06910fe091b',
 'projects/game-lighting-history-01/script/narration.en.json':'266f6378a3d2a07a97d7d5787b12f0b3b808c28e4b07579a9411326516474e0f',
 'projects/game-math-planes-barycentric/project.json':'570b22643cabbc09a217683765974f1e404dc2fa9032257f51ebe3bc141a3898',
 'projects/game-math-planes-barycentric/script/narration.ko.json':'4d585e0820d9f04097a4f377c12f478acde5a54b7416594a086a03ce87beeb84',
 'projects/game-math-planes-barycentric/script/narration.en.json':'f3e01729897a9cf38aafb6c0033dbfe4fbf330dda563989dfe9658feba2a74a6',
 'projects/game-math-planes-barycentric/publishing/youtube-upload.json':'7e6249c3ef731db2d69b19ef6695f53d70ae666599d305c4d24e494dab275a4c',
 'projects/game-math-polygons-triangulation/project.json':'9b6d5011fb870f0583672f4ef28b36043f8c1ac30bcc5e7fac68bc15d05ab2ff',
 'projects/game-math-polygons-triangulation/script/narration.ko.json':'b1bb36c15365d44d38b49327438f9af1284d46c562c149f068ad108ddf6ef159',
 'projects/game-math-polygons-triangulation/script/narration.en.json':'6419867b3d347d3095802942aa0a154ac6c1f00df866035dd65626c16f36336a',
 'projects/game-math-polygons-triangulation/sources/SOURCES.md':'a99061e5790ea6b2da55abb8490a3aa12cf5940e4114ea4b987449ef95618f67',
 'projects/game-math-polygons-triangulation/publishing/youtube-upload.json':'9408bbd3d66181f4508f358fb39e1f73c010e2ae8e4eac7d882bbfd6b674d8f0',
}
assert all(sha(ROOT/f)==h for f,h in expected.items()),'An input changed after the direct read; read the new delta first.'
report=ROOT/'production/batches/sakurai-planning-game-design/preflight/player-customization.json'
ax=ROOT/'shared/output/player-customization/research/studio-current-change-v4.ax.txt'
assert ax.exists()
e=dict(schemaVersion=1,slug='player-customization',reviewedAt=now(),
 priorEvidence='projects/player-customization/production/current-lighting-polygons-private-plane-duplicate-rereview-v3.json',
 originalFullSourceAndPrior15LikelyOverlapPairedReviewPreserved=True,
 changedForeignInputsWholeTextDirectlyRead=True,
 foreignFiles=[dict(path=f,sha256=h) for f,h in expected.items()],completeScripts=[],
 comparisons=[
  dict(project='game-lighting-history-01',question='Stored and updated light, visibility/lightmaps, filtering/TBDR, normals, shadow volumes/RNM, shadow maps/CSM, Forward/Deferred/SSAO.',
       distinction='Reread all13 scenes and108 complete KO/EN paragraphs per language and the whole latest source-matched manifest/outline/sources. Read accepted-script metadata and verify every accepted scene exactly equals the directly read draft scenes. New07p4 official DOOM3,08p6 geometry/normal-map diagram,09a count4/0/1/3 and09b material/buffer export preserve rendering questions. These historical renderer examples and storage/evaluation questions differ from player function choice, trial and expression. Foreign TTS input readiness does not approve its final media or ours.'),
  dict(project='game-math-polygons-triangulation',question='Polygon centers, boundary ordering and convexity, fan/ear-clipping validity and triangle quality.',
       distinction='Read the complete current128-paragraph Korean script, including15p1 coordinate4/1 and22p4 areas2/1.5/1.5/2, and whole changed manifest/sources. Reread the later full manifest59015frames/local visual QA passed and the full current uploading-private receipt with actual receipt ID L7SXFwn4i2k, full KOEN descriptions/chapter claims and pending settings. The actual Studio row shows11% uploading/waiting, so private completion is not inferred. The unchanged128-paragraph English full-read evidence is preserved. These geometric algorithm questions differ from previewing a player choice and trying its action.'),
  dict(project='game-math-planes-barycentric',question='Plane distance, normal conventions, triangle area and barycentric weights, coplanarity and attribute interpolation.',
       distinction='Both complete130-paragraph texts remain byte-identical to the prior direct full read. Read current manifest and full saved-private receipt; actual new Studio row agrees on wsxSYEEj8aQ private. Height/color are geometric quantities here; player customization asks which function/action to choose and how to preview, try and express identity. Foreign40:60/noBGM exceptions are not imported.')
 ],
 studio=dict(path=ax.relative_to(ROOT).as_posix(),sha256=sha(ax),observedAt=now(),
   scope='Latest new polygon row directly read after reload:11% uploading, review will begin, waiting. Prior first30/current full source and overlap evidence retained; no claim that all480 rows were reread.',
   newPolygon=dict(receiptVideoId='L7SXFwn4i2k',row='게임수학 Part 2 · 기하 기본 요소 ③ 삼각형의 중심과 다각형',observedState='11% uploading;waiting;review will begin',rowVideoIdLinkObserved=False,privateCompletionInferred=False),
   newVideo=dict(videoId='wsxSYEEj8aQ',title='게임수학 Part 2 · 기하 기본 요소 ② 평면과 무게중심 좌표',observedState='Private uploaded2026.10.8;17:18;1view;no current alert',
       productionReceipt='projects/game-math-planes-barycentric/publishing/youtube-upload.json'),
   userStateChangesPreserved=[dict(videoId='xtUVcAHtQzg',observed='Scheduled2026.10.10'),dict(videoId='PcxaKEvbzjg',observed='Public2026.10.8')],
   settingsChanged=False),foreignFilesModified=False,foreignCommitsCreated=False,
 currentDistinctCheckPassed=False,finalAllocationApproved=False,finalMixedAsrApproved=False,uploaded=False)
for slug,stem,mode in [('game-lighting-history-01','narration','whole-current108-draft-reread-and-accepted-scenes-exactly-identical-metadata-read'),('game-math-polygons-triangulation','narration','ko-whole-current-reread-en-unchanged-prior-full-read'),('game-math-planes-barycentric','narration','unchanged-prior-full-read')]:
    for lang in ['ko','en']:
        f=ROOT/f'projects/{slug}/script/{stem}.{lang}.json';j=read(f)
        e['completeScripts'].append(dict(path=f.relative_to(ROOT).as_posix(),scenes=len(j['scenes']),paragraphs=sum(len(s['lines']) for s in j['scenes']),sha256=sha(f),directReadEvidence=mode))
target=BASE/'current-lighting108-and-polygon-upload-duplicate-rereview-v5.json'
save(target,e)
reason='Preserve original complete source and prior15 full KOEN overlap comparisons and v3 rereads. Reread complete current lighting108KOEN/13scenes with accepted scene equality and full current manifest/outline/sources, including official DOOM3, normal-map geometry diagram, CSM4/0/1/3 and material/buffer export. Reread latest polygon59015frame/local-QA manifest and full new uploading receipt with KOEN chapter descriptions. Actual Studio polygon row11% uploading/waiting; completion not inferred. Rendering storage/evaluation, polygon algorithms and plane interpolation differ from customization function choice, preview, trial and personal expression. Prior wsxSYEEj8aQ private and user states preserved; no foreign settings changed. See projects/player-customization/production/current-lighting108-and-polygon-upload-duplicate-rereview-v5.json.'
cmd=[NODE,'scripts/review-video-duplicates.cjs','player-customization','--decision','distinct','--reason',reason,'--studio-evidence',target.relative_to(ROOT).as_posix()]
r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8');e.update(recordCommand=cmd,recordExitCode=r.returncode,recordOutput=r.stdout+r.stderr)
if r.returncode==0:
    cmd=[NODE,'scripts/review-video-duplicates.cjs','player-customization','--check']
    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8');e.update(checkCommand=cmd,checkExitCode=r.returncode,checkOutput=r.stdout+r.stderr,currentDistinctCheckPassed=r.returncode==0,currentPreflightSha256=sha(report),existingProjects=len(read(report)['existingProjects']))
e['foreignHashChangesDuringReview']=[f for f in e['foreignFiles'] if sha(ROOT/f['path'])!=f['sha256']]
if e['foreignHashChangesDuringReview']:e['currentDistinctCheckPassed']=False
save(target,e)
cp=read(BASE/'latest-checkpoint.json');cp.update(currentDistinctCheckPassed=e['currentDistinctCheckPassed'],currentDuplicateRereview=target.relative_to(ROOT).as_posix());save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization');i.update(currentDistinctCheckPassed=e['currentDistinctCheckPassed'],currentDuplicateRereview=target.relative_to(ROOT).as_posix());q['updatedAt']=now();save(qp,q)
print(json.dumps({k:e.get(k) for k in ['currentDistinctCheckPassed','existingProjects','completeScripts','foreignHashChangesDuringReview','checkOutput']},ensure_ascii=False,indent=2))
assert e['currentDistinctCheckPassed'],'Read the changed input before proceeding.'

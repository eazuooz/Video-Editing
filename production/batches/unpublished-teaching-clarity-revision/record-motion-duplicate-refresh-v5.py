import json, hashlib, subprocess
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
P=ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'
EXPECTED='b4f4dea8dc73cdecf8b78594f6c885e1836e880d9bb726aebb48d473dcecb20e'
changed={
 'projects/game-math-lines-circles-v2/project.json':'4dcdd40dd9d27395a71386113205796d08e0456dedd25476b24df02e7b3609a0',
 'projects/game-math-lines-circles-v2/publishing/youtube-upload.json':'8380a7ca98f4f96943de90f04eeecf8d5839b878a871ec60c98851e57305917f'
}
report=json.loads(P.read_text(encoding='utf-8'))
assert report['inputsDigest']==EXPECTED and len(report['existingProjects'])==74 and len(report['inputFiles'])==451
for p,s in changed.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==s,p
target=R/'inventory-change-direct-review-v5.json';assert not target.exists()
e={
 'schemaVersion':1,'recordedAt':datetime.now(timezone.utc).isoformat(),'inputsDigest':EXPECTED,
 'projectCount':74,'inputCount':451,'previousReportPreserved':'duplicate-history-current74-v4.json',
 'priorFullContentReviewRetained':'inventory-change-direct-review-v4.json',
 'changedFiles':[{'path':p,'sha256':s,'fullCurrentBodyDirectlyRead':True} for p,s in changed.items()],
 'comparison':'The completed lines/circles episode retains the question of connecting two points, parameters and equal-distance positions; its 16-chapter prepared description covers grapple geometry, circle representations, moving centre, beam redirection, dimensionless t versus metre distance, normals and bounds. Motion-sickness teaches player comfort, separating aim from camera movement, reacquiring a goal and reversible settings. Full changed bodies were read; preparation is not an actual new upload.',
 'newForeignReceipt':{'status':'actual-upload-in-progress; private draft saved; technical platform verification pending','actualVideoId':'cOcuxWKHN5g','actualStudioVerified':True,'publishingCompletionAsserted':False},
 'currentStudio':{'url':'https://studio.youtube.com/video/avLKKfQBV_U/edit','cuaTabId':'58','reloaded':True,
  'title':'게임수학 Part 2 · 기하 기본 요소 ① 직선·구·경계 상자','fullDescriptionDirectlyRead':True,
  'observedDescription':'Grapple start and direction; line/segment/ray; sphere and bounds; rotated-box error and safe affine enclosure. All 15 chapter labels through 17:31 membership and complete channel footer directly read.',
  'visibility':'예약됨','sdComplete':True,'hdComplete':True,'saveButtonDisabled':True,'settingsModified':False},
 'newCurrentStudio':{'url':'https://studio.youtube.com/video/cOcuxWKHN5g/edit','cuaTabId':'58',
  'title':'게임수학 Part 2 · 직선과 경계 ① 두 점으로 연결선을 계산하기','fullDescriptionDirectlyRead':True,
  'all16ChapterLabelsDirectlyRead':True,'draftStateObserved':True,'uploadProgressObservedPercent':80,
  'sdProcessingObserved':True,'sdHdCompleteAsserted':False,'privacyBadgeObserved':False,'saveButtonDisabled':True,'settingsModified':False},
 'foreignFilesModified':0,'foreignPublishingModified':0
}
target.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
reason=e['comparison']+' Evidence: '+str(target.relative_to(ROOT)).replace('\\','/')
studio='CUA58 baseline avLKKfQBV_U reloaded: complete title/description/15 chapters, scheduled, SD/HD complete, Save disabled. Then actual new cOcuxWKHN5g entire title/description/16 chapters read; draft, upload 80%, processing pending, Save disabled. Read-only. '+str(target.relative_to(ROOT)).replace('\\','/')
for name,args in [('decision',['--decision','distinct','--reason',reason,'--studio-evidence',studio]),('check',['--check'])]:
 p=subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games',*args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
 print(p.stdout,end='');print(p.stderr,end='');assert p.returncode==0
 e[name+'ExitCode']=p.returncode
assert json.loads(P.read_text(encoding='utf-8'))['inputsDigest']==EXPECTED
target.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'digest':EXPECTED,'evidence':str(target.relative_to(ROOT))}))

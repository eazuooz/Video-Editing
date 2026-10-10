import json, hashlib, subprocess
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
P=ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'
EXPECTED='4439524653b5436425db4c451ba6e4cc536535f7811f36042727d80e91a92954'
changed={
 'projects/game-math-bounds-transform-v2/project.json':'16731ef65c21e885d3f7daa911e5e06c0b69428951a7eeeed2f684a9f8cacdd3',
 'projects/game-math-bounds-transform-v2/publishing/youtube-upload.json':'b04cded07b27ca50472fd2e3539cb819b0a965ea4da85cfce7bc9019309db82c',
 'projects/game-math-lines-circles-v2/project.json':'8c4bac25b2b33677928c6882b731c9e4b9dda719920f7773511b6f695357cce6',
 'projects/game-math-lines-circles-v2/publishing/youtube-upload.json':'7dd12ffdecddb98f9b496ba604082e9e855e79e8d6be8a2930b3cfb76fc7655a'
}
report=json.loads(P.read_text(encoding='utf-8'))
assert report['inputsDigest']==EXPECTED and len(report['existingProjects'])==74 and len(report['inputFiles'])==452
for p,s in changed.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==s,p
target=R/'inventory-change-direct-review-v6.json';assert not target.exists()
e={
 'schemaVersion':1,'recordedAt':datetime.now(timezone.utc).isoformat(),'inputsDigest':EXPECTED,
 'projectCount':74,'inputCount':452,'previousReportPreserved':'duplicate-history-current74-v5.json',
 'priorFullContentReviewRetained':'inventory-change-direct-review-v5.json',
 'changedFiles':[{'path':p,'sha256':s,'fullCurrentBodyDirectlyRead':True} for p,s in changed.items()],
 'comparison':'The two changed manifests and complete KO/EN receipt bodies were directly read. Lines/circles teaches equal-distance points, moved centres, the difference of two endpoints, line/segment/ray domains, dimensionless t versus metre distance and normals. Bounds/transform continues from that connection to sphere interiors, radius scaling, box minima/maxima, axis-wise overlap, broad versus precise checks and affine transformed-box enclosure using abs(A)*e, explicitly excluding perspective and a necessarily tight enclosure of a point set. The motion-sickness revision instead follows the player question of pursuing a goal with less screen turning, separates aim from camera movement, observes goal-reacquisition landmarks, and connects those observations to comfortable camera settings and reversible changes. Shared projected lines or camera mentions do not reproduce either lecture claim or worked calculation. No foreign content or publishing settings changed.',
 'currentStudio':[
  {'url':'https://studio.youtube.com/video/cOcuxWKHN5g/edit','cuaTabId':'58','reloaded':True,
   'title':'게임수학 Part 2 · 직선과 경계 ① 두 점으로 연결선을 계산하기','fullDescriptionDirectlyRead':True,
   'allChapterLabelsDirectlyRead':16,'visibility':'비공개','sdComplete':True,'hdComplete':True,
   'saveButtonDisabled':True,'receiptCompletionDistinguishedFromHumanRights':True,'settingsModified':False},
  {'url':'https://studio.youtube.com/video/W5UkJkep7yo/edit','cuaTabId':'58','directNavigation':True,
   'title':'게임수학 Part 2 · 직선과 경계 ② 물체의 범위와 회전 뒤 경계','fullDescriptionDirectlyRead':True,
   'allChapterLabelsDirectlyRead':25,'draftBannerObserved':'이 동영상은 임시본 상태입니다.',
   'uploadProgressObservedPercent':17,'sdProcessingObserved':True,'sdHdCompleteAsserted':False,
   'privacyBadgeObserved':False,'saveButtonDisabled':True,'settingsModified':False}
 ],
 'foreignFilesModified':0,'foreignPublishingModified':0
}
target.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
reason=e['comparison']+' Evidence: '+str(target.relative_to(ROOT)).replace('\\','/')
studio='CUA58 cOcuxWKHN5g reloaded: full title/description/16 chapters, private, SD/HD complete, Save disabled. Then actual W5UkJkep7yo full title/description/25 chapters read: draft, upload 17%, SD processing; no complete/visibility assertion. Both read-only. '+str(target.relative_to(ROOT)).replace('\\','/')
for name,args in [('decision',['--decision','distinct','--reason',reason,'--studio-evidence',studio]),('check',['--check'])]:
 p=subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games',*args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
 print(p.stdout,end='');print(p.stderr,end='');assert p.returncode==0
 e[name+'ExitCode']=p.returncode
assert json.loads(P.read_text(encoding='utf-8'))['inputsDigest']==EXPECTED
target.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'digest':EXPECTED,'evidence':str(target.relative_to(ROOT))}))

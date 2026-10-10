import json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
P=ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'
EXPECTED='71159110e4b112c501e596057a86c9dad497dd4d92be560586bc189c3ca196b5'
changed={
'projects/game-math-bounds-transform-v2/publishing/youtube-upload.json':'29dd49f41a954441e3a8fa8cbbc4310c7536019db64f1aa1e8cbcdc0867640b3',
'projects/game-math-plane-distances-v2/project.json':'eb03bacf975929b4d754e7707048413339e27a0e1dae0792d3446195725fc58f',
'projects/game-math-plane-distances-v2/script/narration.ko.json':'af16af479e00fa59450b979b4fcfd078fa387f41c98d3b4abd823ea27a7686e8',
'projects/game-math-plane-distances-v2/script/narration.en.json':'3eca98d7089e22f6bee4fed0f0bfbd3fb9a9342ddf35caf29c7fecf4cad08681',
'projects/game-math-planes-teaching-additions-v2/project.json':'a82288553bd6d1fb4119502608aa1f5c0b8727db57fe70d0d4beb7fffcbaedc3',
'projects/game-math-planes-teaching-additions-v2/script/narration.ko.json':'c4ca00cb4af51414debd2b9703d9874bed2d3fdf4b4c074d4715b130f772f53b',
'projects/game-math-planes-teaching-additions-v2/script/narration.en.json':'b70e7bcd25cfb785e734ba835128146f7b19221c9a89c8407b211a2f45badbcb',
'projects/game-math-triangle-addresses-v2/project.json':'4362f80544c297842f61435252958157f3e2e3e82f233d3a6f55848a4c1e95b9',
'projects/game-math-triangle-addresses-v2/script/narration.ko.json':'cca574c87d55024f4a3ba19c41b0efe71c2df5d9104b5d15339e858c7437fffd',
'projects/game-math-triangle-addresses-v2/script/narration.en.json':'b063740cc9d65fbaa36ddb4826f2ed45216b8aae84526803879302e3712a1924'
}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads(P.read_text('utf-8-sig'))
assert report['inputsDigest']==EXPECTED and len(report['existingProjects'])==77 and len(report['inputFiles'])==461
for p,s in changed.items():assert sha(ROOT/p)==s,p
old=json.loads((R/'duplicate-history-current74-v6.json').read_text('utf-8-sig'))
assert old['inputsDigest']=='4439524653b5436425db4c451ba6e4cc536535f7811f36042727d80e91a92954'
e={'schemaVersion':1,'recordedAt':datetime.now(timezone.utc).isoformat(),'inputsDigest':EXPECTED,'projectCount':77,'inputCount':461,
'previousReportPreserved':'duplicate-history-current74-v6.json','priorFullContentReviewRetained':'inventory-change-direct-review-v6.json',
'changedFiles':[{'path':p,'sha256':s,'fullCurrentBodyDirectlyRead':True} for p,s in changed.items()],
'comparison':'All ten changed full files were read, including both full language scripts for all three new projects and the full changed bounds publishing receipt. Plane distances connects bounded candidates to n dot p equals d, scales both normal and offset, distinguishes residual 6 from distance 3 when normal length is 2, and computes closest point (4,2,-3), cross-product area and ordered Newell boundaries. Triangle addresses connects finite platforms to area, weights, outside signs, coplanarity and affine color interpolation, explicitly separating screen projection from off-plane inclusion and future perspective correction. The nineteen additional bilingual bridges explain prerequisites, changed examples and results through Portal 2 surfaces, bounce/speed gel, Faith Plates and tracked illustrative boundaries without claiming game-world measurements. These teach distances and triangle coordinates; the motion revision instead teaches pursuing a target with less view rotation, separates aiming from camera movement, observes reorientation landmarks and connects the result to accessible/reversible camera controls. Shared colored lines, camera mentions and surface vocabulary do not duplicate the worked calculation or viewer question. New manifests remain preparation with no actual platform ID or final approval. No foreign content or settings changed.',
'currentStudio':[
{'url':'https://studio.youtube.com/video/W5UkJkep7yo/edit','cuaTabId':'58','title':'게임수학 Part 2 · 직선과 경계 ② 물체의 범위와 회전 뒤 경계','fullDescriptionDirectlyRead':True,'allChapterLabelsDirectlyRead':25,'draftBannerObserved':'이 동영상은 임시본 상태입니다.','uploadProgressObservedPercent':82,'sdProcessingObserved':True,'sdHdCompleteAsserted':False,'privacyBadgeObserved':False,'saveButtonDisabled':True,'settingsModified':False},
{'url':'https://studio.youtube.com/video/wsxSYEEj8aQ/edit','cuaTabId':'58','directNavigation':True,'title':'게임수학 Part 2 · 기하 기본 요소 ② 평면과 무게중심 좌표','fullDescriptionDirectlyRead':True,'allChapterLabelsDirectlyRead':15,'visibility':'예약됨','sdComplete':True,'hdComplete':True,'saveButtonDisabled':True,'scheduleNotModified':True,'settingsModified':False}],
'foreignFilesModified':0,'foreignPublishingModified':0}
target=R/'inventory-change-direct-review-v7.json';assert not target.exists()
target.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n','utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
reason=e['comparison']+' Evidence: '+target.relative_to(ROOT).as_posix()
studio='CUA58 full W5UkJkep7yo title/description/25 chapters read: draft, upload82%, processing, Save disabled. Then wsxSYEEj8aQ full title/description/15 chapters, scheduled and SDHD complete. Read-only, all foreign settings preserved. '+target.relative_to(ROOT).as_posix()
for name,args in [('decision',['--decision','distinct','--reason',reason,'--studio-evidence',studio]),('check',['--check'])]:
 p=subprocess.run([node,'scripts/review-video-duplicates.cjs','motion-sickness-games',*args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
 print(p.stdout,end='');print(p.stderr,end='');assert p.returncode==0
 e[name+'ExitCode']=p.returncode
assert json.loads(P.read_text('utf-8-sig'))['inputsDigest']==EXPECTED
target.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'digest':EXPECTED,'evidence':target.relative_to(ROOT).as_posix()}))

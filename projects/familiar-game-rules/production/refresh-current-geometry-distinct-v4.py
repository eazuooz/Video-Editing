import json,pathlib,hashlib,datetime,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[3]
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
pre=ROOT/'production/batches/sakurai-planning-game-design/preflight/familiar-game-rules.json'
old=read(pre);changes=read(ROOT/'shared/output/familiar-game-rules/research/duplicate-input-changes-before-final.json')
for f in changes:assert sha(ROOT/f['path'])==f['current']
proof={'schemaVersion':1,'reviewedAt':now,'previousPreflightSha256':sha(pre),'changedFiles':changes,'allChangedFullBodiesDirectlyRead':True,'scope':'3 new foreign projects, full manifests/outline/source/README and all66KO+66ENscenes, 388paragraphs per language; no foreign files edited','comparisons':[
{'slug':'game-math-lines-bounds','koParagraphs':130,'enParagraphs':130,'distinctReason':'Geometric implicit/parametric forms, t domain and distance units, spheres, AABB/OBB, eight-corner versus abs(A)*extents and point-set bounds. Our question concerns familiar control promises, button assignments and continuous/discrete device functions, not coordinate calculations. Shared words aim/direction describe different learner tasks.'},
{'slug':'game-math-planes-barycentric','koParagraphs':130,'enParagraphs':130,'distinctReason':'Plane normals/distance, Newell winding, triangle areas, signed barycentric weights/coplanarity and linear color attributes. No chapter about remapping controls or input-device functionality.'},
{'slug':'game-math-polygons-triangulation','koParagraphs':128,'enParagraphs':128,'distinctReason':'Centroid/incenter/circumcenter, ordered simple boundary/convexity, fan counterexample/ear clipping and coverage. Tile rotation serves geometry examples, not a control-remapping lesson.'}],
'previousActualStudioEvidence':old['studioEvidence'],'noNewUploadReceiptPresentInChangedInputs':True,'foreign40_60NoBgmExceptionNotCopied':True,'newImages':0,'finalVideoApproved':False}
p=PROOF/'current-geometry-projects-distinct-review-v4.json';p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
reason=old['contentReview']+' 新規3기하강의의 전체66KO/66EN장·각388문단과 manifest/outline/source/README를 직접 읽었다. 직선/구/경계상자, 평면/무게중심좌표, 삼각형중심/다각형분할은 수치 기하계산이며 익숙한 조작 약속·버튼배치·연속/이산 장치기능이라는 현재 질문과 구별된다. 다른40:60/무BGM과GPU보류를 보존한다.'
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','familiar-game-rules','--decision','distinct','--reason',reason,'--studio-evidence',p.relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
subprocess.run([node,'scripts/review-video-duplicates.cjs','familiar-game-rules','--check'],cwd=ROOT,check=True)

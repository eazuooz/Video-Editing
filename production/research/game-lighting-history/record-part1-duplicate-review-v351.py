"""Record the directly read four-file orientation delta and refresh own preflight."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess

ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'production/research/game-lighting-history'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
delta=read(R/'local/part1-duplicate-delta-v350/changes.json')
expected={
 'projects/game-math-orientation-matrices/project.json':'89080bac469e0a598b99552ab3eb55a20509c6ec81f5ecaae0803396e887fdfb',
 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1/publishing/youtube-upload-v1.json':'fccaca1283848d0069d79d2748ae25cb408ca7e0776e4b70467fdfe2254d58cd',
 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1/script/current34-combined-v1.en.json':'3251464551192f1d7ab506f5673a37d426e86a4c76264c7a3453f38e5b5c9d23',
 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1/script/current34-combined-v1.ko.json':'89b16db38deb88e8da85011aa19c25cf9512e142eee61082c8bec0c27deea376'}
assert {d['path']:d['current'] for d in delta}==expected
assert all(sha(ROOT/p)==s for p,s in expected.items())
studio=R/'local/part1-duplicate-delta-v350/orientation-current-studio.ax.txt'
text=studio.read_text(encoding='utf-8')
for term in ('orq0TMVkFts','방향과 회전 행렬','Superflight','Descenders','Trailmakers','Space Engineers','비공개','검토 중','(disabled) 저장'):
 assert term in text,term
reason=('Previous full89-project content review and subsequent current changes retained. Read every current34 KO and34 EN orientation scene,180 lines per language, active manifest and receipt. The orientation lesson distinguishes direction and full body pose, local-to-world column axes, inverse by transpose, composition, orthonormal/determinant tests, Gram-Schmidt, storage and matrix blending through Superflight, Descenders, Trailmakers and Space Engineers. Physical04-1 instead teaches shadow-page addresses, texture/memory/geometry budgets, temporal reconstruction validity and mobile renderer data. Same mathematical vocabulary does not repeat the viewer question or causal chapter claims. Actual current Studio orq0TMVkFts title and entire Korean description/chapter body read: private, SD/HD complete, automatic review pending. No foreign file or Studio setting changed. All four changed file hashes rechecked before recording.')
record={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),'physicalPart':'game-lighting-history-04-1','previousFullInventoryReview':{'path':rel(R/'part1-current-duplicate-direct-review-v204.json'),'sha256':sha(R/'part1-current-duplicate-direct-review-v204.json')},'changedInputs':delta,'allChangedFullBodiesDirectlyRead':True,'scriptCoverage':{'koScenes':34,'enScenes':34,'koLines':180,'enLines':180,'directReadCompletion':'Initial whole-script output plus KO17-24 and EN01-04 explicitly read to cover truncated output.'},'currentForeignViewerQuestion':'Same facing direction but different complete body pose: represent and verify local/world rotation axes.','fourForeignGames':['Superflight','Descenders','Trailmakers','Space Engineers'],'currentOwnViewerQuestion':'How do shadow addresses, limited memory, temporal samples and mobile dataflow produce an image?','mathChecksRead':['right-handed x cross y = z; column local-to-world convention','positive z90: (2,1,0) becomes (-1,2,0)','inverse pure orthonormal R is transpose; determinant +1 excludes reflection','child-to-parent B then parent-to-world A means AB, rightmost first','half identity and z180 produces diag(0,0,1), not a rotation','world(4,5,0)-origin(3,3,0)=(1,2,0); inverse z90 -> (2,-1,0)'],'foreignExceptionsPreserved':'Foreign lecture actual40/explanation60 and noBGM do not change our measured60:40/Nimbus.','actualStudio':{'id':'orq0TMVkFts','url':'https://studio.youtube.com/video/orq0TMVkFts/edit','title':'게임수학 Part 2 · 3D 회전 ① 방향과 회전 행렬','entireDescriptionAndChaptersRead':True,'privateObserved':True,'sdHdComplete':True,'automaticReview':'pending','saveDisabled':True,'rawEvidence':{'path':rel(studio),'sha256':sha(studio),'localOnly':True}},'foreignFilesEdited':False,'foreignStudioMutated':False,'candidate':{'path':rel(R/'candidate-04-1.json'),'sha256':sha(R/'candidate-04-1.json')},'verdict':'distinct','reason':reason}
out=R/'part1-current-duplicate-direct-review-v351.json'
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
base=[node,'scripts/review-video-duplicates.cjs','game-lighting-history-04-1','--candidate-file',rel(R/'candidate-04-1.json')]
subprocess.run(base+['--decision','distinct','--reason',reason,'--studio-evidence',rel(out)],cwd=ROOT,check=True)
subprocess.run(base+['--check'],cwd=ROOT,check=True)
print(json.dumps({'review':rel(out),'changedFiles':len(delta),'foreignMutations':0,'currentDistinctChecked':True},ensure_ascii=False))

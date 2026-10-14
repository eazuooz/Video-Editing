"""Preserve V1 detail renders; repair the baseline header rule crossing subtitle."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
M=ROOT/'manim/projects/game-math-orientation-matrices'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def create(p,t):
 assert not p.exists(),p
 p.write_text(t,'utf-8')
def save(p,v):create(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
s=rd(O/'current34-detailed-explanation-render-execution-v1.json')
assert s['workerDead'] and s['actualOuterExitCode']==0 and len(s['scenes'])==17
proof=rd(O/'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
base=M/'teaching_baseline_detailed_v1.py';text=base.read_text('utf-8-sig')
old="title=fit(txt(s['title'],40),12.65).to_corner(UL,buff=.6)"
new="title=fit(txt(s['title'],40),12.65).move_to([-6.4,3.36,0],aligned_edge=LEFT)"
assert text.count(old)==1;text=text.replace(old,new)
old="sub=fit(txt(f'게임수학 Part 2 / 3D 회전 {data[\"part\"]}편  ·  오른손 / 열벡터 / R: 로컬 → 월드',20,MUTED),12.65).next_to(title,DOWN,aligned_edge=LEFT,buff=.14)"
new="sub=fit(txt(f'게임수학 Part 2 / 3D 회전 {data[\"part\"]}편  ·  오른손 / 열벡터 / R: 로컬 → 월드',20,MUTED),12.65).move_to([-6.4,2.9,0],aligned_edge=LEFT)"
assert text.count(old)==1;text=text.replace(old,new)
old="Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1)"
assert text.count(old)==1;text=text.replace(old,"Line([-6.5,2.6,0],[6.5,2.6,0],color=RULE,stroke_width=1)")
newbase=M/'teaching_baseline_detailed_v2.py';create(newbase,text)
ids=['03','04','06','07','09','10','13','15','16','21','22']
aggregate=M/'teaching_detailed_header_repair_v2.py'
create(aggregate,"from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parent))\nfrom teaching_baseline_detailed_v2 import LectureScene\n"+'\n'.join(f"DetailedScene{i}=type('DetailedScene{i}',(LectureScene,),{{'sid':'{i}','slug':'game-math-orientation-matrices','__module__':__name__}})" for i in ids)+'\n')
prior=rd(O/'current34-detailed-explanation-timing-v1.json')
plan=dict(prior);plan.update(preparedAt=datetime.now(timezone.utc).isoformat(),code=rel(aggregate),codeSha256=sha(aggregate),scenes=[x for x in prior['scenes'] if x['id'] in ids],assets=[dict(path=rel(p),sha256=sha(p)) for p in [aggregate,newbase,M/'detailed_subjects_v1.py']],change='Header title/subtitle/rule positions only; geometry, mathematics, PCM, beat timing and durations unchanged.',sourceVersion1Sha256=sha(base),normalPlaybackApproved=False,finalMovingPixelsApproved=False)
save(O/'current34-detailed-header-repair-timing-v2.json',plan)
worker=(B/'render-orientation-detailed-explanations-v1.py').read_text('utf-8-sig')
for before,after in [('current34-detailed-explanations-v1','current34-detailed-header-repair-v2'),('teaching_detailed_explanations_v1.py','teaching_detailed_header_repair_v2.py'),('current34-detailed-explanation-timing-v1.json','current34-detailed-header-repair-timing-v2.json'),('current34-detailed-explanation-render-execution-v1.json','current34-detailed-header-repair-render-execution-v2.json'),('len(plan[\'scenes\'])==17','len(plan[\'scenes\'])==11'),('seventeen','eleven'),('all17','all11')]:worker=worker.replace(before,after)
create(B/'render-orientation-detailed-header-repair-v2.py',worker)
recorder=(B/'record-orientation-detailed-explanation-worker-v1.py').read_text('utf-8-sig').replace('current34-detailed-explanation-render-execution-v1','current34-detailed-header-repair-render-execution-v2').replace("len(s['scenes'])==17","len(s['scenes'])==11").replace('all17','all11')
create(B/'record-orientation-detailed-header-worker-v2.py',recorder)
sample=next(x for x in s['scenes'] if x['id']=='03')['samples'][4]
assert sha(ROOT/sample['path'])==sample['sha256']
save(O/'detailed-header-layout-held-review-v1.json',dict(reviewedAt=datetime.now(timezone.utc).isoformat(),execution=rel(O/'current34-detailed-explanation-render-execution-v1.json'),executionSha256=sha(O/'current34-detailed-explanation-render-execution-v1.json'),directlyReadSample=sample,observation='The fixed header rule crosses the gray subtitle in the original baseline header. Detailed aircraft canopy/wings/tail/engines are visible; header layout held until repaired moving pixels are read.',subjectDetailSampled=True,wholeSceneApproved=False,affectedBaselineScenes=ids,repairPreparedOnly=True,repairTiming=rel(O/'current34-detailed-header-repair-timing-v2.json'),preservedRevisionScenes=['12','06a','09a','13a','16a','21a'],newTts=0,newImageGit=0))
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
print(json.dumps(dict(prepared=True,headerScenes=11,originalLessonUnchanged=True,newTts=0,renderStarted=False)))

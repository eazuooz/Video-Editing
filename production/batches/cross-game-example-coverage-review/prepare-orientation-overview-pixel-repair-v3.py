"""Preserve held encoded V2; repair diagram scale, label alignment and inverse axes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,py_compile
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
state=rd(O/'current34-overview-render-execution-v2.json');assert state['actualOuterExitCode']==0 and state['workerDead']
src=ROOT/'manim/projects/game-math-orientation-matrices/teaching_overview_revision_v1.py';dst=src.with_name('teaching_overview_revision_v2.py');assert not dst.exists()
code=src.read_text('utf-8')
replacements={
 "left=np.array([-2.8,-1.7,-.28]);right=left+np.array([2.0,1.8,0])":"left=np.array([-2.6,-2.7,-.4]);right=np.array([2.6,2.7,-.4])",
 "a=body(np.eye(3),left,.85);b=body(np.eye(3),right,.85)":"a=body(np.eye(3),left,1.65);b=body(np.eye(3),right,1.65)",
 "left+1.9*P[:,2]":"left+2.7*P[:,2]",
 "right+1.9*P[:,2]":"right+2.7*P[:,2]",
 "self.fixed(txt('같은 앞 방향 · 서로 다른 몸의 기울기',24,BLUE).move_to([0,-2.3,0]))":"self.comparison_label=txt('같은 앞 방향 · 서로 다른 몸의 기울기',24,BLUE).move_to([0,-2.3,0]);self.fixed(self.comparison_label)",
 "basis(np.eye(3),left,1.4,with_body=False);turned=basis(rz(PI/3),right,1.4,with_body=False)":"basis(np.eye(3),left,2.25,with_body=False);turned=basis(rz(PI/3),right,2.25,with_body=False)",
 "self.play(Rotate(b,angle=-PI/3,axis=P[:,2],about_point=right),run_time=.9)":"self.play(Rotate(b,angle=-PI/3,axis=P[:,2],about_point=right),Rotate(turned,angle=-PI/3,axis=P[:,2],about_point=right),run_time=.9)\n                self.remove(self.comparison_label);self.fixed(txt('몸과 세 축이 같은 자세로 되돌아온 결과',24,BLUE).move_to([0,-2.3,0]))",
 "origins=[np.array([-3.3,-2.2,-.5]),np.array([-1.1,-.3,-.5]),np.array([1.15,1.6,-.5]),np.array([3.4,3.5,-.5])]":"camera_right=np.array([-np.sin(-48*DEGREES),np.cos(-48*DEGREES),0]);origins=[camera_right*x/.83+np.array([0,0,-.35]) for x in [-4.9,-1.65,1.65,4.9]]",
 "logical_box([1.55,.12,1.3],[0,-.45,0],PALE)":"logical_box([1.9,.12,1.7],[0,-.5,0],PALE)",
 "body(np.eye(3),o,.58)":"body(np.eye(3),o,.95)",
 "bicycle(o).scale(.72,about_point=o)":"bicycle(o).scale(.95,about_point=o)",
 "logical_box([1.25,.18,.95],[0,0,0],BLUE);part=logical_box([.45,.55,.45],[.35,.4,0],ORANGE)":"logical_box([1.5,.18,1.1],[0,0,0],BLUE);part=logical_box([.55,.7,.55],[.35,.47,0],ORANGE)",
 "axis=P[:,1],about_point=origins[3]":"axis=P[:,1],about_point=models[3][1].get_center()",
 "origin=np.array([-2.45,-2.45,-.28]);obj=basis(np.eye(3),origin);self.add(obj)":"origin=np.array([-2.45,-2.45,-.6]);obj=basis(np.eye(3),origin,2.7);obj[0].scale(1.65,about_point=origin);self.add(obj)",
}
for a,b in replacements.items():assert a in code,a;code=code.replace(a,b)
dst.write_text(code,'utf-8');py_compile.compile(str(dst),doraise=True)
plan=rd(O/'current34-overview-timing-plan-v1.json');plan.update(code=rel(dst),codeSha256=sha(dst),pixelRepair='Larger projected models, matching icon/label projection, and inverse body/axes together. Original voice, frame counts and palette unchanged.')
tp=O/'current34-overview-timing-plan-v2.json';assert not tp.exists();tp.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
worker=B/'render-orientation-overview-v3.py';assert not worker.exists()
worker.write_text((B/'render-orientation-overview-v2.py').read_text('utf-8').replace('orientation/current34-overview-v2','orientation/current34-overview-v3').replace('teaching_overview_revision_v1.py','teaching_overview_revision_v2.py').replace('current34-overview-timing-plan-v1.json','current34-overview-timing-plan-v2.json').replace('current34-overview-render-execution-v2.json','current34-overview-render-execution-v3.json'),'utf-8');py_compile.compile(str(worker),doraise=True)
rec=B/'record-orientation-overview-worker-v3.py';assert not rec.exists();rec.write_text((B/'record-orientation-overview-worker-v2.py').read_text('utf-8').replace('current34-overview-render-execution-v2','current34-overview-render-execution-v3'),'utf-8');py_compile.compile(str(rec),doraise=True)
held=O/'current34-overview-pixel-held-review-v2.json';assert not held.exists()
held.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),renderExecution=rel(O/'current34-overview-render-execution-v2.json'),renderExecutionSha256=sha(O/'current34-overview-render-execution-v2.json'),actualSession=53542,actualOuterExitCode=0,actualCompletion='09092e',directBoardsRead=['scene-01/board-01.png','scene-01/board-04.png','scene-01/board-07.png','scene-01b/board-02.png'],directImageToolChunks=['815871','681eb5'],all110SamplesAnd20BoardsRead=False,approved=False,observations=['Opening model occupies too little screen space for the central comparison.','Opening inverse beat rotates body to neutral while axes remain at previous60degree attitude; held conceptual mismatch.','Four-game overview icon positions differ from fixed labels and airplane icon is small.','Conclusion model enlargement prepared; previous output retained.'],v3RepairPrepared=True,newRenderStarted=False,originalPcmChanged=False,newImageGit=0),ensure_ascii=False,indent=2)+'\n','utf-8')
print('PreparedV3 exact pixel repairs; retainedV2 successful technical output as held, voice unchanged.')

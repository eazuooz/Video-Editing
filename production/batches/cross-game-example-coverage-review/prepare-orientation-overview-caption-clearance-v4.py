"""Preserve sampled depth repair and move own notes above fixed caption clearance."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
s=rd(O/'current34-overview-render-execution-v3.json')
assert s['actualOuterExitCode']==s['exitCode']==0 and s['workerDead']
code=ROOT/'manim/projects/game-math-orientation-matrices/teaching_overview_revision_v2.py'
new=code.with_name('teaching_overview_revision_v3.py');assert not new.exists()
text=code.read_text('utf-8-sig')
changes=[
 ("move_to([0,-2.3,0]);self.fixed(self.comparison_label)","move_to([0,-1.85,0]);self.fixed(self.comparison_label)"),
 ("move_to([0,-2.65,0])","move_to([0,-2.25,0])"),
 ("move_to([0,-2.3,0]))","move_to([0,-1.70,0]))"),
 ("move_to([0,-1.9,0]))","move_to([0,-1.20,0]))"),
 ("이 개요의 모형은 설명이며 실제 게임 예시 시간에 포함하지 않습니다.","게임마다 모양과 규칙은 달라도 같은 기준으로 자세를 비교합니다."),
 ("move_to([0,-2.5,0]))","move_to([0,-2.2,0]))")]
for before,after in changes:
 assert before in text,before
 text=text.replace(before,after)
new.write_text(text,'utf-8')
tp=O/'current34-overview-timing-plan-v3.json';assert not tp.exists()
t=rd(O/'current34-overview-timing-plan-v2.json');t.update(code=rel(new),codeSha256=sha(new),pixelRepair='Preserve V3 larger models and paired inverse body/axes. Move lower notes above two-line boxed fixed captions; replace production quota note with concept comparison. Original PCM/frames unchanged.')
tp.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n','utf-8')
for stem in ['render-orientation-overview','record-orientation-overview-worker']:
 target=B/(stem+'-v4.py');assert not target.exists()
 src=(B/(stem+'-v3.py')).read_text('utf-8-sig')
 src=src.replace('current34-overview-v3','current34-overview-v4').replace('current34-overview-render-execution-v3','current34-overview-render-execution-v4').replace('teaching_overview_revision_v2.py','teaching_overview_revision_v3.py').replace('current34-overview-timing-plan-v2.json','current34-overview-timing-plan-v3.json')
 target.write_text(src,'utf-8')
out=O/'current34-overview-sampled-held-review-v3.json';assert not out.exists()
for row in s['scenes']:
 assert sha(ROOT/row['output'])==row['outputSha256']
 for v in row['samples']+row['boards']:assert sha(ROOT/v['path'])==v['sha256']
review=dict(recordedAt=datetime.now(timezone.utc).isoformat(),execution='current34-overview-render-execution-v3.json',actualSession=35944,actualCompletion='3126e0',actualOuterExitCode=0,all110SamplesReadOn20Boards=True,fullResolutionSpotFrames=['scene01 frame035','scene01b frame010','scene24 frame038'],projectedFacesAndModelLabelsReadable=True,inverseBodyAndAxesTogetherObserved=True,gameOrderLabelsAligned=True,heldReason='Scene01 lower legend reaches the fixed two-line caption clearance. Lower scene24/01b notes also shifted up before final compositing. V4 preserves current geometry and repairs only own lower notes.',finalCaptionPixelsApproved=False,allIntermediateFramesApproved=False,normalPlaybackApproved=False,all79ProtectedUnchanged=True,newImageGit=0,rows=s['scenes'])
out.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(v3Samples=110,boards=20,heldForCaptionClearance=True,v4Prepared=True,renderStarted=False)))

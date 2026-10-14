"""Preserve old pixels, repair observed label collisions, seal measured timing."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math,wave
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):
 assert not p.exists(),p;p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
at=datetime.now(timezone.utc).isoformat();old=read(O/'structural-prototype-execution-v1.json');assert old['actualOuterExitCode']==0
rows=[x for x in old['scenes'] if x['id'] in ['12','18']]
for r in rows:
 for p,h in [(r['output'],r['outputSha256'])]+[(x['path'],x['sha256']) for x in r['samples']+r['boards']]:assert sha(ROOT/p)==h
save(O/'structural-12-18-prototype-held-direct-review-v1.json',dict(reviewedAt=at,actualSession=old['sessionId'],actualOuterExitCode=0,actualCompletion=old['actualOuterExitObservedChunk'],all84SamplesAnd15BoardsDirectlyRead=True,allHashesMatched=True,rows=rows,findings={'12':'World-axis legend and parent/child legend overlap throughout all40 sampledframes. AB/BA values are correct, parent-child changes visible, but labels held.','18':'Matrix36B intersects the matrix cubes. Quaternion cubes cover component/DOF labels. All44 samples read. Counts9/3/4 and36/12/16 are correct; readability held.'},approved=False,continuousAllFramesApproved=False,humanListeningApproved=False,finalCaptionApproval=False))
src=ROOT/'manim/projects/game-math-orientation-matrices/teaching_revision_v1.py';assert sha(src)==old['codeSha256'];code=src.read_text('utf-8')
code=code.replace("move_to([-3.2,-2.2,0])","move_to([-3.2,-2.55,0])")
start=code.index('    def storage(self,slot,beats):');end=code.index("\nfor sid in",start)
new='''    def storage(self,slot,beats):
        # Explicit oblique projection of 3D cube front/top/right faces. Fixed
        # camera-space layout separates every label from geometry and captions.
        def cell(x,y,color):
            a=np.array([x-.235,y-.235,0]); b=np.array([x+.235,y-.235,0])
            c=np.array([x+.235,y+.235,0]); d=np.array([x-.235,y+.235,0])
            depth=np.array([.16,.12,0])
            top=Polygon(d,c,c+depth,d+depth,fill_color=interpolate_color(ManimColor(color),WHITE,.25),fill_opacity=1,stroke_color=WHITE,stroke_width=1)
            side=Polygon(b,c,c+depth,b+depth,fill_color=interpolate_color(ManimColor(color),BLACK,.22),fill_opacity=1,stroke_color=WHITE,stroke_width=1)
            front=Polygon(a,b,c,d,fill_color=color,fill_opacity=1,stroke_color=WHITE,stroke_width=1)
            return VGroup(side,top,front)
        arrays=[]
        for n,cols,x,color in [(9,3,-4.1,BLUE),(3,3,0,GREEN),(4,2,4.1,GOLD)]:
            grid=VGroup(*[cell(x+((j%cols)-(cols-1)/2)*.72,-.5+((j//cols)-(n//cols-1)/2)*.72,color) for j in range(n)])
            self.fixed(grid);arrays.append(grid)
        self.fixed(txt('Matrix / 36 B',30,BLUE).move_to([-4.1,1.05,0]),
                   txt('Euler / 12 B',30,GREEN).move_to([0,1.05,0]),
                   txt('Quaternion / 16 B',30,GOLD).move_to([4.1,1.05,0]),
                   txt('한 칸 = float32 성분 4 B',24,MUTED).move_to([0,-2.15,0]),
                   txt('성분 수와 회전 자유도를 구분',24,MUTED).move_to([0,-2.55,0]))
        for i,beat in enumerate(beats):
            self.wait_until(slot['lineStarts'][i]);self.fixed_note(beat,GREEN if i==5 else BLUE)
            if i==0:self.play(Indicate(arrays[0],color=GOLD,scale_factor=1.12),run_time=.6)
            if i==1:self.fixed(txt('회전 자유도 = 3',26,ORANGE).move_to([0,-1.72,0]))
            if i==2:self.play(Indicate(arrays[0],color=BLUE,scale_factor=1.12),Indicate(arrays[1],color=GREEN,scale_factor=1.12),run_time=.7)
            if i==3:self.play(Indicate(arrays[2],color=GOLD,scale_factor=1.12),run_time=.7)
'''
code=code[:start]+new+code[end:];v2=src.with_name('teaching_revision_v2.py');assert not v2.exists();v2.write_text(code,'utf-8')
starts={'06a':[0,3.68,7.8],'09a':[0,3.62,8.42,10.54],'13a':[0,3.28,6.86,11.66],'16a':[0,6.1,8.7,11.18],'21a':[0,5.66,11.6]};scenes=[]
for sid in starts:
 if sid=='21a':
  p=read(O/'21a-spliced-whole-and-seam-direct-review-v1.json');assert p['current21aCompletenessApproved'];wav=ROOT/p['new21aAdoptedPath'];words=read(O/'post-splice-current-voice-asr-v1/21a-spliced-whole.json')['chunks'];secs=p['seconds'];proof=O/'21a-spliced-whole-and-seam-direct-review-v1.json'
 else:
  p=read(O/'additions-whole-asr-v1'/f'{sid}.json');wav=ROOT/p['sourcePath'];assert sha(wav)==p['sourceSha256'];words=p['words'];secs=p['seconds'];proof=O/'additions-whole-and-independent-direct-review-v1.json'
 assert all(any(abs(w['timestamp'][0]-t)<.001 for w in words) for t in starts[sid])
 frames=math.ceil(secs*60);scenes.append(dict(id=sid,voicePath=rel(wav),voiceSha256=sha(wav),voiceSeconds=secs,frames=frames,seconds=frames/60,lineStarts=starts[sid],currentVoiceReview=rel(proof),currentVoiceReviewSha256=sha(proof)))
timingp=ROOT/'shared/output/narration/game-math-orientation-matrices/qwen3-1.7b-balanced-v1/game-math-orientation-matrices-qwen3-1.7b-balanced-v1.timing.json';timing=read(timingp)
for sid,frames in [('12',1961),('18',2216)]:
 entries=[x for x in timing['entries'] if x['scene_id']==sid];base=entries[0]['start'];line=[round(e['start']-base,8) for e in entries]
 r=next(x for x in read(O/'structural-prototype-timing-v1.json')['scenes'] if x['id']==sid);assert all(abs(a-b)<.00001 for a,b in zip(line,r['lineStarts']))
 wav=ROOT/'shared/output/narration/game-math-orientation-matrices/qwen3-1.7b-balanced-v1/chunks'/f'{sid}-scene.wav';scenes.append(dict(id=sid,frames=frames,seconds=frames/60,lineStarts=line,voicePath=rel(wav),voiceSha256=sha(wav),retainedOriginalTiming=True,baselineTiming=rel(timingp),baselineTimingSha256=sha(timingp),expectedKo=[e['text'] for e in entries]))
tp=O/'measured-manim-timing-v2.json';save(tp,dict(preparedAt=at,narrationTimedNewBridges=True,source='Current measuredPCM and whole/independent word landmarks; current21a splice reviewed; original12/18 timing preserved.',finalBodyTimingApproved=False,code=rel(v2),codeSha256=sha(v2),baselineCode=rel(src),baselineCodeSha256=sha(src),scenes=scenes))
save(O/'measured-manim-preparation-v2.json',dict(preparedAt=at,old12And18HeldReview='structural-12-18-prototype-held-direct-review-v1.json',timing=rel(tp),timingSha256=sha(tp),code=rel(v2),codeSha256=sha(v2),changes=['12 parent/child label moves below axis legend.','18 explicitly projected front/top/right cell faces laid out in screen coordinates; labels above, DOF/unit labels below.','Five bridge animations use measured narration starts, including current21a separate splice.'],renderStarted=False,originalLessonAnd24PcmChanged=False,allMovingPixelsApproved=False,finalCuePixelsApproved=False))
print(json.dumps(dict(timing=rel(tp),sceneFrames=[(x['id'],x['frames']) for x in scenes],oldLabelsHeld=True,preparedOnly=True)))

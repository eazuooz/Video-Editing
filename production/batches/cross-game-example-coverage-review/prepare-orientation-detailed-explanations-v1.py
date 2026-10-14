"""Visual-only subject replacement, retaining current PCM and measured timing."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
MD = ROOT / 'manim/projects/game-math-orientation-matrices'
rd = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()

def create(p, text):
    assert not p.exists(), p
    p.write_text(text, 'utf-8')

def jsave(p, obj):
    create(p, json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

protected = rd(O/'narration-07b-guide-repair-execution-v1.json')
for row in protected['protectedInputs'] + protected['results']:
    assert sha(ROOT/row['path']) == row['sha256']
assert rd(O/'current34-overview-render-execution-v5.json')['workerDead']
assert rd(O/'latest-checkpoint.json')['activeOwnedWorkers'] == 0

base = ROOT/'manim/projects/game-math-part2-full-series/lesson.py'
baseline = base.read_text('utf-8-sig')
begin = baseline.index('def body(R,origin,scale=1.2):')
end = baseline.index('def basis(', begin)
replacement = '''sys.path.insert(0, str(ROOT/'manim/projects/game-math-orientation-matrices'))
from detailed_subjects_v1 import aircraft
def body(R,origin,scale=1.2):
 return aircraft(R,origin,scale)
'''
baseline = baseline.replace('import os,json,math', 'import os,json,math,sys')
begin = baseline.index('def body(R,origin,scale=1.2):')
end = baseline.index('def basis(', begin)
baseline = baseline[:begin] + replacement + baseline[end:]
baseline_path = MD/'teaching_baseline_detailed_v1.py'
create(baseline_path, baseline)

revision_path = MD/'teaching_revision_detailed_v1.py'
original_revision = MD/'teaching_revision_v2.py'
revision = original_revision.read_text('utf-8-sig')
revision = revision.replace("sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))", "sys.path.insert(0,str(ROOT/'manim/projects/game-math-orientation-matrices'))")
revision = revision.replace('from lesson import P,body,basis,arrow,rx,rz,txt,fit,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD',
    'from teaching_baseline_detailed_v1 import P,body,basis,arrow,rx,rz,txt,fit,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD\nfrom detailed_camera_subject_v1 import camera_part')
revision = revision.replace('child=body(B,o+P@offset,.48);child.set_color(ORANGE);self.add(child)',
    'child=camera_part(B,o+P@offset,.48);self.add(child)')
revision = revision.replace('target_child=body(A@B,o+P@A@offset,.48);target_child.set_color(ORANGE)',
    'target_child=camera_part(A@B,o+P@A@offset,.48)')
create(revision_path, revision)
create(MD/'detailed_camera_subject_v1.py', '''"""Original mounted camera illustration; not a measured game component."""
import numpy as np
from manim import VGroup, Circle, Line
from detailed_subjects_v1 import solid_profile, capsule, placed, ORANGE, INK, LIGHT
def camera_part(R, origin, scale=1):
    housing=solid_profile([[-.31,0,-.30],[.31,0,-.30],[.38,0,-.17],[.38,0,.21],
                           [.25,0,.31],[-.25,0,.31],[-.38,0,.21],[-.38,0,-.17]],.43,ORANGE)
    lens=capsule([0,0,.28],[0,0,.65],.18,INK)
    glass=Circle(radius=.145,color=LIGHT,fill_color='#31546e',fill_opacity=1,stroke_width=1.4).shift([0,0,.66])
    mount=capsule([0,-.25,-.03],[0,-.48,-.03],.085,INK)
    trim=VGroup(Line([-.22,.22,-.17],[.22,.22,-.17],color=INK,stroke_width=1.3),
                Line([-.25,.22,.10],[.25,.22,.10],color=LIGHT,stroke_width=1.3))
    return placed(VGroup(housing,lens,glass,mount,trim),R,origin,scale)
''')

base_ids = ['03','04','06','07','09','10','13','15','16','21','22']
revision_ids = ['06a','09a','13a','16a','21a','12']
aggregate = MD/'teaching_detailed_explanations_v1.py'
create(aggregate, '''"""Scoped scene classes only; no original lesson edits."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from teaching_baseline_detailed_v1 import LectureScene
from teaching_revision_detailed_v1 import TeachingRevision
''' + '\n'.join(f"DetailedScene{sid}=type('DetailedScene{sid}',({'LectureScene' if sid in base_ids else 'TeachingRevision'},),{{'sid':'{sid}','slug':'game-math-orientation-matrices','__module__':__name__}})" for sid in base_ids+revision_ids) + '\n')

current = rd(O/'current34-measured-timing-plan-v1.json')
voice_timing = ROOT/'shared/output/narration/game-math-orientation-matrices/qwen3-1.7b-balanced-v1/game-math-orientation-matrices-qwen3-1.7b-balanced-v1.timing.json'
original_timing = rd(voice_timing)
old_revision_timing = rd(O/'measured-manim-timing-v2.json')
rows = []
for sid in ['12', *base_ids, *revision_ids[:-1]]:
    source = next(s for s in current['scenes'] if s['id']==sid)
    if sid in base_ids:
        entries=[e for e in original_timing['entries'] if e['scene_id']==sid]
        line_starts=[round(e['start']-entries[0]['start'],8) for e in entries]
    else:
        prior=next(s for s in old_revision_timing['scenes'] if s['id']==sid)
        assert prior['frames']==source['frames']
        line_starts=prior['lineStarts']
    rows.append(dict(id=sid,frames=source['frames'],seconds=source['frames']/60,
        lineStarts=line_starts,voice=source['voice'],voiceSha256=source['voiceSha256'],
        subject='aircraft with separately mounted camera' if sid=='12' else 'detailed illustrative aircraft',
        features=['tapered fuselage','cockpit canopy','swept wings','tailplane and fin','engine intakes','panel seams'],
        action='Retained narration-ordered rotation, axis reveal, composition or deformation.',
        captionCenter=[960,970],gameWorldMeasurement=False))
assets=[aggregate,baseline_path,revision_path,MD/'detailed_camera_subject_v1.py',MD/'detailed_subjects_v1.py']
tp=O/'current34-detailed-explanation-timing-v1.json'
jsave(tp,dict(preparedAt=datetime.now(timezone.utc).isoformat(),visualOnly=True,newTts=0,
    code=rel(aggregate),codeSha256=sha(aggregate),assets=[dict(path=rel(p),sha256=sha(p)) for p in assets],
    baselineCode=rel(base),baselineCodeSha256=sha(base),retainedRevisionCode=rel(original_revision),
    retainedRevisionCodeSha256=sha(original_revision),scenes=rows,
    retainedAbstractScenes={'18':'Matrix/Euler/quaternion storage cells are actual geometric storage diagrams.','19':'Syntax-colored transformation code is the actual instructional subject.'},
    finalMovingPixelsApproved=False,finalCaptionPixelsApproved=False))

worker=(B/'render-orientation-overview-v5.py').read_text('utf-8-sig')
worker=worker.replace('current34-overview-v5','current34-detailed-explanations-v1')
worker=worker.replace('teaching_overview_revision_v5.py','teaching_detailed_explanations_v1.py')
worker=worker.replace('current34-overview-timing-plan-v5.json','current34-detailed-explanation-timing-v1.json')
worker=worker.replace('current34-overview-render-execution-v5.json','current34-detailed-explanation-render-execution-v1.json')
worker=worker.replace("os.environ['ORIENTATION_OVERVIEW_TIMING']=str(T)","os.environ['ORIENTATION_REVISION_TIMING']=str(T);os.environ['MATH_RENDER_TIMING']=str(T)")
worker=worker.replace('OverviewScene','DetailedScene')
worker=worker.replace("assert sha(ROOT/plan['assetLibrary'])==plan['assetLibrarySha256'];assert [s['id'] for s in plan['scenes']]==['01','01b','24']", "assert len(plan['scenes'])==17\nfor asset in plan['assets']:assert sha(ROOT/asset['path'])==asset['sha256']")
worker=worker.replace("for s in sorted(plan['scenes'],key=lambda x:0 if x['id']=='01b' else 1):","for s in plan['scenes']:")
worker=worker.replace('rendering-three-current34-overviews','rendering-seventeen-detailed-current34-explanations')
worker=worker.replace('rendered-current34-overviews-awaiting-direct-pixel-review','rendered-current34-detailed-explanations-awaiting-direct-pixel-review')
worker=worker.replace('failed-current34-overview-render-preserve-history','failed-current34-detailed-render-preserve-history')
worker=worker.replace('range(0,count,30)','range(0,count,60)')
worker=worker.replace('Directly review all rendered overview/depth samples and normal playback; current mixed context/captions/final pixels remain required. No main promotion/upload.',
    'Directly inspect all17 detailed explanation renders and normal1x playback; preserve current AAC/cues and remaining guide review. Only update assembly after detailed visual approvals.')
create(B/'render-orientation-detailed-explanations-v1.py',worker)
recorder=(B/'record-orientation-overview-worker-v5.py').read_text('utf-8-sig')
recorder=recorder.replace('current34-overview-render-execution-v5','current34-detailed-explanation-render-execution-v1').replace("len(s['scenes'])==3","len(s['scenes'])==17")
recorder=recorder.replace('Read all overview/depth encoded samples and normal playback. Current180 independent AAC diagnostics/captions/baseline guides/final QA/delivery remain pending.',
    'Review all17 detailed subject renders and normal playback; complete guide samples, update current assembly and review244 final caption pixels before delivery.')
create(B/'record-orientation-detailed-explanation-worker-v1.py',recorder)

browser=(B/'prepare-orientation-overview-browser-v4.py').read_text('utf-8-sig')
create(B/'prepare-orientation-overview-browser-v5.py',browser.replace('v4','v5').replace('V4','V5'))
transition=rd(O/'detailed-subject-visual-transition-v1.json')
transition.update(explanationTimingPlan=rel(tp),explanationTimingSha256=sha(tp),
    renderPreparedOnly=True,renderStarted=False,renderSceneCount=17,
    retainedAbstractScenes=['18','19'],oldVisualApprovalsSupersededForSubjects=True)
(O/'detailed-subject-visual-transition-v1.json').write_text(json.dumps(transition,ensure_ascii=False,indent=2)+'\n','utf-8')
for row in protected['protectedInputs']+protected['results']:assert sha(ROOT/row['path'])==row['sha256']
print(json.dumps(dict(prepared=True,scenes=17,newTts=0,all79ProtectedUnchanged=True,originalLessonUnchanged=True)))

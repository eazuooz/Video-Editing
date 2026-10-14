"""User-authorized visual-only transition; keep all original files and PCM."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
D=ROOT/'manim/projects/game-math-orientation-matrices'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,v):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
policy=ROOT/'shared/publishing/illustrative-subject-detail-policy.json'
assert read(policy)['editableAssetsRequired']
proof=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
library=D/'detailed_subjects_v1.py'
new=D/'teaching_overview_revision_v5.py';assert not new.exists()
old=D/'teaching_overview_revision_v3.py';code=old.read_text('utf-8-sig')
start=code.index('def bicycle(origin):');end=code.index('class OverviewRevision',start)
code=code[:start]+'''sys.path.insert(0,str(Path(__file__).resolve().parent))
from detailed_subjects_v1 import aircraft,wingsuit_person,bicycle_with_rider,machinery

def body(R,origin,scale=1.2):return aircraft(R,origin,scale)
def basis(R,origin,scale=2.05,with_body=True):
    axes=VGroup(*[arrow(origin,origin+scale*(P@R[:,i]),c) for i,c in enumerate([RED,GREEN,BLUE])])
    return VGroup(wingsuit_person(R,origin,1.0),axes) if with_body else axes
def bicycle(origin):return bicycle_with_rider(origin,.70)

'''+code[end:]
oldline='a=body(np.eye(3),left,1.65);b=body(np.eye(3),right,1.65)'
assert code.count(oldline)==1
code=code.replace(oldline,'a=wingsuit_person(np.eye(3),left,1.05);b=wingsuit_person(np.eye(3),right,1.05)')
code=code.replace('if i in [0,2]:model=body(np.eye(3),o,.95)',
                  'if i==0:model=wingsuit_person(np.eye(3),o,.88)\n            elif i==2:model=aircraft(np.eye(3),o,.95)')
block='''                base=logical_box([1.5,.18,1.1],[0,0,0],BLUE);part=logical_box([.55,.7,.55],[.35,.47,0],ORANGE)
                model=VGroup(base,part);model.apply_matrix(P);model.shift(o)'''
assert block in code
code=code.replace(block,'                model=machinery(o,.92)')
code=code.replace("obj[0].scale(1.65,about_point=origin)","obj[0].scale(1.20,about_point=origin)")
new.write_text(code,'utf-8')
timing=read(O/'current34-overview-timing-plan-v3.json')
timing.update(code=rel(new),codeSha256=sha(new),assetLibrary=rel(library),assetLibrarySha256=sha(library),
    sourceVisualVersion='current34-overview-v4 preserved',rendered=False,movingPixelApproved=False,
    pixelRepair='Recognizable detailed people, rider/bicycle, aircraft and machinery. Original voice/timing/math/palette unchanged.')
tp=O/'current34-overview-timing-plan-v5.json';assert not tp.exists();save(tp,timing)
wrapper=(B/'render-orientation-overview-v4.py').read_text('utf-8-sig')
wrapper=wrapper.replace('current34-overview-v4','current34-overview-v5').replace('teaching_overview_revision_v3.py','teaching_overview_revision_v5.py')
wrapper=wrapper.replace('current34-overview-timing-plan-v3.json','current34-overview-timing-plan-v5.json').replace('current34-overview-render-execution-v4','current34-overview-render-execution-v5')
wrapper=wrapper.replace("for s in plan['scenes']:\n  sid=", "for s in sorted(plan['scenes'],key=lambda x:0 if x['id']=='01b' else 1):\n  sid=")
wrapper=wrapper.replace("plan=rd(T);assert sha(M)==plan['codeSha256'];", "plan=rd(T);assert sha(M)==plan['codeSha256'];assert sha(ROOT/plan['assetLibrary'])==plan['assetLibrarySha256'];")
wp=B/'render-orientation-overview-v5.py';assert not wp.exists();wp.write_text(wrapper,'utf-8')
rec=(B/'record-orientation-overview-worker-v4.py').read_text('utf-8-sig').replace('current34-overview-render-execution-v4','current34-overview-render-execution-v5')
rp=B/'record-orientation-overview-worker-v5.py';assert not rp.exists();rp.write_text(rec,'utf-8')
record=dict(recordedAt=now(),policy=rel(policy),policySha256=sha(policy),userEvidence=read(policy)['userEvidence'],
    assetLibrary=rel(library),assetLibrarySha256=sha(library),overviewCode=rel(new),overviewCodeSha256=sha(new),
    preservedOverview=rel(old),preservedOverviewSha256=sha(old),
    subjects=[dict(scene='01/24',subject='wingsuit person',details=['helmet/visor','torso/harness','articulated arms and legs','gloves/finger seams','boots','wing fabric'],action='same forward direction, different roll, axes and inverse result'),
        dict(scene='01b',subject='person/bicycle with rider/aircraft/machinery',details=['posed rider','spokes/frame/crank/pedals/handlebars','cockpit/swept wings/tail/engines','panel/vents/bolts/connector'],action='ordered comparison and individual module rotation')],
    additionalExplanationAudit=dict(required=True,scenes=['03','04','06','06a','07','09','09a','10','12','13','13a','15','16','16a','18','19','21','21a','22'],
        next='Retain useful text/calculations and PCM; replace anonymous aircraft/body placeholders through a scoped detailed model. Storage cells/axis geometry and code remain concept-appropriate.'),
    timingChanged=False,newTts=0,newAsr=0,currentMixedReviewPreserved=True,newFinalPixelsApproved=False,
    overviewV4RemainsHistoricalReview=True,overviewV5MovingReviewPassed=False,
    finalAssemblyMayUseOlderSubjectVisuals=False,newImageGit=0,researchChanges=0)
out=O/'detailed-subject-visual-transition-v1.json';assert not out.exists();save(out,record)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='detailed-subject-user-rule-recorded-visual-revision-prepared',
    detailedSubjectTransition=rel(out),detailedExplanationVisualApproved=False,activeOwnedWorkers=0,ownedJob=None,
    next='Fresh resources then one detailed overview V5 render. Inspect detailed subjects/motion/caption clearance; update current explanation model audit before final assembly. Preserve completed audio and guide render/pixels.')
save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],detailedSubjectTransition=rel(out),next=cp['next']);q['updatedAt']=now();assert qp.read_bytes()==before;save(qp,q)
print(json.dumps(dict(policyRecorded=True,overviewPrepared=rel(new),originalInputsUnchanged=True,newTts=0,visualApproved=False)))

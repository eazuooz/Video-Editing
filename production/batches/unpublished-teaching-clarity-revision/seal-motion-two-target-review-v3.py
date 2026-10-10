from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
aim=read(R/'aim-target-qa-execution-v3.json');goal=read(R/'two-target-qa-execution-v2.json')
assert aim['actualExitCode']==0 and goal['actualExitCode']==0
assert read(R/'aim-target-qa-process-closure-v3.json')['actualOuterExitCode']==0
targets=[];boards=[];samples=[]
for ident,state,expected in [('02',aim,184),('06b',goal,38)]:
    rows=[v for v in state['completed'] if v['id']==ident]
    assert len(rows)==2 and sum(len(v['samples']) for v in rows)==expected
    clean=next(v for v in rows if v['variant']=='clean')
    for v in rows:
        assert sha(ROOT/v['source'])==v['sourceSha256'] and v['allPts1500'] and v['actualWholeDecodeExitCode']==0
        for s in v['samples']:
            assert s['pts']==s['frame']*1500 and sha(ROOT/s['path'])==s['sha256'];samples.append(dict(s,target=ident,variant=v['variant']))
        for b in v['boards']:
            assert sha(ROOT/b['path'])==b['sha256'];boards.append(dict(b,target=ident,variant=v['variant'],directlyReviewed=True))
    assert clean['maxNonWhitePixelsBelow910']==0
    targets.append(dict(id=ident,cleanPath=clean['source'],cleanSha256=clean['sourceSha256'],frames=clean['frames'],samples=expected,boards=len([b for b in boards if b['target']==ident]),allCleanFramesCaptionBandEmpty=True))
assert len(samples)==222 and len(boards)==40
for v in read(R/'narration-tts-waiting-v1.json')['protectedInputs']:assert sha(ROOT/v['path'])==v['sha256']
motion02=read(R/'target02-comparison-motion-observed-v3.json');motion06=read(R/'target06b-playback-observation-v3.json')
motion02text=motion02['state'].replace('\\','');motion06text=motion06['state'].replace('\\','')
assert '"paused": false' in motion02text and '"playbackRate": 1' in motion02text
assert '"ended": true' in motion06text and '"playbackRate": 1' in motion06text
review=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),status='two-current-target-repairs-reviewed-awaiting-new-whole-pair',targets=targets,samples=samples,boards=boards,
    scene02BoardObservations=[{"first":1,"last":4,"notes":"Early visual-versus-seated-body states and transition to personal-response qualifier clear; projected faces readable and caption band empty."},{"first":5,"last":8,"notes":"Personal-response qualifier and onset of camera turn are legible; floors/faces separated. Camera turns progressively toward target as role comparison begins."},{"first":9,"last":12,"notes":"All selected turn and fade transition states read. Comparison labels are fully established before left/right narration f1729; blue ray reaches goal, right red camera/shake stays separately labeled; caption band empty."},{"first":13,"last":16,"notes":"All end comparison states including f1860 and last2337 directlyread; left blue camera faces goal, right camera varies whiletarget remainsfixed; all headings and explanatory footers clear."},{"first":17,"last":20,"notes":"All early current fixed-caption cues read; wording/body states correspond, two-line boxes stay in bottom band and do not obscure footers."},{"first":21,"last":24,"notes":"All personal-response qualifier captions and transition-to-role-comparison samples directly read. Fixed two-line captions separate from footers."},{"first":25,"last":28,"notes":"All fixed-caption samples through completed transition read. Comparison state established by f1728/f1729 before new left/right cue starts; selected transition blends remain brief and caption band clear."},{"first":29,"last":32,"notes":"All remaining comparison caption samples read through last2337. Blue ray intersects brown goal, red extra-shake cue stays separate; two-line ending caption clears disclaimer and comparison footers. No unresolved selected-pixel defect."}],
    goalObservation='All 38 clean/captioned samples and eight boards directly read. Projected walls/floor/camera direction/same goal are legible; footer and disclaimer stay above fixed two-line caption.',
    scene02Observation='All 184 clean/captioned samples and 32 boards directly read. Left blue camera ray reaches brown goal before left/right cue; separate right red camera/ray oscillation is visible. Caption and footer spacing clear.',
    allSelectedTargetSamplesDirectlyRead=True,normalSpeedTargetMotionApproved=True,normalSpeedEvidence=['target02-playback-ended-v3.json','target02-comparison-motion-observed-v3.json','target06b-playback-observation-v3.json'],
    allContinuousIntermediateFramesDirectlyRead=False,unresolved=[],allFinalPixelsApproved=False,wholePairReviewPending=True,humanListeningApproved=False,publicRightsApproved=False,newTtsOrAsr=0,other18PiecesRegenerated=False,newGitImages=0,researchManipulations=0)
path=R/'two-target-repair-direct-review-v3.json';assert not path.exists();save(path,review)
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=review['reviewedAt'],stage=review['status'],targetRepairReview='projects/motion-sickness-games/production/revision-teaching-clarity-v1/two-target-repair-direct-review-v3.json',next='Assemble pair v2 with two reviewed repairs and byte-identical other18 pieces/audio; inspect final current cue/cut pixels and normal-speed flow before collection/private upload.')
save(R/'latest-checkpoint.json',cp)
print(json.dumps(dict(samples=len(samples),boards=len(boards),targets=targets,allFinalPixelsApproved=False),ensure_ascii=False))

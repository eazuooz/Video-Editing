"""Reconcile actual crop reading; selected continuous/captioned cuts remain pending."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, time
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
    t=p.with_name(p.name+f'.{os.getpid()}.writing')
    t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
sp=BASE/'gauss129-exact-crop-execution-v1.json';s=read(sp)
assert s['exitCode']==0 and len(s['samples'])==193 and len(s['boards'])==49
assert sha(ROOT/s['sourcePath'])==s['sourceSha256']
files=s['samples']+s['boards'];assert all(sha(ROOT/e['path'])==e['sha256'] for e in files)
cim=subprocess.run(['powershell','-NoProfile','-Command','Get-CimInstance Win32_Process -Filter "ProcessId=7052 or ProcessId=35036" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4'],capture_output=True,text=True,check=True)
assert not cim.stdout.strip(),'Inspect live or reused PID identity before proceeding.'
notes=[
([1,2,3,4],'12–22: blue forward rush over open water/rocks.16.5 is black/occluded. No identifiable enemy reaction; only a short movement-direction comparison can use clear departure frames.'),
([4,5,6,7],'60–68: approach and aim at rock;65.25 blue collision burst has no identified enemy.62.25/63 caster partly clipped. Reject enemy-contact narration and long quota use.'),
([7,8,9,10,11],'132–143: two/three enemies near stones and caster repositioning. Most frames contain waiting/aiming without an attack; only a brief position relation is a candidate.140+ caster aims away from nearby enemy, so exclude that wait.'),
([11,12,13,14,15],'151–162: approach151–152.5 then firearm fire153.25–160 with named Tusk Lancer, hit numbers and falling/tumbling bodies.160.75+ turns into empty repositioning. Generic firearm comparison, not dash proof.'),
([15,16,17,18],'276–285:276.75–280.5 approach/aim/fire at foe, then target falls+156.281.25–283.5 sky/jump/empty ground excluded.284.25 approaches nearby Ballista and285 shows orange ground near caster/foe.'),
([19,20,21],'285.75 blue ground around caster/nearby foe.286.5 excessive orange/blue blur;287.25 structure obscures target.288/288.75 nearby standing enemy;289.5 cast,290.25 enemy in blue field,291 falling body+1636.291.75+ turns/jumps away;293–294 structure/jump excludes clear target proof.'),
([22,23,24],'294.75 elevated Gauss firearm attack is not Jade hovering ability.295.5/296.25 strong burst/blur excluded.297.75–300 show nearby standing enemies, blue ground boundary and body reaction.300.75+ strong orange/blue effects intermittently obscure foes; trim before clarity is lost.'),
([25],'303.75 orange burst masks much of close action;304.5 blue field and distant target are visible,305 jump and305.98 empty travel. Do not allocate the entire tail.'),
([26,27,28],'312 approach,312.75–314.25 aim/fire at visible Tusk Hellion beside structure;315 close movement blurs/clips caster,315.75–317.983 jumps and empty approach.338/338.75 burst near target obscures details,339.5 jump. Use only short clear firearm sequence.'),
([29,30,31,32,33,34],'340–341.75 orange travel/jump is mostly empty.342.5–343.25 near foe and344 forward blue streak approach;344.75 turns away,345.5–347.75 near foes/hit numbers.348.5–353.75 mostly empty turning/rushing;354+ large explosion obscures target. Only short clear near-target action candidates.'),
([34,35,36],'376 blue boundary around caster with distant Tusk Thumper;377.5–379.75 camera moves around structure, sometimes clipping caster.380.5/381.25 close humanoid target and hit;381.983 departure. No demonstrated mechanical equivalence between humanoid and Thumper.'),
([36,37,38,39,40,41,42],'391–392.5 blue forward rush,392.5 foe ahead;393.25 sky/body clip.394.75–395.5 downward firearm hit/reaction is ordinary Gauss, not Jade.396.25–400.75 aim/fire at Tusk Thumper.401.5 sky/402.25 roll excluded.403.75–406 attack with Thumper and approaching humanoids;406.75+ particle burst obscures target.'),
([42,43,44],'412 travel towards Thumper;413.5 close humanoid.414.25 blue ground cast crops/obscures nearby target;415.75 field with distant Thumper,416.5–418 unrelated travel. Do not use for clear nearby-effect proof.'),
([44,45,46,47,48],'423–426 aimed firearm at visible Thumper,426.75 orange burst obscures.427.5–428.25 close target structure/knockdown are blurred.429–433 large countdown overlay occupies view; exclude overlay section rather than counting it as uninterrupted explanatory action.'),
([48,49],'437/437.75 FOCUS EARNED overlay excluded.438.5/438.983 nearby orange foe and blue ground become visible, but less than one clear second remains; do not adopt a longer unobserved tail.')]
candidates=[
    dict(interval=[12,14],kind='movement-direction-only',note='No enemy; short comparison only.'),
    dict(interval=[132,134.8],kind='brief-position-relation',note='Not attack-effect proof; no long idle allocation.'),
    dict(interval=[153.1,160.4],kind='forward-firearm-target-reaction'),
    dict(interval=[276.7,280.7],kind='approach-firearm-target-reaction'),
    dict(interval=[284.5,286.15],kind='nearby-ground-origin'),
    dict(interval=[287.5,291.3],kind='nearby-ground-cast-and-reaction'),
    dict(interval=[297.3,300.25],kind='nearby-ground-and-targets'),
    dict(interval=[312.65,314.7],kind='forward-firearm-target'),
    dict(interval=[342.2,344.6],kind='nearby-foe-and-forward-movement'),
    dict(interval=[345.4,348.1],kind='nearby-foe-action-reaction'),
    dict(interval=[376,377.3],kind='brief-caster-field-and-distant-target'),
    dict(interval=[380.1,381.5],kind='nearby-foe-action'),
    dict(interval=[394.55,395.55],kind='elevated-Gauss-firearm-only'),
    dict(interval=[396.05,400.9],kind='aimed-forward-firearm-target'),
    dict(interval=[403.1,406.2],kind='forward-target-and-approaching-foes'),
    dict(interval=[423,426.3],kind='aimed-forward-firearm-target')]
rp=BASE/'gauss129-exact-crop-direct-review-v1.json'
r=dict(schemaVersion=1,slug='player-customization',reviewedAt=now(),sourcePath=s['sourcePath'],sourceSha256=s['sourceSha256'],sourceVideoId=s['sourceVideoId'],sourceOffsetSeconds=2244,crop=s['crop'],boards=s['boards'],notes=[dict(boards=a,observation=b) for a,b in notes],all49BoardsDirectlyRead=True,all193NativeCropSamplesDirectlyRead=True,hashVerifiedFiles=len(files),hashMismatches=0,actualSessionId=68900,actualSessionExitCodeObserved=0,actualCimPidAbsent=True,liveProcessIdentity=s.get('processIdentity'),localOnly=True,newGitImages=0,candidateIntervals=candidates,limitations=['These are sampled candidate observations; continuous selected-cut playback and exact edge/caption pixels are pending.','Health/status UI partly cropped; preserve caster, target and effects in each adopted shot.','Official development build/infinite-energy demonstration is illustrative, not controlled efficacy or victory evidence.','Gauss shots cannot cover named Jade/Yareli/Dante clauses.'],actualActionApproved=False,finalAllocationApproved=False,bodyRatioApproved=False,allFinalPixels=False)
save(rp,r);s.update(allCropSamplesDirectlyRead=True,directReview=rp.relative_to(ROOT).as_posix(),actualSessionExitCodeObserved=0,actualCimPidAbsent=True,updatedAt=now());save(sp,s)
cp=read(BASE/'latest-checkpoint.json');cp.update(stage='all-source-candidate-crops-read-integer-allocation-pending',recordedAt=now(),gauss129ExactCropReview=rp.relative_to(ROOT).as_posix(),nextAction='Assign disjoint native integer frames to all64 preserved paragraphs, with named caster/action correspondence. Then review continuous cuts and fixed caption pixels; final timing/ratio/mix/render/private remain pending.')
cp['ownedJob'].update(exitCode=0,workerExpectedRunning=False,actualSessionExitCodeObserved=0,actualCimPidAbsent=True);save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization');i.update(stage=cp['stage'],currentExecution=cp['ownedJob'],gauss129ExactCropReview=cp['gauss129ExactCropReview'],nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
print(json.dumps(dict(boards=49,samples=193,hashVerified=242,actualCimAbsent=True,finalApproved=False)))

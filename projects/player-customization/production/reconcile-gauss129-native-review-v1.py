"""Record actual native board reading without approving selected clips."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, time
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
sp=BASE/'gauss129-native-inspection-execution-v1.json';s=read(sp)
assert s['exitCode']==0 and len(s['samples'])==90 and len(s['boards'])==23
assert sha(ROOT/s['sourcePath'])==s['sourceSha256']
files=s['samples']+s['boards'];assert all(sha(ROOT/e['path'])==e['sha256'] for e in files)
cim=subprocess.run(['powershell','-NoProfile','-Command','Get-CimInstance Win32_Process -Filter "ProcessId=12876 or ProcessId=62564" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4'],capture_output=True,text=True,check=True)
assert not cim.stdout.strip(),'Inspect any live/reused PID before continuing.'
notes=[
([1,2,3],'0–50: departure/rushing across water and rocks, blue particles near25 seconds but no recognized enemy.35–50 mostly empty travel/wait. Movement-only candidates cannot illustrate enemy reaction.'),
([4,5,6,7],'55–130:60–68 and80–86 show departure/blue collision burst against rock; no identifiable enemy. Trees obscure110;115–130 mostly empty movement/particles. Rock collision is not an enemy hit.'),
([8,9],'135/140 enemies near stone camp;145 stone occludes targets;150 travel.155 gun action facing foes and160 fallen/tumbling foe with+150.165 tower occludes foe;170 empty movement. Generic firearm engagement, not Mach Rush proof.'),
([10,11],'175–210: jumps/empty travel;190 blue Kinetic Plating around caster without enemy.195–210 mostly empty travel. Exclude unrelated transit.'),
([12,13,14],'215/220/230/235/245/250/255/260 show ground-blue boundary around caster but targets absent.225/240 waiting and270 departure. Can establish a brief geometric origin, cannot fill long enemy-effect quota.'),
([15,16],'275 rush towards camp.280 gunfire/target reaction+156.285 nearby Ballista.290 blue ground ring around nearby standing enemy.295 firearm aimed toward targets below and300 blue ground effect beside two standing foes/one orange.305 close fire/structure obscures;310 jump with empty background. Not Jade/downward-hover narration.'),
([17,18],'315 near enemy in front, motion blur.320 camera turns away;325 waiting;330 rush uphill burning.335 jump over fiery ground.340 rush towards structure;345 nearby enemy and+784;350 nearby foe with blue/orange streaks. Check continuity before assigning dash/contact.'),
([19,20],'355 large bright explosion obscures targets.360 dash away;365 empty hill;370 jump.375 blue shielding with no useful foe.380 nearby running foe.385 camp reposition;390 rush hill. Do not count explosion/empty travel as target proof.'),
([21],'395 firearm aimed down at visible target with hit numbers.400 jump near target.405 Tusk Thumper and ordinary foes visible while aiming.410 movement. Ground Gauss example, not Jade aerial ability.'),
([22,23],'415 blue ground effect around caster/nearby foe;420 rock and dense particles occlude.425 Tusk Thumper target;430 close attack.435 FOCUS EARNED overlay excludes that boundary.439 blue ground effect beside standing foe. Dev-build/infinite-energy context and no controlled performance/victory claims.')]
windows=[[12,22],[60,68],[132,143],[151,162],[276,306],[312,318],[338,355],[376,382],[391,407],[412,418],[423,433.5],[437,439.016667]]
rp=BASE/'gauss129-native-direct-review-v1.json'
r=dict(schemaVersion=1,slug='player-customization',reviewedAt=now(),sourcePath=s['sourcePath'],sourceSha256=s['sourceSha256'],sourceVideoId=s['sourceVideoId'],sourceOffsetSeconds=2244,boards=s['boards'],notes=[dict(boards=a,observation=b) for a,b in notes],all23BoardsDirectlyRead=True,all90NativeSamplesDirectlyRead=True,hashVerifiedFiles=len(files),hashMismatches=0,actualExecSessionId=31586,actualSessionExitCodeObserved=0,actualCimPidAbsent=True,liveProcessIdentity=s.get('processIdentity'),localOnly=True,newGitImages=0,candidateInspectionWindows=windows,limitations=['Five-second native overview samples are not continuous selected-cut review.','Presenter/footer must be excluded and useful caster/target relationship preserved in exact crops.','Named Jade/Yareli/Dante narration cannot use Gauss.','Dev build is conditional footage evidence, not final mechanics/performance proof.'],actualActionApproved=False,finalAllocationApproved=False,bodyRatioApproved=False,allFinalPixels=False)
save(rp,r);s.update(allNativePixelsReviewed=True,directReview=rp.relative_to(ROOT).as_posix(),actualSessionExitCodeObserved=0,actualCimPidAbsent=True,updatedAt=now());save(sp,s)
cp=read(BASE/'latest-checkpoint.json');cp.update(stage='gauss129-native-reviewed-exact-crop-pending',recordedAt=now(),gauss129NativeReview=rp.relative_to(ROOT).as_posix(),nextAction='Inspect only fresh Gauss candidate exact crops; preserve current PCM/white and completed sources. Approve unique action allocation only after matched continuity/crop review.')
cp['ownedJob'].update(exitCode=0,workerExpectedRunning=False,actualSessionExitCodeObserved=0,actualCimPidAbsent=True);save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization');i.update(stage=cp['stage'],currentExecution=cp['ownedJob'],gauss129NativeReview=cp['gauss129NativeReview'],nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
print(json.dumps(dict(boards=23,samples=90,hashVerified=113,actualCimAbsent=True,finalApproved=False)))

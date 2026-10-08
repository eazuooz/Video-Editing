"""Record directly read exact crops; keep allocation and final-pixel gates closed."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, value):
    tmp = p.with_name(p.name + f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)
s_path = BASE / 'yareli155-exact-crop-execution-v1.json'
s = read(s_path)
assert s['exitCode'] == 0 and len(s['samples']) == 152 and s['boardCount'] == 38
assert sha(ROOT / s['sourcePath']) == s['sourceSha256']
files = [*s['samples'], *s['boards']]
assert all(sha(ROOT / x['path']) == x['sha256'] for x in files)
probe = subprocess.run(['powershell', '-NoProfile', '-Command',
    'Get-CimInstance Win32_Process -Filter "ProcessId=35668 or ProcessId=62420" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4'],
    capture_output=True, text=True, check=True)
assert not probe.stdout.strip(), 'PID reused or unexpectedly live: inspect identity before continuing'
notes = [
 ([1,2,3,4,5,6], '112–129.25: bubbles/forward casts are distinct from rotating rings. 114–116.25 and118.75–121.4 show caster/target/bubble relation;117.25/118 and121.75/122.5 column occlusion excluded.123.25/124/127 empty field excluded.125.5/126.25 incoming targets;128.5 pillar partly hides target;129.25 cast begins.'),
 ([7,8,9], '130–136.75 rotating blades follow caster while nearby opponents and toppled bodies remain visible. Some caster left-edge clipping needs selected-cut review.137.5/137.9833 RANK UP overlay excluded; candidate ends136.9.'),
 ([10,11,12,13,14], '142–153.9833 rings follow mounted caster around targets.144.25 large gold pillar hides useful relation, exclude144.1–145.1.147.25 close black opponent;149.5/150.25/151/151.75 nearby targets.152.5/153.25 targets below while caster moves.157/157.75 distinct forward bubble cast begins.'),
 ([15,16], '159.25/160 blue bubbles around standing target;160.75 target on floor.161.5–163.9833 WAVE CLEARED and empty field excluded. No inference about equipment/performance/controlled victory.'),
 ([17,18,19], '169–177.25: moving ring centre follows caster, but most views lack a nearby standing target. Only a short purpose-matched centre-following comparison may use169.75–173.25; it cannot illustrate contact with an unseen enemy or fill unrelated travel time.'),
 ([20,21,22,23,24], '178/178.75/179.5 nearby ground opponents.180.25–182.5 targets absent/obscured.183.25–186.25 opponents beside/beyond pillar and ring.187/187.75/188.5 water column obscures field;187.75 toppled body visible, possible generic effect/reaction only.189.25–191 and208 empty/absent target excluded.'),
 ([25,26,27,28,29], '209.5/210.25 targets through doorway;211 column begins and211.75 column/corpses.218–220.25 mostly empty field.221 enemy near caster then221.75–223.25 column occlusion.224/224.75/225.5 standing nearby opponents and moving ring.226.25–228.5 empty repositioning excluded.'),
 ([30,31,32,33,34,35], '229.25–232.25 bubble cast towards elevated visible target;233 wall-only aiming excluded.233.75–235.9833 no useful target.239.75/240.5/241.25/242/242.75/243.5 visible balcony opponent, aimed from below; not Jade hovering/aiming downward.244.25 target partly blocked by arch,245 turn,246.5/246.9833 WAVE CLEARED excluded.'),
 ([35,36,37,38], '273/273.75 firearm aim and target reaction;274.5 pivot with no useful target.275.25/276 target aim/shot,276.75/277.5 target absent.278.25/279/279.75/280.5/281.25 firearm engagement with nearby gold/black targets.281.9833 bright splash and sparks obscure target; trim before281.7. These are firearm examples, not rotating-ring evidence.')]
candidate_windows = [[114,116.25],[118.75,121.4],[125.5,126.4],[127.75,136.9],
 [142.1,144.1],[145.1,153.9],[157.5,160.9],[169.75,173.25],[177.25,179.85],
 [183.3,186.8],[187.2,188.9],[209.25,211.3],[220.5,221.6],[223.75,225.8],
 [229.5,232.7],[239.5,243.8],[273,274.1],[275.1,276.25],[278.1,281.7]]
record = dict(schemaVersion=1, slug='player-customization', reviewedAt=now(),
 sourcePath=s['sourcePath'], sourceSha256=s['sourceSha256'], sourceVideoId=s['sourceVideoId'],
 crop=s['crop'], boards=s['boards'], notes=[dict(boards=a, observation=b) for a,b in notes],
 all38BoardsDirectlyRead=True, all152ExactSamplesDirectlyRead=True,
 hashVerifiedFiles=len(files), hashMismatches=0, localOnly=True, newGitImages=0,
 actualExecSessionId=48743, actualSessionExitCodeObserved=0, actualCimPidAbsent=True,
 liveCreationIdentityUnobserved=True,
 identityLimitation='CIM was queried after the short extraction had completed; no live creation/command identity observation is claimed.',
 candidateWindows=candidate_windows, candidateUpperSeconds=round(sum(b-a for a,b in candidate_windows),6),
 limitations=['0.75-second native samples are directly reviewed; continuous selected-cut boundary/caption review remains required.',
 'Blanket crop approval is false: left caster can be clipped; matching visible relation must survive each cut.',
 'Named Jade/Dante/Gauss narration cannot use Yareli footage.',
 '59-second upper candidate pool is not final actual-footage capacity; further trims can reduce it.'],
 actualActionApproved=False, finalAllocationApproved=False, bodyRatioApproved=False, allFinalPixels=False)
rp = BASE / 'yareli155-exact-crop-direct-review-v1.json'
save(rp, record)
s.update(allCropSamplesDirectlyRead=True, directReview=rp.relative_to(ROOT).as_posix(),
 actualSessionId=48743, actualSessionExitCodeObserved=0, actualCimPidAbsent=True,
 liveCreationIdentityUnobserved=True, updatedAt=now())
save(s_path,s)
cp_path = BASE / 'latest-checkpoint.json'; cp = read(cp_path)
cp.update(stage='exact-source-crops-reviewed-unique-allocation-pending', recordedAt=now(),
 yareli155ExactCropReview=rp.relative_to(ROOT).as_posix(),
 nextAction='Prepare source-grounded integer allocation of all64 paragraphs/current PCM. Review each selected action/crop/white bridge; keep final timing, ratio, mix, encoded pixels, collection and private upload false.')
cp['ownedJob'].update(sessionId=48743, exitCode=0, workerExpectedRunning=False,
 actualSessionExitCodeObserved=0, actualCimPidAbsent=True, liveCreationIdentityUnobserved=True)
save(cp_path,cp)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'; q=read(qp)
i=next(i for i in q['items'] if i['slug']=='player-customization')
i.update(stage=cp['stage'], currentExecution=cp['ownedJob'], yareli155ExactCropReview=cp['yareli155ExactCropReview'], nextAction=cp['nextAction'])
q['updatedAt']=now(); save(qp,q)
print(json.dumps(dict(boardsRead=38, exactSamplesRead=152, hashVerifiedFiles=len(files), candidateUpperSeconds=record['candidateUpperSeconds'], finalApproved=False)))

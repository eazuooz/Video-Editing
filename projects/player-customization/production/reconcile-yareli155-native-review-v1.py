"""Save direct19-board findings and verify current local hashes, no quota approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
sp=BASE/'yareli155-native-inspection-execution-v1.json';s=read(sp)
assert s['exitCode']==0 and s['boardCount']==19 and s['sampleCount']==76
assert s['sourceSha256']=='72780d2d3ea502d996e7884b93a4e7507ef91f9446ef196a943e717bbbdea03b'
assert sha(ROOT/s['sourcePath'])==s['sourceSha256']
entries=[*s['boards'],*s['samples']]
assert all(sha(ROOT/e['path'])==e['sha256'] for e in entries)
notes=[
 dict(boards=[1,2],seconds=[0,30.0333],observation='0/.0333 white flash rejected. 5 Lotus transmission and10 weapon flourish;15/20 same stationary hallway excluded.25/30 mounted movement begins; no target action yet.'),
 dict(boards=[3,4,5],seconds=[35.0333,90.0333],observation='Mounted turns and repeated door/stair travel in empty room. Exclude from target-action capacity; a short path demonstration needs separate purpose review and cannot fill quota.'),
 dict(boards=[6],seconds=[95.0333,110.0333],observation='95 still empty traversal;100 incoming-wave notice;105/110 waiting/turning near defense structure. Exclude wait and notification.'),
 dict(boards=[7,8],seconds=[115.0333,150.0333],observation='115 close target contact;120 moving past visible opponents;125 repositioning;130/135 bright rotating blades around mounted caster with nearby opponents.140 rank notification rejected.145/150 rings persist with opponents at different distances.'),
 dict(boards=[9,10],seconds=[155.0333,190.0333],observation='155 travel without immediate target excluded.160/165 floating blue bubbles are distinct from near caster ring.170/175/180/185/190 ring and mounted repositioning among opponents; seek exact boundaries and crop.'),
 dict(boards=[11,12],seconds=[195.0333,230.0333],observation='195 distant/absent target rejected.200 movement toward distant opponents candidate.205 large water column occludes field;215 rank notice and column rejected.210 ring near doorway with targets,220/225/230 mounted ring movement and aim with opponents candidate.'),
 dict(boards=[13,14],seconds=[235.0333,270.0333],observation='235 nearby fight at edge;240 upward aim toward balcony,245 target direction visible.250/255/260 empty balcony/stair travel excluded.265 close movement and270 large challenge popup excluded pending exact boundary.'),
 dict(boards=[15],seconds=[275.0333,290.0333],observation='275/280/285 ground firearm engagement; no rotating ring at these samples. Debug console already overlays presenter panel;290 console covers gameplay entirely. Do not infer optimization or code internals.'),
 dict(boards=[16,17,18,19],seconds=[295.0333,366],observation='295 debug console followed by300–366 four-person conversation. Entire discussion/console excluded from actual-game allocation.')]
record=dict(schemaVersion=1,slug='player-customization',reviewedAt=now(),sourcePath=s['sourcePath'],sourceSha256=s['sourceSha256'],
 sourceVideoId=s['sourceVideoId'],sourceOffsetSeconds=2721,nativeFrameCount=s['nativeFrameCount'],nativeDuration=s['nativeDuration'],
 wholeNativeDecodeExitCode=s['wholeDecodeExitCode'],boards=s['boards'],notes=notes,
 all19NativeBoardsDirectlyRead=True,all76NativeSamplesDirectlyRead=True,hashVerifiedFiles=len(entries),hashMismatches=0,
 localOnly=True,newGitImages=0,sourceAudioUsed=False,
 prospectiveWindows=[[112,138],[141,154],[157,193],[200,204],[208,213],[217,237],[239,247],[273,286]],
 cropCandidate=dict(x=550,y=25,w=1216,h=684,approved=False,issue='Presenter-free candidate can clip leftmost caster or nearby targets; full selected-window caption/crop review remains required.'),
 limitations=['Five-second samples identify research windows only; exact continuous action and crop still unapproved.','Stationary waiting, repeated empty doors, rank notices, presenter/debug content excluded.','No final ratio, allocation, timing or encoded pixels approval.'],
 actualActionApproved=False,finalAllocationApproved=False,bodyRatioApproved=False,allFinalPixels=False)
rp=BASE/'yareli155-native-direct-review-v1.json';save(rp,record)
s.update(actualSessionExitCodeObserved=0,actualCimPidAbsent=True,actualExitCheckedAt=now(),allNativePixelsReviewed=True,directNativeReview=rp.relative_to(ROOT).as_posix());save(sp,s)
cp=read(BASE/'latest-checkpoint.json');cp.update(stage='fresh-yareli-native-reviewed-exact-actions-pending',recordedAt=now(),yareli155NativeReview=rp.relative_to(ROOT).as_posix(),
 nextAction='Direct continuous selected-window/crop review and exact-native boundary extraction; allocate unique matching action while preserving all64 paragraphs and useful white explanations.')
cp['ownedJob'].update(status=s['status'],sessionId=s['sessionId'],processIdentity=s['processIdentity'],exitCode=0,workerExpectedRunning=False,actualSessionExitCodeObserved=0,actualCimPidAbsent=True)
server=read(BASE/'yareli155-review-server-process-v1.json');server.update(sessionId=88985,url='http://127.0.0.1:9248/',scope='Read-only acquired native Yareli155 research viewer; no production/media mutations')
cp.setdefault('ancillaryServers',[]).append(server);save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization');i.update(stage=cp['stage'],currentExecution=cp['ownedJob'],yareli155NativeReview=cp['yareli155NativeReview'],nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
print(json.dumps({'boardsRead':19,'nativeSamplesRead':76,'hashVerifiedFiles':len(entries),'finalApproved':False}))

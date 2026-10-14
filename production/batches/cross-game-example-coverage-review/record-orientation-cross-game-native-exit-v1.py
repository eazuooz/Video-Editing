"""Record observed outer completion and exact source PTS/hash closure, not pixel approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
p=O/'cross-game-native-extraction-v1.json';s=read(p)
assert s['exitCode']==0 and s['completedSources']==3 and not s['actualExitObserved']
for key,createkey in [('pid','createTime'),('ffmpegPid','ffmpegCreateTime')]:
    try:proc=psutil.Process(s[key]);assert abs(proc.create_time()-s[createkey])>.01,'Exact worker still alive'
    except psutil.NoSuchProcess:pass
m=read(ROOT/s['manifest'])
assert m['exactSourcePtsVerified'] and len(m['samples'])==217 and len(m['boards'])==45
for src in m['sources']:
    assert sha(ROOT/src['sourcePath'])==src['sourceSha256']
    assert src['ffmpegExitCode']==0 and src['exactPtsMatched']
    assert src['probe']['time_base']=='1/15360'
for row in m['samples']+m['boards']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
for row in m['samples']:assert row['pts']==row['nativeFrame']*256
tts=read(O/'narration-tts-execution-v2.json')
for row in tts['protectedInputs']+tts['results']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
cim=subprocess.check_output(['powershell','-NoProfile','-Command',
    "Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf-8',errors='replace')
proof=dict(recordedAt=now,actualSession=6852,actualOuterExitCode=0,actualCompletion='8cd13e',initialChunk='b8cd0b',
    worker=dict(pid=s['pid'],createTime=s['createTime'],commandLine=s['commandLine'],cwd=s['cwd']),
    registrationAttempt='dd761c exited1 because exact worker had already completed; no live registration claim.',
    workerClosed=True,manifest=s['manifest'],manifestSha256=sha(ROOT/s['manifest']),sources=3,
    samples=217,boards=45,allSampleAndBoardHashesMatched=True,exactPtsVerified=True,
    protected47AndExisting6PcmHashesMatched=True,cimActual=cim,allNativePixelsDirectlyRead=False,
    nativeInOutSelected=False,finalFourGameTeachingApproved=False)
out=O/'cross-game-native-actual-exit-verification-v1.json';assert not out.exists()
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
s.update(sessionId=6852,actualOuterSession=6852,actualExitObserved=True,actualOuterExitCode=0,
    actualCompletion='8cd13e',closureVerification=out.relative_to(ROOT).as_posix(),updatedAt=now)
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=read(O/'latest-checkpoint.json');cp.update(ownedJob=s,activeOwnedWorkers=0,
    stage='cross-game-native-217-pixels-awaiting-direct-review',recordedAt=now,
    next='Directly read all217 native samples/45 boards; select clear native before/action/result cuts before new narration. One21a first paragraph repair held.')
(O/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
qp=B/'queue.json';before=qp.read_bytes();q=read(qp)
q['currentOrientationReview'].update(stage=cp['stage'],ownedJob=s,activeOwnedWorkers=0,actualSession=6852,
    nativeClosure=out.relative_to(ROOT).as_posix(),next=cp['next'])
q['updatedAt']=now;assert qp.read_bytes()==before;qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(session=6852,actualExit=0,workerClosed=True,samples=217,boards=45,protectedMatched=True,pixelApproval=False)))

"""Current-hash numerical readback and actual research resume, not human QA."""
from pathlib import Path
import datetime, hashlib, json
import psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).parent
def read(path):
    return json.loads(path.read_text(encoding='utf8'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf8')

token = 'cec520b2-63d2-4c95-95be-f4a779149071'
receipt = ROOT/f'shared/output/gpu-handoff/{token}.json'
guard = read(receipt)
assert guard['state']=='research_resume_verified' and guard['ttsExitCode']==0
queue = Path(guard['queueDir'])
status = read(queue/'status.json')
assert status['status']=='running' and status['owner_pid']==67256 and status['completed']>=852
owner, child = psutil.Process(status['owner_pid']), psutil.Process(status['child_pid'])
assert child.is_running() and owner.pid in [p.pid for p in child.parents()]
assert owner.cmdline()==guard['resumedQueue']['command']
assert Path(owner.cwd()).resolve()==Path(guard['resumedQueue']['cwd']).resolve()
actual = {'observedAt':datetime.datetime.now().astimezone().isoformat(), 'status':status,
    'owner':{'pid':owner.pid,'created':owner.create_time(),'command':owner.cmdline(),'cwd':owner.cwd()},
    'child':{'pid':child.pid,'created':child.create_time(),'command':child.cmdline(),'cwd':child.cwd()},
    'actualResearchJobVerified':True,'queueOrControlsModified':False}
save(B/'planes-v3-gpu-handoff-completion.json', {
    'guardToken':token,'guardReceipt':receipt.relative_to(ROOT).as_posix(),
    'guardReceiptSha256':sha(receipt),'currentTrainingCompletedBeforePause':guard['completedJobEvidence'],
    'ttsSucceeded':True,'originalCommandAndCwdRestored':True,'immediateResume':guard['resumedStatus'],
    'finalActualResearchResume':actual,'optimizerResumeFromAdapterOnlyClaimed':False,
    'foreignProcessesOrPauseControlsRemoved':False})

p = ROOT/'projects/game-math-planes-retakes-v3'
m = read(p/'project.json'); out = ROOT/m['tts']['outputDir']
records = []
for reference in read(B/'planes-retakes-v3-tts-map.json'):
    ident = reference['ttsScene'] if 'ttsScene' in reference else reference['id']
    rawpath = out/f'asr/{ident}.json'; raw=read(rawpath); wav=out/f'chunks/{ident}-scene.wav'
    assert raw['audio_sha256']==sha(wav)
    records.append({'additionId':reference['additionId'],'rawAsr':rawpath.relative_to(ROOT).as_posix(),
        'rawAsrSha256':sha(rawpath),'audioSha256':sha(wav),'rawText':raw['text'],
        'rawTranscriptUnchanged':True,'humanListeningComplete':False})
texts={r['additionId']:r['rawText'] for r in records}
assert '바닥 높이를 2' in texts['PB01'] and '0, 1, 0' in texts['PB01']
assert '같은 바닥의 높이는 2' in texts['PB03'] and 'y를 숫자 2' in texts['PB03']
assert '끝이 있는 발판' in texts['PG04'] and '넓이로 안쪽 위치' in texts['PG04']
assert '공중이동' in texts['PG07'] and '표면의 어느 점' in texts['PG07']
save(B/'planes-v3-current-asr-review.json', {'reviewedAt':actual['observedAt'],'records':records,
    'semanticChecks':{'PB01':'defined floor y=2, normal(0,1,0), dot selects y; normal does not define height',
      'PB03':'same floor y=2; keep x,z and replace y with2; tilted plane uses unit normal',
      'PG04':'finite platform extent leads to area address calculation',
      'PG07':'separate surface position/value; cube then explicitly separate airborne travel; gel is not engine color-interpolation evidence'},
    'pronunciationNotes':['PG07 raw ASR spells 보간 as 보관; homophone retained in raw record. Human listening pending.',
      'PG04 timestamp warning omitted an ending token but the unchanged raw final phrase is complete; tail-quality gate passed.'],
    'numeralOrSignSubstitution':False,'humanListeningComplete':False,'movingPixelApproval':False})
print('Current-hash retake meaning and actual restored research job recorded; human/pixel QA separate.')

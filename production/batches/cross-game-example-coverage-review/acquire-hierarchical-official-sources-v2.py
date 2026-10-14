"""Acquire only three official candidate video streams; original bank remains untouched."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys
import psutil

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / 'production/batches/cross-game-example-coverage-review'
V = ROOT / 'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
META = V / 'source-research-v2'
MEDIA = ROOT / 'shared/assets/game-footage/hierarchical-game-outlines/revision-teaching-clarity-v1'
FFMPEG = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FFPROBE = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
PYTHON = ROOT / 'qwen3-tts/.venv/Scripts/python.exe'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()
def save(p, value):
    temporary = p.with_name(p.name + '.' + str(os.getpid()) + '.writing')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temporary, p)
state_path = V / 'source-acquisition-execution-v2.json'
assert not state_path.exists(), 'Reuse the recorded actual source acquisition; no duplicate worker'
resource = read(V / 'source-cpu-resource-verification-v2.json')
age = (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()
assert 0 <= age < 240 and resource['cpuAcquisitionEligible'] and not resource['activeOwnedMediaWorkers'], age
assert sha(ROOT / 'projects/game-math-orientation-matrices/project.json') == resource['currentOrientationMainSha256']
sources = read(META / 'metadata-observation-v1.json')['sources']
assert len(sources) == 1 and all(s['success'] for s in sources)
proc = psutil.Process()
other = []
parent_pids = {p.pid for p in proc.parents()}
for p in psutil.process_iter(['pid','name','cmdline','create_time']):
    try:
        cmd = ' '.join(p.info['cmdline'] or [])
        if p.pid not in {os.getpid(), *parent_pids} and 'acquire-hierarchical-official-sources-v2.py' in cmd:
            other.append(dict(pid=p.pid,createTime=p.info['create_time'],command=p.info['cmdline']))
    except (psutil.NoSuchProcess,psutil.AccessDenied):
        pass
assert not other, other
MEDIA.mkdir(parents=True, exist_ok=True)
logs = V / 'source-acquisition-logs-v2'
logs.mkdir(exist_ok=True)
state = dict(schemaVersion=1, startedAt=now(), updatedAt=now(), status='initializing',
    worker=dict(pid=os.getpid(),createTime=proc.create_time(),command=proc.cmdline(),cwd=proc.cwd()),
    resourceVerification='projects/hierarchical-game-outlines/revision-teaching-clarity-v1/source-cpu-resource-verification-v2.json',
    resourceSha256=sha(V / 'source-cpu-resource-verification-v2.json'), cpuThreads=2, gpuJobs=0,
    actualOuterExitCode=None, actualOuterSession=None, children=[], results=[], narrationCreated=False,
    sourceAudioForFinal=False, finalActionSelectionApproved=False, finalPublicRightsApproved=False,
    originalSourceRedownloaded=False)
def update(status):
    state.update(status=status,updatedAt=now())
    save(state_path,state)
    queue_path = B / 'queue.json'
    old = queue_path.read_bytes()
    queue = read(queue_path)
    review = queue['currentHierarchicalReview']
    review.update(stage='official-source-candidate-'+status,
        ownedJob=dict(worker=state['worker'], status=status,
            state=state_path.relative_to(ROOT).as_posix(), cpuThreads=2,gpuJobs=0,
            activeChildren=[x for x in state['children'] if x['status']=='running']))
    queue.update(updatedAt=now(),status='active-hierarchical-source-candidate-review',
        next='Reuse the single actual source acquisition/state/session. After its outer exit, verify worker closure and candidate sources; inspect native frames and normal1x action intervals. Duplicate decision remains gated; baseline Oct14 reservation preserved.')
    assert queue_path.read_bytes()==old, 'Concurrent queue write; preserve it rather than overwrite'
    save(queue_path,queue)
def run(kind,source,command):
    log=logs/(source['videoId']+'-'+kind+'.log.txt')
    with log.open('w',encoding='utf-8') as fd:
        child=subprocess.Popen(command,cwd=ROOT,stdout=fd,stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        cp=psutil.Process(child.pid)
        record=dict(kind=kind,videoId=source['videoId'],pid=child.pid,createTime=cp.create_time(),
            command=command,cwd=str(ROOT),startedAt=now(),status='running',log=log.relative_to(ROOT).as_posix())
        state['children'].append(record)
        update(kind+'-running')
        print(json.dumps(record),flush=True)
        exitcode=child.wait()
        record.update(status='finished' if exitcode==0 else 'failed',actualExitCode=exitcode,endedAt=now())
    update(kind+'-finished' if exitcode==0 else kind+'-failed')
    assert exitcode==0,(kind,source['videoId'],exitcode)
    return record,log
try:
    update('initializing')
    for source in sources:
        sid=source['videoId']
        info_path=META/(sid+'.info.json')
        info=read(info_path)
        assert info['channel']==source['expectedChannel'] and info['id']==sid
        target=MEDIA/(sid+'.mp4')
        assert not target.exists(), 'Existing candidate file requires direct reuse, not redownload'
        run('download',source,[str(PYTHON),'-X','utf8','-m','yt_dlp',
            '--load-info-json',str(info_path),'--no-playlist','--no-write-thumbnail',
            '--retries','3','--fragment-retries','3','--socket-timeout','30',
            '-f','299','-o',str(target)])
        probe=subprocess.run([FFPROBE,'-v','error','-show_format','-show_streams','-of','json',str(target)],
            cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        assert probe.returncode==0,probe.stderr
        pdata=json.loads(probe.stdout)
        streams=pdata['streams']
        assert len(streams)==1 and streams[0]['codec_type']=='video'
        assert streams[0]['width']==1920 and streams[0]['height']==1080
        record,log=run('whole-video-decode',source,[FFMPEG,'-hide_banner','-v','error','-threads','2',
            '-i',str(target),'-map','0:v:0','-an','-threads','2','-f','null','-'])
        assert not log.read_text('utf8').strip(), 'Inspect nonempty decode diagnostics'
        state['results'].append(dict(game=source['game'],videoId=sid,title=info['title'],
            channel=info['channel'],channelId=info['channel_id'],uploadDate=info.get('upload_date'),
            metadataPath=info_path.relative_to(ROOT).as_posix(),metadataSha256=sha(info_path),
            localMediaPath=target.relative_to(ROOT).as_posix(),fileBytes=target.stat().st_size,
            fileSha256=sha(target),video=pdata['streams'][0],duration=pdata['format']['duration'],
            wholeDecode=dict(actualExitCode=0,diagnostics=0,log=log.relative_to(ROOT).as_posix()),
            candidateOnly=True,normalPlaybackReviewed=False,movingActionSelectionApproved=False,
            finalPublicRightsApproved=False))
        update('source-acquired-decoded')
    update('acquired-decoded-awaiting-direct-action-review')
    print(json.dumps(dict(status=state['status'],sources=len(state['results']),wholeDecodes=1,
        originalSourceRedownloaded=False)),flush=True)
except Exception as error:
    state['error']=repr(error)
    update('failed')
    raise

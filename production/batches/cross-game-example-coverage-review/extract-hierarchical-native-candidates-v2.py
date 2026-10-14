"""One bounded native-PTS candidate extraction; all PNGs are local-only research."""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
import re
import subprocess
import psutil
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
OUT=V/'native-candidate-pixels-v2'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def save(p,o):
    temp=p.with_name(p.name+'.'+str(os.getpid())+'.writing')
    temp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
    os.replace(temp,p)
resource=read(V/'native-cpu-resource-verification-v2.json')
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['cpuAcquisitionEligible'] and not resource['activeOwnedMediaWorkers']
closed=read(V/'source-acquisition-execution-v1.session.json')
assert closed['actualOuterExitCode']==0 and closed['exactWorkerDead'] and closed['exactChildrenDead']
source_state=read(V/'source-acquisition-execution-v1.json')
additional_closed=read(V/'source-acquisition-execution-v2.session.json')
assert additional_closed['actualOuterExitCode']==0 and additional_closed['exactWorkerDead'] and additional_closed['exactChildrenDead']
additional_state=read(V/'source-acquisition-execution-v2.json')
assert len(additional_state['results'])==1
sources={s['videoId']:s for s in source_state['results']+additional_state['results']}
previous_review=read(V/'native-candidate-direct-review-v2.json')
assert previous_review['viewedBoardCount']==64 and previous_review['reviewedBoundNativeSampleCount']==371
previous_pts={(s['sourceId'],s['actualDecodedSourcePtsSeconds'])
    for g in previous_review['groups'] for s in read(ROOT/g['indexPath'])['samples']}
assert not (V/'native-candidate-extraction-execution-v2.json').exists(), 'Reuse the actual native worker'
OUT.mkdir(exist_ok=True)
source_groups=[
    dict(id='manor-placement-fine',sourceId='gVkhhrLARU8',offset=18,end=34,times=[18.25+i*.5 for i in range(32)]),
    dict(id='manor-market-fine',sourceId='gVkhhrLARU8',offset=80,end=91,times=[80.25+i*.5 for i in range(22)]),
    dict(id='storm-housing-fine',sourceId='qaK2FWQB7DE',offset=2930,end=2971,times=[2930.25+i*.5 for i in range(82)]),
    dict(id='storm-mine-fine',sourceId='qaK2FWQB7DE',offset=2990,end=3019,times=[2990.25+i*.5 for i in range(58)]),
    dict(id='storm-fishing-fine',sourceId='qaK2FWQB7DE',offset=3080,end=3117,times=[3080.25+i*.5 for i in range(74)]),
    dict(id='timber-early-settlement',sourceId='6TNjosDftog',offset=670,end=1084,times=[float(t) for t in range(670,1084,4)]),
    dict(id='timber-automation',sourceId='6TNjosDftog',offset=2306,end=2814,times=[float(t) for t in range(2306,2814,4)])]
assert sum(len(g['times']) for g in source_groups)==499
assert not any((g['sourceId'],t) in previous_pts for g in source_groups for t in g['times'])
verified_sources=set()
for g in source_groups:
    source=sources[g['sourceId']]
    fps=Fraction(source['video']['avg_frame_rate'])
    assert fps==60, fps
    g['localFrameNumbers']=[int(round((t-g['offset'])*float(fps))) for t in g['times']]
    g['localSourceSha256']=source['fileSha256']
    g['pointCount']=len(g['times'])
plan=dict(recordedAt=now(),groups=source_groups,sampleCount=sum(g['pointCount'] for g in source_groups),
    frameSelection='Decoded local-source native frame selection; copyts/showinfo records actual absolute source PTS. No frame-rate conversion.',
    role='additional Timberborn discovery and new precise action points; not final narration/caption approval',
    previous371PointsRepeated=0,inputDurationBoundedBeforeDecode=True,allSourceFilesWholeDecodedAlready=True,
    repeatedWholeQaDecode=False,allNewPngLocalOnly=True)
save(V/'native-candidate-extraction-plan-v2.json',plan)
process=psutil.Process()
state=dict(startedAt=now(),status='initializing',updatedAt=now(),worker=dict(pid=process.pid,
    createTime=process.create_time(),command=process.cmdline(),cwd=process.cwd()),cpuThreads=2,gpuJobs=0,
    resourceSha256=sha(V/'native-cpu-resource-verification-v2.json'),planSha256=sha(V/'native-candidate-extraction-plan-v2.json'),
    children=[],groups=[],sampleCount=0,boardCount=0,actualOuterExitCode=None,actualOuterSession=None,
    sourcePixelsDirectlyReviewed=False,newNarrationCreated=False)
state_path=V/'native-candidate-extraction-execution-v2.json'
def update(status):
    state.update(status=status,updatedAt=now())
    save(state_path,state)
    qpath=ROOT/'production/batches/cross-game-example-coverage-review/queue.json'
    old=qpath.read_bytes();q=read(qpath)
    q['currentHierarchicalReview'].update(stage='native-candidate-'+status,ownedJob=dict(
        worker=state['worker'],status=status,state=state_path.relative_to(ROOT).as_posix(),cpuThreads=2,gpuJobs=0,
        activeChildren=[c for c in state['children'] if c['status']=='running']))
    q.update(updatedAt=now(),status='active-hierarchical-native-candidate-review',next='Reuse the one actual native extraction/state/session. After actual exit and closure, read every new candidate board/selected full-resolution native image once, then inspect precise normal1x action intervals before any new narration. Original reservation/media/PCM remain preserved.')
    assert qpath.read_bytes()==old
    save(qpath,q)
try:
    update('initializing')
    for g in source_groups:
        source=sources[g['sourceId']]
        if g['sourceId'] not in verified_sources:
            assert sha(ROOT/source['localMediaPath'])==source['fileSha256']
            verified_sources.add(g['sourceId'])
        folder=OUT/g['id'];folder.mkdir(exist_ok=True)
        frames=folder/'frames';frames.mkdir(exist_ok=True)
        assert not list(frames.glob('*.png'))
        filter_path=folder/'select.filter.txt'
        filter_path.write_text("select='"+'+'.join('eq(n,'+str(n)+')' for n in g['localFrameNumbers'])+"',showinfo",'utf8')
        log=folder/'extract.log.txt'
        command=[FF,'-hide_banner','-loglevel','info','-threads','2','-copyts','-ss',str(g['offset']),
            '-t',str(g['end']-g['offset']),'-i',str(ROOT/source['localMediaPath']),
            '-filter_script:v',str(filter_path),'-vsync','0','-an','-threads','2',str(frames/'frame-%04d.png')]
        with log.open('w',encoding='utf8') as fd:
            child=subprocess.Popen(command,cwd=ROOT,stdout=fd,stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            cp=psutil.Process(child.pid)
            record=dict(group=g['id'],pid=child.pid,createTime=cp.create_time(),command=command,cwd=str(ROOT),
                status='running',startedAt=now(),log=log.relative_to(ROOT).as_posix())
            state['children'].append(record);update('extracting')
            print(json.dumps(dict(group=g['id'],pid=child.pid,createTime=cp.create_time(),points=g['pointCount'])),flush=True)
            code=child.wait()
            record.update(status='finished' if code==0 else 'failed',actualExitCode=code,endedAt=now())
        assert code==0,(g['id'],code)
        pts=[float(m.group(1)) for m in re.finditer(r'Parsed_showinfo_.*?\bn:\s*\d+.*?\bpts_time:\s*([-0-9.e+]+)',log.read_text('utf8'))]
        images=sorted(frames.glob('frame-*.png'))
        assert len(images)==len(pts)==g['pointCount'],(g['id'],len(images),len(pts),g['pointCount'])
        samples=[]
        for i,(frame,actual_pts,target) in enumerate(zip(images,pts,g['times'])):
            assert abs(actual_pts-target)<.001,(g['id'],actual_pts,target)
            with Image.open(frame) as img:assert img.size==(1920,1080)
            samples.append(dict(index=i+1,path=frame.relative_to(ROOT).as_posix(),sha256=sha(frame),
                sourceId=g['sourceId'],plannedSourceSeconds=target,actualDecodedSourcePtsSeconds=actual_pts,
                localSourceNativeFrameEstimate=round(actual_pts*60),nativeFrameEstimateIsOriginalYouTubeFrameIdentity=False))
        boards=[]
        for start in range(0,len(samples),6):
            group=samples[start:start+6]
            board=Image.new('RGB',(1920,790),'#18212b');d=ImageDraw.Draw(board)
            for index,sample in enumerate(group):
                x=(index%3)*640;y=(index//3)*390
                with Image.open(ROOT/sample['path']) as img:board.paste(img.convert('RGB').resize((640,360),Image.Resampling.LANCZOS),(x,y+30))
                d.text((x+8,y+7),g['id']+' #'+str(sample['index'])+' / PTS '+str(sample['actualDecodedSourcePtsSeconds'])+'s',fill='white')
            dest=folder/('board-'+str(len(boards)+1).zfill(3)+'.jpg')
            board.save(dest,quality=94)
            boards.append(dict(index=len(boards)+1,path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),
                sampleIndices=[s['index'] for s in group]))
        group_index=dict(**g,samples=samples,boards=boards,allBoardsDirectlyViewed=False,
            wholeSourceDecodeReused=True,actualExtractExitCode=code,allImagesLocalOnly=True)
        save(folder/'index.json',group_index)
        state['groups'].append(dict(id=g['id'],indexPath=(folder/'index.json').relative_to(ROOT).as_posix(),
            indexSha256=sha(folder/'index.json'),sampleCount=len(samples),boardCount=len(boards)))
        state['sampleCount']+=len(samples);state['boardCount']+=len(boards);update('group-complete')
    update('completed-awaiting-direct-review')
    print(json.dumps(dict(status=state['status'],sampleCount=state['sampleCount'],boardCount=state['boardCount'])),flush=True)
except Exception as error:
    state['error']=repr(error);update('failed');raise

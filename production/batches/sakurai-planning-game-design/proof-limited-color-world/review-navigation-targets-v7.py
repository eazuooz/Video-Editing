"""One CPU2/GPU0 job for new useful source candidates, reusing sealed pixels.

No original decode/QA is repeated and no candidate is automatically adopted.
"""
import os
os.environ['OMP_NUM_THREADS'] = '2'
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, re, subprocess, sys, traceback
import psutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[4]
P = Path(__file__).resolve().parent
BASE = ROOT/'projects/limited-color-world/production'
STATE = P/'navigation-targets-execution-v7.json'
QA = ROOT/'shared/output/limited-color-world/preflight/navigation-targets-v7'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: p.relative_to(ROOT).as_posix()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return h.hexdigest()
def save(p,d):
    t = p.with_name(p.name+f'.{os.getpid()}.writing')
    t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
    os.replace(t,p)

ap = argparse.ArgumentParser()
ap.add_argument('--resource', required=True)
args = ap.parse_args()
resource = read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds() < 240
assert resource['ownHeavyJobs'] == 0 and resource['cpuLoadPercent'] < 85 and resource['freePhysicalMemoryKiB'] > 8_000_000
assert not STATE.exists() and not QA.exists()
context = read(BASE/'current-contexts-asr-execution-v1.json')
assert context['actualExitObserved'] and context['actualOuterExitCode'] == 0
assert read(BASE/'current-independent-voice-direct-review-v1.json')['independent24CompleteTextsDirectlyRead']
check = subprocess.run([NODE,'scripts/review-video-duplicates.cjs','limited-color-world','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
assert check.returncode == 0, check.stdout+check.stderr
assert read(P/'extra-native-action-direct-review-v4.json')['all27BoardsAnd134SamplesDirectlyRead']
cuts = [{'key': 'town-entry-navigation', 'source': 'chicory-b-roll-1', 'startFrame': 11400, 'endFrameExclusive': 11580, 'candidateSeconds': 3, 'framingUpPixels': 120, 'provisionalInsertion': 'generic-outline-navigation', 'caveat': 'Coarse190–192 movement after dialogue189, before current193 painting. Verify all native boundaries/ongoing motion/UI; no dialogue or idle quota.', 'selected': False, 'sourceAdoptionApproved': False, 'finalCueUiApproved': False, 'startSeconds': 190, 'endSeconds': 193}, {'key': 'interior-door-navigation', 'source': 'chicory-b-roll-1', 'startFrame': 23040, 'endFrameExclusive': 23160, 'candidateSeconds': 2, 'framingUpPixels': 120, 'provisionalInsertion': 'generic-outline-navigation', 'caveat': 'Coarse384–386 interior movement before dialogue387. Inspect movement/dark outlined objects and correct crop; no claim painting or house-specific geometry.', 'selected': False, 'sourceAdoptionApproved': False, 'finalCueUiApproved': False, 'startSeconds': 384, 'endSeconds': 386}]
assert sum(c['candidateSeconds'] for c in cuts)==5
protected_paths = [ROOT/'projects/limited-color-world/script/narration.ko.json',ROOT/'projects/limited-color-world/script/narration.en.json',
    ROOT/'projects/limited-color-world/sources/game-candidates.json',BASE/'narration-tts-request-v1.json',
    BASE/'current-independent-voice-direct-review-v1.json',ROOT/'projects/limited-color-world/planning/causal-chain-additions-v1.json',P/'source-action-bank-v2.json',ROOT/'projects/limited-color-world/sources/game-candidates-v2.json',BASE/'causal-bridge-targeted-voice-direct-review-v1.json']
protected = {rel(p):sha(p) for p in protected_paths}
tts = read(BASE/'narration-tts-execution-v1.json')
bridge = read(BASE/'causal-bridge-tts-execution-v1.json')
assert bridge['actualOuterExitCode']==0 and bridge['researchResumeVerified']
assert read(BASE/'causal-bridge-targeted-voice-direct-review-v1.json')['current3WholePlus3IndependentPlus2AdaptiveContextsDirectlyCompared']
protected_pcm = {x['path']:x['sha256'] for x in tts['results']+bridge['results']}
assert all(sha(ROOT/p)==h for p,h in protected_pcm.items())
state = dict(schemaVersion=4,slug='limited-color-world',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),
    commandLine=psutil.Process().cmdline(),cwd=str(ROOT),sessionId=None,cpuThreads=2,gpuJobs=0,resource=resource,
    currentDuplicateCheck=dict(exitCode=0,stdout=check.stdout,stderr=check.stderr),protectedInputs=protected,protectedOriginal8Pcm=protected_pcm,
    candidateSeconds=5,planCuts=cuts,children=[],sources=[],cuts=[],exitCode=None,actualExitObserved=False,
    allPixelsDirectlyRead=False,normalPlaybackApproved=False,sourceAdoptionApproved=False,finalCueUiApproved=False,
    finalRatioApproved=False,publicRightsApproved=False,researchManipulated=False,researchResumeClaim=False,
    gitImagesOrMediaAdded=0,
    excludedDrawingMenu='B-roll1 407–422 T-shirt customization is a drawing interface, not selected gameplay. Do not use a menu to fill the actual-game quota even though brush strokes are active. Coarse review remains preserved.')
QA.mkdir(parents=True)
def checkpoint(status):
    state.update(status=status,updatedAt=now())
    session_path = STATE.with_name(STATE.stem+'.session.json')
    if session_path.exists():
        ss = read(session_path)
        if ss['pid'] == os.getpid() and abs(ss['createTime']-state['createTime']) < .01: state['sessionId'] = ss['sessionId']
    save(STATE,state)
    cp = read(BASE/'latest-checkpoint.json')
    job = {k:state[k] for k in ['pid','createTime','commandLine','cwd','sessionId','cpuThreads','gpuJobs','exitCode']}
    job.update(state=rel(STATE),singleJob=True,workerExpectedRunning=state['exitCode'] is None,child=state['children'][-1] if state['children'] else None)
    cp.update(recordedAt=now(),stage='new-navigation-targets-'+status,ownedJob=job,
        nextAction='Observe actual v7 exit and directly read every new navigation/caption sample. Preserve31window bankv2, all11PCM and completed3whole+3complete+2target bridge ASR. Confirm ongoing useful action before allocation; final gates remain false.')
    save(BASE/'latest-checkpoint.json',cp)
    qp = ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    for _ in range(10):
        raw = qp.read_bytes(); q = json.loads(raw)
        item = next(x for x in q['items'] if x['slug']=='limited-color-world')
        assert item['videoId'] is None
        item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction'])
        q['updatedAt']=q['lastProgressAt']=now()
        if qp.read_bytes()==raw: save(qp,q); break
    else: raise RuntimeError('Concurrent queue change; preserve foreign work.')

try:
    if os.name=='nt':
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
    checkpoint('running')
    coarse = read(P/'chicory-coarse-direct-review-v1.json')
    prior = read(P/'chicory-native-candidate-execution-v1.json')
    trimmed = read(P/'chicory-trimmed-framing-execution-v2.json')
    extra = read(P/'extra-native-action-execution-v4.json')
    targets = read(P/'extra-native-targets-execution-v5.json')
    plant=read(P/'plant-endpoints-execution-v6.json')
    assert read(P/'extra-native-target-direct-review-v5.json')['all12BoardsAnd57SamplesDirectlyRead']
    assert extra['actualExitObserved'] and extra['actualOuterExitCode']==0
    allmaps = {}
    for source in coarse['verifiedSources']:
        key = source['source']; media = ROOT/source['path']
        assert sha(media)==source['sha256']
        native = read(ROOT/source['nativePtsPath'])['frames']
        old = {s['nativeFrame']:s for s in source['samples']}
        for d in [prior,trimmed,extra,targets,plant]:
            s = next(x for x in d['sources'] if x['key']==key)
            for x in s['sampleMap']: old.setdefault(x['nativeFrame'],x)
        wanted = set()
        for c in cuts:
            if c['source']==key:
                a,b=c['startFrame'],c['endFrameExclusive']
                wanted.update([] if c.get('endpointsOnly') else range(a,b,30)); wanted.update([a-1,a,a+1,b-1,b,b+1])
        wanted = sorted(n for n in wanted if 0<=n<len(native))
        assert all(int(native[n]['best_effort_timestamp'])==n*256 for n in wanted)
        missing = [n for n in wanted if n not in old]
        sub = QA/key; sub.mkdir()
        new = {}
        if missing:
            pts = [n*256 for n in missing]
            expr = '+'.join(f'eq(pts,{p})' for p in pts)
            logp = sub/'new-missing-pts.log'
            cmd = [FF,'-nostdin','-n','-v','info','-threads','2','-filter_threads','1',
                '-ss',f'{max(0,missing[0]/60-1):.9f}','-copyts','-i',str(media),
                '-vf',"select='"+expr+"',showinfo",'-frames:v',str(len(missing)),
                '-fps_mode','passthrough','-an','-threads','2',str(sub/'new-%04d.png')]
            with logp.open('xb') as log:
                child = subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
                rec = dict(pid=child.pid,createTime=psutil.Process(child.pid).create_time(),commandLine=cmd,log=rel(logp),startedAt=now(),status='running')
                state['children'].append(rec); checkpoint('extracting-new-pts'); child.wait()
                rec.update(status='closed',exitCode=child.returncode,finishedAt=now())
                assert child.returncode==0
            actual = [int(p) for p in re.findall(r'\bn:\s*\d+\s+pts:\s*(-?\d+)',logp.read_text('utf-8',errors='replace'))]
            assert actual==pts,'Preserve output: actual absolute PTS mismatch.'
            files = sorted(sub.glob('new-*.png')); assert len(files)==len(missing)
            new = {n:dict(path=rel(p),sha256=sha(p),nativeFrame=n,pts=n*256,timeSeconds=n/60,reusedPrior=False) for n,p in zip(missing,files)}
        mapping = {}
        for n in wanted:
            if n in old:
                s = old[n]; assert s['pts']==n*256 and sha(ROOT/s['path'])==s['sha256']
                mapping[n]={**s,'reusedPrior':True}
            else: mapping[n]=new[n]
        allmaps[key]=mapping
        state['sources'].append(dict(key=key,path=source['path'],sha256=source['sha256'],nativePtsPath=source['nativePtsPath'],nativePtsSha256=source['nativePtsSha256'],
            actualPtsMatchedFrameTimes256=True,newSamples=len(new),reusedSamples=len(wanted)-len(new),sampleMap=list(mapping.values())))
        checkpoint('source-ready')
    fontp = Path('C:/Windows/Fonts/NotoSansKR-VF.ttf')
    font = ImageFont.truetype(str(fontp),48)
    if hasattr(font,'get_variation_axes'): font.set_variation_by_axes([500 if a['minimum']<=500<=a['maximum'] else a['default'] for a in font.get_variation_axes()])
    lines=['색이 바뀌어도 윤곽과 높이로','길의 상태를 읽을 수 있습니다.']
    bw=round(max(font.getlength(t) for t in lines))+44;bh=146
    rect=[960-bw//2,970-bh//2,960-bw//2+bw,970-bh//2+bh]
    state['captionTest']=dict(lines=lines,font= str(fontp),fontSha256=sha(fontp),size=48,weight=500,boxRect=rect,
        center=[960,970],scope='Two-line placeholder, not final narration cue approval.',upCropAndBottomBlur='same native frame,120px where planned; blur22')
    label = ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
    for c in cuts:
        sub=QA/c['key'];sub.mkdir();a,b=c['startFrame'],c['endFrameExclusive']
        indices=sorted(set([] if c.get('endpointsOnly') else range(a,b,30))|{a-1,a,a+1,b-1,b,b+1});samples=[]
        for n in indices:
            s=allmaps[c['source']][n]
            with Image.open(ROOT/s['path']) as im: original=im.convert('RGB');assert original.size==(1920,1080)
            framed=original.copy();up=c['framingUpPixels']
            if up:
                framed.paste(original.crop((0,up,1920,1080)),(0,0))
                framed.paste(original.crop((0,1080-up,1920,1080)).filter(ImageFilter.GaussianBlur(22)),(0,1080-up))
            d=ImageDraw.Draw(framed);x,y,xx,yy=rect
            d.rectangle((x+14,y+14,xx+14,yy+14),fill='#073c32')
            d.rectangle(rect,fill='white',outline='#161b18',width=3)
            for i,line in enumerate(lines): d.text((960,y+11+(i+.5)*62),line,font=font,fill='#080b09',anchor='mm')
            old_caption=next((x for oldc in extra['cuts']+targets['cuts'] if oldc['source']==c['source'] and oldc['framingUpPixels']==up for x in oldc['samples'] if x['nativeFrame']==n),None)
            if old_caption:
                fp=ROOT/old_caption['captionTestPath'];assert sha(fp)==old_caption['captionTestSha256']
            else:
                fp=sub/f'f{n:06d}-caption-test.png';framed.save(fp)
            role='before-start' if n==a-1 else 'first-included' if n==a else 'after-start' if n==a+1 else 'last-included' if n==b-1 else 'first-excluded' if n==b else 'after-end' if n==b+1 else 'within-candidate'
            samples.append({**s,'inCandidate':a<=n<b,'boundaryRole':role,'captionTestPath':rel(fp),'captionTestSha256':sha(fp)})
        boards=[]
        for off in range(0,len(samples),6):
            board=Image.new('RGB',(1920,816),(24,24,24));d=ImageDraw.Draw(board)
            for k,s in enumerate(samples[off:off+6]):
                x=k%3*640;y=k//3*408
                with Image.open(ROOT/s['captionTestPath']) as im: board.paste(im.resize((640,360)),(x,y+36))
                d.text((x+6,y+3),c['key']+' f'+str(s['nativeFrame']),font=label,fill='white')
                d.text((x+6,y+384),f"{s['boundaryRole']} PTS{s['pts']} t{s['timeSeconds']:.6f}",font=label,fill=(180,230,230))
            bp=sub/f'board-{off//6+1:03}.jpg';board.save(bp,quality=94)
            boards.append(dict(path=rel(bp),sha256=sha(bp),sampleRange=[off,min(off+6,len(samples))]))
        state['cuts'].append({**c,'samples':samples,'boards':boards,'directPixelReview':False})
        checkpoint('caption-framing-ready')
    assert all(sha(ROOT/p)==h for p,h in protected.items())
    assert all(sha(ROOT/p)==h for p,h in protected_pcm.items())
    state.update(exitCode=0,finishedAt=now(),newSampleCount=sum(s['newSamples'] for s in state['sources']),
        reusedSampleCount=sum(s['reusedSamples'] for s in state['sources']),
        totalUniqueSampleCount=sum(len(s['sampleMap']) for s in state['sources']),
        totalCaptionSampleCount=sum(len(c['samples']) for c in state['cuts']),totalBoards=sum(len(c['boards']) for c in state['cuts']),
        protectedInputsAnd11PcmUnchanged=True)
    checkpoint('closed-awaiting-direct-review')
    print(json.dumps({k:state[k] for k in ['pid','createTime','exitCode','newSampleCount','reusedSampleCount','totalUniqueSampleCount','totalCaptionSampleCount','totalBoards']}),flush=True)
except BaseException:
    state.update(exitCode=1,finishedAt=now(),error=traceback.format_exc())
    checkpoint('closed-failed');print(state['error'],flush=True);raise

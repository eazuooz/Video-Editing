"""Inspect missing trimmed endpoints and fixed-caption framing; no footage adoption."""
import os
os.environ['OMP_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,re,subprocess,sys,traceback
import psutil
from PIL import Image,ImageDraw,ImageFont,ImageFilter

ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
STATE=P/'chicory-trimmed-framing-execution-v2.json'
QA=ROOT/'shared/output/limited-color-world/preflight/chicory-trimmed-v2'
QUEUE=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
stamp=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def rel(p):return str(p.relative_to(ROOT)).replace('\\','/')
def write(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
assert not STATE.exists(),'Preserve existing execution; do not rerun.'
planpath=P/'chicory-trimmed-framing-plan-v2.json';plan=json.loads(planpath.read_text(encoding='utf-8'))
priorpath=P/'chicory-native-candidate-execution-v1.json';prior=json.loads(priorpath.read_text(encoding='utf-8'))
reviewpath=P/'chicory-native-sample-direct-review-v1.json';review=json.loads(reviewpath.read_text(encoding='utf-8'))
assert review['actualOuterExitCode']==0 and review['allSamplesAndBoardsDirectlyRead']
check=subprocess.run([NODE,'scripts/review-video-duplicates.cjs','limited-color-world','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
assert check.returncode==0,check.stdout+check.stderr
protected={rel(p):sha(p) for p in [planpath,priorpath,reviewpath,P/'chicory-native-observations-v1.json',P/'source-visual-concept-direct-review-v2.json',P/'content-studio-direct-review-v2.json']}
state={'schemaVersion':2,'slug':'limited-color-world','status':'initializing','startedAt':stamp(),'pid':os.getpid(),'processCreateTime':psutil.Process().create_time(),'commandLine':sys.argv,'workingDirectory':str(ROOT),'sessionId':None,'cpuThreads':2,'gpuJobs':0,'children':[],'sources':[],'cuts':[],'plan':rel(planpath),'planSha256':sha(planpath),'protectedInputs':protected,'currentDistinctCheck':{'exitCode':check.returncode,'stdout':check.stdout,'stderr':check.stderr},'sourceFootageAdopted':False,'exactTrimmedBoundaryApproved':False,'captionFramingApproved':False,'finalCaptionCueApproved':False,'publicRightsApproved':False,'newProjectScriptTtsMc':False,'researchManipulated':False,'ownResearchResumeClaim':False,'gitImagesOrMediaAdded':0}
QA.mkdir(parents=True,exist_ok=False)
def save(status):
    state.update(status=status,updatedAt=stamp())
    sp=STATE.with_name(STATE.name+'.session.json')
    if sp.exists():
        ss=json.loads(sp.read_text(encoding='utf-8-sig'))
        if ss.get('pid')==os.getpid():state['sessionId']=ss['sessionId']
    write(STATE,state)
    before=QUEUE.read_bytes();q=json.loads(before);item=next(x for x in q['items'] if x['slug']=='limited-color-world')
    assert item['videoId'] is None and not any(item['checkpoints'].values())
    item.update(stage='chicory-trimmed-framing-'+status,updatedAt=state['updatedAt'])
    item['execution']={k:state[k] for k in ('status','pid','processCreateTime','commandLine','workingDirectory','sessionId','cpuThreads','gpuJobs')}
    item['execution'].update(phase='trimmed-endpoints-and-caption-framing',state=rel(STATE),child=state['children'][-1] if state['children'] else None)
    item['nextAction']='Read every new exact-PTS trimmed-boundary and fixed-caption framed sample; preserve all prior reviews and approve only observed scope before source adoption.'
    q['updatedAt']=q['lastProgressAt']=state['updatedAt'];assert QUEUE.read_bytes()==before;write(QUEUE,q)
try:
    cim=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|ffmpeg|ffprobe' -or $_.ProcessId -in 27140,63080,56464 } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],capture_output=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    write(P/'chicory-resource-before-trimmed-v2.json',{'recordedAt':stamp(),'processCim':cim.stdout.decode('utf-8-sig',errors='replace'),'gpu':gpu.stdout.decode().strip(),'ownJob':'single CPU2/GPU0 missing endpoint extraction and framing inspection','foreignJobsPreserved':True,'researchManipulated':False})
    fontpath=Path('C:/Windows/Fonts/NotoSansKR-VF.ttf');font=ImageFont.truetype(str(fontpath),48)
    variation=None
    if hasattr(font,'get_variation_axes'):
        axes=font.get_variation_axes();variation=[500 if a['minimum']<=500<=a['maximum'] else a['default'] for a in axes];font.set_variation_by_axes(variation)
    lines=plan['captionTest']['text'].split('\n');bw=round(max(font.getlength(s) for s in lines))+44;bh=len(lines)*62+22
    assert bw<=1614 and bh==146
    state['captionTest']={**plan['captionTest'],'fontPath':str(fontpath),'fontSha256':sha(fontpath),'variationAxes':variation,'boxRect':[960-bw//2,970-bh//2,960-bw//2+bw,970-bh//2+bh],'scope':'Measured QA placeholder. Final narration cues remain unapproved.'}
    label=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
    save('running');allmaps={}
    for source in prior['sources']:
        key=source['key'];cuts=[c for c in plan['cuts'] if c['source']==key];media=ROOT/source['sourcePath'];assert sha(media)==source['sourceSha256']
        old={s['nativeFrame']:s for s in source['sampleMap']};wanted=set()
        for c in cuts:
            a,b=c['startFrame'],c['endFrameExclusive'];wanted.update(range(a,b,30));wanted.update([a-1,a,a+1,b-1,b,b+1])
        wanted=sorted(wanted);missing=[n for n in wanted if n not in old]
        sub=QA/key;sub.mkdir();logpath=sub/'missing-endpoints.log';new={}
        if missing:
            pts=[n*256 for n in missing];expression='+'.join(f'eq(pts,{p})' for p in pts)
            args=[FF,'-nostdin','-n','-v','info','-threads','2','-filter_threads','2','-ss',f'{max(0,pts[0]/15360-1):.9f}','-copyts','-i',str(media),'-vf',"select='"+expression+"',showinfo",'-frames:v',str(len(pts)),'-fps_mode','passthrough','-an','-threads','2',str(sub/'endpoint-%04d.png')]
            with logpath.open('wb') as log:
                child=subprocess.Popen(args,cwd=ROOT,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
                rec={'label':key+'-missing-trimmed-endpoints','pid':child.pid,'processCreateTime':psutil.Process(child.pid).create_time(),'commandLine':args,'startedAt':stamp(),'status':'running','log':rel(logpath)};state['children'].append(rec);save('extracting');child.wait();rec.update(status='exited',exitCode=child.returncode,endedAt=stamp());assert child.returncode==0
            actual=[int(p) for p in re.findall(r'\bn:\s*\d+\s+pts:\s*(-?\d+)',logpath.read_text(encoding='utf-8',errors='replace'))];assert actual==pts,'Actual absolute PTS mismatch; preserve outputs.'
            files=sorted(sub.glob('endpoint-*.png'));assert len(files)==len(missing)
            new={n:{'nativeFrame':n,'pts':n*256,'timeSeconds':n/60,'path':rel(ip),'sha256':sha(ip),'reusedPriorSample':False} for n,ip in zip(missing,files)}
        mapping={}
        for n in wanted:
            if n in old:
                s=old[n];assert s['pts']==n*256 and sha(ROOT/s['path'])==s['sha256'];mapping[n]={**s,'reusedPriorSample':True}
            else:mapping[n]=new[n]
        allmaps[key]=mapping;state['sources'].append({'key':key,'sourcePath':source['sourcePath'],'sourceSha256':source['sourceSha256'],'timeBase':'1/15360','nativeFramePtsStep':256,'actualMissingSelectedPtsVerified':True,'newSamples':len(new),'reusedSamples':len(wanted)-len(new),'sampleMap':list(mapping.values())});save('source-extracted')
    for c in plan['cuts']:
        a,b=c['startFrame'],c['endFrameExclusive'];indices=sorted(set(range(a,b,30))|{a-1,a,a+1,b-1,b,b+1});samples=[];sub=QA/c['key'];sub.mkdir();up=c['framingUpPixels']
        for n in indices:
            s=allmaps[c['source']][n]
            with Image.open(ROOT/s['path']) as im:original=im.convert('RGB');assert original.size==(1920,1080)
            framed=original.copy()
            if up:
                framed.paste(original.crop((0,up,1920,1080)),(0,0));framed.paste(original.crop((0,1080-up,1920,1080)).filter(ImageFilter.GaussianBlur(22)),(0,1080-up))
            plain=sub/f'f{n:06d}-framed.png';framed.save(plain)
            boxed=framed.copy();d=ImageDraw.Draw(boxed);x,y,xx,yy=state['captionTest']['boxRect'];d.rectangle((x+14,y+14,xx+14,yy+14),fill='#073c32');d.rectangle((x,y,xx,yy),fill='white',outline='#161b18',width=3)
            for j,line in enumerate(lines):d.text((960,y+11+(j+.5)*62),line,font=font,fill='#080b09',anchor='mm')
            bp=sub/f'f{n:06d}-caption-test.png';boxed.save(bp)
            samples.append({**s,'inSelectedCut':a<=n<b,'boundaryRole':['before-start' if n==a-1 else 'first-included' if n==a else 'after-start' if n==a+1 else 'last-included' if n==b-1 else 'first-excluded' if n==b else 'after-end' if n==b+1 else 'within-cut'][0],'framedPath':rel(plain),'framedSha256':sha(plain),'captionTestPath':rel(bp),'captionTestSha256':sha(bp)})
        boards=[]
        for off in range(0,len(samples),6):
            board=Image.new('RGB',(1920,816),(24,24,24));d=ImageDraw.Draw(board)
            for k,s in enumerate(samples[off:off+6]):
                x=k%3*640;y=k//3*408
                with Image.open(ROOT/s['captionTestPath']) as im:board.paste(im.resize((640,360)),(x,y+36))
                d.text((x+6,y+3),c['key']+' f'+str(s['nativeFrame']),font=label,fill='white');d.text((x+6,y+384),f"{s['boundaryRole']} t{s['timeSeconds']:.6f}",font=label,fill=(180,230,230))
            bp=sub/f'board-{off//6+1:03d}.jpg';board.save(bp,quality=94);boards.append({'path':rel(bp),'sha256':sha(bp),'sampleRange':[off,min(off+6,len(samples))]})
        state['cuts'].append({**c,'samples':samples,'boards':boards,'directReviewApproved':False});save('framing-generated')
    assert all(sha(ROOT/p)==h for p,h in protected.items())
    state.update(totalUniqueSourceSamples=sum(len(s['sampleMap']) for s in state['sources']),newEndpointSamples=sum(s['newSamples'] for s in state['sources']),reusedSourceSamples=sum(s['reusedSamples'] for s in state['sources']),framedSampleCount=sum(len(c['samples']) for c in state['cuts']),totalBoards=sum(len(c['boards']) for c in state['cuts']),protectedInputHashesUnchanged=True)
    save('exited-awaiting-direct-review');print(json.dumps({k:state[k] for k in ('status','totalUniqueSourceSamples','newEndpointSamples','reusedSourceSamples','framedSampleCount','totalBoards')},ensure_ascii=False),flush=True)
except BaseException:
    state['error']=traceback.format_exc()
    try:save('failed')
    except Exception:write(STATE,state)
    print(state['error'],flush=True);sys.exit(1)

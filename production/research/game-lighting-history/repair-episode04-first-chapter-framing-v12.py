"""CPU2 scoped pixel repair; reuse completed cuts/audio, preserve every old file."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, psutil, shutil

ROOT = Path(__file__).resolve().parents[3]
P = ROOT/'projects/game-lighting-history-04/production'
OLD = ROOT/'production/research/game-lighting-history/local/episode04-first-chapter-review-v10'
OUT = ROOT/'production/research/game-lighting-history/local/episode04-first-chapter-framing-v12'
FF = Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
FP = FF.with_name('ffprobe.exe')
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
stamp = lambda: datetime.now(timezone.utc).isoformat()

review_path = P/'first-chapter-encoded-direct-review-v11.json'
review = read(review_path)
assert review['allFirstChapterSampledPixelsRead'] and not review['firstChapterCaptionClearanceApproved']
build_path = P/'first-chapter-review-build-v11.json'
build = read(build_path)
plan_path = P/'first-chapter-review-plan-v10.json'
plan = read(plan_path)
old_state = read(P/'first-chapter-review-execution-v10.json')
assert len(old_state['results']) == 18 and len(plan['cuts']) == 18
assert sha(plan_path) == build['plan']['sha256']
for x in build['outputs']:
    assert sha(ROOT/x['path']) == x['sha256']
for x in old_state['results']:
    assert sha(ROOT/x['path']) == x['sha256']
assert not OUT.exists(), 'Never overwrite completed or historical media'
assert shutil.disk_usage(ROOT).free > 4*1024**3
resources = []
for p in psutil.process_iter(['pid','ppid','name','cmdline','create_time']):
    try:
        d = p.info
        cmd = ' '.join(d['cmdline'] or [])
        if d['name'] and any(n in d['name'].lower() for n in ['ffmpeg','python']):
            resources.append(d)
        if d['name'] and 'ffmpeg' in d['name'].lower() and 'game-lighting-history' in cmd:
            raise RuntimeError('Owned media slot busy')
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
gpu = subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()

OUT.mkdir()
SP = P/'first-chapter-framing-repair-execution-v12.json'
assert not SP.exists()
me = psutil.Process()
state = {
    'startedAt':stamp(), 'status':'running',
    'worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},
    'resourceObservation':{'processes':resources,'gpu':gpu},
    'cpuThreads':2,'gpuJobs':0,'active':None,'commands':[],'results':[],
    'review':{'path':rel(review_path),'sha256':sha(review_path)},
    'plan':{'path':rel(plan_path),'sha256':sha(plan_path)},
    'preservedInputs':build['outputs'], 'preservedPcm':old_state['pcm'],
    'sourceModelsRerendered':0,'newTts':0,'newGitImages':0,
    'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'qaApproved':False,'uploaded':False
}
def save():
    SP.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def checkpoint():
    p = ROOT/'production/research/game-lighting-history/checkpoint.json'
    j = read(p)
    j['episode04FirstChapterFramingRepair'] = {
        'execution':rel(SP),'status':state['status'],'worker':state['worker'],
        'active':state['active'],'cutsRecorded':len(state['results']),
        'cpuThreads':2,'gpuJobs':0,'allFinalPixelsReviewed':False
    }
    j['ownedActiveWork'] = ({'type':'CPU-first-chapter-framing-repair-v12','execution':rel(SP),'worker':state['worker'],'active':state['active'],'cpuThreads':2,'gpuJobs':0,'next':'Direct encoded repairs/cues review; continuous playback and remaining99 paragraphs pending'}
        if state['status']=='running' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Extract only changed first-chapter encoded pixels; no completed-source rerender'})
    j['updatedAt'] = stamp()
    tmp=p.with_suffix('.framing-v12.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(p)
def run(cmd,label):
    cmd=[str(x) for x in cmd]
    log=OUT/(label+'.log')
    with log.open('w',encoding='utf-8') as f:
        p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f)
        proc=psutil.Process(p.pid)
        state['active']={'pid':p.pid,'createTime':proc.create_time(),'commandLine':cmd,'cwd':str(ROOT),'log':rel(log),'startedAt':stamp()}
        save();checkpoint();code=p.wait()
    result={**state['active'],'exitCode':code,'endedAt':stamp()}
    state['commands'].append(result);state['active']=None;save()
    assert code==0,(label,code)
    return result
def textfilter(text,x,y,size=28,color='white',label='label'):
    file=OUT/(label+'.txt');file.write_text(text,'utf-8')
    return f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='{rel(file)}':x={x}:y={y}:fontsize={size}:fontcolor={color}:box=1:boxcolor=black@0.75:boxborderw=8"
def probe(file):
    cmd=[str(FP),'-v','error','-threads','2','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,duration,sample_rate,channels:format=duration','-of','json',str(file)]
    j=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
    v=next(x for x in j['streams'] if x['codec_type']=='video')
    assert (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_read_frames']))==(1920,1080,'60/1','1/90000',11664)
    assert abs(float(v['duration'])-194.4)<1/90000
    packets=json.loads(subprocess.run([str(FP),'-v','error','-threads','2','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets']
    assert sorted(x['pts'] for x in packets)==list(range(0,11664*1500,1500))
    explicit=[x['duration'] for x in packets if 'duration' in x]
    assert all(d==1500 for d in explicit)
    pa=json.loads(subprocess.run([str(FP),'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(file)],capture_output=True,text=True,check=True).stdout)['packets']
    ah=hashlib.sha256('\n'.join(x['data_hash'] for x in pa).encode()).hexdigest()
    return {'path':rel(file),'sha256':sha(file),'probe':j,'probeCommand':cmd,'frames':11664,'allPresentationPtsContinuous':True,'explicitPacketDurationCount':len(explicit),'missingPacketDurationCount':len(packets)-len(explicit),'aacPayloadSha256':ah}
try:
    save();checkpoint()
    pieces=[]
    for i,(cut,old) in enumerate(zip(plan['cuts'],old_state['results'])):
        assert cut['id']==old['id']
        src=ROOT/old['path']; frames=cut['frames']
        is_model=cut['kind']=='explanation' and not cut.get('freezeFrameOnly')
        is_rdoc=cut['id'] in ['overview-renderdoc','original-silent-boundary']
        if not is_model and not is_rdoc and cut['id']!='overview-cyber':
            state['results'].append({**old,'reusedByteIdentical':True,'repair':None})
            pieces.append(src);save();continue
        dest=OUT/f'cut-{i+1:02d}-{cut["id"]}.mp4'
        inputs=[FF,'-n','-hide_banner','-threads','2','-reinit_filter','0']
        filters=[]
        if is_model:
            inputs += ['-i',src]
            # Crop only the blank top margin, retaining all projected faces/text/motion.
            filters=['[0:v]crop=1920:1020:0:60,pad=1920:1080:0:0:color=black,setsar=1']
            repair={'type':'retained-model-shift-up','pixels':60,'sourceModelRerendered':False,'wholeSourceContentPreservationPendingEncodedReview':True}
        elif cut['id']=='overview-cyber':
            inputs += ['-i',src]
            filters=['[0:v]split=2[base][labels]','[labels]crop=1920:112:0:884[labelstrip]','[base][labelstrip]overlay=0:122:shortest=1']
            repair={'type':'same-frame-original-label-strip','crop':[0,884,1920,112],'position':[0,122],'sourceLabelsRewritten':False,'combinedFeatureDemo':True}
        else:
            assert sha(ROOT/cut['path'])==cut['sha256']
            inputs += ['-ss',str(cut['sourceStart']),'-i',ROOT/cut['path']]
            prefix='[0:v]fps=60'
            if cut.get('freezeFrameOnly'):
                prefix+=',trim=end_frame=1,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0.733333333'
            prefix+=',split=2[base][table]'
            filters=[prefix,'[base]crop=1570:923:244:123,scale=1920:1080,setsar=1[editor]','[table]crop=920:175:592:861,scale=1840:350,setsar=1[values]','[editor][values]overlay=40:195:shortest=1,drawbox=x=38:y=193:w=1844:h=354:color=0x6b7280:t=2']
            filters[-1]+=','+textfilter('같은 프레임의 실제 입력·출력 확대',40,142,28,label='renderdoc-table-caption')
            filters[-1]+=',drawbox=x=42:y=289:w=900:h=54:color=0x36aaa4:t=3'
            # The persistent line identifies the operation, never claims it is still executing.
            filters[-1]+=',drawbox=x=534:y=609:w=162:h=4:color=0xdd3434:t=fill'
            # Earliest reviewed post-step sample is native127.5, not an invented exact step time.
            if not cut.get('freezeFrameOnly'):
                filters[-1]+=",drawbox=x=952:y=233:w=732:h=110:color=0xf39a4b:t=3:enable='gte(t,2.5)'"
            else:
                filters[-1]+=',drawbox=x=952:y=233:w=732:h=110:color=0xf39a4b:t=3'
            filters[-1]+=','+textfilter('RenderDoc · Frame622 / EID14 · 색 입력 따라가기',32,54,28,label='renderdoc-source-identity')
            repair={'type':'original-same-frame-table-magnification','tableCrop':[592,861,920,175],'tablePosition':[40,195],'tableSize':[1840,350],'inputBracket':'teal','codeUnderline':'red identifies return input.color; not a claimed currently executing line','outputBracket':'orange only from native127.5 observed matching outputs','inventedSourceValues':False,'sourceScrollTruncatedNamesPreserved':True}
        filters[-1]+=f',trim=end_frame={frames},settb=1/90000,setpts=N*1500[out]'
        run(inputs+['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[out]','-frames:v',str(frames),'-an','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',dest],f'cut-{i+1:02d}-repair')
        pieces.append(dest)
        state['results'].append({'id':cut['id'],'path':rel(dest),'sha256':sha(dest),'frames':frames,'kind':cut['kind'],'reusedByteIdentical':False,'repair':repair,'preservedOldCut':old})
        save();print(json.dumps({'cut':i+1,'repaired':True,'frames':frames}),flush=True)
    assert sum(x['frames'] for x in state['results'])==11664
    concat=OUT/'concat.txt';concat.write_text('\n'.join("file '"+str(x).replace('\\','/')+"'" for x in pieces)+'\n','utf-8')
    old_clean=ROOT/build['outputs'][0]['path']
    clean=OUT/'game-lighting-history-04-first-chapter.clean.mp4'
    cap=OUT/'game-lighting-history-04-first-chapter.captioned.mp4'
    run([FF,'-n','-hide_banner','-threads','2','-f','concat','-safe','0','-i',concat,'-i',old_clean,'-map','0:v:0','-map','1:a:0','-c','copy','-t','194.4','-video_track_timescale','90000','-movflags','+faststart',clean],'clean-pair')
    ass=OLD/'captions.ko.ass'
    assert sha(ass)==read(OLD/'caption-layout.json')['assSha256']
    run([FF,'-n','-hide_banner','-threads','2','-reinit_filter','0','-i',clean,'-filter_threads','2','-vf','ass='+rel(ass),'-frames:v','11664','-fps_mode','passthrough','-enc_time_base','1:90000','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','copy','-video_track_timescale','90000','-movflags','+faststart',cap],'captioned-pair')
    outputs=[]
    for f in [clean,cap]:
        result=probe(f)
        result['wholeDecode']=run([FF,'-v','error','-threads','2','-i',f,'-f','null','NUL'],f.stem+'-whole-decode')
        outputs.append(result)
    assert outputs[0]['aacPayloadSha256']==outputs[1]['aacPayloadSha256']==build['outputs'][0]['aacPayloadSha256']
    for x in build['outputs']:assert sha(ROOT/x['path'])==x['sha256']
    record={
        'builtAt':stamp(),'scope':'First194.4s collision repair only, not whole-episode final',
        'plan':{'path':rel(plan_path),'sha256':sha(plan_path)},'execution':rel(SP),
        'review':state['review'],'outputs':outputs,'cuts':state['results'],
        'identicalAacPayload':True,'identicalAacToV11':True,
        'preservedPcm':state['preservedPcm'],'captionCues':44,'captionCenter':[960,970],
        'firstChapterFrames':11664,'firstChapterSeconds':194.4,'captionAssSha256':sha(ass),
        'sourceModelsRerendered':0,'newTts':0,'newGitImages':0,
        'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'causalFlowApproved':False,
        'captionTimingApproved':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,
        'qaApproved':False,'collected':False,'uploaded':False,'humanWholeListening':'pending'
    }
    (P/'first-chapter-review-build-v12.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
    state['status']='technical-repaired-pair-ready';state['endedAt']=stamp();save();checkpoint()
    print(json.dumps({'status':state['status'],'frames':11664,'seconds':194.4,'sameAac':True,'allFinalPixelsReviewed':False}),flush=True)
except Exception as e:
    state['status']='failed';state['error']=repr(e);state['endedAt']=stamp();save();checkpoint();raise

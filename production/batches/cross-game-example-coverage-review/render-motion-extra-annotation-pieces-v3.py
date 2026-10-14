"""Two unique normal-speed silent pieces. Manual roles require encoded review."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,os,psutil,traceback,ctypes
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT=ROOT/'shared/output/cross-game-example-coverage/motion/extra-annotation-pieces-v3'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
sp=R/'extra-annotation-pieces-execution-v3.json';assert not sp.exists() and not OUT.exists()
cpu=psutil.cpu_percent(interval=1);ram=psutil.virtual_memory().available//1024
assert cpu<85 and ram>8000000
busy=[]
for p in psutil.process_iter(['pid','cmdline','create_time']):
    cmd=p.info['cmdline'] or [];text=' '.join(cmd)
    if p.pid!=os.getpid() and cmd and cmd[0].lower().endswith(('python.exe','node.exe')) and any(x in text for x in ['extract-motion-extra-anchors-v1.py','render-motion-extra-annotation-pieces-v3.py','render-motion-narration-timed-comparisons-v1.cjs']):busy.append(p.info)
assert not busy,busy
protected=read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs'];assert len(protected)==71
for x in protected: assert sha(ROOT/x['path'])==x['sha256']
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True).stdout.strip()
cim=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|node|ffmpeg' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4"],capture_output=True,text=True,check=True).stdout
(R/'extra-annotation-pieces-current-cim-v3.json').write_text(cim,'utf-8')
plan=read(R/'extra-annotation-observation-plan-v2.json')
for s in plan['observations']:assert sha(ROOT/s['samplePath'])==s['sampleSha256']
pieces=[p for p in read(R/'narration-led-cut-allocation-proposal-v2.json')['cuts'] if p['game']=='PowerWashSimulator']
assert len(pieces)==1
OUT.mkdir()
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',36);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',27)
cf=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',44)
state=dict(schemaVersion=1,startedAt=stamp(),pid=os.getpid(),createTime=psutil.Process().create_time(),
    commandLine=psutil.Process().cmdline(),cwd=str(ROOT),cpuThreads=2,gpuJobs=0,
    resource=dict(cpuLoadPercent=cpu,freePhysicalMemoryKiB=ram,gpuRaw=gpu,ownedHeavyOtherJobs=0),
    cimEvidence='extra-annotation-pieces-current-cim-v3.json',protected71ShaMatched=True,
    status='running',actualOuterExitCode=None,pieces=[],movingAnnotationApproved=False,narrationTimed=False,finalCueApproval=False,
    sourceAudioAdopted=False,localOnly=True)
def save():sp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
save()
cp_path=R/'latest-checkpoint.json';cp=read(cp_path)
cp.update(ownedJob=dict(status='running',active=True,sessionId=None,pid=state['pid'],createTime=state['createTime'],
    command='render-motion-extra-annotation-pieces-v3.py',state=sp.relative_to(ROOT).as_posix()),activeOwnedWorkers=1,
    next='Reuse actual owned extra-annotation piece worker. On exit review all84 encoded anchors/21boards and normal1x playback before adoption; no duplicate render. Full sourceHUD retained in1600x900 fit over same-frame backdrop, caption center960970.')
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
framing=dict(schemaVersion=2,preparedAt=stamp(),previousPreparedPlan='extra-annotation-observation-plan-v1.json',
    previousShift120HeldReason='Upward crop would lose PowerWash top HUD. Unrendered framing hypothesis held.',
    transform='Entire source fitted1600x900 at x160,y0 over same-frame blurred1920x1080 background. Observed1280x720 point -> x*1.25+160,y*1.25. No source HUD crop.',
    captionCenter=[960,970],sourceHudPreservedByConstruction=True,pixelClearanceApproved=False)
# Current framing already reviewed; preserve V2 framing evidence.
def anchor(rows,n,key):
    if n<rows[0]['nativeFrame'] or n>rows[-1]['nativeFrame']:return None
    for a,b in zip(rows,rows[1:]):
        if a['nativeFrame']<=n<=b['nativeFrame']:
            if a[key] is None or b[key] is None:return None
            u=(n-a['nativeFrame'])/(b['nativeFrame']-a['nativeFrame'])
            pt=[a[key][i]+u*(b[key][i]-a[key][i]) for i in [0,1]]
            return [round(pt[0]*1.25+160),round(pt[1]*1.25)]
    pt=rows[-1][key]
    return [round(pt[0]*1.25+160),round(pt[1]*1.25)] if pt else None
try:
    for piece in pieces:
        assert sha(ROOT/piece['path'])==piece['sha256']
        rows=[s for s in plan['observations'] if s['sourceId']==piece['id']]
        first=piece['nativeInFrame'];last=piece['nativeOutFrameExclusive'];count=piece['normalSpeedOutputFrames']
        fps=30000/1001 if piece['game']=='Portal2' else 60
        folder=OUT/piece['id'];folder.mkdir();output=folder/'silent-role-annotation.mp4'
        dec=[FF,'-v','error','-threads','2','-filter_threads','1','-i',str(ROOT/piece['path']),'-vf',
             f'trim=start_frame={first}:end_frame={last},setpts=PTS-STARTPTS,scale=1920:1080,fps=60',
             '-frames:v',str(count),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
        enc=[FF,'-v','error','-threads','2','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','pipe:0',
             '-frames:v',str(count),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(output)]
        rec=dict(id=piece['id'],sourcePath=piece['path'],sourceSha256=piece['sha256'],nativeInFrame=first,nativeOutFrameExclusive=last,
            frames=count,decodeCommand=dec,encodeCommand=enc,status='rendering',samples=[],boards=[])
        state['pieces'].append(rec);save()
        with (folder/'decode.log').open('wb') as dl,(folder/'encode.log').open('wb') as el:
            decoder=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl);encoder=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el)
            rec.update(decoderPid=decoder.pid,encoderPid=encoder.pid);save()
            for f in range(count):
                raw=bytearray();size=1920*1080*3
                while len(raw)<size:
                    c=decoder.stdout.read(size-len(raw));assert c,'Unexpected source decoder EOF';raw.extend(c)
                source=Image.frombytes('RGB',(1920,1080),bytes(raw))
                im=source.resize((480,270)).filter(ImageFilter.GaussianBlur(8)).resize((1920,1080));im.paste(source.resize((1600,900)),(160,0))
                d=ImageDraw.Draw(im);native=first+f*fps/60
                red=anchor(rows,native,'redObservedSamplePoint');blue=anchor(rows,native,'blueObservedSamplePoint')
                if red:
                    d.rectangle((1080,133,1585,188),fill='white',outline='#cc3030',width=3)
                    d.text((1095,139),rows[0]['redLabel'],font=font,fill='#a31818')
                    d.line([(1100,188),(1050,220),tuple(red)],fill='#df3434',width=5)
                    x,y=red;d.line([(x-22,y+14),(x-22,y-14),(x+22,y-14)],fill='#df3434',width=5)
                if blue:
                    d.rectangle((185,138,695,193),fill='white',outline='#087ca6',width=3)
                    d.text((200,144),rows[0]['blueLabel'],font=font,fill='#066685')
                    d.line([(425,193),tuple(blue)],fill='#1bb3d0',width=5)
                    x,y=blue;d.ellipse((x-16,y-16,x+16,y+16),outline='#1bb3d0',width=4)
                credit='Portal 2 · Valve' if piece['game']=='Portal2' else 'PowerWash Simulator · FuturLab 개발 시연 (2022 WIP)'
                box=d.textbbox((0,0),credit,font=small);cw=box[2]-box[0]
                d.rectangle((960-cw/2-12,35,960+cw/2+12,76),fill='white');d.text((960-cw/2,39),credit,font=small,fill='black')
                text='큐브와 방의 단서를 함께 비교해 보세요.' if piece['game']=='Portal2' else '도구가 움직일 때 주변 단서도 함께 보세요.'
                d.rectangle((234,930,1694,1028),fill='#174735');d.rectangle((220,918,1680,1016),fill='white',outline='black',width=2)
                box=d.textbbox((0,0),text,font=cf);d.text(((1920-(box[2]-box[0]))/2,936),text,font=cf,fill='black')
                encoder.stdin.write(im.tobytes())
            decoder.stdout.close();encoder.stdin.close();dc=decoder.wait();ec=encoder.wait();assert dc==ec==0,(dc,ec)
        wd=subprocess.run([FF,'-v','error','-threads','2','-i',str(output),'-f','null','-'],capture_output=True,text=True);assert wd.returncode==0 and not wd.stderr
        stream=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_streams','-of','json',str(output)]))['streams'][0]
        assert int(stream['nb_frames'])==count and stream['time_base']=='1/90000' and stream['avg_frame_rate']=='60/1'
        sampled=sorted(set(min(count-1,round((s['nativeFrame']-first)/fps*60)) for s in rows))
        sample_dir=folder/'samples';sample_dir.mkdir();sel='+'.join(f'eq(n\\,{x})' for x in sampled)
        run=subprocess.run([FF,'-v','error','-threads','2','-filter_threads','1','-i',str(output),'-vf','select='+sel,'-fps_mode','passthrough','-an',str(sample_dir/'sample-%03d.png')],capture_output=True,text=True);assert run.returncode==0,run.stderr
        for f,p in zip(sampled,sorted(sample_dir.glob('sample-*.png'))):rec['samples'].append(dict(frame=f,pts=f*1500,nativeFrameEstimate=first+f*fps/60,path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
        assert len(rec['samples'])==len(sampled)
        bfont=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
        for start in range(0,len(rec['samples']),4):
            chunk=rec['samples'][start:start+4];board=Image.new('RGB',(1920,1160),'#e4e7ec');bd=ImageDraw.Draw(board)
            for k,s in enumerate(chunk):
                x=k%2*960;y=k//2*580;board.paste(Image.open(ROOT/s['path']).resize((960,540)),(x,y+40));bd.text((x+8,y+5),f"{piece['id']} encoded{s['frame']} PTS{s['pts']}",font=bfont,fill='black')
            p=folder/f'board-{len(rec["boards"])+1:02d}.png';board.save(p);rec['boards'].append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),samples=chunk))
        rec.update(status='completed-awaiting-direct-encoded-review',decodeExitCode=dc,encodeExitCode=ec,wholeDecodeExitCode=0,extractionExitCode=0,
                   stream=stream,path=output.relative_to(ROOT).as_posix(),sha256=sha(output),seconds=count/60)
        save()
    state.update(status='completed-awaiting-direct-moving-samples-and-normal-playback',finishedAt=stamp(),exitCode=0,
        encodedSampleCount=sum(len(p['samples']) for p in state['pieces']),boardCount=sum(len(p['boards']) for p in state['pieces']))
    save();print(json.dumps(dict(pieces=2,frames=sum(p['frames'] for p in state['pieces']),samples=state['encodedSampleCount'],boards=state['boardCount'],allDecodeEncodeExtractionExitCodes=0)))
except BaseException:
    state.update(status='failed-preserve-all-current-evidence',exitCode=1,error=traceback.format_exc());save();raise

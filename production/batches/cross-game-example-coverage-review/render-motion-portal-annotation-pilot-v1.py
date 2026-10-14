"""One CPU2 silent3s pilot; manual PTS observations require encoded moving review."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,subprocess,os,traceback,ctypes
import psutil
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OUT=ROOT/'shared/output/cross-game-example-coverage/motion/portal-annotation-pilot-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
plan=read(R/'portal-annotation-observation-plan-v1.json')
for x in plan['observations']:
    assert sha(ROOT/x['sourceSample'])==x['sourceSampleSha256'] and sha(ROOT/x['staticPath'])==x['staticSha256']
assert sha(ROOT/plan['sourcePath'])==plan['sourceSha256']
sp=R/'portal-annotation-pilot-execution-v1.json';assert not OUT.exists() and not sp.exists();OUT.mkdir()
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',36);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',28)
cf=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',44)
me=psutil.Process();state=dict(schemaVersion=1,startedAt=datetime.now(timezone.utc).isoformat(),pid=me.pid,createTime=me.create_time(),
 commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,cpuThreads=2,gpuJobs=0,resource=resource,planSha256=sha(R/'portal-annotation-observation-plan-v1.json'),
 status='rendering-silent-manual-PTS-annotation-pilot',exitCode=None,narrationTimed=False,movingAnnotationApproved=False,
 allFinalPixelsApproved=False,sourceAudioAdopted=False,gitImagesAdded=0)
save(sp,state)
def anchor(frame,key):
    rows=plan['observations'];a,b=rows[-2:]
    for left,right in zip(rows,rows[1:]):
        if left['nativeFrame']<=frame<=right['nativeFrame']:a,b=left,right;break
    u=max(0,min(1,(frame-a['nativeFrame'])/(b['nativeFrame']-a['nativeFrame'])))
    p=[a[key][i]+u*(b[key][i]-a[key][i]) for i in [0,1]]
    return [round(p[0]*1.5),round(p[1]*1.5-120)]
output=OUT/'portal-cube-camera.captioned-pilot.mp4'
decode=[FF,'-v','error','-threads','2','-filter_threads','1','-i',str(ROOT/plan['sourcePath']),'-vf',
 f"trim=start_frame={plan['sourceFirstFrame']}:end_frame={plan['sourceEndExclusiveFrame']},setpts=PTS-STARTPTS,scale=1920:1080,fps=60",
 '-frames:v','180','-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
encode=[FF,'-v','error','-threads','2','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','pipe:0',
 '-frames:v','180','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(output)]
state.update(decodeCommand=decode,encodeCommand=encode);save(sp,state)
try:
    with (OUT/'decode.log').open('wb') as dl,(OUT/'encode.log').open('wb') as el:
        decoder=subprocess.Popen(decode,stdout=subprocess.PIPE,stderr=dl);encoder=subprocess.Popen(encode,stdin=subprocess.PIPE,stderr=el)
        state.update(decoderPid=decoder.pid,encoderPid=encoder.pid);save(sp,state)
        for frame in range(180):
            size=1920*1080*3;raw=bytearray()
            while len(raw)<size:
                chunk=decoder.stdout.read(size-len(raw))
                assert chunk,'Unexpected decoder EOF';raw.extend(chunk)
            scaled=Image.frombytes('RGB',(1920,1080),bytes(raw));im=Image.new('RGB',(1920,1080));im.paste(scaled.crop((0,120,1920,1080)),(0,0))
            im.paste(scaled.crop((0,960,1920,1080)).filter(ImageFilter.GaussianBlur(18)),(0,960))
            d=ImageDraw.Draw(im);native=plan['sourceFirstFrame']+frame/60*30000/1001
            c=anchor(native,'cubeUpperVisiblePoint');b=anchor(native,'wallVisiblePoint')
            d.rectangle((1120,100,1660,157),fill='white',outline='#c73131',width=3);d.text((1140,108),'조작 대상: 큐브',font=font,fill='#a31818')
            d.line([(1130,157),(1080,205),tuple(c)],fill='#df3434',width=5)
            d.line([(c[0]-22,c[1]+12),(c[0]-22,c[1]-12),(c[0]+22,c[1]-12)],fill='#df3434',width=5)
            d.rectangle((80,175,580,232),fill='white',outline='#087ca6',width=3);d.text((100,183),'방의 단서: 벽',font=font,fill='#066685')
            d.line([(580,232),(610,270),tuple(b)],fill='#1bb3d0',width=5);d.ellipse((b[0]-11,b[1]-11,b[0]+11,b[1]+11),outline='#1bb3d0',width=4)
            d.rectangle((1280,30,1870,73),fill='white');d.text((1290,34),'Portal 2 — Valve',font=small,fill='black')
            d.rectangle((134,918,1814,1046),fill='#174735');d.rectangle((120,906,1800,1034),fill='white',outline='black',width=2)
            t='큐브는 화면 가운데를 따라가고, 방의 단서는 위치가 바뀝니다.';box=d.textbbox((0,0),t,font=cf)
            d.text(((1920-(box[2]-box[0]))/2,942),t,font=cf,fill='black')
            encoder.stdin.write(im.tobytes())
        decoder.stdout.close();encoder.stdin.close()
        dc=decoder.wait();ec=encoder.wait();assert dc==0 and ec==0,(dc,ec)
    whole=subprocess.run([FF,'-v','error','-threads','2','-i',str(output),'-f','null','-'],capture_output=True,text=True)
    assert whole.returncode==0 and not whole.stderr
    stream=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_streams','-of','json',str(output)]))['streams'][0]
    assert stream['nb_frames']=='180' and stream['time_base']=='1/90000' and stream['avg_frame_rate']=='60/1'
    frames=[0,1,15,30,45,60,75,90,105,120,150,179];sampleDir=OUT/'samples';sampleDir.mkdir()
    selected='+'.join(f'eq(n\\,{f})' for f in frames)
    ext=subprocess.run([FF,'-v','error','-threads','2','-filter_threads','1','-i',str(output),'-vf','select='+selected,'-vsync','0','-threads','2',str(sampleDir/'sample-%02d.png')])
    assert ext.returncode==0
    rows=[]
    for f,p in zip(frames,sorted(sampleDir.glob('sample-*.png'))):rows.append(dict(frame=f,pts=f*1500,nativeFrameEstimate=plan['sourceFirstFrame']+f/60*30000/1001,path=str(p.relative_to(ROOT)),sha256=sha(p)))
    assert len(rows)==12
    state.update(status='pilot-rendered-awaiting-direct-moving-samples-and-playback',exitCode=0,actualDecodeExitCode=dc,actualEncodeExitCode=ec,
      wholeDecodeExitCode=whole.returncode,extractionExitCode=ext.returncode,path=str(output.relative_to(ROOT)),sha256=sha(output),
      frames=180,seconds=3,stream=stream,samples=rows,actualExitObserved=False)
    save(sp,state);print('Actual decode/encode/wholedecode/extraction0; 180f3s pilot/12samples await direct moving review.')
except BaseException:
    state.update(status='failed-preserve-pilot-records',exitCode=1,error=traceback.format_exc());save(sp,state);raise

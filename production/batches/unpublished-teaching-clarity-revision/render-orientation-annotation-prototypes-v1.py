"""Single CPU2/GPU0 worker for seven bounded annotation prototypes."""
from pathlib import Path
import importlib.util,json,subprocess,os,traceback
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='2'
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
L=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/annotation-prototypes-v1'
spec=importlib.util.spec_from_file_location('pilot',Path(__file__).with_name('render-orientation-observation-pilot-v4.py'));p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
read=p.read;save=p.save;sha=p.sha;rel=p.rel;now=p.now

def visible(w,f):return not any(a<=f<b for a,b in w['hiddenLocalFrameRanges'])
def drawing(im,w,f,point,previous):
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
    p.label(d,(64,28),'Superflight · NCR Gameplay · 화면 관찰','#ffffff',22)
    p.label(d,(64,95),w['title'],p.GOLD,32)
    if f>=20:
        p.arrow(d,(1720,360),(1720,195),p.GOLD)
        p.label(d,(1560,385),'화면의 위',p.GOLD)
    if f>=35 and visible(w,f):
        x,y=point
        d.ellipse((x-15,y-15,x+15,y+15),outline='#10191c',width=6)
        d.ellipse((x-12,y-12,x+12,y+12),outline=p.TEAL,width=4)
        d.ellipse((x-3,y-3,x+3,y+3),fill=p.TEAL)
        p.label(d,(64,178),'청록: 몸통의 화면 관찰점 p',p.TEAL)
    elif f>=35:
        p.label(d,(64,178),'가림 / 작은 대상: 관찰선 잠시 숨김','#ffffff',27)
    if f>=100 and visible(w,f) and visible(w,max(0,f-30)):
        p.arrow(d,previous,point,p.RED,5)
        p.label(d,(64,242),'빨강: 0.5초 동안의 화면 위치 변화',p.RED)
        p.label(d,(64,310),'Δp = p(t) - p(t - 0.5s)',p.RED,26)
    p.label(d,(64,810),'화면 위치에는 카메라의 움직임도 함께 나타납니다.','#ffffff',27)
    p.label(d,(64,855),'몸의 3D 세 축은 개념 모형에서 따로 설명합니다.','#ffffff',25)
    assert layer.getbbox()[3]<=910
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def main():
    sp=R/'annotation-prototype-execution-v1.json'
    assert not sp.exists() and not L.exists(),'Resume existing prototype; never overwrite'
    voice=R/'narration-tts-execution-v2.json'
    if voice.exists():assert read(voice).get('status') in ('failed','completed','completed-approved-voice-awaiting-asr'), 'Wait for current GPU TTS before this CPU prototype'
    baseline=read(R/'baseline-preservation-v1.json');assert all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
    tracks=read(R/'annotation-observation-keyframes-v1.json');source=ROOT/tracks['source'];assert sha(source)==tracks['sourceSha256']
    processes=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|ffmpeg|node)' -and ($_.CommandLine -match 'unpublished-teaching|train_multiview|gpu-handoff|queue|serve-native-review') } | Select-Object ProcessId,ParentProcessId,CreationDate,Name,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf8'))
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True)
    assert psutil.virtual_memory().available>8_000_000_000
    assert not any(x.get('CommandLine') and 'render-orientation-annotation-prototypes' in x['CommandLine'] and x['ProcessId']!=os.getpid() and x['ProcessId']!=os.getppid() for x in processes)
    L.mkdir(parents=True);me=psutil.Process()
    state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,status='rendering-seven-silent-prototypes',cpuThreads=2,gpuJobs=0,resource={'cim':processes,'gpu':gpu.strip()},workerExitCode=None,actualOuterExitCode=None,windows=[],allMovingPixelsApproved=False,finalCueApproved=False,narrationTimed=False,researchManipulations=0,newImageGitAdded=0)
    save(sp,state)
    try:
        for w in tracks['windows']:
            sid=w['scene'];out=L/f'scene-{sid}';out.mkdir();target=out/f'{sid}.silent-prototype.mp4'
            start=w['startNativeFrame'];end=w['endNativeFrameExclusive'];assert end-start==360
            anchors={a['frame']:a for a in w['keyframes']};assert all(sha(ROOT/a['inspectedImage'])==a['inspectedImageSha256'] for a in anchors.values())
            dec=[p.FF,'-hide_banner','-nostdin','-v','error','-threads','1','-filter_threads','1','-ss',str(start/60),'-i',str(source),'-frames:v','360','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
            enc=[p.FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i','pipe:0','-frames:v','360','-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(target)]
            save(out/'commands.json',{'decode':dec,'encode':enc});track=[]
            with (out/'decode.log').open('wb') as dl,(out/'encode.log').open('wb') as el:
                dp=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl,cwd=ROOT);ep=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el,cwd=ROOT)
                state.update(currentScene=sid,decodePid=dp.pid,encodePid=ep.pid);save(sp,state)
                for f in range(360):
                    raw=dp.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3
                    im=Image.frombytes('RGB',(1920,1080),raw)
                    if f in anchors:
                        with Image.open(ROOT/anchors[f]['inspectedImage']) as observed:assert observed.convert('RGB').tobytes()==raw,(sid,f,'native-pixel-mismatch')
                    point=p.point_at(f,w['keyframes']);prev=p.point_at(max(0,f-30),w['keyframes'])
                    track.append(dict(frame=f,sourceFrame=start+f,sourcePts=(start+f)*256,visible=visible(w,f),screenPoint=point,previousScreenPoint=prev,screenOnly=True))
                    ep.stdin.write(drawing(im,w,f,point,prev).tobytes())
                assert dp.stdout.read(1)==b'';dp.stdout.close();ep.stdin.close();dx=dp.wait();ex=ep.wait();assert dx==ex==0
            save(out/'point-track.json',{'scene':sid,'points':track,'gameWorldMeasurement':False})
            decode=[p.FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(target),'-f','null','-']
            with (out/'whole-decode.log').open('wb') as l:q=subprocess.run(decode,stdout=l,stderr=subprocess.STDOUT).returncode
            assert q==0
            samples=sorted(anchors);sel='+'.join(f'eq(pts,{n*1500})' for n in samples)
            cmd=[p.FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(target),'-vf',f"select='{sel}',showinfo",'-fps_mode','passthrough','-frames:v','25','-threads','2',str(out/'encoded-%03d.png')]
            with (out/'extract.log').open('wb') as l:x=subprocess.run(cmd,stdout=l,stderr=subprocess.STDOUT).returncode
            assert x==0
            rows=[dict(frame=f,path=rel(out/f'encoded-{j:03d}.png'),sha256=sha(out/f'encoded-{j:03d}.png')) for j,f in enumerate(samples,1)]
            boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
            for offset in range(0,25,6):
                board=Image.new('RGB',(1920,780),'#171a1e');d=ImageDraw.Draw(board)
                for j,r in enumerate(rows[offset:offset+6]):
                    bx=j%3*640;by=j//3*390
                    with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(bx,by+30))
                    d.text((bx+8,by+5),f"scene{sid} f{r['frame']} image observation",font=font,fill='white')
                bp=out/f'board-{offset//6+1:02d}.png';board.save(bp);boards.append({'path':rel(bp),'sha256':sha(bp)})
            probe=json.loads(subprocess.check_output([p.FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,time_base,nb_frames,duration','-of','json',str(target)],text=True))
            state['windows'].append(dict(scene=sid,output=rel(target),outputSha256=sha(target),frames=360,decodeExitCode=dx,encodeExitCode=ex,wholeDecodeExitCode=q,extractionExitCode=x,probe=probe,samples=rows,boards=boards,hiddenFrames=sum(not t['visible'] for t in track)))
            save(sp,state);print(json.dumps({'scene':sid,'samples':25,'boards':5,'decodeExit':q}),flush=True)
        assert all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
        state.update(status='completed-silent-prototypes-awaiting-direct-review',workerExitCode=0,finishedAt=now(),baseline38Unchanged=True);save(sp,state)
    except BaseException as e:
        state.update(status='failed',workerExitCode=1,error=repr(e),traceback=traceback.format_exc(),finishedAt=now());save(sp,state);raise
if __name__=='__main__':main()

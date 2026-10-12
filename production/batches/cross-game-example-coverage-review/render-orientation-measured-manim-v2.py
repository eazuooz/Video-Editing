"""Scoped CPU2 prototypes for five bridges and two retained-scene repairs."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,datetime,importlib.util,traceback
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='2'
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
L=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/measured-manim-v2'
M=ROOT/'manim/projects/game-math-orientation-matrices/teaching_revision_v2.py'
TIMING=R/'measured-manim-timing-v2.json'
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
if '--render' in sys.argv:
    # Control only this process's encoder; no installed/runtime files change.
    from manim import tempconfig
    from manim.scene.scene_file_writer import SceneFileWriter
    original=SceneFileWriter.open_partial_movie_stream
    def bounded_stream(self,*a,**kw):
        original(self,*a,**kw)
        self._current_encode_job.stream.codec_context.thread_count=2
    SceneFileWriter.open_partial_movie_stream=bounded_stream
    sid=sys.argv[sys.argv.index('--render')+1]
    os.environ['ORIENTATION_REVISION_TIMING']=str(TIMING)
    spec=importlib.util.spec_from_file_location('orientation_teaching',M);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    with tempconfig(dict(pixel_width=1920,pixel_height=1080,frame_rate=60,quality='high_quality',renderer='cairo',media_dir=str(L/'manim'),disable_caching=True,max_inflight_encoders=1,verbosity='WARNING')):
        getattr(mod,'RevisionScene'+sid)().render()
    raise SystemExit(0)

import psutil
from PIL import Image,ImageDraw,ImageFont
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
STATE=R/'measured-manim-execution-v2.json'
assert not STATE.exists() and not L.exists(),'Inspect existing measured work; never duplicate it.'
resource=read(R/'resource-before-cross-game-CPU-v4.json')
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
assert (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
baseline=read(R/'baseline-preservation-v1.json');assert all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
closed=read(R/'post-splice-current-voice-asr-execution-v1.json');assert closed['actualOuterExitCode']==0 and closed['completed']==3
assert read(R/'21a-spliced-whole-and-seam-direct-review-v1.json')['current21aCompletenessApproved']
plan=read(TIMING);assert sha(M)==plan['codeSha256'];scenes=plan['scenes']
for slot in scenes:assert sha(ROOT/slot['voicePath'])==slot['voiceSha256']
processes=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],encoding='utf8',text=True))
assert psutil.virtual_memory().available//1024>8_000_000
L.mkdir(parents=True);me=psutil.Process()
state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,cpuThreads=2,gpuJobs=0,status='rendering-measured-seven-Manim-scenes',resource={'cim':processes,'gpu':subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader'],text=True).strip()},code=rel(M),codeSha256=sha(M),timing=rel(TIMING),timingSha256=sha(TIMING),scenes=[],workerExitCode=None,actualOuterExitCode=None,allMovingPixelsApproved=False,narrationTimed=True,finalCueApproved=False,newImageGitAdded=0,researchManipulations=0)
save(STATE,state)
try:
    for slot in scenes:
        assert sha(ROOT/slot['voicePath'])==slot['voiceSha256']
        sid=slot['id'];cmd=[str(ROOT/'manim/.venv/Scripts/python.exe'),'-X','utf8',str(Path(__file__).resolve()),'--render',sid]
        log=L/f'render-{sid}.log'
        with log.open('wb') as f:
            child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
            state.update(currentScene=sid,childPid=child.pid,childCommand=cmd);save(STATE,state)
            ex=child.wait()
        assert ex==0,(sid,ex,rel(log))
        matches=list((L/'manim/videos').rglob('RevisionScene'+sid+'.mp4'));assert len(matches)==1,(sid,matches)
        video=matches[0];out=L/f'scene-{sid}';out.mkdir()
        with (out/'decode.log').open('wb') as f:dx=subprocess.run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(video),'-f','null','-'],stdout=f,stderr=subprocess.STDOUT).returncode
        assert dx==0
        probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,time_base,nb_frames,duration','-of','json',str(video)],text=True));stream=probe['streams'][0]
        count=int(stream['nb_frames']);assert abs(count-slot['frames'])<=1 and stream['width']==1920 and stream['height']==1080 and stream['r_frame_rate']=='60/1',(sid,stream,slot)
        indices=sorted(set([*range(0,count,60),count-1,*[min(count-1,round(t*60)+45) for t in slot['lineStarts']]]))
        select='+'.join(f'eq(n,{n})' for n in indices)
        with (out/'extract.log').open('wb') as f:xx=subprocess.run([FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(video),'-vf',f"select='{select}',showinfo",'-fps_mode','passthrough','-frames:v',str(len(indices)),'-threads','2',str(out/'frame-%03d.png')],stdout=f,stderr=subprocess.STDOUT).returncode
        assert xx==0
        rows=[dict(frame=n,path=rel(out/f'frame-{j:03d}.png'),sha256=sha(out/f'frame-{j:03d}.png')) for j,n in enumerate(indices,1)]
        boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
        for off in range(0,len(rows),6):
            im=Image.new('RGB',(1920,780),'#171a1e');draw=ImageDraw.Draw(im)
            for j,row in enumerate(rows[off:off+6]):
                bx=j%3*640;by=j//3*390
                with Image.open(ROOT/row['path']) as frame:im.paste(frame.resize((640,360)),(bx,by+30))
                draw.text((bx+8,by+5),f"scene{sid} f{row['frame']}",font=font,fill='white')
            path=out/f'board-{off//6+1:02d}.png';im.save(path);boards.append(dict(path=rel(path),sha256=sha(path)))
        state['scenes'].append(dict(id=sid,output=rel(video),outputSha256=sha(video),renderExitCode=ex,wholeDecodeExitCode=dx,extractExitCode=xx,probe=probe,samples=rows,boards=boards));save(STATE,state)
        print(json.dumps(dict(id=sid,frames=count,samples=len(rows),boards=len(boards),renderExit=ex,wholeDecode=dx)),flush=True)
    assert sha(M)==state['codeSha256'] and all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
    state.update(status='completed-measured-Manim-awaiting-direct-review',workerExitCode=0,finishedAt=now(),baseline38Unchanged=True);save(STATE,state)
except BaseException:
    state.update(status='failed-preserve-structural-prototype',workerExitCode=1,error=traceback.format_exc(),finishedAt=now());save(STATE,state);raise

"""Prepare or render four bounded CPU/Cairo diagrams after root handoff.

Default --prepare is metadata only. --run never starts TTS or uses CUDA.
No other video, model, editor or existing render is interrupted or replaced.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,time
import psutil

H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v7_right_math_prepare',H/'right-prepare.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
ROOT,P,O=M.ROOT,M.P,M.O
SOURCE=H/'right-manim.py';DEST=O/'math-native'
ACTIVE_JOB=None
SPECS=[
 {'sourceBeatId':'v7-math-storage','expectedFrames':181,'reuseBeat':'v6-16.B01','targetParagraphs':['v7-a15.L02','v7-a15.L07','v7-a16.L01'],
  'actions':[{'sourceFrames':[0,72],'meaning':'h,p,b:3 slots fill','cue':'세 개의 양이 필요합니다'},{'sourceFrames':[72,180],'meaning':'3x3:9 slots fill','cue':'아홉 칸의 행렬'}],
  'claimLimit':'Clearly labeled empty storage-slot diagram; h,p,b are field labels above blank boxes,9matrix boxes are blank. No arbitrary values, new byte size, precision assumption or game-internal claim.'},
 {'sourceBeatId':'v7-math-half-step','expectedFrames':121,'reuseBeat':'v6-16.B02','targetParagraphs':['v7-a16.L03'],
  'actions':[{'sourceFrames':[0,60],'meaning':'One full1-degree interval is traced','cue':'일 도 단위로'},{'sourceFrames':[60,120],'meaning':'Half-interval distance0.5degree is traced','cue':'최대 영 점 오 도'}],
  'claimLimit':'One angle component only; not a total3D orientation-error bound. Distance/error bound only. No20.5 tie-breaking choice or output is shown.'},
 {'sourceBeatId':'v7-math-quantize','expectedFrames':121,'reuseBeat':'v6-16.B02','targetParagraphs':['v7-a16.L04'],
  'actions':[{'sourceFrames':[0,120],'meaning':'Input20.0->20.4 and its number-line pointer move; stored output20 is unchanged','cue':'이십 점 사 도'}],
  'claimLimit':'All depicted inputs20.0–20.4 round to20 at nearest1-degree spacing; no tie policy or all-three-angle final-error guarantee.'},
 {'sourceBeatId':'v7-math-stretch','expectedFrames':151,'reuseBeat':'v6-17.B02','targetParagraphs':['v7-a17.L02'],
  'actions':[{'sourceFrames':[0,150],'meaning':'One diagonal entry1->2 changes X length while Y length stays1; dashed original remains','cue':'길이가 늘어나거나'}],
  'claimLimit':'Our labeled worked arbitrary-matrix example, not a rotation matrix or game measurement.'},
]

def prepare():
    M.authorized();DEST.mkdir(parents=True,exist_ok=True)
    reuse=P/'production/revision-v6/math-clips.py'
    data={'schemaVersion':1,'source':M.rel(SOURCE),'sourceSha256':M.sha(SOURCE),'renderer':'Manim Cairo CPU; half-pane-native900x660/60; alpha',
        'reuse':{'source':M.rel(reuse),'sha256':M.sha(reuse),'method':'retain V6 matrix-square/quantization/distance logic and approved quantities; reflow9-world-unit pane, do not scale a full finished slide'},
        'pixelContract':{'canvas':[900,660],'worldSize':[9,6.6],'minimumKeyGlyphHeightPixels':64,'titleGlyphHeightPixels':54,'background':'same retained detailed aircraft dimmed behind alpha source'},
        'clips':SPECS,'scriptSha256':M.sha(M.S.SCRIPT),'newVoiceOrScriptChanged':False,'forcedSilentObservationFrames':0,'renderStarted':False}
    M.save(DEST/'plan.json',data);return data

def run_logged(cmd,log,env):
    with log.open('wb')as f:
        process=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        own=psutil.Process(process.pid);created=own.create_time()
        if ACTIVE_JOB is not None:ACTIVE_JOB['child']={'pid':process.pid,'createTime':created}
        try:code=process.wait()
        except BaseException:
            try:
                if own.is_running()and own.create_time()==created:
                    for child in own.children(recursive=True):
                        try:child.terminate()
                        except psutil.NoSuchProcess:pass
                    own.terminate();process.wait(timeout=30)
            except(psutil.NoSuchProcess,subprocess.TimeoutExpired):pass
            raise
    if code:raise RuntimeError(log.read_text(encoding='utf8',errors='replace')[-4000:])

def run():
    data=prepare()
    env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2')
    spec=importlib.util.spec_from_file_location('v7_right_context_only',H/'right-build.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    context=DEST/'context-background.png';builder.context_background().save(context)
    env['V7_RIGHT_BACKGROUND']=str(context)
    out=DEST/'outputs.json';existing={r['sourceBeatId']:r for r in M.read(out)['outputs']}if out.exists()else{};outputs=[]
    for spec in SPECS:
        M.authorized();key=spec['sourceBeatId'];signature=hashlib.sha256(json.dumps({'spec':spec,'sourceSha256':M.sha(SOURCE),'backgroundSha256':M.sha(context),'fps':60,'resolution':[900,660]},sort_keys=True).encode()).hexdigest()
        if key in existing and existing[key]['signature']==signature and all((ROOT/f['file']).exists()and M.sha(ROOT/f['file'])==f['sha256']for f in existing[key]['files'].values()):
            outputs.append(existing[key]);continue
        work=DEST/key;work.mkdir(exist_ok=True)
        assert not list(work.rglob(key+'.mov')),'Preserve existing nonmatching bounded math render, do not overwrite.'
        command=[str(ROOT/'manim/.venv/Scripts/python.exe'),'-m','manim','--renderer','cairo','--format','mov','-t','-r','900,660','--fps','60','--media_dir',str(work/'manim'),'-o',key,str(SOURCE),'RightDiagram']
        print(json.dumps({'render':key,'cpuOnly':True,'expectedFrames':spec['expectedFrames']}),flush=True)
        run_logged(command,work/'render.log',{**env,'V7_RIGHT_MATH':key})
        movies=list((work/'manim').rglob(key+'.mov'));assert len(movies)==1
        clip=movies[0];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,r_frame_rate,nb_frames,pix_fmt','-of','json',str(clip)],text=True))['streams'][0]
        assert [probe['width'],probe['height']]==[900,660]and probe['r_frame_rate']=='60/1'and int(probe['nb_frames'])==spec['expectedFrames'],(key,probe)
        row=dict(spec,signature=signature,frames=int(probe['nb_frames']),fps=60,dimensions=[900,660],probe=probe,
            files={'clip':{'file':M.rel(clip),'sha256':M.sha(clip)}},background={'file':M.rel(context),'sha256':M.sha(context),'additionalDimOpacity':.82},renderLog=M.rel(work/'render.log'),sourceKind='independently authored mathematical illustration',movingPairedReview='pending actual word-bound composite')
        outputs.append(row);M.save(out,{'schemaVersion':1,'outputs':outputs,'complete':len(outputs)==len(SPECS),'sourceSha256':M.sha(SOURCE),'scriptSha256':M.sha(M.S.SCRIPT)})
    M.save(out,{'schemaVersion':1,'outputs':outputs,'complete':True,'sourceSha256':M.sha(SOURCE),'scriptSha256':M.sha(M.S.SCRIPT)})
    print(json.dumps({'mathClips':len(outputs),'totalFrames':sum(r['frames']for r in outputs),'manifest':M.rel(out)}),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--run',action='store_true');a=ap.parse_args()
    if a.run:
        sp=importlib.util.spec_from_file_location('v7_right_math_finite_lease',H/'job-lease.py');lease=importlib.util.module_from_spec(sp);sp.loader.exec_module(lease)
        with lease.finite('M04-A four finite CPU Manim mathematical diagrams',require_gpu=False)as record:
            ACTIVE_JOB=record;run()
    elif a.prepare:prepare();print('Four finite CPU math sources prepared; no render started.')
    else:ap.print_help()

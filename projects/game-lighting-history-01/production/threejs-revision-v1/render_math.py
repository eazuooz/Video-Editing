"""Single CPU Manim batch; completed outputs are never rerendered."""
import os
os.environ['OMP_NUM_THREADS']='2'
os.environ['OPENBLAS_NUM_THREADS']='2'
import sys,json,datetime,hashlib,subprocess,importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'projects/game-lighting-history-01/production/local/threejs-revision-v1/manim'
OUT.mkdir(parents=True,exist_ok=True)
EXEC=OUT/'execution.json'
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(): EXEC.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert read(ROOT/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
assert read(ROOT/'projects/game-lighting-history-01/production/checkpoint.json')['rendererRevision']['privateUploadAuthorized']
repair_key=sys.argv[sys.argv.index('--repair-key')+1] if '--repair-key' in sys.argv else None
if EXEC.exists():
    state=read(EXEC)
    assert (repair_key=='04f-p5' and state['status']=='complete-awaiting-pixels' and state['sourceSha256']!=sha(HERE/'math_scenes.py')) or ('--resume' in sys.argv and state['status']=='failed'),'Inspect existing execution; no automatic duplicate batch.'
    if repair_key:
        state.setdefault('supersededOutputs',[]).extend([{**x,'reason':'M1 now correctly averages each 2x2 M0 checker block'} for x in state['completed'] if x['key']==repair_key])
        state['completed']=[x for x in state['completed'] if x['key']!=repair_key]
    state.setdefault('attempts',[]).append({k:state.get(k) for k in ('pid','command','startedAt','status','error','endedAt','sourceSha256')})
    state.update(pid=os.getpid(),command=[sys.executable,*sys.argv],startedAt=now(),sourceSha256=sha(HERE/'math_scenes.py'))
else:
    state={'status':'starting','pid':os.getpid(),'command':[sys.executable,*sys.argv],'startedAt':now(),'cpuThreads':2,'gpuComputeJobs':0,'sourceSha256':sha(HERE/'math_scenes.py'),'completed':[]}
save()
try:
    from manim import config,tempconfig
    from manim.scene.scene_file_writer import _PartialMovieEncodeJob
    original_init=_PartialMovieEncodeJob.__init__
    def limited_init(self,*args,**kwargs):
        stream=kwargs['stream'];stream.codec_context.thread_count=2
        stream.codec_context.options={**stream.codec_context.options,'preset':'veryfast','crf':'18'}
        return original_init(self,*args,**kwargs)
    _PartialMovieEncodeJob.__init__=limited_init
    spec=importlib.util.spec_from_file_location('lighting_math_revision',HERE/'math_scenes.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    selections=read(HERE/'scene-plan.json')
    keys=[p['key'] for s in selections['scenes'] for p in s['paragraphs'] if p['renderer']=='Manim']
    for key in keys:
        if repair_key and key!=repair_key: continue
        if any(x['key']==key for x in state['completed']): continue
        state.update(status='rendering',active=key);save()
        name='Insert_'+key.replace('-','_')
        with tempconfig({'pixel_width':1920,'pixel_height':1080,'frame_width':16,'frame_height':9,'frame_rate':60,'renderer':'cairo','media_dir':str(OUT),'output_file':key+('-mip-average-v2' if repair_key else '-frame-exact'),'disable_caching':True,'max_inflight_encoders':1,'progress_bar':'none','verbosity':'WARNING'}):
            scene=getattr(module,name)();scene.render();output=Path(scene.renderer.file_writer.movie_file_path)
        probe=json.loads(subprocess.check_output(['C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(output)],text=True,creationflags=subprocess.CREATE_NO_WINDOW))['streams'][0]
        expected=module.BLOCKS[key]['frames']
        assert int(probe['nb_read_frames'])==expected,(key,probe,expected)
        state['completed'].append({'key':key,'path':output.relative_to(ROOT).as_posix(),'sha256':sha(output),'frames':expected,'probe':probe,'pixelsReviewed':False});save();print('DONE',key,expected,flush=True)
    state.update(status='complete-awaiting-pixels',active=None,exitCode=0,endedAt=now());save()
except BaseException as e:
    state.update(status='failed',error=repr(e),endedAt=now());save();raise

"""Render only three changed mathematical explanations with measured speech timing."""
import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import pathlib,json,hashlib,datetime,sys,subprocess,importlib.util
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01'
H=pathlib.Path(__file__).parent;O=P/'production/local/beginner-revision-v1/manim'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['beginnerRevision']['privateUploadAuthorized']
 assert not (R/'shared/output/GPU_HANDOFF.json').exists(),'Respect active TTS/ASR lease'
 plan=rd(H/'measured-scene-plan.json');assert plan['currentVoiceReviewed'] and plan['sentenceBoundariesDirectlyReviewed']
 assert not (O/'execution.json').exists(),'Inspect existing outputs instead of repeating the batch'
 from manim import tempconfig
 from manim.scene.scene_file_writer import _PartialMovieEncodeJob
 import ctypes
 from ctypes import wintypes
 kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.GetCurrentProcess.restype=wintypes.HANDLE
 kernel.GetProcessTimes.argtypes=[wintypes.HANDLE,*([ctypes.POINTER(wintypes.FILETIME)]*4)]
 kernel.GetProcessTimes.restype=wintypes.BOOL
 created,exited,kernel_time,user_time=(wintypes.FILETIME() for _ in range(4))
 assert kernel.GetProcessTimes(kernel.GetCurrentProcess(),ctypes.byref(created),ctypes.byref(exited),ctypes.byref(kernel_time),ctypes.byref(user_time))
 create_time=((created.dwHighDateTime<<32)|created.dwLowDateTime)/10_000_000-11644473600
 original_init=_PartialMovieEncodeJob.__init__
 def limited(self,*args,**kwargs):
  s=kwargs['stream'];s.codec_context.thread_count=2;s.codec_context.options={**s.codec_context.options,'preset':'veryfast','crf':'18'}
  return original_init(self,*args,**kwargs)
 _PartialMovieEncodeJob.__init__=limited
 src=P/'production/threejs-revision-v1/math_scenes.py'
 spec=importlib.util.spec_from_file_location('retained_math_implementation',src);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 blocks=[b for b in plan['scenes'] if b['renderer']=='Manim'];assert {b['key'] for b in blocks}=={'04f-p3','04f-p5','09-p7'}
 rows={r['key']:r for r in rd(H/'changes.json')['rows']}
 for b in blocks:
  mod.PARAS[b['key']]['focus']=rows[b['key']]['screenLabel']
  mod.BLOCKS[b['key']]={**mod.BLOCKS[b['key']], 'frames':b['frames'],'actionSteps':[dict(actionStartFrame=b['actionStartFrame'],actionDurationFrames=b['actionEndFrame']-b['actionStartFrame'],to=mod.PARAS[b['key']]['to'])]}
 O.mkdir(parents=True,exist_ok=True)
 state=dict(status='running',pid=os.getpid(),createTime=create_time,command=[sys.executable,*sys.argv],startedAt=now(),cpuThreads=2,gpuJobs=0,completed=[],planSha256=sha(H/'measured-scene-plan.json'),implementationSha256=sha(src),allPixelsReviewed=False)
 def save():wr(O/'execution.json',state)
 save();ck=rd(P/'production/checkpoint.json');ck.update(stage='beginner-math-render',activeOwnedHeavyJob={**state,'execution':(O/'execution.json').relative_to(R).as_posix()});wr(P/'production/checkpoint.json',ck)
 try:
  for b in blocks:
   key=b['key'];state['active']=key;save()
   with tempconfig(dict(pixel_width=1920,pixel_height=1080,frame_width=16,frame_height=9,frame_rate=60,renderer='cairo',media_dir=str(O),output_file=key,disable_caching=True,max_inflight_encoders=1,progress_bar='none',verbosity='WARNING')):
    scene=getattr(mod,'Insert_'+key.replace('-','_'))();scene.render();file=pathlib.Path(scene.renderer.file_writer.movie_file_path)
   probe=json.loads(subprocess.check_output(['C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(file)],text=True,creationflags=subprocess.CREATE_NO_WINDOW))['streams'][0]
   assert int(probe['nb_read_frames'])==b['frames'],(key,probe,b['frames'])
   state['completed'].append(dict(key=key,path=file.relative_to(R).as_posix(),frames=b['frames'],sha256=sha(file),probe=probe,pixelsReviewed=False));save();print('DONE',key,flush=True)
  state.update(status='complete-awaiting-pixels',active=None,exitCode=0,finishedAt=now());save()
 except BaseException as e:state.update(status='failed',error=repr(e),finishedAt=now());save();raise
 finally:
  ck=rd(P/'production/checkpoint.json')
  if (ck.get('activeOwnedHeavyJob') or {}).get('pid')==state['pid']:ck['activeOwnedHeavyJob']=None;wr(P/'production/checkpoint.json',ck)
if __name__=='__main__':main()

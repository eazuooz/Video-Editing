"""Render validated independent scenes while other narration is being produced.

The extra frozen ending is an intermediate render reserve. The final timeline
preserves all narration and trims only that unused reserve. No actual footage
is looped, slowed, or frozen to meet the lecture ratio.
"""
from pathlib import Path
import sys,json,hashlib,os,subprocess,time,math
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1]
sys.path.insert(0,str(ROOT/'qwen3-tts'))
from review_project_narration import acoustic_evidence
sys.argv=['align',slug]
import importlib.util
sp=importlib.util.spec_from_file_location('lecture_align',Path(__file__).parent/'align.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=ROOT/'projects'/slug;work=ROOT/'shared/output'/slug;work.mkdir(parents=True,exist_ok=True)
m=read(base/'project.json');out=ROOT/m['tts']['outputDir']
datafile=Path(__file__).parent/'lessons'/f'{slug}.json'
source=ROOT/m['paths']['sharedManimLesson'];stub=ROOT/f'manim/projects/{slug}/scene.py'
recordfile=work/'render-receipts.json';renderfile=work/'render-timing.json';deadline=time.monotonic()+14400
while True:
 data=read(datafile);expected=[s for s in data['scenes'] if s['kind']=='explanation'];records=read(recordfile) if recordfile.exists() else {};ready=[]
 for scene in expected:
  sid=scene['id'];wav=out/'chunks'/f'{sid}-scene.wav';asrfile=out/'asr'/f'{sid}.json'
  if not wav.exists() or not asrfile.exists():continue
  asr=read(asrfile);digest=sha(wav)
  if digest!=asr['audio_sha256'] or not acoustic_evidence(wav,m['tts'])['endingHeuristicPassed']:continue
  audio,sr=sf.read(wav);duration=len(audio)/sr
  try:starts,ends,coverage=a.a.align_characters(' '.join(scene['ko']),asr['words'],duration)
  except ValueError:continue
  offset=0;line_starts=[]
  for line in scene['ko']:
   line_starts.append(float(starts[offset]));offset+=len(a.normalized(line))
  line_starts[0]=0
  ready.append({'id':sid,'seconds':math.ceil((duration+10)*60)/60,'voiceSeconds':duration,'lineStarts':line_starts,'cues':[],'voiceSha256':digest,'coverage':coverage})
 renderfile.write_text(json.dumps({'purpose':'Intermediate render timing; final measured 40:60 timeline supersedes this reserve','scenes':ready},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 for slot in ready:
  sid=slot['id'];fingerprint={'voiceSha256':slot['voiceSha256'],'lessonSha256':sha(source),'dataSha256':sha(datafile),'stubSha256':sha(stub)}
  if source.name!='lesson.py':fingerprint['helperSha256']=sha(source.parent/'lesson.py')
  target=work/f'manim/videos/scene/1080p60/Scene{sid}.mp4'
  if target.exists() and all(records.get(sid,{}).get(k)==v for k,v in fingerprint.items()):continue
  print('Rendering validated scene',sid,slot['voiceSeconds'],'seconds voice',flush=True)
  env=os.environ.copy();env['MATH_RENDER_TIMING']=str(renderfile);env.pop('MATH_PREVIEW',None)
  with (work/f'incremental-scene-{sid}.log').open('w',encoding='utf8') as log:
   subprocess.run([sys.executable,'-m','manim','-qh','--disable_caching','--media_dir',str(work/'manim'),str(stub),'Scene'+sid],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
  records[sid]={**fingerprint,'renderReserveSeconds':10,'coverage':slot['coverage'],'completedAt':time.strftime('%Y-%m-%dT%H:%M:%S')}
  recordfile.write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
  print('Rendered validated scene',sid,flush=True)
 if len(records)==len(expected) and all(any(r['id']==s['id'] for r in ready) for s in expected):break
 if time.monotonic()>deadline:raise TimeoutError('Narration/render checkpoint retained; resume after resolving missing scenes')
 time.sleep(30)

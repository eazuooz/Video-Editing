"""Public official silent comparisons for native selection, never final approval."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'production/research/game-lighting-history/local/cross-game-comparisons-v51'
PY=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
NODE=Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
REQUESTS=[
 dict(id='WXaM4WK3bzg',slug='horizon-forbidden-west-sr',game='Horizon Forbidden West',primary='https://www.nvidia.com/en-us/geforce/news/dlss4-multi-frame-generation-ai-innovations/',primaryDate='2025-01-06',purpose='Same walking view, CNN/New Transformer super-resolution labels; clothing/bow/grass edges during movement. No frame-generation/latency inference.'),
 dict(id='8Ycy1ddgRfA',slug='alan-wake2-ray-reconstruction',game='Alan Wake 2',primary='https://www.nvidia.com/en-us/geforce/news/dlss4-multi-frame-generation-ai-innovations/',primaryDate='2025-01-06',purpose='Ray-reconstruction comparison, separately identify fan/fence/power-line details and actual on/off labels before narration.'),
 dict(id='MhLWH18vXH4',slug='resident-evil-requiem-dlss5-preview',game='Resident Evil Requiem',primary='https://www.nvidia.com/en-us/geforce/news/dlss5-breakthrough-in-visual-fidelity-for-games/',primaryDate='2026-03-16',purpose='Original March2026 DLSS5 preview; distinguish changing lighting/material appearance from measured game simulation/latency.'),
 dict(id='-vMVlfxUDe4',slug='starfield-dlss5-preview',game='Starfield',primary='https://www.nvidia.com/en-us/geforce/news/dlss5-breakthrough-in-visual-fidelity-for-games/',primaryDate='2026-03-16',purpose='Original March2026 appearance comparison; identify actual moving character/room/surface transitions before selection.'),
 dict(id='t50AdVMuxZE',slug='hogwarts-legacy-dlss5-preview',game='Hogwarts Legacy',primary='https://www.nvidia.com/en-us/geforce/news/dlss5-breakthrough-in-visual-fidelity-for-games/',primaryDate='2026-03-16',purpose='Original March2026 appearance comparison; retain OFF/ON conditions and actual camera/character movement. No universal current availability claim.')
]
stamp=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
assert not OUT.exists(),'Preserve prior source media'
resources=[]
for p in psutil.process_iter(['pid','name','cmdline','create_time']):
 try:
  d=p.info;cmd=' '.join(d['cmdline'] or [])
  if 'ffmpeg' in (d['name'] or '').lower() and 'game-lighting-history' in cmd:raise RuntimeError('Owned media slot active')
  if (d['name'] or '').lower().startswith(('python','ffmpeg')):resources.append(d)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip()
OUT.mkdir();target=OUT/'execution.json';me=psutil.Process()
state=dict(schemaVersion=1,startedAt=stamp(),status='running',worker=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=str(ROOT)),cpuThreads=2,gpuJobs=0,gpuObservation=gpu,resources=resources,requests=REQUESTS,active=None,completed=[],sourceAudioAcquired=False,newGitImages=0,finalUseApproved=False)
def save():
 target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
 p=ROOT/'production/research/game-lighting-history/checkpoint.json';c=json.loads(p.read_text('utf-8-sig'))
 c['episode04CrossGameSourceV51']=dict(execution=rel(target),status=state['status'],worker=state['worker'],active=state['active'],completed=len(state['completed']),finalUseApproved=False,cpuThreads=2,gpuJobs=0)
 c['updatedAt']=stamp();tmp=p.with_suffix('.v51.tmp');tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(p)
def run(cmd,label):
 log=OUT/(label+'.log');cmd=list(map(str,cmd))
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW);obs=psutil.Process(p.pid)
  state['active']=dict(label=label,pid=p.pid,createTime=obs.create_time(),command=cmd,log=rel(log));save();code=p.wait()
 state['active'].update(exitCode=code);save();assert code==0,(label,code)
try:
 save()
 for r in REQUESTS:
  stem=OUT/r['slug']
  run([PY,'-X','utf8','-m','yt_dlp','--no-progress','--no-playlist','--no-overwrites','--write-info-json','--no-write-thumbnail','--js-runtimes','node:'+str(NODE),'--retries','0','--fragment-retries','0','--socket-timeout','30','-f','bv*[height<=1080][ext=mp4][vcodec^=avc]/bv*[height<=1080][ext=mp4]','-o',str(stem)+'.%(ext)s','https://www.youtube.com/watch?v='+r['id']],r['slug']+'-public-download')
  media=stem.with_suffix('.mp4');info=json.loads(stem.with_suffix('.info.json').read_text('utf-8'))
  assert info['id']==r['id'] and info.get('channel_id')=='UCL-g3eGJi1omSDSz48AML-g','Actual official NVIDIA GeForce publisher required'
  probe=json.loads(subprocess.check_output([str(FP),'-v','error','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_frames:format=duration,size','-of','json',str(media)],text=True,creationflags=subprocess.CREATE_NO_WINDOW))
  assert not any(s['codec_type']=='audio' for s in probe['streams'])
  run([FF,'-v','error','-threads','2','-i',media,'-f','null','NUL'],r['slug']+'-whole-decode')
  review=OUT/(r['slug']+'-review');review.mkdir()
  run([FF,'-v','error','-threads','2','-i',media,'-filter_threads','2','-vf',"fps=1,scale=640:360,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='%{pts\\:hms}':x=8:y=8:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.8,tile=2x3:nb_frames=6:padding=4:margin=4",'-vsync','0','-threads','2',review/'board-%03d.png'],r['slug']+'-selection-samples')
  record={**r,'path':rel(media),'sha256':sha(media),'publisher':info['channel'],'channelId':info['channel_id'],'uploadDate':info['upload_date'],'title':info['title'],'probe':probe,'wholeDecodeExitCode':0,'sourceAudioUsed':False,'boards':[dict(path=rel(p),sha256=sha(p),directlyRead=False) for p in sorted(review.glob('board-*.png'))],'localOnly':True,'rightsApproved':False,'rightsScope':'Public official technical source identified. Standard platform visibility and SDK license do not grant blanket third-party clip reuse; final public rights review retained pending. No authentication or access bypass.','recentUseCheckPassed':False,'allNativeMotionReviewed':False,'finalUseApproved':False,'adoptedGameCount':0}
  stem.with_suffix('.acquisition.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8');state['completed'].append(record);state['active']=None;save()
  print(json.dumps(dict(id=r['id'],seconds=probe['format']['duration'],boards=len(record['boards']),finalUseApproved=False)),flush=True)
 state.update(status='five-native-comparisons-ready-for-direct-selection',endedAt=stamp());save()
except BaseException as exc:
 state.update(status='failed-preserve-completed-and-partial',error=str(exc),endedAt=stamp());save();raise

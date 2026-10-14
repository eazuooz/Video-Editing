"""Three scoped clarity repairs on CPU; preserve completed research and52takes."""
import pathlib,json,datetime,os,sys,runpy
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/beginner-revision-v1/terminology-r1'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert '--device' in sys.argv and sys.argv[sys.argv.index('--device')+1]=='cpu'
assert rd(P/'production/checkpoint.json')['beginnerRevision']['privateUploadAuthorized']
assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
assert rd(P/'production/local/beginner-revision-v1/voice-contexts/execution.json')['status']=='complete-awaiting-direct-review'
assert not (O/'execution.json').exists()
import psutil
O.mkdir(parents=True,exist_ok=True)
s=dict(status='running',pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=0,researchModified=False,keys=['07-p6','09-p9','g29'],startedAt=now())
wr(O/'execution.json',s)
ck=rd(P/'production/checkpoint.json');ck.update(stage='beginner-three-terminology-repairs',activeOwnedHeavyJob={**s,'execution':(O/'execution.json').relative_to(R).as_posix()});wr(P/'production/checkpoint.json',ck)
try:
 runpy.run_path(str(P/'production/render-voice.py'),run_name='__main__')
 s.update(status='complete-exit0',exitCode=0,finishedAt=now());wr(O/'execution.json',s)
except BaseException as e:
 s.update(status='failed',error=repr(e),finishedAt=now());wr(O/'execution.json',s);raise
finally:
 ck=rd(P/'production/checkpoint.json')
 if (ck.get('activeOwnedHeavyJob') or {}).get('pid')==s['pid']:ck['activeOwnedHeavyJob']=None;wr(P/'production/checkpoint.json',ck)

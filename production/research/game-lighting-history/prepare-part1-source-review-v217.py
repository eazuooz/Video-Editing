"""Prepare local encoded-bank review and record the actual one ASR worker."""
from pathlib import Path
import json,hashlib,os,datetime,html,psutil
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):
 t=p.with_name(p.name+'.writing-'+str(os.getpid()));t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
bank=ROOT/'production/research/game-lighting-history/local/part1-spatial-bank-v206'
plan=read(bank/'plan.json');media=read(bank/'media-verification-v216.json')
assert media['wholeDecodeExitCode']==0 and media['allPtsExact'] and media['frames']==4653
assert sha(ROOT/media['path'])==media['sha256']
out=bank/'review-v217';out.mkdir(exist_ok=False)
points={}
def add(f,label):
 if 0<=f<4653:points.setdefault(f,[]).append(label)
for s in plan['scenes']:
 for f,label in [(s['fromFrame']-1,'before'),(s['fromFrame'],'first'),(s['toFrame']-1,'last'),(s['toFrame'],'after')]:add(f,s['id']+' '+label)
 for i,stage in enumerate(s['stages']):
  for f,label in [(stage['fromFrame'],'start'),((stage['fromFrame']+stage['toFrame']-1)//2,'middle'),(stage['toFrame']-1,'end')]:add(s['fromFrame']+f,f"{s['id']} stage{i+1} {label}")
r=dict(preparedAt=stamp(),source=media,points=[dict(frame=f,labels=points[f])for f in sorted(points)],scenes=plan['scenes'],extracted=False,allMovingPixelsReviewed=False,allFinalCaptionPixelsReviewed=False,localOnly=True,newGitImages=0)
write(out/'plan.json',r)
opts=''.join(f'<option value="{i}">{html.escape(s["id"])}</option>'for i,s in enumerate(plan['scenes']))
data=json.dumps([dict(id=s['id'],fromFrame=s['fromFrame'],toFrame=s['toFrame'],ko=s['originalKo'],stages=s['stages'])for s in plan['scenes']],ensure_ascii=False)
(out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>④-1 검은 2.5D 보완 장면 검수</title><style>body{background:#18191b;color:white;font:16px sans-serif;margin:18px}video{width:min(1152px,96vw);display:block;margin-top:12px}select,input,button{font:16px sans-serif;margin:4px;padding:5px}pre{white-space:pre-wrap;max-width:1152px}#clock{display:inline-block;min-width:170px}</style><h1>④-1 검은 2.5D 보완 장면</h1><p>원본 내레이션 샘플을 보존한 설명 장면 10개. 최종 자막·믹스 승인과 별도입니다.</p><label>장면 <select aria-label="장면" id="scene">'''+opts+'''</select></label><button id="play">장면 재생</button><button id="pause">일시정지</button><button id="first">시작</button><button id="last">마지막</button><label>프레임 <input aria-label="프레임" type="number" id="frame" min="0" max="4652" value="0"></label><button id="seek">프레임 이동</button><span id="clock"></span><video id="video" src="../renders/episode04-part1-spatial-bank-v206.mp4" controls></video><pre id="details"></pre><script>const scenes='''+data+''';const v=document.getElementById('video'),sel=document.getElementById('scene'),f=document.getElementById('frame');function s(){return scenes[Number(sel.value)]}function load(){v.pause();v.currentTime=s().fromFrame/60;document.getElementById('details').textContent=s().ko+'\n'+s().stages.map(x=>((s().fromFrame+x.fromFrame)/60).toFixed(3)+'–'+((s().fromFrame+x.toFrame)/60).toFixed(3)+' '+x.anchor).join('\n')}sel.onchange=load;document.getElementById('play').onclick=()=>{if(v.currentTime<s().fromFrame/60||v.currentTime>=(s().toFrame-1)/60)v.currentTime=s().fromFrame/60;v.play()};document.getElementById('pause').onclick=()=>v.pause();document.getElementById('first').onclick=()=>{v.pause();v.currentTime=s().fromFrame/60};document.getElementById('last').onclick=()=>{v.pause();v.currentTime=(s().toFrame-1)/60};document.getElementById('seek').onclick=()=>{v.pause();v.currentTime=Number(f.value)/60};v.ontimeupdate=()=>{document.getElementById('clock').textContent=v.currentTime.toFixed(3)+'s / '+Math.floor(v.currentTime*60)+'f';if(!v.paused&&v.currentTime>=s().toFrame/60)v.pause()};load();</script>''','utf-8')
ep=BASE/'part1-protected-onsets-asr-execution-v214.json';e=read(ep)
if not e.get('endedAt'):
 p=psutil.Process(e['actualIdentity']['pid'])
 assert abs(p.create_time()-e['actualIdentity']['createTime'])<0.1 and 'review-part1-protected-onsets-v214.py' in ' '.join(p.cmdline())
 active={**e['actualIdentity'],'type':'CPU-protected-onsets-ASR-v214','sessionId':66669,'execution':ep.relative_to(ROOT).as_posix(),'log':ep.relative_to(ROOT).as_posix(),'cpuThreads':2,'gpuJobs':0,'next':'Read both full protected utterances, remove only the disposable preface at an observed PCM pause, resolve the preserved car tail failure before five final whole/context reviews.'}
else:active=None
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=read(cp)
c.update(updatedAt=stamp(),status='episode04-physical01-protected-onsets-CPU-ASR-and-encoded-source-review-v217',ownedActiveWork=active)
c['episode04Part1SpatialBankV216']={'verification':(bank/'media-verification-v216.json').relative_to(ROOT).as_posix(),'sha256':media['sha256'],'frames':4653,'allPtsExact':True,'decodeExitCode':0,'sessionId':93029,'sessionClosed':True,'movingPixelsReviewed':False,'reviewPlan':(out/'plan.json').relative_to(ROOT).as_posix()}
write(cp,c)
print(json.dumps({'points':len(points),'scenes':10,'asrPid':e['actualIdentity']['pid'],'asrSession':66669,'asrClosed':bool(e.get('endedAt'))}))

from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat();se=read(BASE/'observation-guides-tts-session-v1.json');state=read(BASE/'observation-guides-tts-execution-v1.json')
assert state['pid']==se['pid']==51384 and se['processIdentity']['CommandLine'].find('render-observation-guides-cpu-v1.py')>=0
state.update(sessionId=se['sessionId'],processIdentity=se['processIdentity']);save(BASE/'observation-guides-tts-execution-v1.json',state)
job={'pid':state['pid'],'processIdentity':se['processIdentity'],'commandLine':state['commandLine'],'sessionId':se['sessionId'],
 'status':state['status'],'state':'projects/player-customization/production/observation-guides-tts-execution-v1.json',
 'log':state['log'],'cpuThreads':2,'gpu':0,'singleJob':True,'completed':len(state['results']),'total':8,'exitCode':None,
 'next':'Read actual current guide voice/full ASR and independent contexts after this one worker completes. Original eight PCM/ASR/white sources are already preserved and must not be repeated.'}
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now,stage='additional-observation-guides-single-CPU2-measurement',ownedJob=job,
 additionalGuidesTtsStarted=True,nextAction=job['next']);save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization');i.update(stage=cp['stage'],currentExecution=job,nextAction=job['next']);q['updatedAt']=now;save(qp,q)
helper1=ROOT/'motion-canvas/src/projects/player-customization/observation-guide-explanation-v1.tsx';helper2=helper1.with_name('observation-guide-explanation-v2.tsx')
save(BASE/'observation-guides-authoring-typecheck-v2.json',{'schemaVersion':1,'checkedAt':now,
 'historicalFailure':{'helper':helper1.relative_to(ROOT).as_posix(),'sha256':sha(helper1),'exitCode':1,'diagnostic':'TS2554 at20:62: Node constructor requires one argument.'},
 'currentAuthoringHelper':{'path':helper2.relative_to(ROOT).as_posix(),'sha256':sha(helper2),'change':'new Node({}) supplies the required empty configuration. Same text/geometry/timing behavior; historical helper and active TTS-protected inputs preserved.'},
 'command':'node node_modules/typescript/bin/tsc --noEmit --project tsconfig.player-customization.guides-v1.json','workingDirectory':'motion-canvas','exitCode':0,
 'scope':'Only own eight guide wrappers/current helper plus scoped white fixes, their imported shared dependencies and env types. Not a whole-workspace claim.',
 'animatedGuidePixelsApproved':False,'finalVideoComplete':False})
readme=ROOT/'projects/player-customization/README.md'
text=readme.read_text('utf-8-sig')
section='2026-10-08 08:53KST latest actual checkpoint: original8-scene/32KOEN voice223.92s and whole8/independent16ASR directly reviewed; human listening/pronunciation remains pending. Original white source13439frames decoded with contiguous90000PTS. All96 narration-timed motion pixels were read. Two issues in01/05 were repaired in one scoped3001-frame render; all24 correction samples/6boards, exactPTS and wholedecode0 were directly verified. The other six white scenes were preserved and not rerendered. Current eight-source input set is production/current-reviewed-original-white-inputs-v2.json. The beginning rights notice is readable in all12 corrected overview source samples; final burned-caption pixels remain pending.\n\nEight additive, independently paired guide scenes/32KOEN paragraphs were written after inspected Gauss/Jade/Yareli/Dante source footage. Original scripts/outline/all eight PCM remain byte-preserved. One CPU2/GPU0 Qwen1.7/reference guide job is running at actual PID51384/session59534; read its execution and exact creation identity before continuing. All guide whole/context ASR, final unique source edges/crops, measured60:40, final mix/caption pair/QA, collection/private upload/Git remain pending. The own-scope authoring TypeScript repair/check passed for current helper v2; prepared guide motion is not final pixel approval. No original generation, ASR, white source, completed private video or deletion should be repeated.\n\nBelow are preserved earlier checkpoints; use the actual project checkpoint and queue first.\n\n'
readme.write_text(text.replace('# Player customization\n\n','# Player customization\n\n'+section,1),'utf-8')
batch=ROOT/'production/batches/sakurai-planning-game-design/README.md';text=batch.read_text('utf-8-sig')
addition='2026-10-08 08:53KST player-customization 최신: original8장32KOEN/223.92초 PCM, whole8·독립문맥16 직접대조와 실제 white13439프레임을 보존한다. 96입체 표본을 직접읽고01문구가림/05후보겹침만 별도3001프레임으로 수정, 24표본6판/정확PTS/전체decode0을 검수했다. 여섯 통과 흰씬은 재렌더하지 않았다. 실제 행동을 관찰한 추가8장32KOEN을 독립 작성했으며 현재 단일 CPU2/GPU0 Qwen guide PID51384/session59534가 실행 중이다. 다른 GPU학습을 보존한다. 현재혼합ASR·정확60:40·최종자막픽셀/QA/수집/비공개/Git은 아직false이고13완료·중복1·남은10을 유지한다. 실제 production/latest-checkpoint.json과 queue가 우선이며 아래는 이전 이력이다.\n\n'
pos=text.find('\n\n');batch.write_text(text[:pos+2]+addition+text[pos+2:],'utf-8')
print(json.dumps({'pid':state['pid'],'session':se['sessionId'],'currentTypecheck':0,'finalVideoComplete':False}))

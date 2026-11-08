"""Final-only scoped project/worklist commit, preserving foreign index overlays."""
from pathlib import Path
import json,sys,importlib.util,contextlib,datetime,re,os
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/room-v3'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8')
delivery=read(H/'delivery.json');review=read(H/'final-review.json');assert review['encodedVisualReview']=='sampled-pass'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
master=next(x for x in delivery['files'] if x['name'].endswith('.captioned.mp4'))
checkpoint={'updatedAt':now,'stage':'room-v3-local-final-review','selectedScope':'same-room practical eight-tool audit plus native pixel, measured gait, central ledger writing, lighting and twenty-track radio','completed':['51 scene composition','30 baseline PCM sources preserved','21 added passages and all current-mix ASR checked','actual 7 OSS executions and disclosed SSD setup failure','1080p60 four-file delivery and encoded/mobile sample review','public playable room v4 deployed separately by root'],'delivery':delivery,'masterSha256':master['sha256'],'humanReview':'pending','humanListening':'not asserted','youtubeAuthorized':False,'driveAuthorized':False,'next':'User review of this exact local captioned master'}
save(H/'checkpoint.json',checkpoint);save(P/'production/room-v2/checkpoint.json',checkpoint)
project=read(P/'project.json');project['previousDeliveryBeforeRoomRevision']=project.get('previousDeliveryBeforeRoomRevision',project.get('delivery'));project['delivery']={'directory':delivery['directory'],'reviewUrl':delivery['reviewUrl'],'revision':'room-v3','masterSha256':master['sha256']};project['status']='local-final-review'
project['previousEditingBeforeRoomRevision']=project.get('previousEditingBeforeRoomRevision',project.get('editing'))
project['editing']['actualExplanationSeconds']=delivery['duration']-12
project['editing']['actualGameplayShare']=0
project['editing']['actualCommercialGameplaySeconds']=0
project['editing']['explanationStyle']='research-black-v1; actual tool outputs and same-game Canvas execution, native pixel motion, speech-aligned guides'
project['editing']['exampleInterleaving']['reviewStatus']='51-scene room-v3 current encoded samples and canonical captions reviewed; source+AAC semantic ASR checked. Full actual listening/user review pending.'
project['currentRevision']={'id':'room-v3','durationSeconds':delivery['duration'],'sceneCount':51,'plan':'production/room-v3/revision-plan.json','checkpoint':'production/room-v3/checkpoint.json','review':'production/room-v3/final-review.json'}
save(P/'project.json',project)
worklist=read(R/'shared/publishing/video-worklist.json');old=next(x for x in worklist['rows'] if x['id']=='S-AI2D');row={**old,'productionComplete':True,'productionStatus':'방 게임 확장 · 1080p60 로컬 검수본 완성','reviewStatus':'새 room-v3 최종 사용자 검수 대기','humanApproval':'아직 새 영상 검수 전','platformStatus':'이번 수정본 YouTube/Drive 미업로드 · 웹 게임 공개','executionStatus':'room-v3-local-final-review','localMasterAvailable':True,'reviewUrl':delivery['reviewUrl'],'updatedAt':now,'evidence':old.get('evidence',[])+['projects/ai-2d-game-assets/production/room-v3/delivery.json','projects/ai-2d-game-assets/production/room-v3/final-review.json','projects/ai-2d-game-assets/production/room-v3/site-deployment.json'],'notes':'동일 캐릭터·방에7도구 실제 적용. SSD 공식 필수파일 누락 재현시도 공개. 기존30음성 보존+21설명. 원본 완성본 보존. 사용자가 웹 공개를 명시 승인했으며 영상은 로컬 검수 단계.'}
row['evidence']=list(dict.fromkeys(row['evidence']))
helper=R/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py';spec=importlib.util.spec_from_file_location('scoped',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';C='shared/publishing/video-production-control.json'
control=read(R/C);owned=control['ai2dRoomRevision20261108'];owned.update(status='local-final-review',updatedAt=now,checkpoint='projects/ai-2d-game-assets/production/room-v3/checkpoint.json',localMasterSha256=master['sha256'],humanVideoReview='pending')
authorization=control['scopedProductionAuthorizations']['ai-2d-game-assets'];authorization.update(status='local-final-review',updatedAt=now,checkpoint='projects/ai-2d-game-assets/production/room-v3/checkpoint.json')
section='\n<!-- AI2D-20261108 -->\n## AI로 2D 게임 리소스 제작\n\n| 편 | 내용 | 제작 | 검수 | 플랫폼 |\n|---|---|---|---|---|\n| S-AI2D | ComfyUI·LoRA +8도구 실사용·방 게임 확장 | 1080p60 완성 | room-v3 사용자 검수 대기 | 영상 미업로드 · 웹 게임 공개 |\n\n[전체 영상 검수](http://127.0.0.1:9286/) · [직접 플레이](https://yamyam-cartographers-room.eazuooz.chatgpt.site) · [전체 대본](../projects/ai-2d-game-assets/production/room-v3/full-narration.ko.txt)\n<!-- AI2D-20261108-END -->\n'
def overlay(name,raw,spec):
 if name==C:return mod.patch(mod.patch(raw,['ai2dRoomRevision20261108'],owned),['scopedProductionAuthorizations','ai-2d-game-assets'],authorization)
 if name==W:return mod.upsert(raw,'rows','id',row)
 if name==D:
  text=raw.decode('utf-8-sig');pat=r'\n<!-- AI2D-20261108 -->.*?<!-- AI2D-20261108-END -->\n';text=re.sub(pat,lambda _:section,text,flags=re.S) if '<!-- AI2D-20261108 -->' in text else text.rstrip()+'\n'+section;return text.encode('utf8')
 raise ValueError(name)
mod.SHARED={W,D,C};mod.overlay=overlay
for name in mod.SHARED:(R/name).write_bytes(overlay(name,(R/name).read_bytes(),{}))
if '--commit' in sys.argv:
 paths=[]
 for parent,dirs,files in os.walk(P):
  dirs[:]=[d for d in dirs if d not in {'local','__pycache__','.git','node_modules'}]
  if Path(parent)==P/'production/room-v2':dirs[:]=[d for d in dirs if d!='research']
  for name in files:
   p=Path(parent)/name
   if p.suffix in {'.py','.cjs','.json','.md','.txt'} or p.name=='.gitignore':paths.append(p.relative_to(R).as_posix())
 paths=sorted(paths)
 def validate(s):
  assert s['ownedPaths']==paths;assert all(name.startswith('projects/ai-2d-game-assets/') and (R/name).is_file() for name in paths);return paths+sorted(mod.SHARED)
 mod.validate=validate;sp=L/'commit-spec.json';save(sp,{'ownedPaths':paths});sys.argv=[str(helper),'--spec',str(sp),'--execute','--push','--message','Complete AI 2D tools workshop video and playable room revision']
 with (L/'commit-delivery.json').open('w',encoding='utf8') as f,contextlib.redirect_stdout(f):mod.main()
 print(read(L/'commit-delivery.json')['commit'])

from pathlib import Path
import json,sys,importlib.util,contextlib,datetime,re
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
done='--delivered' in sys.argv;commit='--commit' in sys.argv
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
status='local-review-ready' if done else 'narration-and-picture-production'
checkpoint=read(P/'production/checkpoint.json');checkpoint.update(stage=status,updatedAt=now,
 completed=['Both supplied Shorts: complete narration and full-duration visual review','All8primary repositories and original article checked','30paragraph KO/EN script and source-to-screen plan','Actual ComfyUI same-seed base/style run','Actual PixelOE,pixelfx,Pixelbolt exports','1080p and375px representative preflight'],
 next='Human review of complete local master; no platform mutation' if done else 'Finish30paragraph Qwen takes,60fps scenes,caption alignment,current-audio ASR and final four outputs',
 humanReview='pending' if done else 'not-yet-delivered',youtubeAuthorized=False,driveAuthorized=False)
if done:checkpoint['delivery']=read(P/'production/delivery-output.json')
save(P/'production/checkpoint.json',checkpoint)
row={'id':'S-AI2D','slug':'ai-2d-game-assets','series':'S','seriesOrder':6,'title':read(P/'project.json')['titleKo'],'productionComplete':done,
 'productionStatus':'1080p60 로컬 검수본 완성' if done else '8도구·원문 확인 / 실제 생성·후처리 시연 / 음성·화면 제작 중',
 'reviewStatus':'로컬 최종 사용자 검수 대기' if done else '제작 중','humanApproval':'아직 최종 영상 검수 전','platformStatus':'미업로드 · 이번 요청은 로컬 제작',
 'videoId':None,'url':None,'latestRulesPassed':None,'executionStatus':status,'localMasterAvailable':done,
 'evidence':['projects/ai-2d-game-assets/project.json','projects/ai-2d-game-assets/planning/production-plan.json','projects/ai-2d-game-assets/planning/sources.json','projects/ai-2d-game-assets/production/checkpoint.json'],
 'notes':'사용자 제공 두 쇼츠의8도구 + ComfyUI/LoRA 픽셀아트 가이드. 검증한 실행 결과와 원리 도식 구분. 새 캐릭터 LoRA 학습을 실행했다고 주장하지 않음. 추가 BGM 없는 강의. Drive/YouTube 및 다른 편 미착수.', 'updatedAt':now}
if done:
 row['reviewUrl']='http://127.0.0.1:9283/'
 row['evidence']+=['projects/ai-2d-game-assets/production/final-review.json','projects/ai-2d-game-assets/production/delivery-output.json']
helper=R/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
spec=importlib.util.spec_from_file_location('scoped',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';C='shared/publishing/video-production-control.json'
control=read(R/C)['scopedProductionAuthorizations']['ai-2d-game-assets'];control.update(status=status,updatedAt=now,checkpoint='projects/ai-2d-game-assets/production/checkpoint.json')
section='\n<!-- AI2D-20261108 -->\n## AI로 2D 게임 리소스 제작\n\n| 편 | 내용 | 제작 | 검수 | 플랫폼 |\n|---|---|---|---|---|\n| S-AI2D | ComfyUI·LoRA 픽셀아트 + 공개 도구8종 | '+row['productionStatus']+' | '+row['reviewStatus']+' | 업로드 미승인 |\n\n[전체 대본](../projects/ai-2d-game-assets/script/full-script.md) · [제작 계획](../projects/ai-2d-game-assets/planning/production-plan.json)'+(' · [전체 영상 검수](http://127.0.0.1:9283/)' if done else '')+'\n<!-- AI2D-20261108-END -->\n'
def overlay(name,raw,spec):
 if name==C:return mod.patch(raw,['scopedProductionAuthorizations','ai-2d-game-assets'],control)
 if name==W:
  raw=mod.upsert(raw,'rows','id',row)
  order=mod.load(raw)['workOrder']
  return mod.patch(raw,['workOrder'],order+['S-AI2D']) if 'S-AI2D' not in order else raw
 if name==D:
  text=raw.decode('utf-8-sig');pattern=r'\n<!-- AI2D-20261108 -->.*?<!-- AI2D-20261108-END -->\n'
  text=re.sub(pattern,lambda _:section,text,flags=re.S) if '<!-- AI2D-20261108 -->' in text else text.rstrip()+'\n'+section
  return text.encode('utf-8')
 raise ValueError(name)
mod.SHARED={W,D,C};mod.overlay=overlay
for name in mod.SHARED:(R/name).write_bytes(overlay(name,(R/name).read_bytes(),{}))
if commit:
 paths=sorted(p.relative_to(R).as_posix() for p in P.rglob('*') if p.is_file() and 'local' not in p.relative_to(P).parts and '__pycache__' not in p.parts and (p.suffix in {'.py','.cjs','.json','.md','.txt'} or p.name=='.gitignore'))
 def validate(s):
  assert s['ownedPaths']==paths
  assert all(name.startswith('projects/ai-2d-game-assets/') and (R/name).is_file() for name in paths)
  return paths+sorted(mod.SHARED)
 mod.validate=validate;sp=L/'commit-spec.json';save(sp,{'ownedPaths':paths})
 sys.argv=[str(helper),'--spec',str(sp),'--execute','--push','--message',('Deliver' if done else 'Prepare')+' AI 2D asset workflow video with verified tool demonstrations']
 with (L/('commit-delivery.json' if done else 'commit-preproduction.json')).open('w',encoding='utf-8') as stream,contextlib.redirect_stdout(stream):mod.main()
 print(read(L/('commit-delivery.json' if done else 'commit-preproduction.json'))['commit'])
else:print(status)

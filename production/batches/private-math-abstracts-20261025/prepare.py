"""Finite user-selected integration of actual-game abstracts into 18 math reviews."""
from pathlib import Path
import json,hashlib,datetime,subprocess
R=Path('D:/Github/VideoEditing');B=R/'production/batches/private-math-abstracts-20261025';C=Path('C:/Users/1/.codex/video-render-cache/private-math-abstracts-20261025')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def rel(p):return p.relative_to(R).as_posix()
# Source references can explicitly borrow another already-reviewed math source.
# Each range is native speed; extended endpoints require the new contact review.
CONFIG={
'M03-original':('방향 하나와 몸 전체의 자세는 다릅니다',[('totk',995,20.833333333333)]),
'M04':('회전은 각도만큼 순서도 중요합니다',[('totk',279,24.583333333333)]),
'M05':('돌린 자세를 저장하고 다시 되돌리기',[('totk',417,21),('se2',98.5,13.333333333333)]),
'M06':('현재 자세에서 목표 자세까지',[('se2',37.8,15.45),('vs',98.5,13.5)]),
'M07':('중간 자세가 움직임의 경로를 만듭니다',[('M04:totk',279,11),('escape',8,3.6),('release',24.6,9.2),('M08:besiege',59,7.283333333333)]),
'M08':('표현은 달라도 같은 자세인지 확인하기',[('besiege',33,8),('besiege',59,8.183333333333)]),
'M09':('두 점을 잇는 선에서 닿는 범위까지',[('grapple',407,14),('bridge',5.5,6.4),('grapple',370,10.65),('M08:besiege',59,10)]),
'M10':('물체의 크기와 회전 뒤 범위는 다릅니다',[('big',1708,9),('tinyglade',10.5,6.5),('besiege',59,4.666666666667)]),
'M11':('표면까지의 거리와 표면 안의 위치',[('bridge',0,5.4),('bridge',5.5,6.4),('bridge',12,8.45)]),
'M12':('세 기준점으로 위치와 속성을 연결하기',[('townlong',1203,9),('townlong',1504,8),('M20:se2',73,3.983333333333)]),
'M13':('어떤 중심을 고르고 어떤 경계를 지킬까?',[('dorf',38,7),('tinyA',10.5,6.5),('dorf',116,7.8)]),
'M15':('보이는 표면을 고르고 색과 빛을 계산하기',[('big',514,10),('sub',615,10),('big',796,5.183333333333)]),
'M16':('카메라의 위치·줌·출력 창을 구분하기',[('split',30,15),('town',788,7.7)]),
'M17':('세계의 한 점이 화면의 한 점이 되기까지',[('town',1504,8),('tiny',10.5,6.5),('town',639,9.866666666667)]),
'M18':('화면 위치 뒤에도 깊이와 w가 필요합니다',[('town',1491,8),('tinyB',22,7.5),('town',1203,8.883333333333)]),
'M19':('형태를 잇는 정점과 빛을 위한 법선',[('tinyB',34,6),('M15:sub',248,12),('big',595,7.1)]),
'M20':('형태가 바뀌어도 빛과 무늬를 맞추기',[('tinyWidth',10.5,6.5),('tinyB',22,7.5),('tinyB',40,9.983333333333)]),
}
def junction(link,target):
 target.mkdir(parents=True,exist_ok=True)
 if not link.exists():
  assert link.parent==R/'output'
  subprocess.run(['powershell','-NoProfile','-Command',f"New-Item -ItemType Junction -Path '{link}' -Target '{target}' | Out-Null"],check=True)
 assert link.resolve()==target.resolve()
def main():
 w=read(R/'shared/publishing/video-worklist.json');es=w['privateMathPolish']['gameplayTimingRevision']['entries'];by={e['id']:e for e in es};plans={k:read(R/e['plan']) for k,e in by.items()};entries=[]
 for e in es:
  if e['id']=='M14':entries.append(dict(id=e['id'],slug=e['slug'],title=e['title'],status='retained-complete',output=e['newOutput'],masterSha256=e['masterSha256'],humanReview='pending'));continue
  id=e['id'];slug=e['slug'];P=R/'projects'/slug;project=read(P/'project.json');timeline=read(P/'production/concept-fit-v2/timeline.json');title,ranges=CONFIG[id];segments=[];at=2.
  for index,(key,t,seconds) in enumerate(ranges):
   owner,key=key.split(':',1) if ':' in key else (id,key);src=plans[owner]['sources'][key];seconds=round(seconds*60)/60
   segments.append(dict(index=index,start=at,seconds=seconds,end=at+seconds,sourceIn=t,sourceOut=t+seconds,source=src['path'],game=src['game'],sourceKey=key,sourceOwner=owner,rightsEvidence=src['rightsEvidence'],sourceUrl=src.get('url'),sourceAudio='Retain complete existing lecture mix; no new trailer/commentary bed.',nativeSpeed=1,guides=[],review='pending-current-range-review'));at+=seconds
  # Existing spoken overview is the abstract: no duplicate narration or new TTS.
  scenes=[dict(id=s['id'],title=s.get('title'),start=s['start'],seconds=s['seconds'],cues=s.get('cues',[])) for s in timeline['scenes'] if s['start']<at]
  out=R/'output'/f'{slug}-actual-abstract-v6';junction(out,C/'deliveries'/slug)
  plan=dict(id=id,slug=slug,title=e['title'],headline=title,status='source-review-pending',oldOutput=e['newOutput'],oldMasterSha256=e['masterSha256'],output=rel(out),work=str(C/'work'/id),abstractStart=2,abstractEnd=round(at*60)/60,abstractFrames=round((at-2)*60),segments=segments,openingScenes=scenes,totalFrames=timeline['frames'],seconds=timeline['seconds'],existingPlan=e['plan'],projectManifest=rel(P/'project.json'),method='Integrate existing spoken question/overview with actual game examples. Preserve every audio packet, caption cue, body explanation frame and overall length outside the changed opening.',newTts=False,freezePadding=0,captionPosition='boxed-white-forest-v1 unchanged at960,970',humanReview='pending',uploadAuthorized=False)
  save(B/'plans'/f'{id}.json',plan);entries.append(dict(id=id,slug=slug,title=e['title'],status='source-review-pending',plan=rel(B/'plans'/f'{id}.json'),output=rel(out),oldOutput=e['newOutput'],humanReview='pending'))
 now=datetime.datetime.now().astimezone().isoformat();cp=dict(batch='private-math-abstracts-20261025',requestedOn=now,userEvidence='모든 영상에 도입부 넣은거야? 모둔영상에 넣어줘',scope='All18 current math review entries; M14 retained by hash and17 existing openings integrated with real gameplay.',entries=entries,ready=1,total=18,status='source-review-and-edit',newTts=False,automation=False,upload=False,choice='Reuse existing thesis/overview speech instead of duplicating introductions or changing approved voices; open with real-game evidence, then preserve existing teaching sequence. No unrelated video work.',storageRoot=str(C));save(B/'checkpoint.json',cp)
 controlPath=R/'shared/publishing/video-production-control.json';c=read(controlPath);c['scopedBatchAuthorizations']['private-math-abstracts-20261025']=dict(status='active',episodeIds=[e['id'] for e in es],userEvidence=cp['userEvidence'],scope=cp['scope'],renderAuthorized=True,newTtsAuthorized=False,preserveBody=True,preserveExistingM14Hash=True,uploadAuthorized=False,automationAuthorized=False,otherVideoAuthorized=False,checkpoint=rel(B/'checkpoint.json'));c['actualGameAbstractPolicy']['scope']='Explicitly selected18 math reviews plus future selected productions';save(controlPath,c)
 w['privateMathPolish']['abstractRevision']=dict(status=cp['status'],checkpoint=rel(B/'checkpoint.json'),ready=1,total=18,entries=entries);save(R/'shared/publishing/video-worklist.json',w)
 p=R/'docs/VIDEO_WORKFLOW.md';s=p.read_text('utf8');s=s.replace('현재 선택된 다각형 ② 수정과 앞으로 명시 선택하는 제작에 적용한다. 이번 편의 본문 설명·음성·학습 순서는 보존하며 추가 도입 음성만 생성한다.','2026-10-25 후속 사용자 요청으로 현재 게임수학 검수표18편 전체에도 적용한다. 완료된 다각형②는 보존하고 나머지17편은 기존 핵심 질문·개요 음성에 실제 게임 장면을 결합하여 도입부를 통합한다. 기존 개요가 충분하면 새 TTS나 중복 개요를 덧붙이지 않으며 본문 설명·음성·학습 순서·길이를 보존한다. 이18편의 명시된 유한 작업 외에는 앞으로 명시 선택한 제작에 적용한다.');p.write_text(s,encoding='utf8')
 p=R/'AGENTS.md';s=p.read_text('utf8');s=s.replace('Apply to selected M14 and future explicitly selected work; preserve existing M14 body narration/explanations/order, generating only added opening speech. No automatic remake of other completed videos.','The user subsequently selected all18 current math reviews on2026-10-25: retain M14 and integrate actual-game abstracts into the other17 existing openings, preserving useful overview speech and every body explanation/audio/timing; no duplicate introduction or new TTS when existing speech suffices. This finite batch and future explicitly selected work are authorized; no other automatic remakes.');p.write_text(s,encoding='utf8')
 print('Authorized18 reviews: M14 retained,17 actual-game opening revisions prepared.')
if __name__=='__main__':main()

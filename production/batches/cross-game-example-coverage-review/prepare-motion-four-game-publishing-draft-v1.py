"""Prepare bilingual four-game metadata from actual mix timings; no platform mutation."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1';OLD=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(R/'measured-current17-plan-v2.json');mix=read(R/'current-mix-execution-v2.json');defaults=read(ROOT/'shared/publishing/youtube-defaults.json')
assert mix['actualExitCode']==0 and mix['planSha256']==sha(R/'measured-current17-plan-v2.json')
dest=R/'publishing';dest.mkdir(exist_ok=True);out=dest/'prepared-metadata-v1.json';assert not out.exists()
add={lang:{s['id']:s['title'] for s in read(R/f'script/additions.{lang}.json')['scenes']} for lang in ['ko','en']}
english=['Overview: follow the target with less screen turning','Does aiming need to turn the whole view?','Visible movement and bodily sensations','Aiming can move against a stable background','Separate control from added motion','Repositioning and tracking a surface','Options that change one thing at a time','After looking away, how do we find the target again?','When a game mechanic changes orientation','Is slower movement always comfortable?','Does the task target remain readable?','Make choices discoverable and reversible','Read the same task from different positions','Design the choices and responsibilities first']
base={s['id']:title for s,title in zip([s for s in plan['scenes'] if s['retainedBaseline']],english)};assert len(base)==14
chapters=[]
for i,s in enumerate(plan['scenes']):
 sec=0 if i==0 else s['startFrame']//60
 chapters.append(dict(scene=s['id'],startSeconds=sec,exactStartFrame=s['startFrame'],titleKo=s.get('title') or add['ko'][s['id']],titleEn=base.get(s['id']) or add['en'][s['id']]))
chapters[0]['titleKo']='전체 안내: 목표를 따라가며 화면 움직임을 나누기'
chapters.append(dict(scene='membership',startSeconds=plan['bodyEnd']//60,exactStartFrame=plan['bodyEnd'],titleKo='멤버쉽 후원 감사와 프로그래밍 과외',titleEn='Membership thanks and programming coaching'))
assert all(b['startSeconds']-a['startSeconds']>=10 for a,b in zip(chapters,chapters[1:]))
ko="""게임의 목표를 따라가면서도 화면은 덜 돌릴 수 있을까요? 청소 게임의 조준과 시점, 퍼즐에서 방향이 바뀐 뒤 목표를 찾는 단서를 차례로 살펴보고, 카메라 설정과 되돌리기 기능의 설계로 연결합니다.

파워워시 시뮬레이터의 에임 모드 개발 시연, 탈로스 프린서플2의 방향 단서, 포털2의 큐브·장치 조작, 하프라이프 알릭스의 목적지 선택과 도착 후 손 조작을 비교합니다. 게임이 바뀔 때 필요한 규칙과 관찰할 대상을 먼저 설명하고, 무엇을 조작하는지·화면의 무엇이 움직이는지·움직인 뒤 어떤 단서가 남는지를 함께 살펴봅니다.

빨간선과 역할별 색 표식으로 실제 물줄기·큐브·목적지·주변 단서를 짚습니다. 이 표식은 화면에서 보이는 관계를 설명하며 게임 엔진의 실측 좌표가 아닙니다. 필요한 방향 전환과 부가 연출을 구분하고, 설정의 의미·현재 방향·목표를 알아보기 쉽게 설계하는 방법을 설명합니다. 개발 당시 자료와 설명용 제안을 구분하며 개인에게 같은 결과를 약속하지 않습니다."""
en="""Can we follow a game's target while turning the whole view less? We examine aiming and viewing in a cleaning game, then cues for finding a target after the view changes. These observations lead to camera choices and a way to restore the original settings.

We compare the PowerWash Simulator Aim Mode development demonstration, orientation cues in The Talos Principle 2, cube and device manipulation in Portal 2, and destination selection followed by hand interaction in Half-Life: Alyx. Each example introduces the necessary rules and visible objects before asking what we control, what moves on screen, and which cues remain afterward.

Red lines and role-colored markers identify the spray, cube, destination and surroundings in actual gameplay. They explain visible screen relationships, not measured game-engine coordinates. The diagrams separate necessary changes in viewing direction from added presentation, and show how to make settings, targets and current orientation understandable. Development-era footage and proposed interfaces are labelled separately. Individual responses can differ."""
titles=dict(ko='게임 멀미와 카메라 설계: 화면 움직임을 선택하게 만들기',en='Camera Comfort in Games: Giving Players Control over Motion');descriptions={}
for lang,intro,label,key in [('ko',ko,'챕터','titleKo'),('en',en,'Chapters','titleEn')]:
 old=(OLD/f'publishing/upload-description.{lang}.txt').read_text('utf-8-sig');footer='🎮'+old.split('🎮',1)[1]
 lines=[f"{v['startSeconds']//60:02d}:{v['startSeconds']%60:02d} {v[key]}" for v in chapters]
 text=intro+'\n\n'+label+'\n'+'\n'.join(lines)+'\n\n'+footer
 assert defaults['coaching']['url'] in text and defaults['membershipUrl'] in text and 'https://discord.gg/wZuqe7fqkR' in text and len(text)<5000
 target=dest/f'upload-description.{lang}.txt';assert not target.exists();target.write_text(text,'utf-8');descriptions[lang]=dict(path=target.relative_to(ROOT).as_posix(),sha256=sha(target),characters=len(text))
comment='화면 움직임을 줄이는 선택을 만들 때도 게임의 작업과 방향 단서가 남아야 합니다. 네 게임의 비교를 바탕으로 카메라·조준을 직접 설계하고 구현하는 방법을 함께 배우고 싶다면 프로그래밍 과외를 확인해 주세요.\n'+defaults['coaching']['url']
p=dest/'pinned-comment.ko.txt';assert not p.exists();p.write_text(comment+'\n','utf-8')
out.write_text(json.dumps(dict(preparedAt=datetime.now(timezone.utc).isoformat(),actualVideoId=None,status='local-draft-before-final-video-QA',titles=titles,descriptions=descriptions,chapters=chapters,chapterCount=18,planSha256=sha(R/'measured-current17-plan-v2.json'),mixAacSha256=mix['mixAacSha256'],channelFooterPreserved=True,publicSourceCreditListIncluded=False,pinnedComment=dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),status='pending-video-publication',posted=False),uploaded=False,savedOnPlatform=False,fullSettingsVerified=False,currentMixedAudioApproved=False,allFinalPixelsApproved=False,scheduleVerified=False,obsoleteDeleted=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(preparedOnly=True,chapters=18,descriptions=descriptions,actualVideoId=None,platformMutations=0)))

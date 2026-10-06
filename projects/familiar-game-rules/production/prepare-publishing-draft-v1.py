"""Prepared metadata only. Never creates actual platform receipt or video ID."""
from final_cpu_common import *
p=read(BASE.parent/'project.json');chap=read(BASE.parent/'planning/chapter-plan.json');plan=read(FINAL/'plan.json')
dest=BASE.parent/'publishing';dest.mkdir(exist_ok=True)
en=['Overview: familiar controls and new decisions','Familiar view, new actions','Start with familiar conventions','Kicking and directional relationships','Remapping action assignments','Separate umbrella actions from movement','Compare functions when devices change','Separate movement direction and aiming','Alternative input changes available choices','Check functions across connected actions','Design familiar conventions and new decisions together']
chapters=[]
for row,title in zip(chap['chapters'],en):
    t=0 if row['id']=='01' else min(x['startFrame'] for x in plan['pieces'] if x['logicalScene']==row['id'])/60
    sec=int(t);chapters.append(dict(id=row['id'],startFrame=round(t*60),seconds=t,time=f'{sec//60:02}:{sec%60:02}',ko=row['title'],en=title))
sec=plan['membership']['startFrame']//60;chapters.append(dict(id='membership',startFrame=22970,seconds=22970/60,time=f'{sec//60:02}:{sec%60:02}',ko='멤버쉽 감사 및 프로그래밍 과외 안내',en='Membership thanks and programming coaching'))
ko='익숙한 조작을 유지하면서 새로운 행동을 더하려면 무엇을 나누어 봐야 할까요? 앵거 풋, 건브렐라, 마이 프렌드 페드로의 실제 플레이에서 이동·조준·실행의 관계를 관찰합니다.\n\n버튼 재배치와 입력 장치 변경을 구분하고, 동시 행동·상황별 안내·대상 선택의 범위를 자신의 설계에서 점검하는 방법을 설명합니다. 도식의 대체 입력은 우리의 설계 비교이며, 게임의 실제 설정이나 포팅 결과를 증명하는 장면이 아닙니다.\n\n챕터\n'+'\n'.join(x['time']+' '+x['ko'] for x in chapters)
english='What should you separate when adding new actions to familiar controls? Observe movement, aiming and execution in actual gameplay from Anger Foot, Gunbrella and My Friend Pedro.\n\nWe distinguish button remapping from changing input devices, then examine simultaneous actions, contextual prompts and the range of target choices. Alternative input diagrams are our design comparisons, rather than evidence of these games\' settings or porting results.\n\nChapters\n'+'\n'.join(x['time']+' '+x['en'] for x in chapters)
comment='익숙한 버튼 배치만 따라 하기보다 이동·조준·실행이 어떻게 연결되는지 자신의 코드에서 확인해보세요. 직접 구현한 코드와 막힌 지점을 바탕으로 피드백을 받고 싶다면 얌얌코딩 프로그래밍 코칭·과외 안내를 확인해보세요.\n\n▶ 프로그래밍 코칭·과외\n'+read(ROOT/'shared/publishing/youtube-defaults.json')['coaching']['url']+'\n'
(dest/'pinned-comment.ko.txt').write_text(comment,'utf-8')
write(dest/'publishing-prepared-v1.json',dict(preparedAt=now(),status='prepared-only-not-uploaded',planSha256=sha(FINAL/'plan.json'),frames=23570,seconds=23570/60,chapters=chapters,metadata=dict(title=p['titles']['ko'],descriptionBody=ko,privacyStatus='private',defaultLanguage='ko'),englishMetadata=dict(title=p['titles']['en'],descriptionBody=english),actualVideoId=None,receipt=None,uploaded=False,thumbnailSaved=False,fullSettingsVerified=False,pinnedCommentStatus='pending-video-publication',stopAfterCurrent=STOP))
print(json.dumps(dict(preparedOnly=True,chapters=len(chapters),actualVideoId=None,uploaded=False)))

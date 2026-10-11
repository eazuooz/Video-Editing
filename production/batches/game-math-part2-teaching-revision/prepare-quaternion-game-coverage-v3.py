"""Draft four distinct narrated-game mappings; no final coverage approval."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
candidates=read(R/'candidate-comparison.json')['selectedForLocalDraft']
newgames={c['game']:c for c in candidates};baseline=read(R/'baseline.json')
descriptions={
 'Trailmakers':dict(before='Aircraft on runway; identify nose and two wing ends.',action='Takeoff, bank, changing observed body directions with a moving following camera.',after='Aircraft continues traveling while its wings approach level.',prerequisite='Read the red nose/front direction and blue wing direction separately. Screen projection and camera movement are not measured world angles.',common='Position and orientation are distinct; rotate all directions of the same object consistently.',difference='Aircraft front and wing reveal two body directions instead of relying on a skier silhouette.'),
 'Space Engineers':dict(before='Asymmetric component appears in a green placement-preview box over a floor grid.',action='The preview is turned sideways/upright; later placement is a separate action.',after='An actually placed upright component remains visible; inspect its side faces too.',prerequisite='The movable preview is a part being oriented before placement. An upright long axis alone does not determine full3D orientation.',common='Compare current and target orientation; exact inverse/difference is calculated in the defined model.',difference='A building part changes direction independently of travel; never claim the filmed keystrokes are a measured inverse quaternion.'),
 'Besiege':dict(before='Orange highlighted cannon subset beside unselected machine pieces; identify the subset before the transformation.',action='Rotation manipulator changes the selected barrel directions together.',after='Selected directions have changed while adjacent unselected structures retain their pose; later translation is separately identified.',prerequisite='Highlight selects which machine parts receive the transformation; colored observed barrel lines are not measured game axes.',common='One rotation acts on every direction/vector of its selected rigid object, preserving lengths and mutual angles.',difference='The selected subset changes while surrounding references remain; translate manipulator is a separate operation.')
}
for e in baseline['episodes']:
 P=ROOT/'projects'/e['newSlug'];lesson=read(P/'production/lesson.json');old=read(R/'baseline'/e['slug']/'production/lesson.json')['scenes'];oldids={s['id'] for s in old}
 assert [s for s in lesson['scenes'] if s['id'] in oldids]==old
 cuts=read(ROOT/f'projects/{e["slug"]}/sources/gameplay-cuts.json')['cuts']
 riders=[]
 for c in cuts:
  segments=c.get('segments') or c.get('sourceSegments') or [c]
  riders.append(dict(scene=c['scene'],sourceId=c.get('sourceId'),sourceFile=c.get('sourceFile'),actualIntervals=[[seg['in'],seg['in']+seg.get('seconds',seg.get('duration',seg.get('maxSeconds')))] for seg in segments],preservedOriginalEncodedClip=True))
 games=[dict(gameId='riders-republic',gameTitle='Riders Republic',centralClaim='Distinguish body/ski direction and orientation changes from travel and camera motion; read the following exact model calculation.',prerequisites='Observe skier/body and direction before the turn; the following camera is not a fixed world reference.',beforeActionAfter='Retained ski/traversal action with the originally narrated orientation observations; retain every approved cut and narration.',sourceRecords=riders,sourceRights='Retained source records/permissions, game-IP and human review retain their actual pending state.',comparisonGame='Trailmakers',commonPrinciple='Position and orientation are different states.',meaningfulDifference='A skier body versus an aircraft with a clearly visible nose and wings.',footageAdopted=True,narratedExample=True,normalSpeedPlaybackReviewed='Retained historical review; new full episode review pending',finalMovingPixelsReviewed=False,captionAndUiClearanceReviewed=False,mixedAudioReviewed=False)]
 for name,prefix in [('Trailmakers','10'),('Space Engineers','20'),('Besiege','30')]:
  actual_id=('QF' if e['newSlug'].endswith('foundations-v3') else 'QC')+prefix
  s=next(x for x in lesson['scenes'] if x['id']==actual_id);c=newgames[name];description=descriptions[name]
  explanation_id=actual_id[:-1]+'1';idx=next(i for i,x in enumerate(lesson['scenes']) if x['id']==actual_id)
  games.append(dict(gameId=name.lower().replace(' ','-'),gameTitle=name,centralClaim=description['common'],prerequisites=description['prerequisite'],before=description['before'],action=description['action'],after=description['after'],sourceUrl='https://www.youtube.com/watch?v='+c['sourceId'].removeprefix(name.lower().replace(' ','-')+'-'),primarySource=c['primarySource'],sourceRights=c['rights'],sourceSha256=c['sourceSha256'],maximumNativeIntervals=s['intervals'],sourceSegments=s['sourceSegments'],actualScene=actual_id,followedByExplanation=explanation_id,bodySceneIndex=idx,canonicalNarration=s['ko'],comparisonGame='Riders Republic' if name!='Besiege' else 'Trailmakers',commonPrinciple=description['common'],meaningfulDifference=description['difference'],sourceConditionChoicePending=name=='Besiege',footageAdopted='local draft only',narratedExample=False,narratedExamplePlanned=True,normalSpeedPlaybackReviewed=True,finalMovingPixelsReviewed=False,captionAndUiClearanceReviewed=False,mixedAudioReviewed=False,editableAnnotationTrack=s['annotation']['trackFile'],currentTrackSha256=sha(ROOT/s['annotation']['trackFile'])))
 write(P/'planning/game-example-coverage.json',dict(minimumDistinctGames=4,distinctPlannedExistingGames=4,centralViewerQuestion=('How does a quaternion change an object direction, and what does its inverse actually undo?' if 'foundations' in e['newSlug'] else 'How do quaternion order, current-to-target difference and vector rotation produce visible results?'),games=games,all80OriginalScenesAndPcmPreserved=True,wholeEpisodeTransferApproval=False,finalRatio='.4 actual/.6 explanation; measured plan required',musicAndSourceAudio=False,finalMixedListeningAndPublishing='pending'))
 lines=['# 기존 설명을 보존하는 네 게임 비교','',f'이 수정본은 {e["slug"]}의 모든 장면·수식·음성을 보존합니다. 새 비공개 업로드와 예약은 아직 없습니다.','', '게임 사례: 라이더스 리퍼블릭, 트레일메이커스, 스페이스 엔지니어스, 비시지. 비시지는 필수 출처 링크 선택이 미완료이므로 외부 업로드를 보류합니다.','', '본문 실제40/설명60, BGM·원본 소리 없음, 기존 흰색 Manim·고정 하단 자막을 유지합니다.','', '실제 본편 순서의 추가 위치:']
 for i,s in enumerate(lesson['scenes']):
  if s['id'] not in oldids:lines.append(f'- {lesson["scenes"][i-1]["id"]} 다음 {s["id"]}: {s["title"]} ({s["kind"]})')
 lines+=['','게임별 원본 구간·전/행동/후·전제·공통 원리와 차이는 game-example-coverage.json에 기록했습니다. 후보/무음 재생은 최종 녹음·자막·연속 렌더 승인과 구분합니다.']
 (P/'planning/outline.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
 print('Four-game draft mapping; actual chronological insertion points recorded',e['newSlug'])

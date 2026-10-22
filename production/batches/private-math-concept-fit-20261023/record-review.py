"""Record the agent's direct 50-sheet/556-frame review, not an automatic QA pass."""
from pathlib import Path
import collections, datetime, json
R=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
defaults={
 'M04':('replace','비행·캐릭터 이동·추적 카메라가 동시에 변해 물체의 회전만 구별하기 어렵다.','제자리에서 선택 물체를 회전·배치하는 실제 건축/조립 조작과 고정 카메라의 축 비교'),
 'M05':('replace','주행·활강 장면에서 축·반각·단위 노름·역원은 관찰할 수 없다.','정지한 조립 부품의 자세 변화와 동일 물체의 검증된 수학 구현'),
 'M06':('replace','라이더와 카메라가 함께 움직여 합성 순서·목표 자세·좌표 기준의 구별이 흐려진다.','고정 물체의 방향 맞추기, 두 순서 비교, 실제 계산한 회전값'),
 'M07':('replace','자동차/스케이트 이동이 회전 보간 경로와 각속도 차이를 직접 보여주지 않는다.','위치를 고정한 물체의 두 자세 사이 회전과 같은 끝점의 보간 A/B'),
 'M08':('replace','스케이트 동작·주행은 atan/표현 변환/왕복 변환의 결과를 검증하지 못한다.','같은 조립 물체의 자세를 유지하며 표현만 바꾸는 계산 화면'),
 'M09':('replace-or-recut','비슷한 갈고리 이동 장면이 반복되고 직선의 매개변수와 수직선 성질은 화면에서 보이지 않는다.','끝점이 분명한 연결 조작을 짧게 관찰하고 동일 선분의 계산으로 연결'),
 'M10':('replace','전투·폭발·마을 이동은 경계 상자나 회전 후의 범위를 직접 보여주지 않는다.','긴 물체를 제자리에서 돌리고 배치하며 AABB/OBB를 구별하는 비교'),
 'M11':('replace','이동·발사·갈고리 동작이 평면과 거리의 관계를 가린다.','고정된 바닥/경사판 위 물체와 수선·부호 있는 거리의 동시 설명'),
 'M12':('replace','일반 플레이에 삼각형 가중치·퇴화·속성 보간이 보이지 않고 같은 동작이 반복된다.','실제 삼각형 표면을 짧게 관찰한 뒤 같은 모양 위 점 이동과 가중치 계산'),
 'M13':('replace','목적별 중심과 경계를 설명하지만 전투/지형 이동이 계산 대상과 맞지 않는다.','배치 중인 타일/건물/윤곽에 중심·경계·빈 공간을 직접 표시'),
 'M14':('replace','동굴 통과나 공장 운반은 다각형의 삼각형 분할을 실행하는 장면이 아니다.','실제 편집한 경계와 구멍을 보존하며 분할을 실행하는 설명'),
 'M15':('recut','해당 빛 현상은 일부 보이지만 메뉴/이동/다른 장소가 길게 섞인다.','관련 표면과 광원·가림·재질의 전후만 선택하고 통제된 계산에 연결'),
 'M16':('replace-or-recut','건물 형상과 시점이 함께 바뀌어 카메라 한 변수의 효과를 비교하기 어렵다.','완성된 고정 건물/물체에서 회전·이동·시야각을 하나씩 바꾸는 화면'),
 'M17':('replace','건물 추가·레이저 퍼즐이 섞여 한 고정점의 좌표 변환을 따라가기 어렵다.','정지한 한 물체의 동일 점을 월드→뷰→클립→픽셀로 추적'),
 'M18':('replace','반복적인 건물 배치 화면은 깊이·w·원근 보정 UV를 보여주지 못한다.','경사진 동일 격자 표면과 실제 계산한 깊이/w/UV A/B'),
 'M19':('replace-or-recut','옥상 주행·전투·벽 무늬가 길게 이어져 메시·면/정점 법선의 대상이 불명확하다.','정지한 식별 가능한 모델의 윤곽과 실제 삼각형/법선 구현 비교'),
 'M20':('replace','반복되는 전투·옥상 이동은 법선 변환과 UV 주소의 차이를 보여주지 않는다.','고정 모델에서 크기·법선·텍스처 주소를 각각 바꾸고 차이를 표시'),
}
overrides={
 'M05/QF10':('replace','비행기 이륙·뱅크는 보이나 이동과 카메라가 함께 변한다.','같은 게임의 조립 화면에서 정지 부품 회전'),
 'M05/QF30':('retain-recut','선택한 주황 통 묶음만 회전하고 주변 부품은 고정되어 있어 직접적인 회전 예시다.','선택 영역·회전 중심·고정 기준을 표시; 동일 컷 장시간 반복 금지'),
 'M05/QF20':('retain-recut','고정 격자 위 배치 미리보기 부품의 세운/눕힌 자세가 바뀐다.','서로 다른 자세와 배치 목표 표시; 녹화자/게임 권리 확인 후 채택'),
 'M06/QC10':('replace','M05와 같은 비행 예시가 반복되고 조립 시 자세 비교가 아니다.','별도의 정지 부품 목표 맞추기 조작'),
 'M06/QC20':('replace-or-recut','물체 자세는 명확하나 M05의 동일 짧은 컷을 다시 사용한다.','새 목표에 방향을 맞추는 다른 조작 또는 짧고 명시적인 복습'),
 'M06/QC30':('replace-or-recut','M05의 통 회전 컷과 중복된다.','벡터 방향 설명에 필요한 다른 부품/다른 동작'),
 'M09/02':('retain-recut','손과 바위의 연결선이 보여 시작점·끝점·방향을 설명할 수 있다.','보이는 두 끝점을 따라가는 표식; 가림 시 숨김'),
 'M09/LG01':('retain-recut','큐브에서 수신기로 이어진 레이저와 문 반응이 직접 보인다.','레이저 선분과 도착점을 짧게 추적; 승인된 소스 해상도 범위 재확인'),
 'M10/LG05':('recut','들고 있는 큐브의 형태는 명확하지만 장면 전환과 다른 퍼즐이 섞인다.','큐브를 놓는 전후만 관찰하고 계산 경계는 자체 구현이라고 표시'),
 'M11/PG01':('recut','바닥 위 튀어 오르고 내려오는 동작은 높이/평면 관계에 적합하다.','첫 유의미한 반동만 사용하고 뒤 발사 장면은 제거'),
 'M11/PG02':('recut','경사 패널이 펼쳐지며 표면 방향이 바뀐다.','패널 전개 전후에 수선과 면을 표시하고 무관한 컷 제거'),
 'M13/02':('retain-recut','육각 타일의 배치·회전과 윤곽이 명확하다.','해당 타일의 중심과 외곽에 표식'),
 'M13/QG01':('retain-recut','건물을 직접 옮기고 회전하며 높이를 바꾸는 동작이 보인다.','한 변수씩 회전 중심·윤곽 표시'),
 'M13/QG02':('retain-recut','벽에 아치가 생겨 경계와 열린 공간이 직접 드러난다.','구멍 경계와 벽 영역을 나눠 표시'),
 'M13/08':('recut','동굴의 오목한 윤곽은 개념과 맞지만 화면이 어둡고 반복된다.','잘 보이는 단일 짧은 윤곽 관찰로 제한'),
 'M13/11':('retain-recut','이어진 타일의 외곽과 빈 곳이 관찰된다.','동일 맵의 연속 배치 전후를 유지'),
 'M14/QG04':('recut','호수를 만들며 육지 안 빈 공간을 만드는 조작은 적합하다.','고정 시점의 호수 생성만 남기고 뒤 동굴 반복 컷 제거'),
 'M14/QG06':('replace','원 모양 분류/공장 운반은 삼각형 분할의 증거가 아니며 제목 카드까지 포함된다.','선택한 다각형에서 실제 분할을 실행하는 자체 구현'),
 'M14/QG09':('retain-recut','타일 추가·되돌리기로 외곽이 바뀌는 전후가 명확하다.','경계 변경을 따라가는 선'),
 'M14/21':('recut','타일 외곽은 적절하지만 다른 맵의 반복은 요약에 불필요하다.','한 배치 전후로 경계·구멍·분할 결론 연결'),
 'M15/02':('recut','바위와 인물의 앞뒤 가림이 보인다.','가리는 경계를 짧게 따라 표시'),
 'M15/05':('retain-recut','벽의 구멍과 흐린 유리를 통해 보이는 모습이 구별된다.','구멍/투과 영역을 각각 표시하여 실제 관찰과 계산 구분'),
 'M15/11':('replace','망원경/이동 장면에는 RGB와 스펙트럼 관계가 직접 보이지 않는다.','동일 재질에 다른 광원을 비추는 실제 구현과 스펙트럼 도식'),
 'M15/17':('recut','조명 설치는 맞는 예시지만 뒤 수중 장면이 무관하다.','설치 전·동작·설치 후 밝아진 방이 모두 보이는 구간 확보'),
 'M16/02':('retain-recut','분할 화면의 두 플레이어 시점이 동시에 보인다.','각 출력 창과 해당 카메라를 연결'),
 'M16/11':('recut','분할 화면에서 거리 차이를 관찰할 수 있으나 시야각 수치를 추정할 수 없다.','거리 관찰만 짧게 사용하고 고정 조건의 시야각 비교는 자체 구현'),
 'M17/02':('recut','카메라가 움직일 때 기둥의 화면 위치가 바뀌어 고정점 추적에 적합하다.','기둥 하나를 연속 추적하고 다른 물체로 대상 변경 금지'),
 'M17/11':('recut','큐브 배치와 시점 이동은 구별할 수 있지만 레이저/문 퍼즐이 길게 섞인다.','물체 이동/카메라 이동의 차이만 보이는 연속 구간'),
 'M19/02':('recut','옥상 표면을 볼 수 있으나 장식 선을 메시 모서리로 단정할 수 없다.','정지한 옥상 관찰 뒤 실제 메시 구현을 나란히 비교'),
 'M19/06':('recut','벽 무늬와 실제 메시 구분에는 유용하나 반복이 길다.','한 번의 짧은 표면 관찰로 제한'),
 'M19/10':('retain-recut','휘어진 난간의 윤곽을 볼 수 있다.','같은 난간 윤곽에서 곡면 근사의 필요성을 연결'),
 'M19/11':('recut','노란 벽의 구멍과 모서리가 보인다.','이 한 구간만 실제 형상 관찰로 사용하고 법선 내부값은 구현으로 설명'),
}
d=read(B/'scene-audit.json')
for s in d['scenes']:
 key=s['episode']+'/'+s['scene']
 if not s.get('samples'):
  s.update(decision='recover-original-before-review',actualPixelReview='unavailable-original-master',reviewReason='원래 15:03 마스터와 음성을 아직 복원하지 못함. 이후 25:04/34분판으로 대체하지 않음.')
  continue
 decision,reason,target=overrides.get(key,defaults[s['episode']])
 s.update(decision=decision,reviewReason=reason,replacementGoal=target,
          actualPixelReview='four-distributed-frames-directly-reviewed',sampleStatus='sampled-frames-reviewed-moving-review-pending',
          reviewEvidence={'reviewedAt':now,'kind':'agent-direct-pixel-inspection','sampleCount':4,'narrationCompared':True,'entireMovingIntervalReviewed':False,'finalApproval':False},
          movingReview='required-after-selection',replacement=None)
counts=collections.Counter(s['decision'] for s in d['scenes'])
reuse=collections.defaultdict(list)
for s in d['scenes']:
 for p in s.get('currentParts',[]): reuse[p['source']].append({'episode':s['episode'],'scene':s['scene'],'sourceIn':p.get('sourceIn'),'seconds':p.get('seconds')})
d.update(updatedAt=now,currentSourceReuse=[{'source':k,'uses':v} for k,v in reuse.items()],reviewSummary={'sceneCount':len(d['scenes']),'sampledScenesReviewed':139,'framesReviewed':556,'sheetsReviewed':50,'decisions':dict(counts),'finalReady':0,'movingQA':'pending; sampled evidence is an initial editorial audit only'})
save(B/'scene-audit.json',d)
c=read(B/'checkpoint.json');c.update(updatedAt=now,status='replacement-source-selection',auditSummary=d['reviewSummary'],nextAction='Verify stationary object-manipulation footage and rights; recover original M03 audio; edit source-matched narration only, then render separately from existing masters.')
for e in c['entries']:
 e['status']='original-audio-recovery-required' if e['id']=='M03-original' else 'sampled-scene-audit-complete-replacement-selection'
c['blocked']=[{'id':'M03-original','stage':'original-audio-recovery','reason':'15:03 original master/PCM not local; original private upload is identified, recovery is being attempted.','otherEpisodesMayContinue':True}]
save(B/'checkpoint.json',c)
print(json.dumps(d['reviewSummary'],ensure_ascii=False))

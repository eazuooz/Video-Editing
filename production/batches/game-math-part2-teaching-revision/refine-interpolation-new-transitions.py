"""Remove repetition only from unrecorded additions; original material is exact."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-interpolation-teaching-additions-v2'
assert not any((ROOT/f'shared/output/narration/{slug}').rglob('*.wav')),'Do not change a recorded script'
rows={
 'IF01':('앞 편에서는 시작에서 목표까지의 회전 차이를 구했습니다. 이번에는 그 회전의 중간 자세를 하나씩 만들겠습니다.','The previous episode found the rotation difference from the starting to the target orientation. We now construct intermediate orientations along that rotation.'),
 'IB03':('차체가 방향을 바꾸는 모습을 보았으니, 시작과 끝의 네 숫자를 섞어 중간 자세를 만들면 될까요?','After observing the body changing direction, can we make intermediate poses by mixing the four numbers at the start and end?'),
 'IB07':('단위 호를 얻었지만 두 끝점이 겹치면 분모도 작아집니다. 같은 자세에 가까울 때를 먼저 처리하겠습니다.','We found the unit arc, but its denominator becomes small as the endpoints coincide. Handle nearly identical orientations first.'),
 'IB09':('카메라가 움직인 관찰을 검산할 수 있도록, 이번에는 카메라와 제트축을 고정하고 구십 도의 중간 자세를 계산합니다.','To verify the observation made with a moving camera, fix the camera and z axis and compute the intermediate poses of a ninety-degree turn.'),
 'IB12':('중간 자세의 계산을 실제 재생에 쓰려면, 티를 시간에 따라 얼마나 늘릴지도 정해야 합니다.','Using intermediate orientations in playback also requires deciding how t increases over time.'),
 'IB13':('시간에 맞춰 움직였더라도, 한 바퀴 더 돈 기록이 끝 자세에 남는지는 또 확인해야 합니다.','Even after choosing a timing rule, we must check whether the final orientation retains the record of an extra complete turn.'),
 'IB19':('각도에서 만든 세 축을 이제 쿼터니언에서도 만들고, 같은 방향 벡터가 나오는지 비교하겠습니다.','Now build the three axes from the quaternion as well as the angles, and compare the resulting direction vector.'),
 'IB24':('같은 자세를 옮겼으니, 축과 각도로 돌아갈 때 영도와 반 바퀴에 남는 정보도 확인하겠습니다.','Having converted the same pose, check what information remains at zero and half a turn when returning to axis and angle.'),
 'IB25':('예외 자세까지 처리한 식에 구십 도의 중간 자세를 넣어, 같은 방향 벡터가 나오는지 검산하겠습니다.','Insert the midpoint of a ninety-degree rotation into the formulas, including their exceptional cases, and verify the same direction vector.')
}
data={'scope':'Only unrecorded new-only transitions; no supplied scene, line, formula or audio changed','overrides':[{'id':k,'ko':[ko],'en':[en]} for k,(ko,en) in rows.items()],'omit':['IB16'],'omitReason':'IF03 already narrates and previews the coordinate/order convention immediately before original16. An extra identical bridge repeats its purpose.'}
(B/'interpolation-transition-refinement.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Unrecorded transition repetition refined; supplied content unchanged.')

"""Reuse saved Unity aircraft motions at the ORIGINAL upload's speech cues."""
import argparse,copy,json
from types import SimpleNamespace
import common as c
b=c.module('polish_existing_spatial',c.P/'production/revision-v2/render-spatial.py')
b.OUT=c.O/'unity';b.OUT.mkdir(parents=True,exist_ok=True)
MAPPING={
 '03':[2,0,0,0,6,3], '04':[0,1,2,3,4,5], '06':[0,1,2,3,1,1],
 '07':[0,1,2,3,4,5], '09':[0,1,2,3,4,5], '10':[0,1,2,3,4,5],
 '12':[0,1,2,3,4,5], '16':[0,('10',0),2,3,4,5], '18':[0,1,2,3,3,4], '19':[0,1,2,4,5,6],
 '21':[0,1,2,3,3,4], '22':[0,2,3,4,5,5]}
FORMULAS={
 '03':['h · p · b\n각도 + 축 + 순서','v_world = R v_body','heading: y\npitch: body x\nbank: body z','R = Ry(h) Rx(p) Rz(b)','다른 규약으로 옮길 때\n축 · 부호 · 곱의 순서 확인','오른손 엄지 → 양의 축\n감기는 손가락 → 양의 회전'],
 '04':['h: 0° → 45°','움직인 body x축\np: 0° → 30°','움직인 body z축\nb: 0° → 35°','내재적 회전\nIntrinsic rotation','+z → −y\n이름보다 축·부호를 확인','heading·pitch: 앞 방향\nbank: 앞 방향 주위 비틀림'],
 '06':['외재적 회전: 월드 축 고정','몸체 Y → X → Z = 고정 Z → X → Y','R = Ry(h) Rx(p) Rz(b)','v에 가까운 Rz부터 → Rx → Ry','yaw·pitch·roll: 사용한 좌표계와 축을 먼저 확인','같은 최종 행렬 · 서로 다른 축 기준의 설명'],
 '07':['시작 v = (0, 0, 1)','왼쪽: Rx(90°) v = (0, −1, 0)','왼쪽: Ry(90°) Rx(90°) v = (0, −1, 0)','오른쪽: Ry(90°) v = (1, 0, 0)','오른쪽: Rx(90°) Ry(90°) v = (1, 0, 0)','같은 두 각도여도 결과는 다름: Ry Rx ≠ Rx Ry'],
 '09':['세 각도는 사람이 읽고 편집하기 쉬움','0°와 360°: 같은 끝 자세','A = (0°, 135°, 0°)','B = (180°, 45°, 180°) → R(A) = R(B)','h,b ∈ (−180°,180°] · p ∈ [−90°,90°]','p = ±90°: b = 0을 고르는 추가 규칙'],
 '10':['피치 p → +90°','world y와 body z\n같은 직선에 놓임','world +y와 body +z\n양의 방향은 반대','두 손잡이가\n같은 축선에 영향','짐벌 락 (Gimbal lock)\n독립적인 변화 방향 감소','표현의 특이점\n물체는 여전히 회전 가능'],
 '12':['p = +90° → h − b','30° − 10° = 20°','(30°,90°,10°)와 (20°,90°,0°): 같은 자세','p = −90° → h + b','자세는 표현 가능 · 개별 각도는 크게 튈 수 있음','표현 하나를 골라도 경계의 불연속은 남음'],
 '16':['한 축의 짧은 차이 ≠ 가장 짧은 3D 회전','p ≈ 90°\n두 축선이 가까워짐','각 숫자를 같은 비율로 바꿔도 몸체 움직임은 다를 수 있음','같은 끝 자세를 표현해도 절반 지점의 자세는 다름','편집할 각도와 보간할 경로를 구분','쿼터니언에도 단위 길이·부호 규칙이 필요'],
 '18':['두 자세의 차이\n한 축 주위의 회전','축·각 표현 (Axis–angle)\n||n|| = 1 · 회전각 θ','n = (0,1,0) · θ = 90°\n+z → +x','몸에 붙은 세 축 전체가\n같이 회전','축 성분 3 + 각도 1\n축의 길이 제약 → 자유도 3','같은 축의 90° × 1/2\n= 같은 축의 45°'],
 '19':['회전벡터 (Rotation vector)\ne = θn','지수 사상 (Exponential map)\n회전벡터를 회전으로 변환','n = (0,1,0), θ = π/2\ne = (0,π/2,0) rad','θ = ||e||\n||e|| > 0이면 n = e / ||e||','e = 0 → 항등 자세\n0으로 나누지 않기','(−θ)(−n) = θn\n다른 중복은 여전히 남음'],
 '21':['+90°와 −270°: 같은 끝 자세','n × 90°와 (−n) × 270°','둘 다 360° 미만이어도 같은 자세 → 유일하지 않음','일반적으로 0° ≤ θ ≤ 180°를 선택','180°에서는 n과 −n 모두 같은 회전','θ = 0: 축이 달라도 항등 자세 · 회전벡터는 0'],
 '22':['유한한 회전의 합성 ≠ 회전벡터 성분 합','Rx(90°) 후 Ry(90°) ≠ Exp(eₓ + eᵧ)','벡터 합은 순서를 바꿔도 같지만 회전 합성은 다름','정확한 합성: 순서를 정한 행렬곱 또는 쿼터니언곱','성분 합은 작은 각도에서만 근사 가능','회전량과 순간적인 회전 변화율을 구분']}
ROLES={'06':['몸체 Y → X → Z','고정 Z → X → Y'], '07':['고정 X → Y','고정 Y → X'],
 '09':['표현 A','표현 B'], '12':['각도 묶음 A','같은 자세의 묶음 B'],
 '16':['목표 A: (0°,135°,0°)','목표 B: (180°,45°,180°)'],
 '21':['+n 축 · +90°','−n 축 · +270°'], '22':['X90° 후 Y90°','벡터 성분 합으로 한 회전']}
PAIRS=set(ROLES)

def overlay(scene,lesson,slots,out):
 sid=scene['id'];pair=sid in PAIRS;ov=b.Overlay();frames=scene['frames']
 if sid=='21':ov.white_band(0,frames,(0,0,1920,220));ov.white_band(0,frames,(0,735,1920,1080))
 if sid=='16':
  pass # The near-singularity reminder uses the same single-model stage.
 elif pair:
  ov.text(0,frames,b.wrap(lesson['title'],1660,54,True,2),120,42,54,bold=True)
  if sid!='21':
   for x,role in zip([160,1080],ROLES[sid]):ov.text(0,frames,role,x,162,38,bold=True)
 else:
  ov.text(0,frames,b.wrap(lesson['title'],730,54,True,2),1050,60,54,bold=True)
  ov.text(0,frames,'회전 모형 · 오른손 규칙',1050,190,30)
 previous=None
 for slot in slots:
  i=slot['lineIndex'];start,end=slot['startFrame'],slot['endFrame'];formula=FORMULAS[sid][i]
  pair=sid in PAIRS and not(sid=='16' and i==1)
  if sid=='16':
   if pair:
    ov.text(start,end,b.wrap(lesson['title'],1660,54,True,2),120,42,54,bold=True)
    for x,role in zip([160,1080],ROLES[sid]):ov.text(start,end,role,x,162,38,bold=True)
   else:
    ov.text(start,end,b.wrap(lesson['title'],730,54,True,2),1050,60,54,bold=True)
    ov.text(start,end,'회전 모형 · 오른손 규칙',1050,190,30)
  if sid=='21':
   labels=ROLES[sid] if i<3 else ['+n 축 · 180°','−n 축 · 180°'] if i<5 else ['+n 축 · 0°','−n 축 · 0°']
   for x,role in zip([160,1080],labels):ov.text(start,end,role,x,162,38,bold=True)
  if pair:ov.text(start,end,b.wrap(formula,1680,48,True,1),120,759,48,bold=True)
  else:
   ov.text(start,end,b.wrap(lesson['beats'][i],730,41,False,2),1050,280,41)
   ov.text(start,end,b.wrap(formula,730,49,True,3),1050,435,49,bold=True)
  states=[json.loads(x) for x in Path(slot['anchors']).read_text(encoding='utf8').splitlines()]
  assert len(states)==slot['captureFrames']
  previous=b.add_anchors(ov,slot,states,pair,previous)
  if sid=='16':ov.text(start,end,'world: 고정 축 / body: 몸체 축',120 if pair else 1050,824 if pair else 800,32)
 if sid!='16':ov.text(0,frames,'world: 고정 축 / body: 몸체 축',120 if pair else 1050,824 if pair else 800,32)
 path=out/f'{sid}-overlay.ass';ov.save(path);return path,len(ov.lines)

from pathlib import Path
def main():
 c.authorized();ap=argparse.ArgumentParser();ap.add_argument('--scene',action='append');args=ap.parse_args()
 old=c.read(c.P/'production/local/revision-v2/unity-spatial-placement.json')['placements']
 slots=[];records=[]
 for sid,mapping in MAPPING.items():
  s=c.SCENES[sid];lesson=c.LESSON[sid];assert len(mapping)==len(s['lineStarts'])==len(FORMULAS[sid])
  for i,j in enumerate(mapping):
   source_sid,source_index=j if isinstance(j,tuple) else (sid,j)
   src=next(x for x in old if x['sceneId']==source_sid and x['lineIndex']==source_index)
   start=round(s['lineStarts'][i]*60);end=round(s['lineStarts'][i+1]*60) if i+1<len(mapping) else s['frames']
   assert src['captureFrames']<=end-start,(sid,i,'original speech window too short; do not speed source motion')
   row={**src,'sceneId':sid,'lineIndex':i,'lineNumber':i+1,'startFrame':start,'endFrame':end,
        'startSeconds':start/60,'endSeconds':end/60,'narration':lesson['ko'][i],
        'holdFinalFrames':end-start-src['captureFrames'],'originalUnityScene':source_sid,'originalUnityLineIndex':source_index,
        'timing':'Original upload lineStarts; visible native action during existing speech; no added silence.'}
   slots.append(row)
 c.save(c.H/'unity-placement.json',{'revision':'private-baseline-visual-polish-v1','placements':slots,
  'renderers':'Existing Unity6000.6.0f1 native built-in captures; canonical editable scenes use URP17.6.',
  'sourceSceneDirectory':'unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/Scenes',
  'catalogConsulted':'shared/assets/unity-asset-library.json','reuseReason':'Original self-authored recognizable aircraft already matches body axes; library has no better matching aircraft. No vendor changes or duplicate capture.',
  'originalTimingSha256':c.sha(c.P/'production/timeline.json')})
 b.build_overlay=overlay
 for sid in MAPPING:
  if args.scene and sid not in args.scene:continue
  c.authorized()
  records.append(b.render(c.SCENES[sid],{**c.LESSON[sid],'polishCompositorSha256':c.sha(__file__)},slots,SimpleNamespace(force=False)))
  source=b.OUT/f'{sid}.mp4';destination=c.O/'clips'/f'{sid}.mp4';destination.parent.mkdir(exist_ok=True)
  import shutil;shutil.copy2(source,destination)
 c.save(c.O/'unity-render-report.json',{'reports':records,'narrationRewritten':False,'newTts':False})

if __name__=='__main__':main()

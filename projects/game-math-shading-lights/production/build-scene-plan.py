"""Bind every retained paragraph to editable visuals and speech anchors.

This is a preproduction plan, not permission to render unverified imagery.
Actual durations/stepTimes come from the final approved PCM alignment later.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib

PROJECT=Path(__file__).resolve().parents[1]
STAGING=PROJECT/'production/unity-staging'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
draft=load(PROJECT/'script/draft-narration.ko.json')['segments']
narration=load(PROJECT/'script/narration.ko.json')['scenes']
coverage=load(STAGING/'draft-scene-coverage.json')['beats']
footage={s['id']:s for s in load(PROJECT/'planning/footage-audit.json')['candidateSegments']}
terms={
 1:('Local Illumination','국소 조명','표면 한 점의 빛을 계산하는 규칙'),
 2:('Bidirectional Reflectance Distribution Function','양방향 반사 분포 함수 · BRDF','들어온 방향과 나가는 방향 사이의 반사'),
 3:('Direct Lighting','직접광','광원에서 표면으로 바로 도착한 빛'),
 5:('Lighting Components','조명 성분','발광 · 정반사 · 난반사 · 환경광'),
 6:('Component-wise Product','성분별 곱','R·G·B 같은 채널끼리 곱하기'),
 7:('Specular Reflection','정반사','보는 방향에 따라 달라지는 반짝임'),
 8:('Surface Normal','표면 법선','표면에 수직인 단위 방향 N'),
 9:('Reflection Vector','반사 벡터','입사 방향을 법선을 기준으로 반사'),
 11:('Phong Reflection Model','퐁 반사 모델','반사 방향 R과 보는 방향 V를 비교'),
 12:('Shininess Exponent','광택 지수','반짝임의 폭을 정하는 지수'),
 14:('Light Cookie / Gobo','광원 쿠키 · 고보','빛에 붙여 투영하는 무늬'),
 15:('Specular Strength and Shininess','정반사 세기 · 광택 지수','밝기와 반짝임의 폭을 따로 비교'),
 16:('Halfway Vector','하프웨이 벡터','L과 V 사이의 가운데 방향 H'),
 17:('Blinn–Phong Reflection','블린–퐁 정반사','법선 N과 하프웨이 H를 비교'),
 18:('Lambertian Reflection','램버트 난반사','입사각에 따라 달라지는 넓은 반사'),
 22:('Lambertian BRDF','램버트 BRDF','반사율 ρ를 π로 나눈 방향 함수'),
 24:('Ambient Lighting','환경광','간접광을 한 값으로 대신하는 근사'),
 26:('Emission','발광','표면 자체에서 나오는 빛의 성분'),
 29:('Light Visibility','광원 가시성','광원과 표면 사이를 가리는지 확인'),
 30:('Half Lambert','하프 램버트','어두운 쪽 형태를 살리는 응답 조절'),
 35:('Fresnel / Retroreflection','프레넬 효과 · 재귀반사','방향에 따라 달라지는 반사 규칙'),
 36:('Anisotropic Reflection','비등방성 반사','표면의 결 방향에 따라 달라지는 반사'),
 37:('Shading Frequency','셰이딩 계산 위치','면 · 정점 · 픽셀에서 계산한 결과 비교'),
 38:('Flat Shading','플랫 셰이딩','면을 대표하는 값으로 한 면을 칠하기'),
 39:('Gouraud Shading','구로 셰이딩','정점의 조명 색을 보간하기'),
 41:('Phong Shading','퐁 셰이딩','법선을 보간한 뒤 픽셀에서 계산하기'),
 46:('Coordinate Space','좌표 공간','비교하는 방향들의 기준을 일치시키기'),
 48:('Point Light / Omni Light','점 광원 · 전방향 광원','한 위치에서 모든 방향으로 빛을 보내기'),
 49:('Spot Light','스폿 광원','정해진 원뿔 안으로 빛을 보내기'),
 51:('Directional Light','방향성 광원','평행한 방향의 빛'),
 52:('Dirac Delta','디랙 델타','한 위치에 모인 유한한 전체 양'),
 53:('Inverse-square Falloff','역제곱 감쇠','거리 2배 → 같은 면적의 입사량 1/4'),
 54:('Radiant Flux / Irradiance','복사속 · 복사조도','전체 출력과 면적당 입사량'),
 55:('Radiance','복사휘도','표면의 면적·방향을 함께 고려한 양'),
 56:('Solid Angle','입체각','표면에서 본 광원이 차지하는 방향 범위'),
 58:('Linear Attenuation','선형 감쇠','안쪽·바깥쪽 거리 사이를 직선으로 줄이기'),
 60:('Doom 3 Light Volume','둠 3 광원 영향 영역','표면 조명이 영향을 주는 공간'),
 62:('Projective Texture Mapping','투영 텍스처 매핑','표면 위치를 빛의 무늬에 대응시키기'),
 63:('Orthographic Projection','직교 투영','같은 크기의 단면으로 나란히 투영'),
 65:('Perspective Projection','원근 투영','한 점에서 퍼지는 방향으로 투영'),
 69:('Baked Lighting','베이크 조명','변하지 않는 조명을 미리 계산해 저장'),
 70:('Lightmap / Atlas','라이트맵 · 아틀라스','표면 위치와 조명 텍셀을 연결'),
 71:('Baked Vertex Lighting','정점에 저장한 조명','정점 색에 계산 결과를 저장하고 보간'),
 72:('Directional Irradiance','방향별 복사조도','표면이 향하는 방향에 따른 입사량'),
 73:('Spherical Harmonics','구면 조화 함수 · SH','구면의 방향 분포를 기저의 합으로 압축'),
 74:('Baked Lighting: Static Configuration','베이크 조명의 고정 조건','물체를 옮겨도 저장된 그림자는 남음'),
 75:('Mixed Lighting','혼합 조명','실시간 직접광과 저장된 간접광의 결합'),
 76:('Light Probe','라이트 프로브','공간 여러 위치에 저장한 조명 표본'),
 77:('Diffuse / Specular Environment','난반사 · 정반사 환경 정보','표면 반사 성질에 맞게 다른 필터 사용'),
}
patches={
 1:{'variable':'specularStrength','from':0,'to':1},
 2:{'normalArrow':True,'lightArrow':True,'viewArrow':True},
 3:{'diagram':'geometry:directPaths'},
 4:{'diagram':'geometry:directPaths','showLamp':False},
 5:{'components':{'x':0,'y':0,'z':0,'w':1},'emission':{'r':.15,'g':.04,'b':.01,'a':1},'componentSteps':[{'x':0,'y':0,'z':0,'w':1},{'x':0,'y':1,'z':0,'w':0},{'x':1,'y':0,'z':0,'w':0},{'x':0,'y':0,'z':1,'w':0},{'x':1,'y':1,'z':1,'w':1}]},
 6:{'diagram':'math:rgb'},9:{'diagram':'geometry:reflectConstruction'},10:{'diagram':'math:reflect','normalArrow':True,'lightArrow':True,'reflectionArrow':True,'viewArrow':False,'aimAtSubject':False,'lightType':0,'lightEuler':{'x':53.1301024,'y':-90,'z':0}},
 12:{'diagram':'math:gloss'},13:{'materialMap':True},15:{'diagram':'specularGrid','normalArrow':False,'lightArrow':False,'showLamp':False},
 19:{'diagram':'geometry:cosineRays','lightType':0,'aimAtSubject':False,'lightEuler':{'x':90,'y':0,'z':0}},
 21:{'diagram':'math:diffuse','diffuse':{'r':.8,'g':.4,'b':.2,'a':1}},
 22:{'diagram':'math:lambert-brdf'},23:{'diagram':'math:lambert-brdf'},
 24:{'variable':'ambientStrength','from':0,'to':1,'diagram':'advanced:ambient-bounce'},
 27:{'components':{'x':0,'y':0,'z':0,'w':1},'emission':{'r':.6,'g':.3,'b':.1,'a':1}},
 28:{'emission':{'r':.1,'g':.025,'b':.01,'a':1},'componentSteps':[{'x':1,'y':0,'z':0,'w':0},{'x':1,'y':1,'z':0,'w':0},{'x':1,'y':1,'z':1,'w':0},{'x':1,'y':1,'z':1,'w':1}]},
 30:{'diagram':'math:half-lambert'},
 31:{'variable':'secondLightStrength','from':0,'to':1,'lightColor':{'r':.8,'g':.12,'b':.08,'a':1},'secondLightColor':{'r':.05,'g':.3,'b':.9,'a':1},'emission':{'r':.06,'g':.02,'b':0,'a':1}},
 32:{'diagram':'math:custom','explanationSteps':['계산할 픽셀 수','광원 수와 표면 반사 계산','정확도 · 처리할 양 · 제어성']},
 33:{'model':1,'halfArrow':True,'viewArrow':True},
 35:{'diagram':'advanced:fresnel-retro'},36:{'diagram':'advanced:anisotropy'},
 37:{'diagram':'shadingComparison','normalArrow':False,'lightArrow':False,'showLamp':False,'lightType':0},39:{'diagram':'math:gouraud'},
 40:{'diagram':'triangle-highlight','variable':'none','normalArrow':False,'lightArrow':False,'showLamp':False,'urpLit':False,'perspectiveCamera':False},42:{'diagram':'math:nonlinear'},
 43:{'materialMap':True,'diagram':'math:factor'},44:{'diagram':'math:factor'},
 45:{'shading':3,'materialMap':True,'secondLightStrength':1,'formula':'보간한 조명값 × 픽셀의 재질값 + 발광'},
 46:{'diagram':'math:spaces'},47:{'lightType':1,'diagram':'geometry:directPaths'},48:{'diagram':'math:point'},
 51:{'variable':'lightTranslationX','from':-1,'to':2,'aimAtSubject':False,'lightType':0,'diagram':''},
 53:{'diagram':'geometry:rangeShells'},54:{'diagram':'math:units'},
 55:{'variable':'cameraDistance','from':7,'to':12,'perspectiveCamera':True,'diagram':'','components':{'x':1,'y':0,'z':1,'w':0}},
 56:{'diagram':'geometry:solidAngle'},
 57:{'diagram':'math:custom','explanationSteps':['거리 r → 0: 1/r²가 커짐','멀리 가도 정확히 0은 아님','발광체 크기의 근사를 확인','가까운 값 제한 · 먼 범위 종료']},
 58:{'diagram':'math:falloff'},60:{'lightType':2,'volumeMode':2,'diagram':'geometry:volumeBounds'},
 61:{'diagram':'math:gobo-product'},62:{'diagram':'math:gobo-product'},
 63:{'diagram':'geometry:volumeBounds'},64:{'diagram':'math:uv'},65:{'diagram':'geometry:volumeBounds'},
 66:{'diagram':'geometry:volumeBounds'},67:{'diagram':'geometry:volumeBounds'},
 68:{'lightType':1,'volumeMode':1,'diagram':'geometry:volumeBounds'},
 69:{'diagram':'advanced:bake-paths'},
 70:{'urpLit':True,'bakeMode':'all','bakeAction':'','lightType':1,'range':8,'diagram':'surface:lightmap'},
 71:{'diagram':'surface:vertex','shading':4,'lightType':0,'normalArrow':False,'lightArrow':False},
 72:{'diagram':'math:radiometry'},
 73:{'diagram':'advanced:sh-sum'},77:{'diagram':'advanced:environment-filter'},
 74:{'urpLit':True,'bakeMode':'all','bakeAction':'moveOccluder','lightType':1,'range':8,'sourceKind':'Unity URP · 실제 베이크 결과'},
 75:{'urpLit':True,'bakeMode':'indirect','bakeAction':'switchOff','lightType':1,'range':8,'sourceKind':'Unity URP · 간접광 베이크 + 실시간 직접광'},
 76:{'urpLit':True,'bakeMode':'indirect','bakeAction':'walk','diagram':'','lightType':1,'range':8,'sourceKind':'Unity URP · 실제 라이트 프로브 보간'},
 78:{'diagram':'advanced:final-grid','normalArrow':False,'lightArrow':False,'showLamp':False},
}
anchors={
 5:['스스로 밝아','특정 방향에서','넓게 퍼져','환경광입니다','각각 계산한 뒤'],
 6:['세 값','광원의 색','같은 채널끼리','영점이','영점영이'],
 10:['법선이','내적은','두 배는','빼면','리플렉트 함수'],
 12:['같은 방향','영점팔','제곱하면','여덟 제곱','지수가 클수록'],
 15:['함께 비교','가로로','아래쪽','정반사 색이 영'],
 19:['정면으로','종이를 기울이면','작은 칸','법선과','지구에서도'],
 21:['흰빛의 세기','정면에서는','육십 도','영점사','절반'],
 22:['몇 퍼센트','로 나누기 파이','코사인 가중치','파이가','반사량'],
 28:['난반사가','정반사가','환경광이','발광이'],
 30:['내적에 영점오','제곱하는','내적이 영','영점이오','의도적으로'],
 31:['한 광원의','광원을 하나 더','빨간빛과 파란빛','한 번만','오류'],
 39:['꼭짓점에서','보간합니다','영점이','영점사예요','매끄러운'],
 42:['영과 일','평균 낸 뒤','영점이오','각각 제곱','영점오'],
 44:['영점이와 영점삼','각각 곱해','영점사','먼저 더한','영점팔을 곱해도'],
 48:['하나의 위치','표면의 위치','그 길이','방향을 얻고','범위'],
 54:['복사속','복사조도','거리의 제곱','같은 방향','사라진다는 뜻'],
 58:['안쪽 거리','바깥 거리','직선으로','사 미터','명확하게'],
 61:['좌표로','고보에서','감쇠 맵에서','영점사','그 지점'],
 64:['가로 길이','왼쪽 끝','중심의','오른쪽 끝','월드 좌표'],
}
game_map={0:'S01-headlamp-abstract',7:'S08-optional-forzavista-specular',18:'S02-matte-faces',27:'S06-brightbloom-emission-light',31:'S05-add-light',49:'S04-spot-sweep',60:'S07-doom3-projector'}
# These still need geometry/engine behavior beyond the staged general renderer.
remaining={78:'Supply four hash-verified finished same-scene body captures to the implemented final comparison; no placeholders accepted.'}
rows=[];current_term=('Local Illumination','국소 조명','표면과 광원이 함께 만드는 색')
for i,(source,speech,base) in enumerate(zip(draft,narration,coverage)):
    if i in terms:current_term=terms[i]
    cue={'id':f'm21-{i:03d}','section':source['section'],'termEnglish':current_term[0],'termKorean':current_term[1],'plainMeaning':current_term[2],
         'sourceKind':'우리 구현 · 국소 조명','duration':None,'normalArrow':False,'lightArrow':False,'cardSeconds':3 if i in terms else 0}
    cue.update(base['candidateCuePatch']);cue.update(patches.get(i,{}))
    row={'id':speech['id'],'sourceBeatId':source['id'],'speech':speech['lines'][0],
         'sourceParagraphs':source['sourceParagraphs'],'visibleTeachingPurpose':source['screenPlan'],
         'renderer':'Unity 6000.6.0f1 / URP 17.6.0 + Motion Canvas compositing','classification':'explanation',
         'cue':cue,'speechAnchorPhrases':anchors.get(i,[]),'timing':'actual PCM and clause alignment pending',
         'hold':0,'independentEditableSceneRequired':True,'layoutQa':'pending 1080p / 375px with final fixed captions',
         'status':'staged-code-needs-runtime-and-speech-timing','remainingImplementation':remaining.get(i)}
    if i in game_map:
        c=footage[game_map[i]]
        row['actualGamePart']={k:c[k] for k in ('id','sourceId','sourceIn','sourceOut','duration','teachingRole','annotationPlan','claimLimits')}
        row['actualGamePart'].update({'speed':1,'freezePadding':False,'loop':False,'cutToExplanation':'At concept handoff; keep useful native before/action/result; never stretch to fit longer calculation.'})
        row['classification']='actual-game-then-explanation' if i else 'actual-game-thesis-abstract'
        row['visibleTeachingPurpose']=c['teachingRole']+' → '+source['screenPlan'] if i else c['teachingRole']
        row['renderer']='Independent native gameplay with tracked editorial guides'+(' → Unity lesson scene' if i else '')
    rows.append(row)
assert len(rows)==79 and all(r['sourceParagraphs']==s['sourceParagraphs'] for r,s in zip(rows,draft))
save(PROJECT/'planning/scene-bindings.json',{'schemaVersion':1,'updatedAt':datetime.now(timezone.utc).isoformat(),
 'status':'complete-paragraph-mapping-runtime-and-listed-implementation-pending','sourceNarrationSha256':hashlib.sha256((PROJECT/'script/narration.ko.json').read_bytes()).hexdigest(),
 'actualNativeGameParts':len(game_map),'allBodyParagraphsRetained':True,'pendingImplementationBeatCount':len(remaining),'humanViewed':False,'scenes':rows})
plan=load(PROJECT/'planning/production-plan.json')
plan['sceneBindings']='planning/scene-bindings.json';plan['terminology']=[{'firstBeat':f'{i:03d}','english':v[0],'korean':v[1],'meaning':v[2]} for i,v in terms.items()]
plan['readthroughReview']='planning/readthrough-review.json';plan['sourceFigures']='research/figure-audit.json'
plan['sceneBindingsFinal']=False
save(PROJECT/'planning/production-plan.json',plan)
print(f'79 retained beats mapped; {len(game_map)} actual-game segments; {len(remaining)} implementation checks remain, no final approval asserted.')

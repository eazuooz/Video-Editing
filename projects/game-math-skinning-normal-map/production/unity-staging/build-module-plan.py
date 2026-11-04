from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;project=P.parent.parent
draft=json.loads((project/'script/draft-narration.ko.json').read_text(encoding='utf-8-sig'))
final=json.loads((project/'script/narration.ko.json').read_text(encoding='utf-8-sig'))
terms=[
('Actual Game Abstract','실제 게임 도입','실제 움직임에서 두 좌표 변환을 소개합니다'),
('Articulation','관절 구조','전체 이동과 관절별 움직임을 구분합니다'),
('Skeletal Animation','골격 애니메이션','본은 움직이는 좌표계입니다'),
('Skin Weights','스킨 가중치','각 본이 정점에 미치는 비율입니다'),
('Linear Blend Skinning','선형 블렌드 스키닝','본으로 옮긴 위치를 가중평균합니다'),
('Weighted Position','위치의 가중평균','가중치를 바꾸면 결과점이 옮겨집니다'),
('Skin Vertex Data','스키닝 정점 데이터','본 번호와 가중치, 기준 위치를 저장합니다'),
('Skinning Loop','스키닝 계산 순서','각 본의 기여를 더합니다'),
('Normal Transformation','법선 변환','방향에는 평행이동을 더하지 않습니다'),
('Bind Pose','바인드 포즈','메시와 골격을 연결한 기준 자세입니다'),
('Inverse Bind Matrix','바인드 역행렬','기준 정점을 먼저 본의 공간으로 옮깁니다'),
('Bind-to-Current Transform','기준에서 현재로','2 − 1 + 3 = 4를 확인합니다'),
('Matrix Blending','행렬 블렌딩','변환을 미리 합쳐 공통 계산을 줄입니다'),
('Linear Blend Limitation','선형 혼합의 한계','회전을 섞어도 순수 회전이 되지는 않습니다'),
('Deformation Validation','변형 검토','극단적인 자세에서 형태를 확인합니다'),
('Bump Mapping','범프 매핑','표면 방향의 변화로 요철을 표현합니다'),
('Normal Encoding','법선 인코딩','방향을 색 채널 숫자로 저장합니다'),
('Normal Data Pipeline','노멀 데이터 흐름','선형 데이터로 읽고 방향을 복원합니다'),
('Tangent-Space Reuse','접선 공간의 재사용','같은 무늬도 각 표면의 바깥을 향해야 합니다'),
('Tangent Frame','접선 공간 기저','T·B·N으로 표면의 기준축을 만듭니다'),
('Normal Decoding','노멀 디코딩','8비트 값을 복원하고 정규화합니다'),
('TBN Transformation','TBN 변환','각 성분에 해당 축을 곱해 더합니다'),
('Interpolated Frame','보간한 기저','곡면과 UV 배치에 따라 축이 달라집니다'),
('Coordinate-Space Agreement','좌표 공간 일치','내적하는 방향은 같은 공간에 있어야 합니다'),
('Tangent Handedness','접선 기저의 핸디드니스','외적으로 만든 축의 방향 부호를 저장합니다'),
('Triangle and UV Edges','삼각형과 UV의 변','두 공간에서 이동한 차이를 연결합니다'),
('Tangent Linear System','접선 연립방정식','변을 T와 B의 선형결합으로 씁니다'),
('UV Determinant','UV 행렬식','부호를 보존하며 역행렬을 구합니다'),
('Worked Tangent Basis','접선 기저 계산 예','같은 삼각형에 숫자를 대입합니다'),
('Signed Determinant','부호 있는 행렬식','거울 UV에서는 접선 방향이 뒤집힙니다'),
('Degenerate UV','퇴화한 UV','행렬식이 0이면 역행렬이 없습니다'),
('Tangent Accumulation','접선 누적','면의 접선과 비탄젠트를 정점에 모읍니다'),
('Gram–Schmidt Orthogonalization','그람–슈미트 직교화','법선 방향 성분을 빼고 정규화합니다'),
('Mirrored UV Seams','거울 UV 이음선','서로 다른 기저는 정점을 분리합니다'),
('Authoring to Runtime','제작 데이터에서 실행까지','미리 맞춘 약속으로 런타임을 단순하게 만듭니다'),
('Moving Coordinate Frames','움직이는 좌표계','큰 형태와 작은 요철을 같은 약속으로 옮깁니다')]
illustration={5,6,7,8,10,11,12,16,17,18,20,22,23,25,26,27,28,29,30,31,32,33,34}
shots=[]
for i,(segment,scene) in enumerate(zip(draft['segments'],final['scenes'])):
 assert segment['id']==scene['sourceBeatId']
 en,ko,meaning=terms[i]
 shots.append({'sourceBeatId':segment['id'],'sceneId':scene['id'],'sourceSection':scene['section'],'sourceScreenPlan':segment['screenPlan'],'correctionIds':segment.get('correctionIds',[]),'status':'independent-gameplay-parent-timeline-required' if i==0 else 'source-implemented-CPU-compiled-runtime-and-visual-QA-pending','renderer':'independent-gameplay' if i==0 else 'Unity','sourceKind':'actual-recording' if i==0 else 'illustration' if i in illustration else 'our-implementation','module':'SkinNormalTeachingStage.Evaluate' if i else None,'shot':{'beatId':segment['id'],'beatIndex':i,'englishTerm':en,'koreanTerm':ko,'meaning':meaning,'durationSeconds':0,'stepSeconds':[],'expandedTerm':True,'useObservedClip':False,'bendFrom':0,'bendTo':105},'scenePathPlanned':None if i==0 else 'Assets/Yamyam/M22/Scenes/'+scene['id']+'.unity','sceneSaved':False,'speechAndMotion':'Overlap; root must bind phase cue boundaries to approved speech. Normalized preview phases are not final timings.','formulas':segment.get('sourceFormulaBlocks',[])})
rig=json.loads((P/'rig-source-audit.json').read_text(encoding='utf8'))
data={'schemaVersion':1,'episodeId':'M22','scope':'CPU module/staging only; no Unity editor launched, shared project changed, GPU capture or final playback QA','readInputs':{str(project/'script/narration.ko.json'):hashlib.sha256((project/'script/narration.ko.json').read_bytes()).hexdigest(),str(project/'planning/source-audit.json'):hashlib.sha256((project/'planning/source-audit.json').read_bytes()).hexdigest()},'engine':{'editor':'6000.6.0f1','pipeline':'URP 17.6.0','finalResolution':[1920,1080],'fps':60},'assetRecord':{'catalogConsulted':'shared/assets/unity-asset-library.json','selectionReason':'The main imported catalog has no Knight entry; use the existing proven CC0 KayKit rig already used by AiCraftSampleBuilder. It includes recognisable articulated geometry, actual arm blend weights and finite motion clips.','assetPath':'Assets/ThirdParty/KayKitAdventurers/Knight.fbx','guid':rig['assetGuid'],'source':rig['source']['repository'],'commit':rig['source']['commit'],'license':'CC0','licenseEvidence':'unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers/LICENSE.txt','requiredCredits':False,'descriptionOptionalCredit':'KayKit Adventurers by Kay Lousberg (CC0)','verifiedSourceHash':rig['source']['files'][0]['sha256'],'boneCount':len(rig['boneNames']),'animationStackCount':len(rig['animationStacks']),'runtimeInspection':False,'reimportPolicy':'Only isolated copy may set ModelImporter.isReadable. Original FBX, materials, source .meta and shared Unity are unchanged. Keep copied binaries/Library/recordings local.'},'coordinateAndAccuracy':{'math':'Right-handed vectors and column-vector transforms J_current × B_bind^-1 × p_bind. Display maps (x,y,z) to Unity (x,y,-z).','unityProbe':'Actual weighted world point = sum w_i * (bone.localToWorldMatrix * mesh.bindposes[i]) * bindVertex. Uses all four imported influences; actual weights are not replaced with worked 60/40 numbers.','normalShader':'Independent XYZ data decoder and TBN directional-response shader. Not Unity Lit/PBR or actual game internals. Knight itself uses actual URP Lit.','normalMap':'Procedural analytic grooves and separately RGB(37,128,218) constant texture are generated as Texture2D(...linear:true). No artistic sRGB conversion.','normalNumeric':'Raw=(-.7098039216,.0039215686,.7098039216), normalized=(-.7071013853,.0039066375,.7071013853).','mirror':'Preserve signed UV determinant, then Gram–Schmidt and h=sign(dot(cross(N,T),B)). Split incompatible seam vertices.','units':'Sleeve numeric points are dimensionless teaching coordinates. No unverified game measurement.'},'entryPoints':{'cpuVerification':'python -X utf8 production/unity-staging/verify-source.py','readOnlyFbxInspection':'python -X utf8 production/unity-staging/inspect-knight.py','rootOnlyUnityCPUValidation':'SkinNormalSceneBuilder.ValidateRigOnly','rootOnlyBuild':'SkinNormalSceneBuilder.BuildStage(shot)','evaluate':'stage.Evaluate(cueSeconds) after durationSeconds/stepSeconds binding; EvaluateNormalized is preview-only','capture':'Root URP capture pipeline, actual captions and source-kind label required'},'pending':['Root creates isolated project under this staging/LocalUnity* and copies exact engine packages and licensed FBX/texture/provenance; no huge Library copy.','Run ValidateRigOnly in owned isolated instance; compare CPU LBS versus BakeMesh for 15 sampled finite poses.','Set up shared 1080p60 capture with generated mesh/material assets persisted for independently editable per-beat scene files. No .unity scene has been saved by this module.','Bind all animation/step times to approved narration. Observe one finite action; do not loop or stretch a clip to fill narration.','Visually inspect rig elbow axis, surface facing, correct shader/culling, glyphs, label/diagram overlap and caption zone at 1080p and 375px.','Ensure three-axis arrows remain visible in front of targets but respect occlusion; exact layout is not visually approved.','017 baked-data transfer is a labelled analytic illustration, not a performed GPU bake. 022 curve and 033 seam views are explanatory diagrams, not production retopology.','Independent gameplay and its callouts remain parent-owned; 000 deliberately refuses to render from this module.'], 'shots':shots}
(P/'module-plan.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'beats':len(shots),'moduleScenes':len(shots)-1,'runtimeQA':False,'assetHashVerified':all(x['matches'] for x in rig['hashVerification'])}))

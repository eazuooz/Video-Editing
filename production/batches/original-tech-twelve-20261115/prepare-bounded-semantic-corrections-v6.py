"""New semantic wording only for reviewed failed units; retain unaffected PCM."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def write(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
# Each replacement was checked against the already acquired primary evidence.
# Technical names remain in source notes and visual labels where speech is simplified.
REPLACEMENTS={
'shorts-journey-sand-sparkle':{
 'r0181':[('마지막은 모래 언덕에 넓게 흐르는 빛입니다.','Finally, broad light flows over the dunes.')],
 'r0182':[('이 반사광이 언덕의 큰 형태를 살립니다.','This reflection reveals their large shapes.')],
 'u019':[],
 'r0201':[('세 가지 빛 표현이 모여 모래를 완성합니다.','Three treatments of light come together to complete the sand.')]
},
'shorts-horizon-gpu-placement':{
 'u006':[('지역마다 식물 종류와 모양을 정합니다.','Plant types and appearance are set by region.'),('아티스트는 지도와 식물 자산을 조절합니다.','Artists adjust the maps and plant assets.')],
 'u008':[('다음은 밀도 지도를 만듭니다.','Next, build a density map.'),('식물을 얼마나 놓을지 정하는 지도입니다.','It determines how much vegetation to place.')],
 'u009':[('길과 물이 있는 곳은 제외합니다.','Exclude areas occupied by roads and water.')],
 'u010':[('여러 조건을 연결해 배치용 지도를 완성합니다.','Combine the conditions into a map for placement.')],
 'u011':[('이제 후보 점을 지도와 대조합니다.','Now compare candidate points with the map.')],
 'u013':[('점 사이의 간격과 패턴도 조절합니다.','Spacing and point patterns are also controlled.'),('아무 곳에나 나무를 쌓는 방식과는 다릅니다.','This differs from piling trees at arbitrary positions.')]
},
'shorts-inside-temporal-antialiasing':{
 'u004':[('매번 픽셀 안에서 다른 위치를 검사합니다.','Each frame samples a different location inside the pixel.')],
 'u007':[('카메라나 물체가 움직이면 화면 속 위치도 바뀝니다.','A moving camera or object changes its screen position.')],
 'u008':[('깊이와 움직임 정보를 함께 사용합니다.','Use depth and motion information together.'),('같은 점이 이전 화면에서 어디에 있었는지 찾습니다.','Find where the same point was in the previous frame.')],
 'u009':[('이렇게 과거 화면의 대응 위치를 찾습니다.','This finds the corresponding position in the old frame.')],
 'u010':[('가려졌던 곳이 드러나면 과거 정보가 틀릴 수 있습니다.','When a hidden area appears, old information may be wrong.')],
 'u011':[('현재 픽셀 주변의 색 범위를 확인합니다.','Check the color range around the current pixel.'),('어울리지 않는 과거 색은 그 범위에 맞춥니다.','Bring incompatible past colors within that range.')],
 'u014':[('빠른 움직임에는 모션 블러도 따로 사용합니다.','Fast motion also uses separate motion blur.'),('그 흐림은 과거 기록에 계속 쌓지 않습니다.','That blur is not repeatedly accumulated in history.')],
 'u015':[('작은 위치 차이로 정보를 모읍니다.','Gather information from small position differences.'),('같은 점을 찾고 잘못된 과거 색을 고쳐 섞습니다.','Find the same point, correct wrong past colors, and blend.')]
},
'shorts-spiderman-swing-anchor':{
 'u010':[('제작 도구로 넓은 도시의 표시를 자동화했습니다.','Production tools automate marking the large city.'),('마지막에는 실제 지형에 닿는지도 검사합니다.','Finally, check whether the result touches real geometry.')],
 'u013':[('건물 면의 가까운 점과 진행 방향의 점을 조합합니다.','Combine a nearby point on the building with one toward travel.'),('너무 깊이 떨어질 후보는 위치를 고칩니다.','Adjust candidates that would let the player fall too deeply.')],
 'u015':[('점수가 좋은 부착점을 선택합니다.','Choose a well-scoring attachment point.'),('좋지 않은 곳에 억지로 연결하지는 않습니다.','Avoid forcing a connection to a poor location.')],
 'u017':[('줄이 팽팽해지면 중력과 줄 방향을 고려합니다.','Once the web is taut, consider gravity and its direction.')],
 'u018':[('좋은 부착점이 있어야 원하는 방향으로 나갈 수 있습니다.','A good anchor lets you travel in the intended direction.')],
 'u019':[('게임이 붙일 곳을 고르면 우리는 이동에 집중합니다.','The game chooses the attachment so we can focus on moving.')]
},
'shorts-control-destruction-pipeline':{
 'u010':[('조각을 나누기만 하면 처음부터 흩어집니다.','Pieces would scatter immediately if they were only separated.')],
 'u011':[('그래서 조각 사이의 연결과 강도도 준비합니다.','Prepare connections between pieces and their strength.')],
 'u012':[('만들어 둔 조각과 물리 정보를 엔진에 보냅니다.','Send the prepared pieces and physics data to the engine.'),('어디가 떨어지고 어디가 남을지 다룰 수 있습니다.','Then control what breaks away and what remains attached.')],
 'u013':[('충격으로 연결이 풀리면 물리 조각이 움직입니다.','An impact breaks connections and physical pieces move.')],
 'u014':[('충돌과 부서짐은 작은 파편과 먼지도 만듭니다.','Collisions and breakage also generate chips and dust.'),('재질에 맞는 효과를 함께 부르는 겁니다.','Trigger effects appropriate to the material.')],
 'u015':[('큰 조각과 작은 효과가 함께 충격을 전합니다.','Large pieces and small effects communicate the impact together.')],
 'u016':[('표면에 남은 자국도 파괴를 풍부하게 만듭니다.','Marks left on surfaces also enrich the destruction.')]
},
'shorts-returnal-particle-tentacles':{
 'u003':[('점들이 연결되고 서로의 움직임을 따라갑니다.','Connected points follow one another’s motion.'),('그 둘레에 굵은 표면을 만드는 과정을 보겠습니다.','Then we will build a thick surface around them.')],
 'u004':[('처음에는 뼈대마다 물리 몸체를 붙이려 했습니다.','The initial approach attached a physical body to each bone.')],
 'u005':[('하지만 계산 비용과 표현 조절에 어려움이 있었습니다.','But computation cost and artistic control were difficult.')],
 'u006':[('개발진은 지피유 이펙트 도구에서 입자 구조를 발전시켰습니다.','The team developed the particle structure in a GPU effects tool.'),('점들은 부모와 자식 관계로 이어집니다.','The points connect through parent and child relationships.')],
 'u008':[('자식은 부모의 한 프레임 전 정보를 사용합니다.','A child uses its parent’s information from one frame earlier.')],
 'u011':[('처음의 납작한 띠에서 원통형 표면으로 바꿨습니다.','The initial flat ribbons became cylindrical surfaces.'),('점들을 따라 부드러운 곡선을 만든 겁니다.','Smooth curves are built along the points.')],
 'u017':[('아티스트와 애니메이터는 공격을 알아보기 좋게 타이밍을 맞췄습니다.','Artists and animators timed the motion to make attacks readable.')],
 'u018':[('부모의 이전 움직임을 따라가는 입자가 있습니다.','Particles follow the parent’s earlier movement.'),('그 둘레의 표면과 함께 촉수의 생동감을 만듭니다.','Together with the surrounding surface, they bring the tentacles to life.')]
},
'shorts-ratchet-dimension-streaming':{
 'u001':[('차원을 넘으면 화면 속 세계가 크게 바뀝니다.','Crossing dimensions can change the world on screen.')],
 'u002':[('위치만 바꾼다고 끝나지는 않습니다.','Changing position alone is not enough.')],
 'u003':[('피시판 개발진의 설명을 따라 자료 준비 과정을 보겠습니다.','Follow the PC team’s account of preparing the required data.')],
 'u006':[('피시판은 다이렉트스토리지를 사용합니다.','The PC edition uses DirectStorage.'),('높은 그래픽 설정에서는 지피유도 압축 해제를 돕습니다.','At high graphics settings, the GPU also assists decompression.')],
 'u007':[('압축 해제는 보통 중앙 처리 장치가 맡았습니다.','Decompression was typically handled by the CPU.'),('이 일을 그래픽 장치가 도울 수 있는 겁니다.','The graphics device can help with that work.')],
 'u013':[('이 기능은 빠른 저장 장치에서만 쓰는 것은 아닙니다.','The feature is not limited to fast storage.')],
 'u014':[('공식 피시 안내는 하드디스크도 지원한다고 설명합니다.','The official PC guidance also lists hard drive support.'),('더 좋은 경험을 위해서는 에스에스디를 권장합니다.','It recommends an SSD for a better experience.')],
 'u015':[('자료 읽기와 압축 해제, 속도에 맞춘 공급이 함께 작동합니다.','Reading, decompression, and supply adjusted to storage speed work together.')]
},
'shorts-doom-push-forward-healing':{
 'u003':[('접근과 공격이 회복으로 이어지는 순환을 보겠습니다.','Follow the loop from approach and attack to recovery.')],
 'u012':[('체력 보상과 탄약 보상은 다르게 다룹니다.','Health and ammunition rewards are handled differently.')],
 'u013':[('어떤 자원을 얼마나 주는지도 따로 설계합니다.','Design each resource type and reward amount separately.'),('한 행동만 반복하는 해법을 피하려는 겁니다.','This helps avoid a solution that repeats only one action.')],
 'u016':[('자원을 얻는 행동에도 비용이 있습니다.','Even actions that obtain resources have a cost.'),('연료를 써야 전기톱의 탄약 보상을 얻습니다.','The chainsaw’s ammunition reward requires fuel.')],
 'u018':[('둠은 싸우는 도중에도 회복할 길을 만들었습니다.','DOOM creates a path to recovery during combat.')]
},
'shorts-botw-chemistry-rules':{
 'u001':[('야생의 숨결에서는 풀에 불이 붙고 비가 불을 끕니다.','In Breath of the Wild, grass burns and rain puts fire out.')],
 'u002':[('이런 조합을 장면마다 따로 준비했을까요?','Were these combinations authored separately for every scene?')],
 'u003':[('물체의 움직임과 불붙음 같은 상태 변화는 구별됩니다.','Object motion is distinguished from state changes such as ignition.')],
 'u007':[('첫 규칙은 원소가 물질의 상태를 바꾼다는 겁니다.','The first rule: an element changes a material’s state.')],
 'u008':[('불이 나무에 닿으면 불붙은 상태가 됩니다.','Fire touching wood changes it into a burning state.')],
 'u009':[('공통 규칙을 두면 여러 장소에 적용할 수 있습니다.','A shared rule can apply in many locations.')],
 'u013':[('세 번째 규칙은 물질끼리의 관계입니다.','The third rule concerns relationships between materials.'),('이 화학 규칙에서는 서로의 상태를 직접 바꾸지 않습니다.','Within these chemistry rules, they do not directly change each other’s states.')],
 'u014':[('서로 부딪힐 수 없다는 뜻은 아닙니다.','That does not mean they cannot collide.')],
 'u015':[('움직임을 계산하는 물리와 상태 변화의 규칙을 구별한 겁니다.','This distinguishes motion physics from the rules for state changes.')]
}}
def main():
 summaries=[]
 for slug,replacements in REPLACEMENTS.items():
  p=ROOT/'projects'/slug;j='journey'in slug;old_source=p/('planning/narration-repair-v3.json'if j else'planning/narration-sentence-v2.json');old=read(old_source);vp=MEDIA/slug/('voice-repair-v4'if j else'voice-sentence-v2')/'voice-generation-complete-proof.json';proof=read(vp);rp=Path(read(MEDIA/slug/('asr-repair-v4'if j else'asr-sentence-v2')/'status.json')['review']['path']);lp=rp.parent/'levels.json';assert lp.exists();units=[];new=[];reuse=[];new_en={}
  assert set(replacements)<=set(u['id']for u in old['units'])
  for i,u in enumerate(old['units']):
   if u['id']in replacements:
    for k,(ko,en)in enumerate(replacements[u['id']]):
     uid='s6'+u['id']+str(k+1);x=dict(id=uid,paragraph=u['paragraph'],ko=ko,originUnit=u['id']);units.append(x);new.append(x);new_en[uid]=en
   else:
    row=proof['rawChunks'][i];assert pin(row['path'])['sha256']==row['sha256'];x=dict(u,sourceRaw=row);units.append(x);reuse.append(x)
  paragraphs=[]
  for para in old['paragraphs']:
   selected=[u for u in units if u['paragraph']==para['id']];paragraphs.append(dict(id=para['id'],ko=' '.join(u['ko']for u in selected),unitIds=[u['id']for u in selected],previousEnglishMeaning=para['previousEnglishMeaning']))
  locked=p/'planning/narration-repair-v6.json';write(locked,dict(schemaVersion=1,slug=slug,origin=pin(old_source),sourceVoice=pin(vp),sourceAsr=pin(rp),sourceLevels=pin(lp),sourceInputs=old['sourceInputs'],units=units,newUnits=new,reuseUnits=reuse,newEnglish=new_en,paragraphs=paragraphs,narrationLocked=True,approvedForTts=True,sourceOrderPreserved=True,reason='Actual independent recognition omissions/ambiguities and unchanged sustained-decline flags reviewed. Rewrite only affected sentences in plainer natural language; retain the primary-source teaching sequence and unaffected raw PCM.',qualityPolicy='Unchanged approved model/reference/profile and numerical thresholds; no voice gain, fade, compression, trim or speed changes.',humanApproval=False,voiceAcceptedForFilm=False))
  script=p/'script/narration.repair-v6.json';write(script,dict(title=slug,scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in new]));manifest=read(p/'production/tts-manifest-sentence-v2.json');manifest['revision']='bounded-semantic-corrections-v6';manifest['paths']['script']=str(script.relative_to(ROOT)).replace('\\','/');manifest['tts']['outputDir']='shared/output/original-tech-twelve-20261115/'+slug+'/voice-repair-v6';manifest['tts']['filenameStem']='targeted-voice-repair-v6';write(p/'production/tts-manifest-repair-v6.json',manifest);summaries.append(dict(slug=slug,newUnits=len(new),reusedUnits=len(reuse),physicalUnits=len(units),source=pin(locked)))
 write(HERE/'bounded-semantic-corrections-source-review-v6.json',dict(projects=summaries,actualRecognitionAndNumericEvidenceReviewed=True,primaryMeaningAndOrderPreserved=True,newVoiceGenerated=False,finalFilmsComplete=False));print(json.dumps(summaries))
if __name__=='__main__':main()

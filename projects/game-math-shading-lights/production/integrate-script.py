"""Bind the complete source-faithful draft to observed gameplay; keep production gates explicit."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib,copy
PROJECT=Path(__file__).resolve().parents[1]
ROOT=PROJECT.parents[1]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ko=load(PROJECT/'script/draft-narration.ko.json')
en=load(PROJECT/'script/draft-narration.en.json')
assert [s['id'] for s in ko['segments']]==[s['id'] for s in en['segments']]
segments=copy.deepcopy(ko['segments']);english=copy.deepcopy(en['segments'])
changes=[]
def replace(i,text,text_en,why):
    changes.append({'segment':segments[i]['id'],'before':segments[i]['text'],'after':text,'reason':why})
    segments[i]['text']=text;english[i]['text']=text_en
def prepend(i,text,text_en,why):
    replace(i,text+' '+segments[i]['text'],text_en+' '+english[i]['text'],why)
replace(0,'서브노티카 투의 어두운 물속입니다. 장비의 전조등이 움직이자 빛을 받는 바위도 달라지고, 숨어 있던 굴곡이 드러납니다. 게임은 어느 면을 얼마나 밝게 만들지 어떻게 정할까요? 오늘은 한 지점의 반사 계산에서 출발해 물체 전체의 셰이딩, 광원의 모양, 조명을 미리 저장하는 방법까지 연결하며 화면이 만들어지는 과정을 따라가 보겠습니다.',
    'In the dark waters of Subnautica 2, the equipment’s headlights move across the rocks, revealing their shape. How does a game decide which surfaces to brighten, and by how much? We will follow the picture from reflection at one point to shading the whole object, shaping light sources, and storing lighting in advance.',
    'Actual-game thesis abstract uses inspected Subnautica 2 source240–268s at native speed. No claim of an isolated view-only experiment or proprietary BRDF.')
prepend(18,'타운스케이퍼의 둥근 탑을 둘러보면 넓은 벽면의 밝기 변화만으로도 형태가 읽힙니다.',
    'As we look around the round tower in Townscaper, broad changes in brightness make its shape readable.',
    'Inspected independent Townscaper405–435s demonstrates broad visible shading; mathematical Lambert model follows in our own test bed.')
prepend(7,'포르자 모터스포츠 식스에서 정지한 자동차를 둘러보면, 보닛 위에 비친 밝은 창문 무늬가 보는 방향을 따라 달라집니다. 이런 방향 의존성을 이해하려고, 우선 광원 하나가 만드는 간단한 반짝임부터 계산해 볼게요.',
    'As the camera moves around a stationary car in Forza Motorsport 6, bright window reflections move across its hood. To understand this dependence on viewing direction, let us first calculate a simple highlight from one light.',
    'Adopt inspected19-second native Forzavista interval; observed environment reflection introduces view dependence, without attributing the teaching Phong model to this game. Keep the moving door outside the annotated bonnet target.')
prepend(27,'왕국의 눈물에서는 어두운 바위에 조명꽃 씨앗을 쏘자 식물뿐 아니라 주변 바위도 밝아집니다. 물체가 스스로 빛나 보이는 것과, 다른 표면을 밝히는 것은 이렇게 나누어 볼 수 있어요.',
    'In Tears of the Kingdom, firing a Brightbloom Seed at dark rock makes both the plant and the surrounding rock visible. Looking bright itself and illuminating another surface are two effects we can distinguish.',
    'Inspected481–499s selection is ordinary Brightbloom Seed, not Giant Brightbloom Seed; no claim about Nintendo internal light type.')
prepend(31,'서브노티카 투에서는 천장등을 설치하자 방 안의 표면이 더 밝아집니다.',
    'In Subnautica 2, installing a ceiling light makes the room’s surfaces brighter.',
    'Inspected764.5–778.25s installation and result; fixture shape is not used as proof of point/area type.')
prepend(49,'앞에서 본 장비가 다시 바위 사이를 지나갑니다. 장비 앞쪽의 빛은 이동과 방향 전환을 따라 바위와 바닥으로 옮겨 가고, 빛이 닿지 않는 물속은 어둡게 남습니다.',
    'The same equipment now travels between the rocks. As its position and heading change, the light in front moves across rock and ground, while the surrounding water stays dark.',
    'Independently inspected non-overlapping Subnautica2 interval378–392s. Equipment/hand/UI remain continuous; no dismount or tool change. Position and heading both change, so this is not a controlled direction-only experiment. Replaces rejected343–363s.')
prepend(60,'둠 쓰리에서는 손전등으로 통로와 난간, 문을 차례로 비춥니다. 원형 무늬가 표면을 따라 움직이는 모습을 이제 광원의 좌표와 연결해 보겠습니다.',
    'In Doom 3, a flashlight sweeps across a corridor, railing and door. We can now connect this moving circular footprint to the light’s coordinates.',
    'Independent original Doom3 FHD60 interval82–108s supports the observed footprint; internal gobo/falloff structure is supported separately by primary renderer source and our labelled implementation.')
replace(38,segments[38]['text'].replace(' 이런 표현은 현재의 셰이더에서도 만들 수 있으며, 무조건 지원되지 않는 옛 방식은 아닙니다.',''),
    english[38]['text'].replace(' Modern shaders can also produce this appearance; it is not inherently unsupported.',''),
    'Omit a redundant historical rebuttal from KO and EN narration; current flat-shading implementation and source correction evidence retain the accurate lesson.')
# These aliases change caption spelling only. Speech keeps approved Korean
# pronunciation; math symbols are introduced in the synchronized diagrams.
aliases={'서브노티카 투':'서브노티카 2','포르자 모터스포츠 식스':'포르자 모터스포츠 6','비알디에프':'BRDF','에스에이치':'SH','둠 쓰리':'둠 3','리플렉트 함수':'reflect 함수','유브이 좌표':'UV 좌표'}
def display(text):
    for a,b in aliases.items():text=text.replace(a,b)
    return text
scenes=[];scenes_en=[]
for i,(s,e) in enumerate(zip(segments,english)):
    sid=f'{i:03d}'
    scenes.append({'id':sid,'sourceBeatId':s['id'],'title':s['title'],'lines':[s['text']],'displayLines':[display(s['text'])],'section':s['section']})
    scenes_en.append({'id':sid,'sourceBeatId':s['id'],'title':e['title'],'lines':[e['text']]})
common={'schemaVersion':1,'slug':ko['slug'],'status':'integrated-draft-runtime-and-final-readthrough-pending','isFinalNarration':False,'sourceDraftSha256':hashlib.sha256((PROJECT/'script/draft-narration.ko.json').read_bytes()).hexdigest(),'chapterOrderPreserved':True,'actualDurationSeconds':None}
save(PROJECT/'script/narration.ko.json',dict(common,language='Korean',scenes=scenes))
save(PROJECT/'script/narration.en.json',dict(common,language='English',scenes=scenes_en))
save(PROJECT/'planning/script-integration.json',{'updatedAt':datetime.now(timezone.utc).isoformat(),'changes':changes,'remaining':['Full integrated KO/EN readthrough','Unity runtime sample and all79 beat bindings','Actual TTS duration and word-aligned cues'],'ttsStarted':False})
plan=load(PROJECT/'planning/production-plan.json')
plan['sourceFinal']=True
plan['narrationFinal']=False;plan['sceneBindingsFinal']=False
plan['stage']='full-draft-gameplay-integration'
plan['learningSteps']=[{'id':s['id'],'section':s['section'],'sourceParagraphs':s['sourceParagraphs'],'retainedExplanation':s['text'],'screenIntent':s['screenPlan']} for s in segments]
plan['teachingBeats']=[{'id':s['id'],'speech':s['text'],'visual':s['screenPlan'],'hold':0,'timing':'pending actual PCM and observed motion binding'} for s in segments]
plan['nativeGameCueBindings']=[{'beat':'M21-000-abstract','sourceId':'dYyWmhVuc3w','sourceIn':240,'sourceOut':268,'role':'thesis abstract','status':'native duration must fit actual narration'}, {'beat':'M21-018-diffuse-start','candidate':'S02-matte-faces','role':'broad visible surface shading'}, {'beat':'M21-027-emission-gi','candidate':'S06-brightbloom-emission-light','role':'luminous object versus illuminated receiver'}, {'beat':'M21-031-many-lights','candidate':'S05-add-light','role':'one more light, visible room change'}]
plan['nativeGameCueBindings'] += [{'beat':'M21-007-spec-observe','candidate':'S08-optional-forzavista-specular','role':'view-dependent reflected bright window on a stationary bonnet'}, {'beat':'M21-049-spot','candidate':'S04-spot-sweep','role':'direction-dependent footprint without reusing the abstract'}, {'beat':'M21-060-doom-scope','candidate':'S07-doom3-projector','role':'Doom3 original observed circular footprint; internal calculation from primary source'}]
plan['rejectedCandidateCuts']=[{'id':'S03-glossy-wall','reason':'7-second hatch transition was too brief for the main view-dependence example; replaced by longer stationary-car observation.'}]
plan['gameMix']={'adoptedGames':5,'nintendoGames':1,'nintendoGame':'The Legend of Zelda: Tears of the Kingdom','reason':'Non-reference technical lecture uses concept-matched sufficient examples; Doom3 is the source-specific implementation case, Forza supplies the needed view-dependence observation. No extra game is added just to pad a quota.'}
plan['boundaryLinks']=[{'from':'M21-006-rgb','to':'M21-007-spec-observe','carriedResult':'Four components and RGB products are defined; isolate view-dependent specular contribution.'},{'from':'M21-017-blinn','to':'M21-018-diffuse-start','carriedResult':'Specular changes with view; contrast broad diffuse appearance on an actual rounded tower.'},{'from':'M21-023-brdf-normalization','to':'M21-024-ambient-path','carriedResult':'Direct light calculated but back-facing surfaces black; need indirect illumination.'},{'from':'M21-027-emission-gi','to':'M21-028-sum-one','carriedResult':'Distinguished self-lit surface from illumination; reassemble four terms on same object.'},{'from':'M21-036-anisotropy','to':'M21-037-where-shade','carriedResult':'Established reflection rule and limits; next vary where it is evaluated.'},{'from':'M21-046-coordinate-space','to':'M21-047-lights-transition','carriedResult':'All surface vectors share one space; now produce light direction and intensity inputs.'},{'from':'M21-059-spot-falloff','to':'M21-060-doom-scope','carriedResult':'Separated angular/distance distribution; express a freer volume with textures.'},{'from':'M21-068-doom-advantages','to':'M21-069-bake-bridge','carriedResult':'Reduced direct-light work with a volume; static indirect-light work can instead be stored.'},{'from':'M21-075-mixed-lighting','to':'M21-076-probes','carriedResult':'Static room stores lighting but moving object cannot share fixed lightmap placement; sample space around it.'}]
save(PROJECT/'planning/production-plan.json',plan)
print('Integrated complete79-beat draft with4 observed game roles; final narration/render gates remain closed pending listed checks.')

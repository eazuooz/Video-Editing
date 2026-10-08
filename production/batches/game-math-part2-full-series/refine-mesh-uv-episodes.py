"""Preserve the full draft and refine complete normal-construction/transform units."""
from pathlib import Path
import json,copy,hashlib,datetime,shutil
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;S='game-math-mesh-uv';N='game-math-normal-transform-uv';W=R/'shared/output/game-math-part2-full-series'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat();d=read(B/'lessons'/f'{S}.json');assert len(d['scenes'])==23
baseline=R/f'shared/output/{S}/before-conceptual-episode-refinement';baseline.mkdir(parents=True,exist_ok=True)
for p in [B/'lessons'/f'{S}.json',R/f'projects/{S}/project.json',R/f'projects/{S}/script/narration.ko.json',R/f'projects/{S}/script/narration.en.json',R/f'projects/{S}/sources/gameplay-cuts.json']:
 target=baseline/p.name;assert not target.exists();shutil.copy2(p,target)
fine=read(W/'inspection/mesh-uv-megabonk-fine/generated-samples.json');assert len(fine['records'])==9
mega=dict(status='all3coarse-and9fine-sheets-directly-reviewed-before-dependent-narration',atUtc=now,sourceId='kc8aMSmWSgw',sourceSha256=fine['sourceSha256'],sourceAudioUsed=False,sheets=[dict(**x,directlyViewed=True,sha256=sha(R/x['sheet'])) for x in fine['records']],selected='0–6,10–20,22–47,90–108,132–150,156–180;379–410,534–545,610–638. Exact boundary guards and subject alignment pending measured narration. Exclude observed upgrade/chest menus8,20,48–53,58+,110,118,122–125,130,152–154,367,377,546.',visibleAction='Actual player/camera movement past faceted rock,pillars,cacti and marked walls. Talk only about visible plane/edge/pattern; never infer vertex count or normal algorithm.',priorUse='ExactMegabonk and sourceID search of project/production/publishing metadata before download found no matches.',permissionProof='shared/output/game-math-part2-full-series/mesh-uv-preflight/megabonk-recording-permission.ax.txt',gameIpReview='pending')
write(B/'preflight/mesh-uv-megabonk-fine-review.json',mega)
extra=read(W/'inspection/mesh-uv-bigwalk-extra/generated-samples.json');write(B/'preflight/mesh-uv-bigwalk-extra-review.json',dict(atUtc=now,status='all4extra-sheets-directly-viewed',sheets=[dict(**x,directlyViewed=True,sha256=sha(R/x['sheet'])) for x in extra['records']],selected='Only bright red deck810–834 as short flat-deck/curved-rail comparison; not long dialogue/panorama.',rejected='100–190 predominantly sunset panorama,descent,dark forest;192–200 only8seconds clear green room,not selected.'))
index=read(B/'footage-index.json');permission=W/'mesh-uv-preflight/megabonk-recording-permission.ax.txt';assert 'Free to use Gameplay Recorded on PC' in permission.read_text(encoding='utf8')
index['kc8aMSmWSgw']=dict(id='kc8aMSmWSgw',game='Megabonk',uploader='NCR Gameplay',url='https://www.youtube.com/watch?v=kc8aMSmWSgw',file=fine['source'],sha256=fine['sourceSha256'],reviewedBeforeNarration=True,recordingPermissionObserved='Native description2026-10-09: Free to use Gameplay Recorded on PC,for your videos. Recording grant only; gameIP public review pending. No CC BY claim.',licenseLabel='uploader free-to-use recording statement',metadataProof=permission.relative_to(R).as_posix(),metadataSha256=sha(permission),sourceAudioUsed=False,priorUse='Exact title/source searches found no previous use before chapter refinement.',visibleAction=mega['visibleAction'],inspection=['production/batches/game-math-part2-full-series/preflight/mesh-uv-megabonk-fine-review.json'],publicGameIpReview='pending')
write(B/'footage-index.json',index)
def E(title,mode,lines):return dict(title=title,kind='explanation',mode=mode,ko=[x[0] for x in lines],en=[x[1] for x in lines],beats=[x[2] for x in lines])
def A(title,source,segments,lines,focus,claim):return dict(title=title,kind='actual',sourceId=source,sourceSegments=[dict(**{'in':a},maxSeconds=b-a) for a,b in segments],**{'in':segments[0][0]},maxSeconds=sum(b-a for a,b in segments),ko=[x[0] for x in lines],en=[x[1] for x in lines],focus=focus,claim=claim)
mesh_game=A('각진 바위와 매끄러운 밝기는 같은 정보일까요?','kc8aMSmWSgw',[(22,47),(90,108),(132,150),(156,180)],[
 ('메가봉크의 사막에서 바위와 선인장 사이를 움직입니다. 바위의 꺾인 바깥 윤곽과 면 안의 밝기를 따로 관찰해 보세요.','Move among rocks and cacti in Megabonk. Separate angular rock outlines from brightness inside their faces.'),
 ('카메라가 따라 움직여도 큰 바위의 평평한 면과 꺾이는 가장자리는 남습니다. 화면에 각진 모양이 보인다고 모든 면의 법선 처리까지 알 수는 없습니다.','The moving view retains planar rock faces and angular edges; an angular appearance does not expose their normal treatment.'),
 ('이어지는 구간에서는 큰 바위 옆을 지나고, 다시 선인장과 낮은 바위 사이를 이동합니다. 같은 방향의 빛이라도 표면이 향하는 방향은 다를 수 있습니다.','Pass a large rock, then cacti and lower rocks; differently oriented surfaces can receive the same directional light differently.'),
 ('밝기 차이는 재질과 그림자에도 영향을 받습니다. 그래서 화면의 색만으로 법선 수치를 맞히는 대신, 다음 도식에서 방향 하나만 바꾸어 비교합니다.','Materials and shadows also affect brightness. Our next diagram changes only normal direction rather than inferring its numerical values from pixels.'),
 ('마지막에는 기둥과 꺾인 지붕 같은 큰 형태가 보입니다. 바깥 모양을 만드는 위치와 조명에 사용하는 방향을 서로 다른 입력으로 생각하세요.','The final interval shows pillars and angular roof forms. Treat geometry positions and lighting directions as separate inputs.'),
 ('정점의 위치를 움직이지 않고도 밝기를 매끄럽게 할 수 있을까요? 우리가 만든 육각기둥에 면 법선과 정점 법선을 넣어서 확인하겠습니다.','Can shading look smoother without moving vertices? Compare face and vertex normals on our original hexagonal prism.')],
 '실제 사막 이동 중 바위의 평평한 면·각진 실루엣·선인장·기둥','위치와 셰이딩 방향의 역할을 구분하며 내부 알고리즘은 화면에서 추정하지 않는다')
deck=A('평평한 갑판과 굽은 난간의 경계','wzQLP0Z3zII',[(810,834)],[
 ('빅 워크의 붉은 갑판에서 캐릭터가 움직입니다. 넓은 바닥과 굽은 난간, 기울어진 조작판의 경계를 보세요.','Characters move on Big Walk red deck; observe the broad floor, curved rail and tilted control panels.'),
 ('밝기를 부드럽게 만드는 방향과 실제 형태의 경계는 다른 역할입니다. 곡면으로 이을 곳과 날카롭게 나눌 곳을 구분해야 합니다.','Smooth shading directions and geometric boundaries differ; distinguish intended smooth surfaces from hard joins.'),
 ('이제 정점에 연결된 면을 모두 모아 법선을 만들고, 필요한 경계에서 공유를 끊어 보겠습니다.','Now accumulate all neighboring face directions and split sharing at the required boundaries.')],
 '밝은 붉은 갑판의 실제 캐릭터 이동과 바닥·난간·조작판','관찰한 형태를 단서로 법선 공유와 분리의 목적을 연결')
first=copy.deepcopy(d); first['sourceSections']=['10.4','10.4.1','10.4.2-normal-construction'];first['totalParts']=9
fsc=copy.deepcopy(d['scenes'][:13]);fsc.insert(6,mesh_game);fsc.insert(9,deck)
fsc[0]=E('정점과 법선으로 표면을 저장하기','overview',[
 ('삼차원 물체의 형태와 빛 방향을 저장하려면 정점에 어떤 정보를 넣어야 할까요?','What vertex information represents3D shape and lighting directions?','정점 데이터: 형태 / 방향'),
 ('먼저 게임의 지붕과 바위를 보고, 삼각형을 인덱스로 연결하는 방법과 메모리 크기를 계산합니다.','Inspect game roofs and rocks, then calculate indexed connections and memory size.','실제 표면 → 인덱스·메모리'),
 ('이어서 면 법선과 정점 법선을 비교하고, 이웃 면의 방향을 합산하는 알고리즘을 끝까지 따라갑니다.','Compare face and vertex normals and follow the complete neighboring-face accumulation algorithm.','면·정점 법선 → 누적 알고리즘'),
 ('마지막에는 날카로운 모서리와 삼각분할의 편향을 처리하고, 직접 정한 작은 메시로 답을 확인하겠습니다.','Finally handle sharp edges and triangulation bias and verify the answers on an explicitly defined mesh.','모서리·편향 → 직접 검산')])
fsc.append(E('정점 공유와 법선 만들기를 검산하기','practice',[
 ('정점 네 개가 각각 삼십이 바이트이고 인덱스 여섯 개가 각각 이 바이트면 모두 백사십 바이트입니다. 전체 메시와 한 정점을 공유하는 국소 계산은 구분합니다.','Four32-byte vertices and six2-byte indices total140 bytes; distinguish whole-mesh storage from a local shared-record calculation.','전체 quad: 4×32+6×2=140B'),
 ('같은 인덱스는 같은 전체 레코드를 가리킵니다. 위치가 같아도 법선이나 유브이가 다르면 레코드를 나누어야 합니다.','One index shares an entire record; equal positions with different normals or UVs require distinct records.','같은 위치 ≠ 같은 속성 레코드'),
 ('기본 법선 알고리즘은 초기화, 유효한 면 법선 계산, 세 정점에 누적, 마지막 정규화 순서입니다. 영벡터와 퇴화 면은 별도로 처리합니다.','The basic algorithm initializes, computes valid face normals, accumulates at three vertices and normalizes last, with explicit zero/degenerate handling.','zero → face → accumulate → normalize'),
 ('상자 모서리는 법선을 분리하고, 매끄러운 표면에서는 가중치 정책을 정합니다. 방향의 평균만으로 실루엣이 둥글어지는 것은 아닙니다.','Split cube hard edges and choose a weighting policy on smooth regions; averaging directions does not round silhouettes.','hard edge 분리 / smooth 가중치'),
 ('다음 편에서는 물체를 확대했을 때 법선을 수직으로 유지하는 변환과, 이미지 무늬를 연결하는 유브이 좌표를 계산하겠습니다.','Next we transform normals while preserving perpendicularity and calculate UV coordinates that map image patterns.','다음: 법선 변환 / UV 대응')]))
second=copy.deepcopy(d);second.update(slug=N,part=6,totalParts=9,sourceSections=['10.4.2-normal-transform','10.5'])
ssc=[E('확대된 표면의 법선과 무늬를 연결하기','overview',[
 ('물체를 가로로 늘렸을 때 빛 방향과 무늬가 어색해진다면 무엇을 확인해야 할까요?','What should you check when lighting directions or patterns look wrong after stretching a shape?','확대 뒤 법선·무늬 검수'),
 ('먼저 접선과 법선의 수직 조건을 계산하고, 역전치가 필요한 이유를 작은 수치 예제로 확인합니다.','First verify normal-tangent perpendicularity and the inverse-transpose rule in a numerical example.','수직 조건 → inverse transpose'),
 ('그다음 게임의 벽과 지붕 무늬를 보며 유브이 좌표의 대응과 확대, 회전, 반전을 설명합니다.','Then inspect game wall and roof patterns and explain UV correspondence, crop, rotation and flipping.','실제 무늬 → UV 대응'),
 ('마지막에는 반복과 클램프를 비교하고, 정점에서 반복을 먼저 처리하면 왜 틀리는지 검산하겠습니다.','Finally compare repeat and clamp and demonstrate why wrapping vertices before interpolation fails.','보간 → 주소 모드 → 조회')]),copy.deepcopy(d['scenes'][13]),copy.deepcopy(d['scenes'][14])]
ssc.append(A('각진 바위와 벽 무늬의 대응 보기','kc8aMSmWSgw',[(379,410),(534,545),(610,638)],[
 ('메가봉크에서 바위와 건물 사이를 움직입니다. 꺾인 바위의 면과 뒤쪽 벽에 있는 무늬를 구분해서 보세요.','Move among Megabonk rocks and buildings, separating faceted rock surfaces from wall markings.'),
 ('카메라가 돌아도 바위의 바깥 윤곽은 남습니다. 면 안의 밝기와 벽의 표시는 각각 조명 방향과 표면 속성이라는 질문을 만듭니다.','View changes preserve angular outlines, while face brightness and wall markings motivate lighting and surface-property questions.'),
 ('다음 이동에서는 낮은 바위와 사막 지면을 지나고, 마지막에는 건물의 앞면과 옆면이 번갈아 나타납니다.','The next passage crosses low rocks and sand; the final section alternately reveals building front and side faces.'),
 ('창문과 줄 모양의 표시가 면 위에 놓여 있지만, 실제 유브이나 텍스처 파일을 읽은 것은 아닙니다. 보이는 형태와 무늬의 관계를 관찰합니다.','Windows and strip-like marks appear on faces; we observe their relationship without reading game UVs or texture files.'),
 ('앞의 수치 예제는 접선과 법선을 수직으로 만들었습니다. 이제 무늬를 위한 이미지 좌표를 별도로 연결하겠습니다.','Our numerical example preserved normal-tangent perpendicularity; next connect separate image coordinates for patterns.'),
 ('형태와 법선을 올바르게 저장해도 잘못된 이미지 부분을 조회하면 무늬는 틀릴 수 있습니다. 세 종류의 데이터를 나누어 확인해야 합니다.','Correct geometry and normals cannot fix lookup of the wrong image region; verify these data roles separately.')],
 '실제 사막 이동·시점 변화로 각진 바위·건물 앞뒤·벽 표시 관찰','법선 방향과 이미지 대응을 별도 입력으로 다룬다'))
ssc.extend(copy.deepcopy(d['scenes'][15:19]))
ssc.append(A('면 안의 반복 무늬를 따라 관찰하기','wzQLP0Z3zII',[(270,348)],[
 ('빅 워크의 녹색 방에서 캐릭터들이 움직입니다. 뒤쪽 판의 검은 격자와 벽 위의 둥근 표시를 찾아보세요.','Characters move in Big Walk green room; locate the black grid panel and circular wall markings.'),
 ('시점이 돌아가면서 같은 판의 선이 기울어 보입니다. 화면에서 차지하는 위치와 면 위에 놓인 무늬 위치는 다른 좌표입니다.','Turning views changes the grid apparent angle; screen locations differ from pattern locations on a surface.'),
 ('캐릭터가 가까워지고 옆으로 이동해도 뒤쪽 무늬는 표면의 같은 부분에 이어집니다. 면을 따라 무늬를 조회하는 대응을 떠올려 보세요.','As characters approach and move sideways, markings remain associated with their surface regions, motivating texture correspondence.'),
 ('벽에는 같은 모양이 여러 번 나타나지만 이것만으로 반복 주소 모드라고 결론내릴 수 없습니다. 이미지 안에 반복 무늬가 들어 있을 수도 있습니다.','Repeated shapes do not prove repeat addressing; the repetitions could be contained within the image itself.'),
 ('또한 검은 격자는 실제 삼각형의 연결선이라고 확인되지 않았습니다. 무늬의 반복과 기하의 연결을 구분하는 것이 오늘의 관찰입니다.','The black grid has not been verified as triangle topology; distinguish repeated markings from geometric connections.'),
 ('다음 도식에서는 같은 작은 이미지를 사용하고 유브이 범위와 주소 규칙을 우리가 직접 정합니다. 어떤 결과가 왜 나오는지 계산으로 확인할 수 있습니다.','Our next diagram uses one original image with explicitly chosen UV spans and addressing, letting us verify the resulting patterns.'),
 ('면 안의 위치를 먼저 보간한 다음 이미지에 접근한다는 순서를 기억하세요. 정점의 좌표를 미리 접어 버리는 오류도 함께 비교하겠습니다.','Remember to interpolate within the face before texture lookup; we also compare the failure of folding vertex coordinates too early.')],
 '실제 캐릭터·카메라 움직임에서 격자 판과 벽의 반복된 원형 표시','표면·화면 좌표를 구분하고 겉보기 반복과 실제 주소 모드를 분리한다'))
ssc.extend(copy.deepcopy(d['scenes'][19:]))
for lesson,scenes in [(first,fsc),(second,ssc)]:
 mapping={}
 for i,s in enumerate(scenes,1):
  old=s.get('id');s['id']=f'{i:02}'
  if old:mapping[old]=s['id']
 lesson['scenes']=scenes;lesson['coverage']={k:[mapping[x] for x in v if x in mapping] for k,v in d['coverage'].items() if any(x in mapping for x in v)}
 lesson['episodeRefinement']=dict(atUtc=now,fullDraft=baseline.relative_to(R).as_posix(),boundary='Complete normal accumulation/detach/weighting before normal-transform/UV lesson; no algorithm cut, all useful full-draft paragraphs retained except split-specific overviews/conclusions.',timing='Planning estimate only; refine after measured speech. No padding to20minutes.')
 lesson['timingReview']=dict(status='awaiting measured narration',maximumPlannedSourceSeconds=sum(s.get('maxSeconds',0) for s in scenes))
 for c in lesson['gameCandidates']['selected']:
  if c['sourceId']=='wzQLP0Z3zII':c['reason']='Prior rendering-light source; all newly reviewed green/yellow/red intervals exclude previously delivered footage.'
 lesson['gameCandidates']['selected'].append(dict(game='Megabonk',sourceId='kc8aMSmWSgw',reason='Fresh game/recording;3coarse and9fine sheets directly inspected, menus omitted, faceted silhouette/planes/marked walls support the exact narrated questions.'))
 write(B/'lessons'/f'{lesson["slug"]}.json',lesson)
# Reconcile only the current new, unsynthesized project. No delivered outputs exist.
base=R/'projects'/S;m=read(base/'project.json');m['titles']=dict(ko='게임수학 Part 2 · 렌더링 ⑤ 메시·법선 만들기',en='Game Math Part 2 · Rendering 5: Building Meshes and Normals');m['lecture'].update(totalParts=9,coveredSections=first['sourceSections']);m['editing']['openingOverview']['question']='정점을 공유하며 메시를 저장하고, 날카로운 모서리와 매끄러운 표면에 맞는 법선을 어떻게 만들까요?';write(base/'project.json',m)
for lang in ['ko','en']:write(base/f'script/narration.{lang}.json',dict(title=m['titles'][lang],scenes=[dict(id=s['id'],title=s['title'],lines=s[lang]) for s in fsc]))
cuts=[]
for s in fsc:
 if s['kind']!='actual':continue
 src=index[s['sourceId']];cuts.append(dict(scene=s['id'],**{'in':s['in']},maxSeconds=s['maxSeconds'],duration=None,sourceId=s['sourceId'],sourceFile=src['file'],sourceSegments=s['sourceSegments'],credit=src.get('requiredVisibleCredit') or src['game']+' - '+src['uploader'],licenseLabel=src['licenseLabel'],focus=s['focus'],claim=s['claim'],action=src['visibleAction'],connection='Exact visible surface/outline observation → adjacent independent normal/mesh explanation; no proprietary inference',inspection=src['inspection'],**({'sourceFraming':src['sourceFraming']} if src.get('sourceFraming') else {})))
write(base/'sources/gameplay-cuts.json',dict(reviewedBeforeNarration=True,reviewedAt=now,sources={s['sourceId']:index[s['sourceId']] for s in fsc if s['kind']=='actual'},cuts=cuts))
write(base/'sources/game-candidates.json',first['gameCandidates']);write(base/'planning/coverage-audit.json',dict(source='10.4 full +10.4.2 normal construction; continuation in '+N,coverage=first['coverage'],coreClaimsRetained=True,fullDraftPreserved=baseline.relative_to(R).as_posix(),overviewReviewedBeforeTts=True,noBgm=True))
write(base/'planning/outline.md','# 전체 강의 흐름\n\n'+'\n'.join(f'- {s["id"]} {s["kind"]}: {s["title"]}' for s in fsc)+'\n\n법선 생성 알고리즘과 경계·편향 처리를 완결한다. 다음 편에서 역전치 변환과 UV를 완결한다. 음성 실측 후 길이 확정; 실제게임40% / 설명60%, BGM 없음.\n')
mc=R/f'motion-canvas/src/projects/{S}';imports=["import {makeProject} from '@motion-canvas/core';","import audio from './assets/final-mix.wav';"];entries=[('intro','brand-intro'),*[(f's{s["id"]}',f'scene{s["id"]}') for s in fsc],('outro','membership-outro')]
for var,file in entries:
 imports.append(f"import {var} from './scenes/{file}?scene';");clip='intro' if var=='intro' else 'outro' if var=='outro' else var[1:];write(mc/f'scenes/{file}.tsx',f"import {{makeScene2D}} from '@motion-canvas/2d';\nimport {{playScene}} from './play-clip';\nimport clip from '../assets/{clip}.mp4';\nexport default makeScene2D(function*(view) {{yield* playScene(view,clip,'{clip}');}});\n")
write(mc/'project.ts','\n'.join(imports)+f"\nexport default makeProject({{name:'{S}',audio,scenes:[{','.join(v for v,_ in entries)}]}});\n")
candidate=read(B/'candidates'/f'{S}.json');candidate.update(titleKo='렌더링 ⑤ 메시·법선 만들기',titleEn='Rendering5: Building Meshes and Normals',viewerQuestion=m['editing']['openingOverview']['question'],sections=first['sourceSections'],chapterClaims=['Indexed vertex memory/topology','Face versus vertex normals and interpolation','Complete accumulation,hard-edge detach,degenerate/opposing cases and angle weighting'],episodeBoundary=first['episodeRefinement']['boundary']);write(B/'candidates'/f'{S}.json',candidate);write(base/'planning/candidate.json',candidate)
newCandidate=copy.deepcopy(candidate);newCandidate.update(slug=N,titleKo='렌더링 ⑥ 법선 변환과 UV',titleEn='Rendering6: Transforming Normals and UV Mapping',viewerQuestion='확대된 표면의 법선을 수직으로 유지하고, UV와 주소 모드로 올바른 무늬를 연결하려면?',sections=second['sourceSections'],chapterClaims=['Inverse transpose and explicit perpendicularity exercise','Normalized UVs and independent positions','Crop/rotate/mirror mapping','Unmodified UV interpolation before floor-repeat/clamp/mirror lookup']);write(B/'candidates'/f'{N}.json',newCandidate)
q=read(B/'queue.json');item=next(x for x in q['items'] if x['slug']==S);original=copy.deepcopy(item);order=item['order'];item.update(titleKo=candidate['titleKo'],titleEn=candidate['titleEn'],viewerQuestion=candidate['viewerQuestion'],sections=first['sourceSections'],totalParts=9,status='full-source-and-footage-prepared-awaiting-tts',preflightComplete=False)
assert not any(x['slug']==N for x in q['items'])
for x in q['items']:
 if x['order']>order:
  x['order']+=1
  if x.get('chapter')==10:x['part']+=1;x['totalParts']=9
newItem=copy.deepcopy(original);newItem.update(order=order+1,slug=N,part=6,totalParts=9,titleKo=newCandidate['titleKo'],titleEn=newCandidate['titleEn'],viewerQuestion=newCandidate['viewerQuestion'],sections=second['sourceSections'],status='queued',preflightComplete=False,renderComplete=False,privateUploadComplete=False,gitDelivered=False)
q['items'].append(newItem);q['items'].sort(key=lambda x:x['order']);q.setdefault('episodeRefinementHistory',[]).append(dict(atUtc=now,original=original,result=[S,N],reason=first['episodeRefinement']['boundary'],baseline=baseline.relative_to(R).as_posix()));write(B/'queue.json',q)
write(B/'preflight/mesh-uv-episode-refinement.json',dict(atUtc=now,status='full-source-preserved-before-tts',episodes=[dict(slug=x['slug'],scenes=len(x['scenes']),koCharacters=sum(len(t) for s in x['scenes'] for t in s['ko']),actualCapacitySeconds=x['timingReview']['maximumPlannedSourceSeconds']) for x in [first,second]],fullDraftSha256=sha(baseline/f'{S}.json'),remaining='Review numerical assertions,rendered spatial pixels,measured speech and every caption before private delivery. Second episode stays queued until current delivery.'))
print(json.dumps(read(B/'preflight/mesh-uv-episode-refinement.json'),ensure_ascii=False))

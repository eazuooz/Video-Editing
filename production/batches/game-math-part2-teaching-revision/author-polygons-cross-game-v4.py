"""Append cross-game prerequisites/comparisons, keeping every earlier scene.

Run only after normal-speed source review. No old narration WAV is replaced.
"""
from pathlib import Path
import copy,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011'
SLUG='game-math-polygons-cross-game-additions-v4'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert read(B/'queue.json')['execution']['mode']=='active'
proof=read(R/'first-candidate-native-proof.json');assert all(p['rate']==1 and p['ended'] for p in proof)
assert any(p['id']=='dorf-convex-versus-union' for p in proof)
historical=read(B/'polygons-candidate-comparison.json');assert all(c['nativeNormalSpeedComplete'] for c in historical['candidates'])
data=[
 ('QF04','centers','01','explanation','이번 편과 다음 편의 범위',[
  '방금 소개한 다각형 전체 내용은 두 편으로 나눕니다. 이번 편은 중심을 고르고 경계를 검사하는 데까지입니다. 삼각형으로 나누는 방법은 다음 편에서 이어갑니다.'
 ],['The complete polygon chapter is split into two episodes. This one ends after choosing centers and validating boundaries. The following episode continues with triangle partitioning.']),
 ('QB11','centers','11','explanation','게임이 달라도 기준점과 경계는 구분합니다',[
  '도르프로만틱의 타일과 타이니 글레이드의 건물은 배치할 위치를 정합니다. 반면 시리어스 샘의 화면 표시는 대상을 찾게 하고, 노이타의 지형 경계는 갈 수 있는 빈 공간과 막힌 땅을 구분합니다.',
  '목적은 달라도 한 점과 전체 외곽은 다른 정보입니다. 가운데 점만 같다고 두 모양이 같아지지는 않습니다. 좌표 평균인지, 변까지 같은 거리인지부터 정한 뒤 계산해야 합니다. 게임 내부가 이 공식으로 구현되었다는 뜻은 아닙니다.'
 ],[
  'A Dorfromantik tile and a Tiny Glade building need placement references. A Serious Sam screen marker helps locate a target, while a Noita terrain boundary separates open space from solid land.',
  'Across these different purposes, one point and a complete outline carry different information. Equal center points do not make two shapes identical. Choose coordinate averaging or equal distances to sides before calculating. These observations do not identify the games’ internal implementation.'
 ]),
 ('QG08','centers','QB11','actual','다른 동굴에서도 경계와 빈 공간을 확인합니다',[
  '노이타의 다른 구간입니다. 캐릭터가 오른쪽 발판 옆을 지나갑니다. 점 하나로 캐릭터를 표시해도, 빨간 지형 경계와 그 옆의 빈 틈은 따로 남습니다.',
  '별도 장면에서는 아래로 내려갔다가 다시 올라옵니다. 발판 위를 곧게 이어 빈 틈을 덮는다면, 원래 지나갈 수 있던 공간을 잘못 채운 셈입니다.'
 ],[
  'In another Noita interval, the character passes the right ledge. A point may mark the character, but the red terrain outline and the empty gap beside it remain separate information.',
  'A separate shot descends and returns upward. Bridging across the ledge’s notch could incorrectly fill space that was originally open.'
 ]),
 ('QB12','partition','18','explanation','셰이프즈 투를 처음 보는 분께',[
  '셰이프즈 투는 도형을 가공하고 목표 도형을 납품하는 공장 게임입니다. 벨트는 도형을 옮깁니다. 이제 기계에 들어가는 도형과 밖으로 나오는 조각을 비교하세요.'
 ],['Shapez2 is a factory game about processing and delivering target shapes. Belts move the shapes. Compare the shape entering a machine with the pieces leaving it.']),
 ('QB13','partition','QG06','explanation','잘랐다는 사실보다 남긴 영역을 검사합니다',[
  '셰이프즈 투의 가공은 목표 조각을 만드는 일입니다. 불필요한 부분을 버리는 작업도 있습니다. 반면 삼각형 분할은 모든 조각을 합쳐 원래 영역을 그대로 남겨야 합니다.',
  '타이니 글레이드의 문과 노이타의 통로도, 비어 있어야 하는 곳을 채우면 원래 모양이 달라집니다. 도르프로만틱의 땅도 같은 기준으로 확인합니다. 그림의 모양과 조각은 설명용 예제입니다.'
 ],[
  'Shapez2 processing produces target pieces; some operations discard unwanted material. Triangle partitioning instead requires all pieces together to retain the complete original region.',
  'Filling a Tiny Glade doorway or a Noita passage changes space that should remain empty. Apply the same check to Dorfromantik land. The shapes and pieces in this diagram are defined teaching examples.'
 ]),
 ('QB14','partition','20','explanation','통로의 경계에서 경로의 순서로',[
  '다음 공장 장면은 경계와 경로를 비교하기 위한 것입니다. 벨트는 이동 경로이고 다각형의 외곽선은 아닙니다. 둘 다 점의 순서가 중요하지만, 연결만 된다고 영역까지 올바른 것은 아닙니다.'
 ],['The next factory shot compares a boundary with a path. A belt is a transport route, not a polygon outline. Both depend on point order, but connectivity alone does not prove that a region is correct.']),
 ('QG09','partition','QB13','actual','타일을 더하거나 되돌리면 경계도 바뀝니다',[
  '도르프로만틱은 육각형 타일을 이어 땅을 만듭니다. 빈 칸에 타일을 놓으면 바깥선이 달라집니다. 타일 하나의 모양과 합쳐진 땅을 따로 보세요.',
  '별도 장면에서는 놓았던 타일을 되돌립니다. 경계가 다시 바뀝니다.'
 ],[
  'Dorfromantik joins hexagonal tiles into land. Placing a tile in an empty slot changes the outline. Inspect an individual tile separately from the combined land.',
  'A separate shot undoes a placed tile. The boundary changes again.'
 ])]
scenes=[]
for ident,ep,after,kind,title,ko,en in data:
 assert len(ko)==len(en)
 scenes.append({'id':ident,'episode':ep,'insertAfter':after,'title':title,'kind':kind,'mode':ident,'ko':ko,'en':en,'sourceType':'actual-footage' if kind=='actual' else ('framing' if ident=='QF04' else 'supplement'),'sceneSourceModule':'polygons_cross_game','preservesEarlierScenes':True,'visual':'Independent spatial projected faces; reveal comparisons in narration order. Fixed bottom caption clearance. Numbers are defined examples, not game measurements.'})
actual={
 'QG08':('noita-outline-b','shared/output/game-math-part2-full-series/sources/igcymdI4XYM.mp4',[(451,469),(788,802)],['noita-outline-b','noita-outline-d']),
 'QG09':('dorfromantik-official-trailer','shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm',[(90,107),(116,123)],['dorfromantik-official-trailer']*2)
}
for s in scenes:
 if s['id'] not in actual:continue
 ident,file,intervals,ids=actual[s['id']]
 s.update(sourceId=ident,sourceFile=file,intervals=intervals,maximumSeconds=sum(hi-lo for lo,hi in intervals),sourceGroupStartsAtLines=[0,1])
 s['sourceSegments']=[{'sourceId':sid,'sourceFile':file,'sourceSha256':sha(ROOT/file),'in':lo,'maxSeconds':hi-lo} for (lo,hi),sid in zip(intervals,ids)]
 s['annotation']={'red':'visible terrain/land boundary; observed screen projection','blue':'observed character/tile reference','teal':'open passage','reveal':'narrated sequence; reset each cut','tracking':'editable observed landmarks; hide occluded/uncertain edges','worldMeasurement':False,'engineInternalsAsserted':False,'movingPixelApproval':False}
 s['causalConnection']='An observed change tests the preceding distinction between a reference, complete boundary, and retained region.'
 s['selection']={'comparedBeforeNarration':True,'record':str((R/'polygon-cross-game-content-v4.json').relative_to(ROOT)),'priorUse':'Existing official/permission-recorded sources, new intervals within this independent episode. Other episode reuse is disclosed. No repeated loop within an episode.','finalAnnotatedPixels':'pending'}
write(R/'polygon-cross-game-content-v4.json',{'createdAt':datetime.datetime.now().astimezone().isoformat(),'rulesSource':'docs/VIDEO_EXAMPLE_TRANSFER_REVIEW.md','shapezPrimarySource':'https://store.steampowered.com/app/2162800/shapez_2/','scenes':scenes,'preserveEarlierNarrationAndFormulas':True,'actualShare':.4,'explanationShare':.6,'backgroundMusic':False,'nativeClipReview':'New excerpt/native proof plus historical candidate comparison; final annotated pixels pending','shapezCutRepair':'Current second cut39.5–46.8 also contains throughput and paint montage. Repair the cut and cue alignment before final approval; do not infer that every machine preserves area.','complete':False})
base=read(ROOT/'projects/game-math-polygons-teaching-additions-v2/project.json');m=copy.deepcopy(base)
m.update(slug=SLUG,title='다각형 네 게임 비교와 초보자 연결 설명',revisionOf='game-math-polygons-triangulation')
m['paths']={k:v.replace(base['slug'],SLUG) for k,v in m['paths'].items()}
for k in ['outputDir','filenameStem']:m['tts'][k]=m['tts'][k].replace(base['slug'],SLUG)
write(ROOT/f'projects/{SLUG}/project.json',m)
maps=[]
for lang in ['ko','en']:
 write(ROOT/f'projects/{SLUG}/script/narration.{lang}.json',{'project':SLUG,'language':lang,'status':'authorized-additions-only','scenes':[{'id':f'{i:02}','title':s['title'],'lines':s[lang]} for i,s in enumerate(scenes,1)]})
for i,s in enumerate(scenes,1):maps.append({'additionId':s['id'],'ttsScene':f'{i:02}','sourceType':s['sourceType'],'episode':s['episode'],'sceneSourceModule':s['sceneSourceModule']})
write(R/'polygons-v4-tts-map.json',maps)
# Check, and freeze, every pre-existing scene and its preserved dictionary.
baseline=read(B/'baselines/game-math-polygons-triangulation/lesson.json');old_ids={s['id'] for s in baseline['scenes']};retained=[];snapshots={}
for ep in ['centers','partition']:
 slug=f'game-math-polygon-{ep}-v2';p=ROOT/f'projects/{slug}/production/lesson.json';lesson=read(p)
 snapshots[slug]={'lessonSha256':sha(p),'scenes':lesson['scenes']}
 retained.extend(s for s in lesson['scenes'] if s['id'] in old_ids)
assert retained==baseline['scenes']
write(R/'before-polygon-v4-insertions.json',snapshots)
write(R/'polygons-v4-pretts-audit.json',{'createdAt':datetime.datetime.now().astimezone().isoformat(),'project':SLUG,'original22DictionariesAndOrderExact':True,'existingV2WavsPreserved':True,'projectManifestSha256':sha(ROOT/f'projects/{SLUG}/project.json'),'scriptSha256':{l:sha(ROOT/f'projects/{SLUG}/script/narration.{l}.json') for l in ['ko','en']},'voiceSettingsExact':base['tts'],'voiceReferenceSha256':{k:sha(ROOT/m['tts'][k]) for k in ['reference','referenceText']},'checks':[{'name':'Prerequisites are narrated before Shapez2 and boundary/path contrast','passed':True},{'name':'No claim of verified proprietary engine internals or measured world values','passed':True},{'name':'No new formula or numerical result; original convention/order exact','passed':True},{'name':'Four-game transfer distinction stated explicitly; counts are not approval','passed':True}],'wholeAsrAndPixelsPassed':False})
runner=(B/'render-polygons-retakes-v3.py').read_text(encoding='utf8').replace("slug='game-math-polygons-retakes-v3'",f"slug='{SLUG}'").replace("B/'polygons-retakes-v3-pretts-audit.json'","B/'cross-game-review-20261011/polygons-v4-pretts-audit.json'").replace("B/'polygons-retakes-v3-line-provenance.json'","B/'cross-game-review-20261011/polygons-v4-line-provenance.json'")
(B/'render-polygons-cross-game-v4.py').write_text(runner,encoding='utf8')
print('Seven new independent additions prepared; every pre-existing scene and voice remains unchanged.')

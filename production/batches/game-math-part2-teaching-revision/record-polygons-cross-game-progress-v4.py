"""Save current adopted cuts and distinct teaching cases without pixel approval."""
from pathlib import Path
from datetime import datetime
import copy, hashlib, json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for z in iter(lambda:f.read(8*1024*1024),b''):h.update(z)
 return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
slugs=['game-math-polygon-centers-v2','game-math-polygon-partition-v2'];stamp=datetime.now().astimezone().isoformat()
sources={}
for slug in slugs:sources.update(read(ROOT/'projects'/slug/'production/footage-sources.json')['sources'])
def game(sid):
 if sid.startswith('tiny-glade'):return 'tiny-glade','Tiny Glade'
 if sid.startswith('noita') or sid=='igcymdI4XYM':return 'noita','Noita'
 if sid.startswith('dorfromantik'):return 'dorfromantik','Dorfromantik'
 if 'shapez' in sid:return 'shapez-2','shapez 2'
 if 'serious' in sid or sid=='4s7nMfXt8uQ':return 'serious-sam-2','Serious Sam 2'
 raise ValueError('Unresolved adopted game: '+sid)
notes={
 'tiny-glade':{'prerequisite':'건물/호수 편집을 통해 지형과 열린 공간을 변경하는 건축 게임. 화면 커서는 선택한 관찰 기준일 뿐 실제 엔진 피벗/중심이 아니다.',
   'beforeActionAfter':'기존 건물과 열린 문/땅 → 건물 편집 또는 호수 경계 그리기 → 문과 호수의 열린 영역을 보존하면서 외곽이 달라짐.',
   'common':'한 기준점과 전체 외곽은 다르며 빈 영역을 임의로 채우면 같은 도형이 아니다.',
   'difference':'자유로운 건물/지형 편집; 육각 타일 조합이나 캐릭터 이동의 조건과 다름.'},
 'noita':{'prerequisite':'캐릭터가 지형 발판과 동굴의 빈 틈을 지나간다. 선은 영상에 투영된 관찰 경계이며 픽셀을 엔진의 삼각형으로 측정하지 않는다.',
   'beforeActionAfter':'발판 옆 열린 틈 → 캐릭터가 옆을 지나거나 아래로 내려갔다 올라옴 → 통로가 실제 열린 공간임을 확인.',
   'common':'기준점으로 위치를 표시해도 전체 지형과 지나갈 빈 영역은 별도로 보존해야 한다.',
   'difference':'배치 편집 대신 이동 가능 공간을 관찰; 기하 분할 알고리즘은 별도 정의한 도형에서 계산.'},
 'dorfromantik':{'prerequisite':'육각형 타일을 회전/배치해 연결된 땅을 만든다. 개별 타일과 전체 합친 땅의 경계는 다르다.',
   'beforeActionAfter':'연결된 타일과 빈 배치칸 → 타일 회전·배치, 별도 장면에서 되돌리기 → 외부 윤곽과 홈이 달라짐.',
   'common':'중심의 목적과 순서 있는 외곽을 구분하고 합쳐진 영역/빈 공간을 검사.',
   'difference':'볼록한 육각 타일을 모아도 합친 땅은 오목할 수 있으며 특정 엔진의 분할 구현을 뜻하지 않는다.'},
 'shapez-2':{'prerequisite':'도형을 가공하여 목표 도형을 납품하는 공장 게임; 벨트는 운반 경로. 원형/사각형 절단은 서로 다른 발췌 장면이다.',
   'beforeActionAfter':'기계에 들어가는 원/사각 도형 → 분리 동작 → 출력 조각 확인. 별도 벨트 장면에서 꺾인 경로의 순서 관찰.',
   'common':'입력·작업·결과를 분리하여 원래 영역과 출력 조각의 관계를 확인; 경로와 영역 경계 모두 순서가 중요.',
   'difference':'목표 조각을 만들기 위해 버릴 수도 있는 게임 가공과 원래 영역 전체를 보존하는 삼각형 분할은 목적이 다름. 벨트는 다각형 외곽선이 아님.'},
 'serious-sam-2':{'prerequisite':'화면의 조준/표시는 대상을 찾게 한다. 화면 중앙과 물체 중심·경계의 목적을 비교한다.',
   'beforeActionAfter':'카메라와 화면 표시 → 대상/시점 이동 → 표시와 물체 윤곽의 위치 관계가 달라짐.',
   'common':'한 점의 용도를 정해 중심을 계산; 같은 기준점이 같은 외곽을 보장하지 않음.',
   'difference':'배치·통로 대신 시점과 타깃 찾기의 사례; 조준점이 실제 물체의 무게중심이라는 주장은 하지 않음.'}}
summaries=[]
for slug in slugs:
 P=ROOT/'projects'/slug;m=read(P/'project.json');t=read(P/'production/timeline.json');lesson=read(P/'production/lesson.json')
 lines={s['id']:s for s in lesson['scenes']};cuts=[];selected={};ids=set()
 for slot in t['scenes']:
  if slot['classification']!='actual':continue
  cut=slot['cut'];segments=cut.get('segments',cut.get('sourceSegments'))
  assert segments
  for segment in segments:
   sid=segment.get('sourceId',cut['sourceId']);file=segment.get('sourceFile',cut['sourceFile']);ids.add(sid)
   if sid not in sources:
    same=[x for x in sources.values() if x.get('sourceFile',x.get('file'))==file]
    assert same,(sid,file)
    sources[sid]={**copy.deepcopy(same[0]),'id':sid,'aliasOf':same[0].get('id'),'sourceFile':file,'file':file}
   gid,title=game(sid);observed=selected.setdefault(gid,{'gameId':gid,'gameTitle':title,'cases':[],**notes[gid]})
   duration=segment.get('seconds',segment.get('frames',0)/60) or segment['maxSeconds']
   assert 0<duration<=segment['maxSeconds']+.02
   observed['cases'].append({'scene':slot['id'],'sourceId':sid,'sourceFile':file,
     'sourceSha256':sha(ROOT/file),'sourceUrl':sources[sid].get('url',sources[sid].get('sourceUrl')),
     'rightsRecord':rel(P/'production/footage-sources.json'), 'nativeIn':segment['in'],'nativeOut':segment['in']+duration,
     'sourceSpeed':1,'completeKoNarration':lines[slot['id']]['ko'],'completeEnNarration':lines[slot['id']]['en'],
     'sceneStart':slot['start'],'sceneSeconds':slot['seconds'],'fixedBottomCaptions':True,
     'annotatedTrackRegistry':rel(B/'polygons-annotation-tracks.json')})
  cuts.append({k:slot[k] for k in ['id','frames','seconds','start','cut','baselineClip','preservedOriginal'] if k in slot})
 assert len(selected)>=4
 for gid,row in selected.items():
  row.update(footageAdopted=True,narratedExample=True,comparisonGames=[k for k in selected if k!=gid],
   normalSpeedPlaybackReviewed='See native candidate comparison records; final whole playback remains separate',
   finalMovingPixelsReviewed=False,captionAndUiClearanceReviewed=False,mixedAudioReviewed=False,
   comparisonScene='QB11' if slug.endswith('centers-v2') else 'QB13,QB14,21,QB10',
   limits='Observed screen projection and defined math examples; no measured world values or proprietary engine inference.')
 prior=read(P/'production/footage-sources.json')
 prior.update(sources={sid:sources[sid] for sid in sorted(ids)},currentV4SelectionRecord=rel(R/'polygon-native-candidate-decisions-v4.json'),
   finalMovingPixelApproval=False,humanRightsReviewComplete=False)
 write(P/'production/footage-sources.json',prior)
 write(P/'production/footage-cuts.json',{'recordedAt':stamp,'status':'Current V4 measured native1x cuts; final whole moving/audio review pending',
   'timelineSha256':sha(P/'production/timeline.json'),'scenes':cuts,'noArtificialLoopsFreezeOrSlowdown':True,'humanRightsReviewComplete':False})
 write(P/'planning/game-example-coverage.json',{'recordedAt':stamp,'guide':'docs/VIDEO_EXAMPLE_TRANSFER_REVIEW.md',
   'actualDistinctGames':len(selected),'minimum':4,'games':list(selected.values()),'sourceCountIsApproval':False,
   'original22ScenesAndPcmPreservedAcrossEpisodes':True,'bodyRatio':[.4,.6],'bgm':False,
   'currentWholeCoverageApproved':False,'wholeMixedAudioReview':'pending','finalContinuousPixelReview':'pending'})
 old_pause=copy.deepcopy(m.get('userPauseCheckpoint',{}))
 if old_pause.get('productionPausedByUser'):
  m['userPauseCheckpoint']={'productionPausedByUser':False,'resumedAt':stamp,'explicitUserEvidence':'미게시(예약 포함)와 기존 업로드의 부족한 사례를 최소4종으로 검수·수정 진행',
   'historicalPause':old_pause,'publishAllowed':'Reviewed private replacement and existing schedule authorization; final verification required'}
 m['status']='cross-game-additions-rendered-final-review-in-progress'
 m['paths']['gameExampleCoverage']=rel(P/'planning/game-example-coverage.json')
 m['approvals']['script']='All22 original dictionaries/order/128KO/128EN and PCM retained; seven additive cross-game prerequisite/contrast scenes reviewed; final mixed ASR pending'
 m['publishReady']=False;write(P/'project.json',m)
 summaries.append({'slug':slug,'seconds':t['seconds'],'frames':t['frames'],'games':list(selected),
   'actualSeconds':t['actualFrames']/60,'explanationSeconds':t['explanationFrames']/60,
   'ratioErrorFrames':t['ratioErrorFrames'],'captionCount':len(t['koCaptions'])})
write(B/'polygons-measured-episode-plan.json',{'episodes':summaries,'originalAudioUnchanged':True,'newRenderAndPublishingComplete':False})
write(R/'polygons-v4-asr-meaning-review.json',{'recordedAt':stamp,'fullNewExpectedAndRawRecognizedTextDirectlyRead':True,
 'scenes':7,'currentHashEvidence':rel(R/'polygons-v4-alignment-progress.json'),
 'mathematicalMeaningPreserved':'Point versus complete boundary, purpose before formula, retained empty region, complete union versus discarded output, route versus outline. No new numerical result.',
 'rawAsrNotRewritten':True,'properNameAliasesUsedOnlyForAlignment':['Tiny Glade','Shapes2/셰이프즈 투'],
 'remainingListeningNote':'QB12 raw ASR says 델트 for 벨트. No mathematical condition changed; actual pronunciation/human whole listening remains pending.',
 'humanWholeListeningComplete':False,'finalMixedAsrComplete':False})
queue=read(B/'queue.json');queue['execution']['stage']='polygons-v4-two-four-game-episodes-final-mixed-asr-and-continuous-caption-pixel-review'
item=next(x for x in queue['items'] if x['slug']=='game-math-polygons-triangulation')
item['status']='additive-four-game-episodes-final-review-in-progress'
item['revision'].update(narrationComplete=True,originalPreservationAuditPassed=True,renderComplete=False,
 localOutputsCollected=False,privateUploadComplete=False,scheduleReplacementComplete=False,gitDelivered=False)
queue['crossGameReview'].update(currentProgress=rel(R/'polygons-v4-current-progress.json'),wholeReviewComplete=False,currentReplacementsComplete=False)
queue['updatedAt']=stamp;write(B/'queue.json',queue)
write(R/'polygons-v4-current-progress.json',{'recordedAt':stamp,'episodes':summaries,'additionalNarratedScenes':7,
 'newVoiceComplete':True,'original22ScenesAndPcmPreserved':True,'currentGpuHandoff':rel(R/'polygons-v4-gpu-handoff-result.json'),
 'researchQueueRestoredAndVerified':True,'wholeMixedAudioReview':'in progress on CPU2',
 'currentCaptionedRender':'partition current; centers red-track repair remixed, reburn pending completion',
 'newPlatformMutations':0,'newUploadsComplete':0,'fullTaskComplete':False,
 'otherCountGaps':'Retained in adopted-game-inventory.json; orientation/polar foreign owner work preserved.'})
print(json.dumps({'episodes':summaries,'fullTaskComplete':False},ensure_ascii=False))

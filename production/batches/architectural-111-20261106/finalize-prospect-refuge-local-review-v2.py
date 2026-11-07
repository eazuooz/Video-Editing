"""Finalize ONLY actual06.02 local delivery. Default is read-only; --execute is explicit.

No probe/decoder/model/renderer/Git/platform subprocess is available in this file.
The eight owned JSON files are compare-and-swapped with exact byte backups.
The prior111 integration main() and progress-sync scripts are never invoked.
"""
from __future__ import annotations
import argparse,copy,hashlib,html,importlib.util,json,math,os,sys,uuid
from datetime import datetime,timezone
from pathlib import Path

R=Path('D:/Github/VideoEditing');B=R/'production/batches/architectural-111-20261106'
C=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
SLUG='shorts-leveldesign-06-02';P=R/'projects'/SLUG;T=C/SLUG
AUTH='explicitArchitectural111Batch20261106';KEY='architectural111Batch20261106'
RENDER=T/'render-attempts-v2/20261107-040447-8eaa151aeb/render-manifest.json'
RENDER_SHA='35d0322f59ff40bf530fdf75d04c28b91fe754798c2778b498b0cbf49694cc4c'
MASTER='8a4daeaa2b87c50290f1b852d7a6067116a429aaa39d65b010013d74c4359630'
NARRATION=P/'narration-expanded-draft-v4.json'
NARRATION_SHA='80efff7c8d0b875130e8a28597542db349133cc4e26f873f4dfbbd85d8ce5ff0'
META=P/'publishing-draft-v4.json';META_SHA='53eb604a620bd88e4cf332d4d676484b1d940cb26cf96e60b2e30e8abd886374'
OVERVIEW=B/'integrate-planning.py';OVERVIEW_SHA='e6217ec589fcade53175cef2e0ea9173f721649450b98ee6f053f2192ff8ee6f'
COLLECTOR=B/'collect-prospect-refuge-review.py' # Root must supply the newly reviewed collector SHA explicitly.
OUTPUT=R/'output'/SLUG;LINK=C/'delivery/shorts-leveldesign-06-02-v2.html'
OWNED=[P/'project.json',P/'checkpoint.json',B/'batch.json',B/'checkpoint.json',B/'worklist.json',B/'continuation.json',R/'shared/publishing/video-worklist.json',R/'shared/publishing/shorts-worklist.json']
SUFFIX={'clean':'clean.mp4','captioned':'captioned.mp4','ko':'ko.srt','en':'en.srt'}
STATUS='local-final-review-ready;whole-listening-realtime-user-review-pending'
VERSION='06.02-v2-held-note-clearance-103-96'
class Pending(RuntimeError):pass

def require(ok,message):
 if not ok:raise Pending(message)
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
 with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(path):return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def within(path,root):
 p=Path(path).resolve();require(p.is_relative_to(root.resolve()),'Path escaped selected scope: '+str(p));return p
def bound(row,root=None):
 require(isinstance(row,dict)and isinstance(row.get('path'),str)and isinstance(row.get('sha256'),str),'Exact path/SHA256 pin required')
 p=within(row['path'],root)if root else Path(row['path']).resolve();require(p.is_file()and sha(p)==row['sha256'],'Changed pinned input: '+str(p));return p
def exact_arg(args,name,root):
 path=getattr(args,name);expected=getattr(args,name+'_sha256');require(path and expected,'Missing explicit path/hash: '+name)
 require(len(expected)==64 and all(c in '0123456789abcdef'for c in expected),'Invalid expected SHA256: '+name)
 p=within(path,root)if root else Path(path).resolve();require(p.is_file()and sha(p)==expected,'Input does not match root-selected hash: '+name);return p

def authorize(collector_sha):
 control=read(R/'shared/publishing/video-production-control.json')[AUTH]
 require(control.get('userEvidence')=='111개 전체 제작 들어가줘'and control.get('status')not in('paused','stopped','cancelled'),'Current exact111 authorization unavailable')
 require(control.get('humanFinalReviewRequired')is True and control.get('youtubeAuthorized')is False,'Platform/review boundaries changed')
 require(read(B/'checkpoint.json').get('currentTopicId')=='06.02','06.02 is no longer selected; preserve newer state')
 require(sha(RENDER)==RENDER_SHA and sha(NARRATION)==NARRATION_SHA and sha(META)==META_SHA,'Selected actual render/source/metadata changed')
 require(isinstance(collector_sha,str)and len(collector_sha)==64 and all(c in '0123456789abcdef'for c in collector_sha),'Root-reviewed collector SHA256 is required after the current balanced-select fix')
 require(sha(OVERVIEW)==OVERVIEW_SHA and sha(COLLECTOR)==collector_sha,'Reviewed delivery helpers changed')

def verify(args):
 authorize(args.collector_source_sha256)
 paths={name:exact_arg(args,name,T if name in('review_receipt','official_collection','encoded_audio_review','cover')else P if name=='collection_manifest'else None if name in('visual_review','cover_review')else P)for name in('review_receipt','official_collection','collection_manifest','visual_review','cover','cover_review','encoded_audio_review')}
 # Pixel/cover receipts may be tracked under the selected project, never another project.
 for name in('visual_review','cover_review'):
  q=Path(getattr(args,name)).resolve();require(q.is_relative_to(P.resolve())or q.is_relative_to(T.resolve()),'Receipt outside selected06.02 scope')
 review=read(paths['review_receipt']);folder=paths['review_receipt'].parent
 require(folder.parent==T/'local-final-review'and folder.name==review.get('fingerprint','')[:24],'Not the selected immutable collector review directory')
 require(review.get('status')=='technical-four-output-qa-complete-visual-listening-review-pending'and review.get('humanFinalReview')is False and review.get('platformActions')==[],'Collector receipt scope/approval changed')
 require(Path(review.get('output','')).resolve()==folder and set(review.get('deliverables',{}))==set(SUFFIX),'Incomplete or foreign review receipt')
 require(paths['official_collection']==folder/'official-collection.json'and paths['collection_manifest']==P/'production/delivery-output.json','Official collection paths must be exact')
 require(review['pins']['renderManifest']==pin(RENDER)and review['pins']['metadata']==pin(META)and review['pins']['encodedAudioReview']==pin(paths['encoded_audio_review']),'Review does not bind this render/metadata/AAC report')
 require(review['pins']['reviewHelperSHA256']==args.collector_source_sha256,'Review was not made by frozen selected collector')
 render=read(RENDER);require(render.get('schemaVersion')=='06-02-render-manifest-v2'and render.get('topicId')=='06.02'and render.get('complete')is True,'Actual completed06 render required')
 require(render.get('format')=={'width':1080,'height':1920,'fps':60}and render.get('totalFrames')==28311,'Unexpected final format/clock')
 require(render['outputs']['captioned']['sha256']==MASTER,'Wrong selected master')
 timeline=read(bound(render['timeline'],T));require(timeline.get('totalFrames')==28311 and len(timeline.get('sections',[]))==110,'Final timeline coverage changed')
 require(review['pins']['timeline']==render['timeline'],'Collector timeline differs')
 for row in timeline['inputs']:bound(row)
 require(sha(folder/'index.html')==review['indexSHA256'],'Technical review link changed')
 artifacts=review.get('reviewArtifacts',[]);require(artifacts and len({r['file']for r in artifacts})==len(artifacts),'Missing/duplicated collector artifacts')
 for row in artifacts:
  require(Path(row['file']).name==row['file'],'Collector artifact traversal');q=folder/row['file'];require(q.is_file()and sha(q)==row['sha256']and q.stat().st_size==row['bytes'],'Collector artifact changed')
 qa=read(folder/'technical-qa.json');metadata=read(folder/'publishing-metadata.json')
 require(metadata==review['metadata']and metadata['masterSHA256']==MASTER and metadata['sourceMetadata']==pin(META),'Final metadata differs from selected publishing draft')
 authored=read(META)
 require(metadata['titles']=={'ko':authored['titleKo'],'en':authored['titleEn']}and metadata['descriptions']=={'ko':authored['descriptionKo'],'en':authored['descriptionEn']},'Publishing title/description text changed')
 require(qa.get('wholeDecodePerformed')is True and qa.get('actualFullPlaybackPerformed')is False and qa.get('actualHumanListening')is False and qa.get('userFinalReview')is False,'Technical decode is not human viewing/listening')
 require(qa.get('pins')==review['pins']and qa['sameAac'].get('identicalPacketPayloadAndTiming')is True,'Technical QA/current AAC proof mismatch')
 require(qa['captions']['koCues']==190 and qa['captions']['enCues']==234,'Bilingual cue counts changed')
 for name in('clean','captioned'):
  v=qa['videos'][name];require(v['decodedFrames']==28311 and(v['width'],v['height'],v['fps'])==(1080,1920,60),'Both whole decoded frame clocks required')
 official=read(paths['official_collection']);collection=read(paths['collection_manifest'])
 require(official.get('status')=='official-four-output-collection-complete-human-review-pending'and official.get('masterSHA256')==MASTER and official.get('humanFinalReview')is False and official.get('platformActions')==[],'Official collection is incomplete or foreign')
 require(Path(official.get('sourceReview','')).resolve()==folder and official.get('delivery')==collection,'Official collection does not match actual delivery-output.json')
 require(collection.get('slug')==SLUG and collection.get('directory')=='output/'+SLUG and collection.get('publishReady')is False and collection.get('cueCounts')=={'ko':190,'en':234},'Wrong official output manifest')
 entries=collection.get('files',[]);require(len(entries)==4 and len({r['name']for r in entries})==4,'Exactly four official files required')
 files={}
 for kind,suffix in SUFFIX.items():
  name=SLUG+'.'+suffix;rows=[r for r in entries if r['name']==name];require(len(rows)==1,'Missing official file: '+name);row=rows[0];reviewrow=review['deliverables'][kind]
  require(reviewrow['file']==name and reviewrow['sha256']==row['sha256']==render['outputs'][kind]['sha256'],'Four-output lineage differs')
  for q in [OUTPUT/name,folder/name,bound(render['outputs'][kind],T)]:require(q.is_file()and sha(q)==row['sha256']and q.stat().st_size==row['bytes'],'Actual four-output bytes differ')
  files[kind]=pin(OUTPUT/name)
 require({q.name for q in OUTPUT.iterdir()if q.is_file()}==({SLUG+'.'+s for s in SUFFIX.values()}|{'index.html'}),'Official output folder must contain exactly four deliverables plus its index; preserve unknown files')
 require(args.output_index_sha256 and sha(OUTPUT/'index.html')==args.output_index_sha256,'Root-selected official output index SHA256 required')
 aac=read(paths['encoded_audio_review'])
 require(aac.get('schemaVersion')=='06-02-encoded-audio-numerical-review-v1'and aac.get('topicId')=='06.02'and aac.get('status')=='encoded-numerical-complete-listening-pending','Actual AAC review required')
 require(aac.get('renderManifest')==pin(RENDER)and aac.get('timeline')==render['timeline']and aac.get('masters')=={k:render['outputs'][k]for k in('clean','captioned')},'AAC review belongs to another actual render')
 require(aac.get('actualPcmDecoded')is True and all(aac.get(k)is False for k in('actualListening','fullRealtimePlayback','humanApproval','automaticSpeechPass','voiceDspChanged')),'AAC numerical review cannot imply hearing approval')
 require(aac.get('remainingReview',{}).get('existingTargetsCleared')is False,'Original numerical/literal watches must remain')
 pixel=read(paths['visual_review'])
 require(pixel.get('topicId')=='06.02'and pixel.get('schemaVersion')=='06-02-encoded-mobile-sample-review-v1'and pixel.get('captionedMasterSHA256')==MASTER,'Actual encoded-image review belongs to another master')
 require(pixel.get('blockingIssues')==[]and pixel.get('actualEncodedFramesInspected')is True and pixel.get('encoded1080And375Inspected')is True,'Final encoded1080/mobile pixel inspection is pending/blocked')
 require(all(pixel.get(k)is False for k in('humanApproval','actualWholeListening','actualRealtimePlayback')),'Still review is not full playback/hearing/user review')
 require(pixel.get('samples')and isinstance(pixel['samples'],list),'Explicit inspected encoded sample pins required')
 for sample in pixel['samples']:
  require(type(sample['frame'])is int and 0<=sample['frame']<28311,'Invalid inspected frame');bound(sample['native'],T);bound(sample['mobile'],T)
 cover=read(paths['cover_review']);require(cover.get('schemaVersion')=='06-02-cover-actual-game-review-v1'and cover.get('topicId')=='06.02'and cover.get('captionedMasterSHA256')==MASTER,'Actual selected-game cover provenance required')
 require(cover.get('cover')==pin(paths['cover'])and cover.get('actualAgentVisualInspection')is True and cover.get('blockingIssues')==[],'Actual1080/375 cover review missing or blocked')
 require(all(cover.get(k)is False for k in('actualFullListening','fullRealtimePlayback','humanApproval'))and cover.get('platformActions')==[],'Cover inspection is not human film approval')
 bound(cover['mobile'],T);provenance=read(bound(cover['provenance'],T))
 require(provenance.get('schemaVersion')=='06-02-cover-provenance-v1'and provenance.get('topicId')=='06.02'and provenance.get('cover')==cover['cover']and provenance.get('mobile')==cover['mobile'],'Cover provenance/artifact mismatch')
 source=provenance['sourceFrame'];bound(source,T)
 adopted=[r for r in read(P/'source-footage.json')['sources']if r.get('sha256')==source.get('sourceMediaSHA256')and r.get('sourceUrl')==source.get('originalURL')]
 require(len(adopted)==1 and adopted[0].get('selectedForCut')is True and adopted[0].get('rightsReviewed')is True and adopted[0].get('rightsVerified')is True,'Cover is not from one adopted rights-checked actual source')
 require(source.get('decodedDimensions')==[1920,1080]and provenance.get('actualGameImage')is True and provenance.get('sourcePixelsSynthesized')is False,'Cover source is not the actual FHD game image')
 # Verify actual physical103 completion; never derive voice completion from a delivered link.
 timing_role=next(r for r in timeline['inputs']if r.get('role')=='caption-timing');timing=read(bound(timing_role,T));voice_refs=[r for r in timing['inputs']if r.get('role')=='voiceEvidence'];require(len(voice_refs)==1,'One actual selected raw voice proof required')
 voice=read(bound(voice_refs[0]));require(voice.get('status')=='raw-voice-structurally-complete-independent-ASR-listening-pending'and voice.get('rawSceneCount')==103 and len(voice['sceneWavs'])==len(voice['identity']['scenes'])==103 and len(voice['paragraphMapping'])==103 and [r['sceneId']for r in voice['paragraphMapping']]==[r['id']for r in voice['identity']['scenes']]and sorted({r['paragraph']for r in voice['paragraphMapping']})==list(range(1,26))and voice['aggregateWav']==timeline['audio']['voice'],'Actual103 physical mappings across25 paragraphs required')
 holds=copy.deepcopy(collection.get('notices',[]));require(holds and isinstance(holds,list),'Official remaining-review notices missing')
 holds+=['전체 실제 청취·실시간 시청·사용자 최종 검수는 아직 완료되지 않았습니다.','원본·혼합·AAC의 수치 및 용어 검수 대상을 보존했습니다. 수치 확인은 청취·자연스러움 판정이 아닙니다.']
 return dict(collectorSHA256=args.collector_source_sha256,selectedInputPins=[pin(q)for q in list(paths.values())+[OUTPUT/'index.html',RENDER,NARRATION,META,OVERVIEW,COLLECTOR,P/'source-footage.json',P/'footage-rights-review-v1.json',folder/'index.html',folder/'publishing-metadata.json']]+[dict(path=r['path'],sha256=r['sha256'])for r in timeline['inputs']]+list(files.values()),paths=paths,review=review,folder=folder,render=render,timeline=timeline,qa=qa,metadata=metadata,collection=collection,files=files,aac=aac,holds=list(dict.fromkeys(holds)),voice=voice,voicePin=voice_refs[0])

def page(data,final):
 esc=html.escape;uri=lambda p:esc(Path(p).resolve().as_uri(),quote=True);meta=data['metadata'];links=''.join('<li><a href="'+uri(v['path'])+'">'+k+'</a> <code>'+v['sha256']+'</code></li>'for k,v in final['files'].items())
 return ('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(meta['titles']['ko'])+'</title><style>body{background:#101311;color:#f4f6f2;font:16px/1.7 "Malgun Gothic",sans-serif;max-width:940px;margin:auto;padding:24px;overflow-wrap:anywhere}h1,h2{color:#ffdc7b}a{color:#9de0bb}video{width:100%;max-height:78vh;background:#000}pre{white-space:pre-wrap;font:inherit}code{font-size:12px}img{width:100%;max-width:375px}</style><main><h1>'+esc(meta['titles']['ko'])+'</h1><p>'+esc(VERSION)+' · 1080×1920/60fps · 실제 영상 '+str(data['qa']['videos']['captioned']['videoDurationSeconds'])+'초 · KO190/EN234</p><video controls playsinline preload="none" poster="'+uri(final['cover'])+'" src="'+uri(final['captioned'])+'"></video><h2>남은 실제 검수</h2><ul>'+''.join('<li>'+esc(x)+'</li>'for x in data['holds'])+'</ul><p>전체 디코드·프레임 시간축·AAC 수치 및 실제 인코딩 이미지 표본을 확인한 범위만 기록했습니다. 전체 청취·실시간 재생·사용자 승인과 Shorts 플랫폼 적격성은 미확인입니다.</p><p><a href="'+uri(OUTPUT)+'">전체 출력 폴더</a> · <a href="'+uri(data['folder']/'index.html')+'">기술 검사·표본 모음</a></p><h2>네 출력 / SHA256</h2><ul>'+links+'</ul><h2>정확한 한국어 제목·설명</h2><p>'+esc(meta['titles']['ko'])+'</p><pre>'+esc(meta['descriptions']['ko'])+'</pre><h2>English title / description</h2><p>'+esc(meta['titles']['en'])+'</p><pre>'+esc(meta['descriptions']['en'])+'</pre><img src="'+uri(final['cover'])+'"></main></html>').encode('utf-8')

def prepare(data):
 before={p:p.read_bytes()for p in OWNED};docs={p:json.loads(v.decode('utf-8-sig'))for p,v in before.items()};now=datetime.now(timezone.utc).isoformat()
 batch=docs[B/'batch.json'];rows=batch['projects'];require(len(rows)==111 and len({r['topicId']for r in rows})==111,'Exact111 catalog required')
 selected=[r for r in rows if r['topicId']=='06.02'];require(len(selected)==1 and selected[0]['slug']==SLUG,'Selected row missing')
 completed=[r for r in rows if r.get('productionComplete')is True];require({r['topicId']for r in completed}=={'03.02','07.04'},'Expected exactly two prior deliveries; preserve changed completion state')
 for row in completed:
  old=row['localFinalReview'];require(old.get('humanFinalReview',False)is False and Path(old['index']).is_file()and Path(old['captioned']).is_file(),'Prior actual delivery links missing; preserve history')
 final=dict(status=STATUS,version=VERSION,createdAt=now,index=str(LINK),captioned=data['files']['captioned']['path'],outputFolder=str(OUTPUT),cover=str(data['paths']['cover']),masterSHA256=MASTER,files=data['files'],technicalReview=pin(data['paths']['review_receipt']),officialCollection=pin(data['paths']['official_collection']),collectionManifest=pin(data['paths']['collection_manifest']),encodedPixelReview=pin(data['paths']['visual_review']),encodedAudioReview=pin(data['paths']['encoded_audio_review']),coverReview=pin(data['paths']['cover_review']),metadata=pin(data['folder']/'publishing-metadata.json'),officialOutputIndex=pin(OUTPUT/'index.html'),renderManifest=pin(RENDER),pendingReview=data['holds'],remainingEncodedNumericalReview=copy.deepcopy(data['aac']['remainingReview']),encodedNumericFlags=copy.deepcopy(data['aac']['encodedFlags']),humanFinalReview=False,actualWholeListening=False,actualRealtimePlayback=False,platformActions=[])
 step='06.02 four outputs locally delivered for exact master '+MASTER+'. Preserve all literal/numerical/music/ending targets and previous deliveries. Whole listening, full realtime playback and user approval remain pending. No YouTube/Drive/platform action. Next topic is not started by this finalizer.'
 for path in(P/'project.json',P/'checkpoint.json',B/'checkpoint.json',B/'continuation.json'):
  d=docs[path];d.update(updatedAt=now,localFinalReview=copy.deepcopy(final),selectedVersion=copy.deepcopy(final),nextStep=step)
  current=d.setdefault('currentProduction',{});require(current.get('topicId')=='06.02','Foreign currentProduction; preserve rather than replace')
  current.update(phase=STATUS,finalOutputsVerified=True,localFinalReview=copy.deepcopy(final),completeFinalFilm=True,actualEncodedQaComplete=True,currentCompositeWorkerAlive=False,currentSoftwareWorkerActive=False,actualListening=False,fullRealtimePlayback=False,humanApproval=False,naturalnessOrListeningAccepted=False,platformActions=[],nextStep=step)
 project=docs[P/'project.json'];project.setdefault('localDeliveryOperativeAliasHistory',[]).append(dict(recordedAt=now,reason='Local delivery operative-pointer correction; original values retained',values={k:copy.deepcopy(project.get(k))for k in('currentNarration','nativeVisualQa','voicePreflight','scriptSourceVerification','formatStatus')}));project.update(status=STATUS,currentStage=STATUS,publishReady=False,finalOutputsVerified=True,currentNarration=pin(NARRATION),nativeVisualQa=pin(P/'native-voice-qa-v3.json'),scriptSourceVerification='Full14sourcelearningroles retained;25KO/EN V4 source and actual103/96 mapping reviewed; actual native corrective captures bound',formatStatus='Portrait concept-sized lesson; actual encoded duration recorded; Shorts eligibility and user media review unverified')
 project.setdefault('finalRender',{}).update(status=STATUS,version=VERSION,captionedMasterSHA256=MASTER,renderManifest=pin(RENDER),videoDurationSeconds=data['qa']['videos']['captioned']['videoDurationSeconds'],openItems=data['holds'])
 # Historical preparation field becomes explicitly historical; actual current proof stays separate.
 if project.get('voicePreflight')is not None:project.setdefault('historicalVoicePreflight',copy.deepcopy(project['voicePreflight']))
 project['voicePreflight']=dict(status='actual103-source-complete;old-preflight-preserved',actualVoiceEvidence=data['voicePin'],sourceNarration=pin(NARRATION))
 chk=docs[P/'checkpoint.json'];chk.setdefault('localDeliveryOperativeAliasHistory',[]).append(dict(recordedAt=now,reason='Local delivery operative-count/source-status correction; original values retained',values={k:copy.deepcopy(chk.get(k))for k in('draftParagraphCount','sourceMappingStatus')}));chk.update(stage=STATUS,phase=STATUS,draftParagraphCount=25,currentDraftParagraphCount=25,sourceMappingStatus='full14roles/current25V4-and103physical96logicalconformance-complete',finalOutputsVerified=True,humanReview='delivered-awaiting-human-review',actualHumanReview=False,currentFiniteWorkerRunning=False,currentGpuJobActive=False,wholeListening=False,fullRealtimePlayback=False)
 stages=chk.setdefault('completedStages',[])
 for value in('103physical96logical-actual-source-complete','205blind-raw-asr-and-existing-numeric-review','49full-mix-blind-asr','actual-four-output-technical-collection','actual-encoded-image-sample-review','local-final-review-delivered'):
  if value not in stages:stages.append(value)
 for path,key in((B/'batch.json','projects'),(B/'worklist.json','rows')):
  d=docs[path];require(len(d[key])==111,'Other catalog row count changed');row=next(r for r in d[key]if r['topicId']=='06.02')
  row.update(status=STATUS,productionComplete=True,finalOutputsVerified=True,localFinalReview=copy.deepcopy(final),selectedVersion=copy.deepcopy(final),humanApproval=False,actualHumanReview=False,platformStatus='not-uploaded',draftParagraphCount=25,narrationStatus='CurrentV4/103physical96logical/205rawASR/49mixASR/actualfouroutputs complete; whole-media review pending',voiceGenerated=True,voiceRunning=False,voiceAsrRunning=False,voiceRepairPending=False,visualCorrectionPending=False,voiceQualityAcceptancePending=True,nativeVisualQa=pin(P/'native-voice-qa-v3.json'),nextStep=step)
  d.update(updatedAt=now,currentPhase=STATUS)
  if key=='projects':d['completedLocalReviewCount']=3
 cp=docs[B/'checkpoint.json'];cp.setdefault('localDeliveryOperativeAliasHistory',[]).append(dict(recordedAt=now,reason='Completed current103/205 evidence replaces stale pending aliases; original values retained',values={k:copy.deepcopy(cp.get(k))for k in('completedVoiceCount','currentEditingReadiness','voiceRepairQueued','currentAsrPending','asrVerifiedComplete','asrReview','rawLevelReview','remainingStages','nextSelectedTopicId')}));cp.update(phase=STATUS,nextSelectedTopicId=next((r['topicId'] for r in sorted(rows,key=lambda value:value['order']) if r['topicId']!='06.02'and not r.get('productionComplete')),None),completedLocalReviewCount=3,completedVoiceCount=3,voiceRepairQueued=False,currentAsrPending=False,asrVerifiedComplete=True,currentEditingReadiness='Current103 source/205rawASR/49mixedASR/scalar/encodedtechnical checks complete; delivered for actual whole listening/realtime/user review',finalOutputsVerified=True,ownFiniteQueueRunning=False,currentGPUJobActive=False,wholeListening=False,fullRealtimePlayback=False,actualHumanReview=False,nextStep=step,remainingStages=['현재 납품 버전의 전체 실제 청취 및 보존된 용어·수치 확인 대상 검수','현재 납품 버전의 전체 실시간 영상 재생 검수','같은 masterSHA256 버전의 사용자 최종 검수; 납품 링크는 승인 아님','정확111목록의 다음 미완성 주제 '+next((r['topicId'] for r in sorted(rows,key=lambda value:value['order']) if r['topicId']!='06.02'and not r.get('productionComplete')), '(모두 완료)')+' 선택을 현재 제어·체크포인트와 대조; 이 finalizer는 새 주제 작업을 시작하지 않음'])
 # Current103 raw reviews are already bound by the immutable current timing inputs.
 timing=read(bound(next(r for r in data['timeline']['inputs']if r.get('role')=='caption-timing'),T))
 for role,key in(('rawAsrReview','asrReview'),):
  matches=[r for r in timing['inputs']if r.get('role')==role]
  require(len(matches)==1,'Current raw-ASR review pin missing');cp[key]={k:matches[0][k]for k in('path','sha256')}
 audio_build=read(bound(next(r for r in data['timeline']['inputs']if r.get('role')=='audio-build'),T));bound(audio_build['rawNumericalLevelReview']);cp['rawLevelReview']=audio_build['rawNumericalLevelReview']
 continuation=docs[B/'continuation.json'];continuation.update(currentFirstStep=step,latestLocalDelivery=copy.deepcopy(final),currentTopicId='06.02')
 # Pin final project bytes only after the selected project and checkpoint patches are final.
 for d in(cp,continuation):
  d['currentSelectedProject']={'path':str(P/'project.json'),'sha256':hashlib.sha256(encoded(project)).hexdigest()}
  d['currentSelectedCheckpoint']={'path':str(P/'checkpoint.json'),'sha256':hashlib.sha256(encoded(chk)).hexdigest()}
 cp['currentProjectCheckpoint']=copy.deepcopy(cp['currentSelectedCheckpoint'])
 for path,key in((B/'batch.json','projects'),(B/'worklist.json','rows')):
  next(r for r in docs[path][key]if r['topicId']=='06.02')['currentCheckpoint']=copy.deepcopy(cp['currentSelectedCheckpoint'])
 for path in OWNED[-2:]:
  d=docs[path];row=d[KEY];require(row.get('youtubeAuthorized')is False and row.get('humanFinalReviewRequired')is True,'Shared owned-key boundary changed')
  row.update(updatedAt=now,status='three-local-final-reviews-ready;06.02-awaiting-human-review',currentStage=STATUS,completedLocalReviewCount=3,currentSelectedTopicId='06.02',currentTopicId='06.02',latestLocalReview=str(LINK),latestOutputFolder=str(OUTPUT),latestCaptioned=final['captioned'],latestMasterSHA256=MASTER,latestVersion=VERSION,actualWholeListening=False,actualRealtimePlayback=False,humanReviewedCount=0,remainingActualReview=data['holds'],currentCheckpoint={'path':str(B/'checkpoint.json'),'sha256':hashlib.sha256(encoded(cp)).hexdigest()})
 # Verify surgical preservation: all110 nonselected rows and all foreign shared keys survive.
 for path,key in((B/'batch.json','projects'),(B/'worklist.json','rows')):
  old=json.loads(before[path].decode('utf-8-sig'));require([r for r in old[key]if r['topicId']!='06.02']==[r for r in docs[path][key]if r['topicId']!='06.02'],'Foreign catalog row changed')
 for path in OWNED[-2:]:
  old=json.loads(before[path].decode('utf-8-sig'));require({k:v for k,v in old.items()if k!=KEY}=={k:v for k,v in docs[path].items()if k!=KEY},'Foreign shared key changed')
 return before,{p:encoded(docs[p])for p in OWNED},final,page(data,final)

def replace_if(path,before,after):
 require(path.read_bytes()==before,'Concurrent write detected; preserve: '+str(path))
 tmp=path.with_name(path.name+'.06-final-'+uuid.uuid4().hex+'.tmp')
 try:
  with tmp.open('xb')as f:f.write(after);f.flush();os.fsync(f.fileno())
  require(path.read_bytes()==before,'Concurrent write before replacement: '+str(path));os.replace(tmp,path)
 finally:
  if tmp.exists():tmp.unlink()

def execute(data,before,after,final,page_bytes):
 authorize(data['collectorSHA256']);require(all(p.read_bytes()==before[p]for p in OWNED),'Owned inputs advanced after dry preparation')
 for q in data['selectedInputPins']:bound(q)
 require(not LINK.exists(),'Preserve existing delivery page; finalization already exists or differs')
 work=C/'06-02-finalization-history'/(datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10]);work.mkdir(parents=True,exist_ok=False)
 overview_paths=[B/'worklist.html',C/'delivery/index.html'];overview_before={p:p.read_bytes()if p.exists()else None for p in overview_paths}
 for i,path in enumerate(OWNED):(work/(str(i)+'-'+path.name)).write_bytes(before[path])
 for i,(path,value)in enumerate(overview_before.items()):
  if value is not None:(work/('overview-'+str(i)+'.html')).write_bytes(value)
 backups={'schemaVersion':'06-02-finalization-byte-backups-v1','source':pin(__file__),'createdAt':final['createdAt'],'files':[{'path':str(p),'beforeSHA256':hashlib.sha256(before[p]).hexdigest(),'backup':pin(work/(str(i)+'-'+p.name)),'afterSHA256':hashlib.sha256(after[p]).hexdigest()}for i,p in enumerate(OWNED)]}
 (work/'backups.json').write_bytes(encoded(backups))
 changed=[];records_committed=False
 try:
  # This transaction never invokes production or launches a process.
  LINK.parent.mkdir(parents=True,exist_ok=True)
  with LINK.open('xb')as f:f.write(page_bytes);f.flush();os.fsync(f.fileno())
  require(sha(LINK)==hashlib.sha256(page_bytes).hexdigest(),'Delivery link must exist with exact page bytes before count update')
  for path in OWNED:replace_if(path,before[path],after[path]);changed.append(path)
  records_committed=True
  require(all(p.read_bytes()==after[p]for p in OWNED),'Concurrent metadata edit before overview; stop without overwrite')
  for p,old in overview_before.items():require((p.read_bytes()if p.exists()else None)==old,'Concurrent overview edit; preserve')
  require(sha(OVERVIEW)==OVERVIEW_SHA,'Overview helper changed')
  # Import is side-effect-free; ONLY build_html, never main(), performs the two allowed HTML writes.
  sys.path.insert(0,str(B));spec=importlib.util.spec_from_file_location('delivery06_existing_overview',OVERVIEW);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  plans={}
  for name in('planning-a.json','planning-b.json','planning-c.json'):
   value=read(B/name);entries=value if isinstance(value,list)else value.get('topics',value.get('plans',[]))
   for row in entries:plans[row['topicId']]=row
  m.build_html(read(B/'batch.json'),read(B/'worklist.json')['rows'],plans,read(B/'checkpoint.json'),write_delivery=True)
  require(LINK.is_file()and sha(LINK)==hashlib.sha256(page_bytes).hexdigest(),'Local delivery link changed')
  receipt={'schemaVersion':'06-02-local-delivery-finalization-v1','complete':True,'final':final,'index':pin(LINK),'backups':pin(work/'backups.json'),'updatedOwnedFiles':[pin(p)for p in OWNED],'overviews':[pin(p)for p in overview_paths],'completedLocalReviewCount':3,'wholeListening':False,'fullRealtimePlayback':False,'humanApproval':False,'platformActions':[]}
  (work/'finalization-receipt.json').write_bytes(encoded(receipt));return receipt
 except Exception as error:
  # Preserve partial evidence. Roll back ONLY our exact bytes; never overwrite a subsequent writer.
  rollback=[]
  for path in reversed(changed):
   if not records_committed and path.read_bytes()==after[path]:replace_if(path,after[path],before[path]);rollback.append(str(path))
  (work/'failed-preserved.json').write_bytes(encoded({'complete':False,'error':repr(error),'recordsCommitted':records_committed,'overviewCompletionPending':records_committed,'restoredOnlyOwnExactBytes':rollback,'deliveryPagePreserved':LINK.exists(),'humanApproval':False,'platformActions':[]}))
  raise

def parser():
 q=argparse.ArgumentParser(description=__doc__)
 for name in('review-receipt','official-collection','collection-manifest','visual-review','cover','cover-review','encoded-audio-review'):
  q.add_argument('--'+name);q.add_argument('--'+name+'-sha256')
 q.add_argument('--output-index-sha256');q.add_argument('--collector-source-sha256');q.add_argument('--execute',action='store_true');return q

def main():
 args=parser().parse_args()
 try:
  data=verify(args);before,after,final,body=prepare(data)
  preview={'ready':True,'dryRun':not args.execute,'masterSHA256':MASTER,'requiredActualOutputCount':4,'completedCountAfterVerifiedDelivery':3,'ownedJsonWrites':[str(p)for p in OWNED],'localLink':str(LINK),'overviewFunction':'build_html(...,write_delivery=True)','humanApproval':False,'wholeListening':False,'fullRealtimePlayback':False,'platformActions':[]}
  result=execute(data,before,after,final,body)if args.execute else preview
  print(json.dumps(result,ensure_ascii=False))
 except (Pending,FileNotFoundError,KeyError,ValueError)as error:
  print(json.dumps({'ready':False,'complete':False,'dryRun':not args.execute,'reason':str(error),'humanApproval':False,'platformActions':[]},ensure_ascii=False));return 1 if args.execute else 0
 return 0
if __name__=='__main__':raise SystemExit(main())

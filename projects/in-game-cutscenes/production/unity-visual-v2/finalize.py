"""Collect verified D27/D28 visual revisions without replacing their baselines."""
from __future__ import annotations
import argparse, copy, hashlib, json, re, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
SLUGS=('in-game-cutscenes','start-with-climax')

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p): return p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for data in iter(lambda:f.read(8*1024*1024),b''):h.update(data)
 return h.hexdigest()

def finish(slug):
 project=ROOT/'projects'/slug; revision=project/'production/unity-visual-v2'
 local=project/'production/local/unity-visual-v2';spec=read(revision/'plan.json');edit=local/spec.get('mediaEditDirectory','edit')
 structure=read(edit/'structural-verification.json')
 pixels=read(revision/'encoded-visual-review.json')
 assert structure['status']=='pass' and structure['aacIdenticalToBaselineAndEachOther'] and structure['srtIdenticalToBaseline']
 assert pixels['status']=='pass' and pixels['allChangedCutsInspected']
 assert pixels['captionedSha256']==structure['outputs']['captioned']['sha256']
 for kind in ('captioned','clean'):
  assert sha(edit/f'{slug}.{kind}.mp4')==structure['outputs'][kind]['sha256']
 for lang in ('ko','en'):assert sha(edit/f'{slug}.{lang}.srt')==spec['baselineSha256'][lang+'.srt']
 manifestPath=project/'project.json';old=read(manifestPath)
 baselinePath=revision/'baseline-project.json'
 if not baselinePath.exists():write(baselinePath,old)
 baseline=read(baselinePath)
 oldDelivery=project/'production/delivery-output.json'
 if not (revision/'baseline-delivery-output.json').exists():write(revision/'baseline-delivery-output.json',read(oldDelivery))
 now=datetime.now(timezone.utc).isoformat();manifest=copy.deepcopy(old)
 manifest['revision']='unity-visual-v2';manifest['status']='local-review-ready'
 manifest['latestCheckpoint']=rel(revision/'latest-checkpoint.json')
 manifest.setdefault('finalPlan',spec['baselinePlan'])
 manifest['visualRevisionPlan']=rel(revision/'plan.json')
 manifest['delivery']['localStorageRoot']=rel(local/'delivery')
 paths=manifest['paths']
 for key,suffix in [('videoBurnedCaptions','captioned.mp4'),('videoClean','clean.mp4'),('captionsKo','ko.srt'),('captionsEn','en.srt')]:paths[key]=rel(edit/f'{slug}.{suffix}')
 manifest['publishReady']=False
 manifest['membershipOutro']['appliedToFinal']=True
 manifest['finalRender']={'status':'complete-local-review-ready','knownIssues':[],
  'openItems':['새 설명 화면이 들어간 전체 영상의 최종 시청·청취를 기다리고 있습니다.']}
 manifest['review']={'actualUserViewed':False,'humanWholeListening':'pending new visual revision',
  'priorUserFeedback':'Story and sequence praised; explanation imagery revision requested, not approval of this new master.'}
 history=manifest.setdefault('revisionHistory',[])
 if not any(x.get('revision')==baseline['revision'] for x in history):
  history.append({'revision':baseline['revision'],'manifest':rel(baselinePath),
   'localFinalReview':baseline.get('localFinalReview'),'paths':baseline['paths'],
   'latestCheckpoint':baseline['latestCheckpoint'],'preserved':True})
 manifest['updatedAt']=now
 # Collection reads exact configured paths, preserves any prior delivered set,
 # verifies all four copied files and regenerates the project rebuild manifest.
 write(manifestPath,manifest)
 subprocess.run(['node','scripts/collect-video-output.cjs',slug],cwd=ROOT,check=True)
 delivery=read(project/'production/delivery-output.json');dest=ROOT/delivery['directory']
 files={};hashes={};localFiles=[]
 for f in delivery['files']:
  suffix=f['name'][len(slug)+1:];path=dest/f['name'];assert sha(path)==f['sha256']
  files[suffix]=rel(path);hashes[suffix]=f['sha256'];localFiles.append({'name':f['name'],'path':rel(path),'sha256':f['sha256'],'bytes':f['bytes']})
 review={
  'slug':slug,'episode':manifest['seriesOrder'],'revision':'unity-visual-v2','status':'local-review-ready',
  'stage':'internal-qa-complete-awaiting-user-final-review','updatedAt':now,
  'fourOutputsVerified':True,'durationSeconds':structure['durationSeconds'],
  'captionedSha256':hashes['captioned.mp4'],
  'technicalSummary':{'resolution':[1920,1080],'fps':60,'decodedFrames':structure['totalFrames'],
   'actualFrames':structure['bodyGameplayFrames'],'explanationFrames':structure['bodyExplanationFrames'],
   'actualShare':structure['bodyGameplayShare'],'completeDecodeAndPts':'pass'},
  'audioSummary':{'changed':False,'method':'Original encoded AAC packet copy; narration, source game audio and BGM are identical.',
   'audioPacketsSha256':structure['outputs']['captioned']['audioPacketsSha256'],
   'baselineReview':rel(project/'production/batch-v1/review-status.json'),
   'finalASRReusedOnlyBecauseAACIdentical':True,'srtUnchanged':True},
  'visualSummary':pixels,'humanReview':'pending new visual revision','humanListening':'pending',
  'humanWholeReview':'pending','nativeReplacedCutCount':len(spec['cuts']),
  'savedScenePaths':['unity/VideoEditing/'+c['scenePath'] for c in spec['cuts']],
  'reviewFocus':(['컷신 방식과 프레임 레이트의 차이가 동작으로 보이는지',
   '넘기기·구간 이동·속도 조절·QTE의 서로 다른 결과가 자연스럽게 연결되는지']
   if slug=='in-game-cutscenes' else ['첫 행동·위협·판단이 도입부의 재미로 이어지는지',
   '사건 전달 순서 변화와 역전재판 증거 선택 설명이 보이는지']),
  'platformUpload':False,'localFiles':localFiles,'index':rel(dest/'index.html'),
  'evidence':{'delivery':rel(project/'production/delivery-output.json'),
   'structural':rel(edit/'structural-verification.json'),'pixels':rel(revision/'encoded-visual-review.json'),
   'preflight':rel(revision/'preflight-review.json'),'preservation':rel(edit/'assembly-inputs.json'),
   'plan':rel(revision/'plan.json'),'baselineManifest':rel(baselinePath)}}
 write(revision/'review-status.json',review)
 checkpoint={'slug':slug,'revision':'unity-visual-v2','stage':'local-review-ready-human-review-pending',
  'updatedAt':now,'renderedMedia':'Four complete outputs collected and SHA256 verified; exact old AAC and SRT retained.',
  'sourcePlan':spec['baselinePlan'],'visualRevisionPlan':rel(revision/'plan.json'),
  'reviewStatus':rel(revision/'review-status.json'),'currentCaptionedSha256':hashes['captioned.mp4'],
  'counts':{'fps':60,'totalFrames':structure['totalFrames'],'actualFrames':structure['bodyGameplayFrames'],
   'explanationFrames':structure['bodyExplanationFrames'],'explanationSegments':len(spec['cuts'])},
  'baselinePreserved':True,'baselineCheckpoint':baseline['latestCheckpoint'],
  'platformMutations':False,'humanFinalReview':'pending','humanListening':'pending',
  'next':'User reviews new full video; no YouTube, Drive, schedule or further video authorized.'}
 write(revision/'latest-checkpoint.json',checkpoint)
 manifest=read(manifestPath)
 manifest['localFinalReview']={'index':rel(dest/'index.html'),'files':files,'sha256':hashes,
  'durationSeconds':structure['durationSeconds'],'actualUserViewed':False,'humanWholeListening':'pending',
  'internalQa':'complete within explicitly recorded structural and sampled visual scope',
  'reviewRecord':rel(revision/'review-status.json')}
 write(manifestPath,manifest)
 spec['status']='local-review-ready-human-review-pending'
 provenance=read(ROOT/spec['rightsRecord']);assetsByPath={x['path']:x for x in provenance['assets']}
 assembly=read(edit/'assembly-inputs.json');parts={x['id']:x for x in assembly['parts']}
 pipeline=read(ROOT/'unity/VideoEditing/Packages/packages-lock.json')['dependencies']['com.unity.render-pipelines.universal']['version']
 for c in spec['cuts']:
  c['actualCaptureReviewed']=True
  scene=ROOT/'unity/VideoEditing'/c['scenePath'];assert scene.exists();c['sceneSha256']=sha(scene)
  receiptPath=local/'render'/c['captureVersion']/c['id']/'render-success.json';receipt=read(receiptPath)
  assert sha(receiptPath)==parts[c['id']]['successReceiptSha256']
  c['sharedAssetPaths']=receipt['assets'];c['animationPaths']=receipt['animations'];c['assetRecords']=[]
  for asset in receipt['assets']:
   if asset in assetsByPath:c['assetRecords'].append(assetsByPath[asset])
   else:
    source=next(x for x in spec['sourceScreenshots'] if x['sha256']==Path(asset).stem)
    path=ROOT/'unity/VideoEditing'/asset;assert sha(path)==source['sha256']
    guid=re.search(r'^guid: (.+)$',path.with_suffix(path.suffix+'.meta').read_text('utf-8'),re.M).group(1)
    c['assetRecords'].append({**source,'sourceFile':source['path'],'path':asset,'guid':guid,'kind':'retained-independent-gameplay-still'})
  c['capture']={'receipt':rel(receiptPath),'receiptSha256':sha(receiptPath),
   'unityVersion':receipt['unity'],'renderPipeline':'Universal Render Pipeline '+pipeline,
   'width':1920,'height':1080,'fps':60,'frames':c['frames'],
   'compiledSourceFingerprint':receipt['compiledSourceFingerprint'],'camera':'orthographic; identical shared stage framing',
   'sourceCodeSha256':c['captureStageSourceSha256'],'outputSha256':parts[c['id']]['sourceSha256']}
 write(revision/'plan.json',spec)
 print(json.dumps({'slug':slug,'index':rel(dest/'index.html'),'files':files,'sha256':hashes},ensure_ascii=False))

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('slug',choices=SLUGS);finish(a.parse_args().slug)

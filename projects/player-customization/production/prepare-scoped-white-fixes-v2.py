"""Record the directly read original samples and prepare only the two visual fixes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,v):
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
state=read(BASE/'current-white-source-verification-v1.json')
assert state['exitCode']==0 and len(state['boards'])==24 and len(state['samplePlan'])==96
assert not (BASE/'current-white-motion-direct-review-v1.json').exists()
for item in state['boards']+state['samplePlan']:assert sha(ROOT/item['path'])==item['sha256']
review={'schemaVersion':1,'reviewedAt':now,'slug':'player-customization',
 'source':state['currentWhite'],'verificationExitCodeObserved':0,'verificationSessionClosed':True,'verificationSessionId':55504,
 'directlyReadBoards':state['boards'],'all96SamplesDirectlyRead':True,
 'reviewMethod':'Directly read all24 contact boards, all three narration-timed phases of each of32 paragraphs. Compared projected top/front/side faces, travel/lift/occlusion and meaning against each paragraph.',
 'passedScenes':['02-visible-effects','03-readable-outcome','04-situations','06-quick-trial','07-expression','08-conclusion'],
 'fixesRequired':[
  {'scene':'01-overview','problem':'Moving token partly covers the projected 예상/시험/표현 labels.','fix':'Raise and move the labels behind the platforms; retain the prominent exact rights notice and all original narration/timing.'},
  {'scene':'05-manageable-choice','problem':'Selected green candidate arrives on the blue current-choice token instead of its separate right pedestal.','fix':'Move the candidate from x=-500 to x=595 with1095 travel; retain the blue current choice and distinct candidate pedestal.'}],
 'allOriginalWhiteApproved':False,'allActualAnimatedSamplesRead':True,'genuineProjectedDepthObserved':True,
 'rightsNoticeVisibleInAll12OverviewSamples':True,'allOriginalPcmPreserved':True,
 'finalCaptionPixelsReviewed':False,'finalMixedAsrApproved':False,'finalVideoComplete':False}
save(BASE/'current-white-motion-direct-review-v1.json',review)
mc=ROOT/'motion-canvas/src/projects/player-customization'
old=mc/'spatial-explanation-v1.tsx';new=mc/'spatial-explanation-fixes-v2.tsx'
assert not new.exists()
text=old.read_text('utf-8')
assert "x,-150,45,37" in text and "?850*u(1):0" in text
text=text.replace("x,-150,45,37","x,-220,150,37").replace("?850*u(1):0","?1095*u(1):0")
new.write_text(text,'utf-8')
scene_dir=mc/'white-fixes-scenes-v2';scene_dir.mkdir()
for name in ['01-overview','05-manageable-choice']:
 p=mc/'current-voice-scenes-v1'/f'{name}.tsx'
 (scene_dir/p.name).write_text(p.read_text('utf-8').replace('../spatial-explanation-v1','../spatial-explanation-fixes-v2'),'utf-8')
project=mc/'white-fixes-project-v2.ts'
project.write_text("import {makeProject} from '@motion-canvas/core';\nimport overview from './white-fixes-scenes-v2/01-overview?scene';\nimport choice from './white-fixes-scenes-v2/05-manageable-choice?scene';\nexport default makeProject({name:'player-customization-white-fixes-v2',scenes:[overview,choice]});\n",'utf-8')
cfg=ROOT/'motion-canvas/vite.player-customization.white-fixes-v2.config.ts'
source_cfg=ROOT/'motion-canvas/vite.player-customization.current-voice-v1.config.ts'
cfg.write_text(source_cfg.read_text('utf-8').replace('port:9243','port:9246').replace('current-voice-white-project-v1.ts','white-fixes-project-v2.ts').replace("output:'../shared/output/player-customization/white-current-voice-v1'","output:'../shared/output/player-customization/white-fixes-v2'"),'utf-8')
timing=read(mc/'current-voice-timing-v1.json');rows=[timing['rows'][0],timing['rows'][4]]
save(BASE/'scoped-white-fixes-preparation-v2.json',{'schemaVersion':1,'preparedAt':now,'status':'prepared-only-await-CUA-preview-and-single-render',
 'originalSourcePreserved':review['source'],'originalHelperSha256':sha(old),'patchedHelper':{'path':rel(new),'sha256':sha(new)},
 'currentReview':rel(BASE/'current-white-motion-direct-review-v1.json'),'scenes':rows,'plannedFrames':sum(r['frames'] for r in rows),
 'passedOtherSixScenesWillNotBeRerendered':True,'allOriginalPcmPreserved':True,'renderStarted':False,'fixPixelsApproved':False,'finalVideoComplete':False})
cp=read(BASE/'latest-checkpoint.json');cp['ownedJob'].update(actualExitObserved=True,actualSessionExitCode=0,actualCimPidAbsent=True)
cp['executionHistory'].append(cp['ownedJob']);cp.update(recordedAt=now,stage='two-white-pixel-fixes-required',ownedJob=None,
 nextAction='Preview and render only original01/05 fixes; preserve the passed other six white scenes. Add source-grounded observation guides before final ratio/mix.')
cp['currentWhiteMotionDirectReview']=rel(BASE/'current-white-motion-direct-review-v1.json');save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization')
i.update(stage=cp['stage'],currentExecution=None,nextAction=cp['nextAction'],currentWhiteMotionDirectReview=cp['currentWhiteMotionDirectReview']);q['updatedAt']=now;save(qp,q)
print(json.dumps({'directBoardsRead':24,'samplesRead':96,'fixScenes':2,'plannedFixFrames':sum(r['frames'] for r in rows),'originalHelperUnchanged':sha(old)==review.get('originalHelperSha256',sha(old))}))

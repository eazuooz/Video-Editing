"""Record actual sampled viewing and source-scoped narration finalization."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
RIGHTS='production/batches/distinctive-ten-shorts-20261025/blizzard-rights-receipt.json'
BASE='production/batches/distinctive-ten-shorts-20261025/local/d2r-official/'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
rights=read(ROOT/RIGHTS);launch=read(ROOT/BASE/'receipt.json');comparison=read(ROOT/BASE/'comparison/receipt.json')
DATA={
 'shorts-d2r-ultrawide-ai-range':dict(topic='ultrawide',cuts=[{'source':launch,'sourceStart':27,'availableUntil':35}],
   viewing={'rangeSeconds':[12,84],'samplingFps':2,'frames':144,'allSampledFramesViewed':True,'evidenceDirectory':'projects/shorts-d2r-ultrawide-ai-range/production/local/source-review','observed':'Sorceress uses ranged spells and monsters approach/react in normal release footage. Grass, corpses and movement visible.','notObserved':'2021 alpha defect is not shown in this source.','fullSpeedPlayback':False,'audioListening':False},
   role='Normal release-game ranged combat gives the setting for a question. The historical defect begins only in our labeled diagram.'),
 'shorts-d2r-loot-grass-clearance':dict(topic='grass',cuts=[{'source':launch,'sourceStart':588,'availableUntil':597}],
   viewing={'rangeSeconds':[535,645],'samplingFps':1,'frames':110,'allSampledFramesViewed':True,'evidenceDirectory':'projects/shorts-d2r-loot-grass-clearance/production/local/act3-review','observed':'Act III party combat, lush vegetation, enemies dying and small ground objects/loot context.','notObserved':'Grass movement caused by an item drop cannot be isolated confidently at this camera distance. No claim that the source proves the deformation.','fullSpeedPlayback':False,'audioListening':False},
   role='Actual vegetation/combat is the setting for the conditional question. The reported development solution is based on the direct developer interview and shown only in our illustration.'),
 'shorts-d2-modular-sprite-equipment':dict(topic='sprites',cuts=[{'source':next(x for x in comparison if x['path'].endswith('tristram_old_comparison_slider.mp4')),'sourceStart':0,'availableUntil':5.3},{'source':next(x for x in comparison if x['path'].endswith('barracks_old_comparison_slider.mp4')),'sourceStart':0,'availableUntil':5.3}],
   viewing={'clips':['tristram_old_comparison_slider.mp4','barracks_old_comparison_slider.mp4'],'rangeSecondsEach':[0,6],'samplingFps':2,'frames':24,'allSampledFramesViewed':True,'evidenceDirectory':'projects/shorts-d2-modular-sprite-equipment/production/local/legacy-review','observed':'Legacy sprites move and attack; original 4:3 image is embedded in the genuine 1920x1080 official capture.','notObserved':'No equipment-change action occurs in these captures. The composition mechanism is demonstrated in our separately authored character.','fullSpeedPlayback':False,'audioListening':'not-applicable; official source has no audio stream'},
   role='Legacy rendered character is the visible target of the question. No modern 3D model is shown as proof of a sprite implementation.')
}
for slug,row in DATA.items():
 p=ROOT/'projects'/slug
 if row['topic']=='grass':
  c=read(p/'script/clauses.json')
  c['clauses']=[x for x in c['clauses'] if x['lineIndex']!=0]
  c['clauses'][:0]=[dict(id='p1-1',lineIndex=0,spoken='디아블로 투의 전리품이,',ko='디아블로 II의 전리품이,',en='The loot in Diablo II:'),dict(id='p1-2',lineIndex=0,spoken='풀에 가려서 보이지 않는다면요?',ko='풀에 가려서 보이지 않는다면요?',en='what if the grass hides it?')]
  write(p/'script/clauses.json',c)
  lines=[' '.join(x['spoken'] for x in c['clauses'] if x['lineIndex']==i) for i in range(6)]
  eng=[' '.join(x['en'] for x in c['clauses'] if x['lineIndex']==i) for i in range(6)]
  n=read(p/'script/narration.spoken.ko.json');n['scenes'][0]['lines']=lines;write(p/'script/narration.spoken.ko.json',n)
  for lang,paras in [('ko',lines),('en',eng)]: (p/f'script/narration.{lang}.txt').write_text('\n\n'.join(paras)+'\n',encoding='utf8')
 sourceRecord={'status':'selected-for-narration-scope','sources':row['cuts'],'role':row['role'],'viewing':row['viewing'],'rightsReceipt':RIGHTS,'rightsVerified':True,'fhdVerified':True,'independentFootageViewed':True,'originalAspectRatioPreserved':True,'nativeSpeedRequired':True,'actualSourceAudio':'Preserve selected original synchronized audio if source has a stream; legacy comparison has none. Final mixing/listening pending.','sourceAudioSeparationClaimed':False}
 write(p/'sources/selected-footage.json',sourceRecord)
 plan=read(p/'planning/production-plan.json');lines=read(p/'script/narration.spoken.ko.json')['scenes'][0]['lines']
 for i,beat in enumerate(plan['scenePlan']):
  beat['speech']=lines[i]
  if i==0:beat.update(visualRole='actual-game-context',sourceRecord='sources/selected-footage.json',purpose=row['role'])
 plan.update(scriptFinalized=True,independentFootageViewed=True,scriptStatus='source-matched-narration-ready-for-parent-tts',sourceViewing=row['viewing'],sourceRightsReceipt=RIGHTS)
 plan['scriptSha256']=hashlib.sha256((p/'script/narration.spoken.ko.json').read_bytes()).hexdigest()
 plan['visualReview'].update(native1080='sample-frames-reviewed-not-final',mobile375=False,movingPlayback=False)
 plan['captionSafeArea']={'center':[510,1380],'fontSize':60,'maxLines':2,'maxWidth':930,'bottomExplanationLines':'at or above y1250; no extra disclaimer line behind captions','reactionBehavior':'Diagram shifts left and shrinks only during brief cat beat. Supplementary bottom labels hide; essential objects remain visible. Final caption composite pending.'}
 plan['headingFreeScriptReadthrough']={'ko':True,'en':True,'conditions':'Historical alpha/current footage separated; grass response is reported evidence plus own illustration; sprite scope is original game only.','audioListening':False}
 write(p/'planning/production-plan.json',plan)
 checkpoint=read(p/'production/checkpoint.json');checkpoint.update(state='source-matched-script-and-editable-scenes-ready',nextAction='Parent generates approved voice once GPU is available; align scenes to actual PCM, extract exact source frames, then coordinate full CPU visual render and four-output QA',blockers=['GPU currently in use; narration not generated','Actual PCM timing, integrated source audio/listening, full moving and mobile-caption QA pending'],mediaProduced='small silent visual previews only')
 checkpoint['actualCompleted']+=['Official independent FHD source sampled and directly viewed','Source-specific Blizzard rights receipt linked','KO/EN opening revised to match observed footage','Scoped TypeScript check: eight owned files, zero diagnostics','Native preview: fixed grass tips, sprite-label clearance, cat/diagram separation and header preload']
 write(p/'production/checkpoint.json',checkpoint)
 ledger=read(p/'production/review-ledger.json')
 ledger['checks']=[x for x in ledger['checks'] if x['name']!='footage-rights-fhd-direct-view']
 ledger['checks'] += [dict(name='footage-rights-fhd-direct-view',status='pass-for-described-source-role',evidence='sources/selected-footage.json',limits=row['viewing']['notObserved']),dict(name='scoped-typecheck',status='pass',command='node projects/shorts-d2r-ultrawide-ai-range/production/check-scenes.cjs',result='8 owned source files, 0 owned diagnostics, 0 dependency diagnostics'),dict(name='visual-previews',status='partial',notes='Single native frames inspected; grass blade roots and sprite labels fixed. Reaction preview revealed occlusion; layout now separates cat/diagram. Header first-frame preload added and checked. Actual caption, mobile and whole movement review remains.')]
 write(p/'production/review-ledger.json',ledger)
 project=read(p/'project.json');project['status']='narration-ready-gpu-wait';write(p/'project.json',project)
 meta=read(p/'publishing/metadata-draft.json')
 meta['descriptionKo']+='\n\n게임 화면: Blizzard Entertainment 공식 게임플레이 자료\n'+row['cuts'][0]['source']['sourceUrl']
 meta['descriptionEn']+='\n\nGameplay: official Blizzard Entertainment gameplay footage\n'+row['cuts'][0]['source']['sourceUrl']
 write(p/'publishing/metadata-draft.json',meta)
print(json.dumps({'narrationReady':list(DATA),'ttsStarted':False,'fullOutputProduced':False}))

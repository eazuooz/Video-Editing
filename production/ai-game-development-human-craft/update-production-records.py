from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,urllib.request
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft';P=ROOT/'projects'/SLUG
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
licenses=P/'sources/licenses';licenses.mkdir(exist_ok=True)
license_urls={'Splatoon-Ink.txt':'https://raw.githubusercontent.com/mixandjam/Splatoon-Ink/10a730cc26d48d9a3f8a34983827291f4ecef5b2/LICENSE','Jammo-Character.txt':'https://raw.githubusercontent.com/mixandjam/Jammo-Character/master/LICENSE'}
for name,url in license_urls.items():
 dest=licenses/name
 if not dest.exists():dest.write_bytes(urllib.request.urlopen(url,timeout=30).read())
manifest=read(P/'sources/source-manifest.json')
for i,f in enumerate(manifest['files']):
 if i<2:f.update(usageStatus='selected-visual-only-license-notice-preserved',review='Whole duration observed in 2fps filmstrip; movement review at capture/edit stage remains pending. Audio omitted.',licenseEvidence=['sources/licenses/Splatoon-Ink.txt','sources/licenses/Jammo-Character.txt','https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html'])
 else:f['usageStatus']='excluded-not-in-cut'
manifest.update(updatedAt=now,rightsNote='Repository permission notice retained verbatim; Jammo Character MIT license separately checked. Mixamo FAQ permits royalty-free rendered commercial use. No Nintendo game footage claim. All source audio excluded.',selectedRanges=read(ROOT/'shared/output'/SLUG/'selected-footage/selection.json'))
manifest['independentGameplay']=[{'sourceId':'wow-nyhver-classic-2020','url':'https://www.youtube.com/watch?v=A2VQbPrw9-g','permissionPage':'https://www.warcraftmovies.com/movieview.php?id=252801','permissionExcerpt':'You are free to use any of my footage/videos.','creator':'Nyhver','published':'2020-03-13','classification':'independent-gameplay','selectionReason':'Original reference discusses persistent art direction. Classic visibly shows exaggerated forms and painted appearance; a rights-cleared newer recording was not secured. Do not identify it as the latest game version.','differences':'Creator notes visual morph/transmog in parts. Judge broad scene forms/colors, not a current default character appearance or measured shader implementation.','audio':'Entire source audio omitted; description lists third-party music.','review':'Initial 16 frames observed; full selected 55s dense visual review pending.'}]
manifest['browserEvidence']={'epic':{'path':'shared/output/'+SLUG+'/source-review/epic-announcement.png','url':'https://www.unrealengine.com/news/the-road-to-ue-6','scope':'Actual official title/date header; brief cropped documentary quotation'},'spark':{'path':'shared/output/'+SLUG+'/source-review/unity-spark.png','url':'https://unity.com/spark','observed':'COMING SOON / Join the waitlist','date':'2026-10-14'},'reddit':{'status':'network-security-blocked','usedInCut':False,'bypassed':False}}
write(P/'sources/source-manifest.json',manifest)
m=read(P/'project.json');m['paths']['scriptEn']=f'projects/{SLUG}/script/narration.en.json'
m['audio']['backgroundMusic']={'required':True,'approvalStatus':'existing-user-approved-calm-track-reused; current-mix-comparison-pending','title':'Wholesome','artist':'Kevin MacLeod','source':'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Wholesome.mp3','license':'CC BY 4.0','attribution':'Wholesome Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/','file':'shared/assets/music/incompetech/Wholesome.mp3','sha256':'9eadc79a1a2cb68cd63be1432ebf8f8ae3387cb9d2e85f9b8dbc74ba5a96b231','priorApproval':'2026-09-26 calm track selection recorded in Wholesome.LICENSE.md','startingLufs':-31}
m['membershipOutro'].update(scenePath=f'motion-canvas/src/projects/{SLUG}/member-scene.tsx',originalScreenshot='shared/assets/membership/member-list-20260929.png',displayedMembers=12,identityMode='original-profile-displayed-handle-and-badge; no invented expansion of truncated handle',renderStatus='source-built-pending-render-review')
write(P/'project.json',m)
plan=read(P/'planning/production-plan.json');plan['status']='production-scenes-and-narration-in-progress'
plan['preproduction']['wholeKoEnScriptAndCausalFlow'].update(status='pass-text-review-rendered-joins-pending',evidence='KO revision3 retained:28 scenes/185 paragraphs. Corresponding EN translation:185 paragraphs; content/order reviewed. Actual caption/audio alignment pending.')
plan['preproduction']['allSceneDetailedSubjectsAndMotionPlan'].update(status='source-built-preflight-in-progress',evidence=f'motion-canvas/src/projects/{SLUG}/scene-data.json; production/{SLUG}/capture-plan.json;12 independent saved Unity scenes. Estimated layout timing is not final narration timing.')
plan['sourceStatus']={'developmentDemo':'Mix and Jam001/002 licensed visual-only clips selected','commercialGameplay':'Nyhver WoW Classic55s selected; dense review pending','announcements':'actual Epic and Unity browser screenshots acquired','unavailable':'Reddit network blocked; no substitute/fabricated comments'}
write(P/'planning/production-plan.json',plan)
design=read(P/'planning/scene-design.json');capture=read(ROOT/'production'/SLUG/'capture-plan.json');cap={s['id']:s for s in capture['scenes']}
for s in design['scenes']:
 s['motionCanvasProject']=f'motion-canvas/src/projects/{SLUG}/scenes/{s["id"]}/project.ts'
 s['timingStatus']='layout-estimate-pending-measured-narration'
 if s['id'] in cap:
  scene=next((ROOT/'unity/VideoEditing/Assets/VideoScenes'/SLUG).glob(s['id']+'-*.unity'))
  s.update(renderer=['Unity','Motion Canvas'],implementationKind='self-authored-engine-explanation',designStatus='saved-and-compilable-preflight-in-progress')
  s['unityProduction']={'project':'unity/VideoEditing','scene':scene.relative_to(ROOT/'unity/VideoEditing').as_posix(),'editor':'6000.6.0f1','pipeline':'URP17.6.0','capture':{'width':1920,'height':1080,'fps':60,'seconds':cap[s['id']]['seconds']},'events':cap[s['id']]['events'],'settings':'Black background; camera-only URP capture; layer31; no fake measured renderer buffers; deterministic C# lesson state.','saveStatus':'saved'}
 if s['id']=='06':s['screenDirection']='실제 UV 좌표를 가진 물약 병과 평면 이미지를 함께 표시하고 같은 셀을 강조한다. Substance Painter의 실제 UI/실행 화면으로 표시하지 않는다.'
 if s['id']=='22':s['sourceIds']=['wow-nyhver-classic-2020']
 if s['id']=='16':s['sourceIds']=['mixandjam-recording-001','mixandjam-recording-002']
write(P/'planning/scene-design.json',design)
ledger=read(P/'production/review-ledger.json')
updates=[{'id':'english-source-paragraph-alignment','status':'pass','scope':'28scene IDs,185 paired paragraphs; original Korean SHA preserved','evidence':f'projects/{SLUG}/script/narration.en.json'}, {'id':'unity-scene-source-build','status':'pass','scope':'12 saved scenes; compilation and5 in-memory transaction assertions','evidence':f'shared/output/{SLUG}/unity-production/build-status.json'}, {'id':'full-narration-production','status':'running','scope':'Qwen3 approved reference; selected-video GPU lease; source chunks retained','evidence':f'shared/output/{SLUG}/narration-job/status.json'}, {'id':'independent-source-rights','status':'selected-visual-ranges-cleared-with-notices','scope':'Mix and Jam001/002,Jammo,Nyhver gameplay; original audio excluded','evidence':f'projects/{SLUG}/sources/source-manifest.json'}, {'id':'full-composite-visual-qa','status':'pending','scope':'Early layout samples exist; final aligned caption and movement review not complete','evidence':f'shared/output/{SLUG}/composite'}, {'id':'narration-level-continuity','status':'pending','scope':'Source/stem/final aligned speech-active400ms/100ms measurements and contextual review required','evidence':None}]
for item in updates:
 ledger['checks']=[c for c in ledger['checks'] if c['id']!=item['id']];ledger['checks'].append(item)
ledger['updatedAt']=now;write(P/'production/review-ledger.json',ledger)
cp=read(P/'production/checkpoint.json');cp.update(updatedAt=now,stage='narration-and-editable-scene-production')
cp.pop('currentInterruption',None)
cp['activeJobs']=[{'kind':'narration','statusFile':f'shared/output/{SLUG}/narration-job/status.json','log':f'shared/output/{SLUG}/narration-run.log'},{'kind':'unity-capture-after-tts','statusFile':f'shared/output/{SLUG}/unity-production/job-status.json'},{'kind':'local-preview-server','port':9199,'scope':SLUG}]
cp['completed']+=['English source aligned to185 Korean paragraphs; Korean narration source unchanged','12 independent Unity scenes saved and compiled;28 editable Motion Canvas scene projects authored','Actual Epic and Unity official-page screenshots acquired; Mix and Jam and creator-permitted WoW visual clips normalized without source audio']
cp['pending']=['Narration completion, full cached ASR text review and caption alignment','All final motion/layout/mobile-caption checks; Unity captures and composite exports','Existing60:40 footage ratio: requested exception has no user answer; do not silently approve','Full mix, local narration-level continuity, current final-mix ASR and four-output integrity','Complete captioned Drive review upload, actual playback/access verification and selective Git','User review of completed Drive version before YouTube']
cp['nextAction']='Continue current narration/capture jobs, complete measured scene/caption timing and final QA. Do not start another video.';write(P/'production/checkpoint.json',cp)
print('Updated current source, plan, scene, audio and checkpoint records; completion gates remain pending.')

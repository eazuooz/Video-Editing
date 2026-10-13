"""Reconcile the existing plan with this completed revision; no production jobs."""
from pathlib import Path
import json, datetime
P=Path(__file__).resolve().parent
R=P.parents[3]
H=P.parents[1]
read=lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
rel=lambda p: p.relative_to(R).as_posix()
planpath=H/'planning/production-plan.json'
j=read(planpath)
t=read(P/'final-timeline-v1.json')
review=read(P/'final-direct-review-v1.json')
assert review['approvedForPrivateUpload']
n=read(P/'narration.ko.json')
settings=read(P/'publishing/private-settings-direct-review-v1.json')
assert settings['privateSavedAndReopened'] and settings['fullAvailableSettingsVerified']
j.update(updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='private-delivered-awaiting-user-review',nextAction='Finish the selected Git delivery, then stop for user review. No next video, scheduling or replacement.')
j['scripts']={'ko':rel(P/'narration.ko.json'),'en':rel(P/'narration.en.json'),'status':'current-independent-27-paired-paragraphs-reviewed'}
j['sourceCapacity'].update(status='independent-sources-rendered-and-reviewed',duration=t['totalFrames']/t['fps'],bodyFrames=t['bodyFrames'],actualFrames=t['actualFrames'],explanationFrames=t['explanationFrames'],evidence=rel(P/'final-timeline-v1.json'))
j['preservation'].update(combinedScenes=len(n['scenes']),combinedParagraphsPerLanguage=27,currentScriptPreservationStatus='User-selected Pokemon introduction and independent explanations adopted; unchanged approved PCM retained with current splice evidence.')
j['audio'].update(sourceSfxRestored=True,currentMixReview=rel(P/'mix-direct-review-v1.json'),sourceSfxAvailability='Quiet native game/menu audio retained; two dense passages ducked under narration. No claim of isolated effects.',humanListening=False)
if 'inputHashes' in j:
    j['historicalInputHashes']=j.pop('inputHashes')
j['currentEvidence']={'finalReview':rel(P/'final-direct-review-v1.json'),'collection':rel(P/'collection-verification-v2.json'),'settings':rel(P/'publishing/private-settings-direct-review-v1.json'),'voicePreservation':rel(P/'current-voice-splice.json')}
old={s['id']:s for s in j['sceneDesigns']}
designs=[]
for scene in n['scenes']:
    row=old.get(scene['id'],dict(id=scene['id'],palette='research-paper-white-v1',captionCenter=[960,970],captionReservedY=[894,1080],narrationParagraphs=3))
    row['title']=scene['title']
    row['timing']='Final measured frame timing in final-timeline-v1.json; current captions and all planned samples reviewed.'
    row['renderer']='Motion Canvas'
    row['rendererReason']='Document rows, indentation and semantic highlights explain the relationship directly; a spatial simulation is unnecessary.'
    if scene['id'] in ['01','01a']:
        row['visual']='Independent Pokemon Red gameplay with authored flat-list and indented planning-document diagrams; explicitly not an original developer document.'
    designs.append(row)
j['sceneDesigns']=designs
j['reference']['extraGames']=['Pokémon Red — explicit user-selected early-game planning example']
for row in j['referenceAlignment']:
    if row['source']=='01:24–01:56':
        row['retain']='Distinguish personal working notes from a polished document for others; the latest user request removes biography and all spoken/on-screen creator-name references.'
        row['ppt']='Compare working questions and a reader-facing specification in independently authored explanations.'
j['approvals']['postUploadUserReview']['status']='pending'
j['currentPrivateVideoId']=settings['videoId']
planpath.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'plan':rel(planpath),'videoId':settings['videoId'],'scenes':len(designs),'nextVideo':False}))

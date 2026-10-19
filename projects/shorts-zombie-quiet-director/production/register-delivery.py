"""Register observed final artifacts and Drive evidence; never publish a video."""
from pathlib import Path
import json,hashlib,datetime,argparse
P=Path(__file__).resolve().parents[1]; R=P.parents[1];L=P/'production/local'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--playback',action='store_true');args=parser.parse_args()
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 controlpath=R/'shared/publishing/video-production-control.json';control=read(controlpath);owned=control['shortsRecurringAuthorization'];assert owned['selectedShort']==P.name
 collected=read(P/'production/delivery-output.json'); master=next(f for f in collected['files'] if f['name'].endswith('.captioned.mp4'))
 assert master['sha256']=='537988bd6f023da3e06645c2eff2baa770b1a37cc06ac6b40fc6e28d2439d6a4'
 assert sha(R/collected['directory']/master['name'])==master['sha256']
 integrity=read(L/'integrity.json');assert integrity['status']=='pass' and integrity['identicalAac']
 receipt=dict(fileId='1ZKIJqek3v14DBJ0r4TSbM5C7LImE3E6z',
  url='https://drive.google.com/file/d/1ZKIJqek3v14DBJ0r4TSbM5C7LImE3E6z/view?usp=drivesdk',
  revisionId='0B__JCPwFbAsxdDRzRWh1SXM1NlJRaVFOQXkzZk1FZDFDbHNFPQ',
  bytes=13127972,sourceSha256=master['sha256'],source=collected['directory']+'/'+master['name'],
  remoteChecksum='not returned by connector; source upload hash recorded, remote bytes readback matches',
  access='owner-only observed from metadata and Drive UI; unchanged',
  uploadCompleted=True,metadataReadback=True,playback='complete44.2secFHD observed' if args.playback else 'processing',
  humanReview='pending this exact version',youtubeUploadAuthorized=False,recordedAt=now)
 if args.playback:
  proof=read(P/'publishing/drive-playback.json');assert proof['fileId']==receipt['fileId'] and proof['ended'] and abs(proof['duration']-44.2)<.08 and proof['width']==1080 and proof['height']==1920
  receipt['playbackEvidence']='projects/'+P.name+'/publishing/drive-playback.json'
 save(P/'publishing/drive-receipt.json',receipt)
 visual=dict(status='pass for inspected current visual scope',masterSha256=master['sha256'],
  allCaptionCues=26,sourceCutBoundaries=8,diagramPhases='before/sound/move/result and equal-threat-block spacing inspected',
  native1080=True,mobileWidth=375,contactSheets='production/local/qa/sheet-01..04.jpg',
  movingPlayback='375px browser video played through44.2s; phase/cat/crop frame sequences separately inspected',
  limits='Sampled moving output, not continuous human audiovisual listening',
  sourceFix='full-v1 upper source label intersected header; moved outside cat transform in full-v2; corrected actual-game ranges rechecked',
  captionAndCatClearance='fixed510,1380 max2lines; native780px lower-right cat yields player area; labels and credits cleared',
  pureDiagramEvidenceRetained='same diagram code/timing/ASS; no animation change in label-only repair')
 save(P/'production/visual-review.json',visual)
 ledger=read(P/'production/review-ledger.json');ledger['entries']=[e for e in ledger['entries'] if e['kind']=='explicit-new-human-selection']+[
  dict(kind='primary-claims-and-independent-footage',result='pass',sources=['sources/claims.json','sources/footage-candidates.json'],limits='PZ quiet footage is context, not proof of actual meta-event causation'),
  dict(kind='voice-and-final-mix',result='text completeness and technical continuity checked; listening pending',evidence='production/audio-review.json',mixSha256=read(L/'audio-build.json')['artifacts']['final-mix.m4a']['sha256']),
  dict(kind='current-output-integrity',result='pass',cleanAndCaptionedDecoded=True,frames=2652,width=1080,height=1920,fps=60,identicalAAC=True,evidence='production/local/integrity.json'),
  dict(kind='caption-visual-review',result='pass within recorded scope',evidence='production/visual-review.json'),
  dict(kind='four-file-collection',result='pass',evidence='production/delivery-output.json'),
  dict(kind='drive-final-review-copy',result=receipt['playback'],evidence='publishing/drive-receipt.json',humanApproval='pending')]
 ledger['pending']=['Human final review of exact Drive master, including pronunciation and contextual loudness listening','YouTube upload only after exact-version review approval']
 save(P/'production/review-ledger.json',ledger)
 checkpoint=read(P/'production/checkpoint.json');checkpoint.update(stage='awaiting-human-drive-final-review' if args.playback else 'drive-playback-processing',driveId=receipt['fileId'],humanFinalReview='pending exact44.2sec master',next='Wait for final human review; do not start another video',nextAction='Wait for final human review',youtubeUploaded=False,currentMasterSha256=master['sha256']);checkpoint['voice']['fullTextDirectReview']='All11linespresent in whole voice and mix; independent context repeated three lexical variants, pronunciation remains pending human listening';save(P/'production/checkpoint.json',checkpoint)
 project=read(P/'project.json');project['status']=checkpoint['stage'];project['finalRender']=dict(complete=True,captionedSha256=master['sha256'],durationSeconds=44.2,width=1080,height=1920,fps=60,openItems=['최종 청취: 좀보이드·총성·레포데 발음과 게임/BGM 음량']);project['driveFinalReview']=receipt;save(P/'project.json',project)
 plan=read(P/'planning/production-plan.json');plan.update(status=checkpoint['stage'],humanFinalReview='pending exact Drive version',lockedTiming='projects/'+P.name+'/production/visual-timing.json');plan['explicitGameSelection']=dict(games=['Left4Dead: cooperativeFPS','ProjectZomboid: isometricsurvival'],nintendoCount=0,total=2,reason='Latest direct user nominated these two games; do not add an unrelated third example to this Short');save(P/'planning/production-plan.json',plan)
 publishing=read(P/'publishing/plan.json');publishing.update(driveFinalReview=receipt,durationSeconds=44.2,masterSha256=master['sha256'],youtubeId=None,humanApproval='pending complete exact version');save(P/'publishing/plan.json',publishing)
 workpath=R/'shared/publishing/shorts-worklist.json';work=read(workpath);row=next(r for r in work['rows'] if r['slug']==P.name);row.update(productionStatus='complete44.2secFHD60',reviewStatus='awaiting-final-human-review' if args.playback else 'Drive processing',status=checkpoint['stage'],activeReviewSlot=True,userApproval='pending exact Drive version',driveId=receipt['fileId'],driveFinalReview=receipt,durationSeconds=44.2,youtubeId=None);row.pop('production',None);row.pop('review',None);work['updatedAt']=now;save(workpath,work)
 owned['latestSelection'].update(productionStatus=checkpoint['stage'],driveFinalReview=receipt,humanReview='pending exact version');save(controlpath,control)
 print(json.dumps(dict(stage=checkpoint['stage'],masterSha256=master['sha256'],drive=receipt['fileId'])))
if __name__=='__main__':main()

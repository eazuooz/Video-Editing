"""06.02 held-note correction PROGRESS only. Dry-run by default; no process launch."""
import argparse,copy,hashlib,json,os,uuid
from datetime import datetime,timezone
from pathlib import Path
R=Path('D:/Github/VideoEditing');B=R/'production/batches/architectural-111-20261106';C=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106');P=R/'projects/shorts-leveldesign-06-02';T=C/P.name
TIMELINE=T/'film-timelines-v2/f698557a95210fdb9e42d484/timeline.json';TSHA='bd9974dbab5f3becaaf4d5221bdb16df88fff72006fbdd89f72d13992081e734'
RENDERER=B/'render-prospect-refuge-film-v2.py';RSHA='3ba569d8b8340e338f5ab58e2be1c0944af58e6466bca8b1b69f8d75b421abe9';PREFLIGHT=P/'held-note-composite-preflight-v2.json';STATE=C/'06-02-composite-progress.json'
OLD=T/'local-final-review/aa005b98aff7d6c236bb1383';MASTER='5fb5621f810943510371c7f394490de0dae7f73619262358a1854d81f89c136e';KEY='architectural111Batch20261106';PHASE='06.02-held-note-correction;new-full-software-render-active'
FILES=[P/'project.json',P/'checkpoint.json',B/'batch.json',B/'checkpoint.json',B/'worklist.json',B/'continuation.json',R/'shared/publishing/video-worklist.json',R/'shared/publishing/shorts-worklist.json']
def need(ok,why):
 if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def dump(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def path(value):
 q=Path(value);return q.resolve()if q.is_absolute()else(R/q).resolve()
def actual(args):
 need(args.preflight_sha256 and Path(args.preflight).resolve()==PREFLIGHT.resolve()and sha(PREFLIGHT)==args.preflight_sha256,'Actual root preflight path/SHA is required; no fixture substitute')
 need(sha(TIMELINE)==TSHA and sha(RENDERER)==RSHA,'New timeline/renderer changed')
 q=read(PREFLIGHT);need(q.get('schemaVersion')=='06-02-held-note-composite-preflight-v2'and q.get('topicId')=='06.02'and q.get('timeline')==pin(TIMELINE)and q.get('renderer')==pin(RENDERER),'Wrong preflight/source binding')
 need(q.get('actualAgentVisualInspection')is True and q.get('inspectedFrames')==[510,28251]and q.get('blockingIssues')==[],'Actual new510/28251 compositor pixel preflight is pending/blocked')
 need(all(q.get(k)is False for k in('actualWholeListening','actualRealtimePlayback','humanApproval')),'Preflight is not hearing/user approval')
 control=read(R/'shared/publishing/video-production-control.json')['explicitArchitectural111Batch20261106'];need(control.get('userEvidence')=='111개 전체 제작 들어가줘'and control.get('status')not in('paused','stopped','cancelled')and control.get('youtubeAuthorized')is False,'Exact111 control not active')
 cp=read(B/'checkpoint.json');need(cp.get('currentTopicId')=='06.02'and cp.get('completedLocalReviewCount')==2,'Preserve advanced selection/completion state')
 old=read(OLD/'review-receipt.json');need(old['metadata']['masterSHA256']==MASTER,'Wrong old blocked technical version')
 prior=read(old['pins']['timeline']['path']);current=read(TIMELINE);need({k:v for k,v in prior.items()if k not in('inputs','fingerprint')}=={k:v for k,v in current.items()if k not in('inputs','fingerprint')},'Audio/captions/geometry/clocks/cuts/cat changed')
 inputs=copy.deepcopy(prior['inputs']);matches=[r for r in inputs if r['role']=='renderer'];need(len(matches)==1,'One renderer input required');matches[0].update(path=str(RENDERER.resolve()),sha256=RSHA);need(inputs==current['inputs'],'A non-renderer input changed')
 state_bytes=STATE.read_bytes();worker=json.loads(state_bytes.decode('utf-8-sig'));need(worker.get('protocol')=='architectural111-06-02-composite-v1'and worker.get('owner')=='architectural-111-06-02-composite'and worker.get('timelineSHA256')==TSHA and worker.get('status')=='owned-software-compositing'and worker.get('complete')is False,'Actual live FULL new renderer state required')
 import psutil
 process=psutil.Process(worker['pid']);argv=process.cmdline();created=process.create_time();need(process.is_running()and abs(created-worker['createTime'])<1e-6,'Worker identity is stale')
 script_at=next((i for i,a in enumerate(argv)if path(a)==RENDERER.resolve()),-1);tail=argv[script_at+1:]
 need(script_at>=0 and len(tail)==3 and tail.count('--execute')==tail.count('--timeline')==1 and path(tail[tail.index('--timeline')+1])==TIMELINE.resolve(),'Worker argv is not exact new FULL compositor; sample flags/abbreviations/extra arguments forbidden')
 need(worker.get('gpuEncoding')is False and worker.get('modelsStarted')is False and path(worker['output']).is_relative_to((T/'render-attempts-v2').resolve()),'Unexpected worker/output scope')
 identity=dict(pid=worker['pid'],createTime=created,argv=argv,commandSHA256=hashlib.sha256(json.dumps(argv,ensure_ascii=False,separators=(',',':')).encode()).hexdigest())
 need(STATE.read_bytes()==state_bytes,'Worker state advanced during observation; retry read-only')
 return worker,identity,old,current

def prepare(args):
 worker,identity,old,timeline=actual(args);before={p:p.read_bytes()for p in FILES};docs={p:json.loads(v.decode('utf-8-sig'))for p,v in before.items()};now=datetime.now(timezone.utc).isoformat()
 previous=dict(status='PREVIOUS-pixel-blocked-technical-version-not-delivered',captionedMasterSHA256=MASTER,renderManifest=old['pins']['renderManifest'],technicalReview=pin(OLD/'review-receipt.json'),officialCollection=pin(OLD/'official-collection.json'),encodedAudioReview=old['pins']['encodedAudioReview'],preflight=pin(P/'composite-preflight-visual-review-v1.json'),pixelBlocker=pin(C/'06-02-encoded-pixel-peer-v1.json'))
 step='Continue only current06.02 held-note visual correction. New510/28251 preflight passed; full software encode is active. After actual new outputs, recheck encoded pixels/technical four outputs and prove audio identity before evidence reuse. Old5fb/aa005 remains blocked, not delivered. Count stays2;11.05 is not started; whole listening/realtime/user review remain pending.'
 for p in(P/'project.json',P/'checkpoint.json',B/'checkpoint.json',B/'continuation.json'):
  d=docs[p];v=d['currentProduction'];need(v.get('topicId')=='06.02','Foreign current production')
  v.update(phase=PHASE,observedAt=now,previousBlockedTechnicalVersion=copy.deepcopy(previous),actualFilmTimeline=pin(TIMELINE),currentCompositeWorker=worker,currentCompositeWorkerAlive=True,actualFullCompositorProcesses=[identity],compositePreflightVisualReview=pin(PREFLIGHT),completeFinalFilm=False,actualEncodedQaComplete=False,finalOutputsVerified=False,actualListening=False,fullRealtimePlayback=False,humanApproval=False,platformActions=[],nextStep=step)
  d.update(updatedAt=now,nextStep=step)
 project=docs[P/'project.json'];project.setdefault('heldNoteOperativeAliasHistory',[]).append(dict(recordedAt=now,values={k:copy.deepcopy(project.get(k))for k in('currentNarration','nativeVisualQa')}));project.update(status=PHASE,currentStage=PHASE,currentNarration=pin(P/'narration-expanded-draft-v4.json'),nativeVisualQa=pin(P/'native-voice-qa-v3.json'),publishReady=False,finalOutputsVerified=False)
 oldpaths={k:project.get('paths',{}).get(k)for k in('videoBurnedCaptions','videoClean','captionsKo','captionsEn','captionAlignmentReview')if k in project.get('paths',{})}
 for value in oldpaths.values():need(path(value).is_relative_to((P/'production/local/publishing-source'/MASTER).resolve()),'Preserve unexpected operative official path')
 project['currentProduction']['previousBlockedTechnicalVersion']['projectPaths']=oldpaths
 for key in oldpaths:project['paths'].pop(key)
 chk=docs[P/'checkpoint.json'];chk.setdefault('heldNoteOperativeAliasHistory',[]).append(dict(recordedAt=now,values={k:copy.deepcopy(chk.get(k))for k in('draftParagraphCount',)}));chk.update(stage=PHASE,phase=PHASE,draftParagraphCount=25,currentDraftParagraphCount=25,currentFiniteWorkerRunning=True,currentGpuJobActive=False,finalOutputsVerified=False,actualHumanReview=False)
 for p,key in((B/'batch.json','projects'),(B/'worklist.json','rows')):
  d=docs[p];need(len(d[key])==111,'Exact111 rows required');row=next(r for r in d[key]if r['topicId']=='06.02');need(not row.get('productionComplete'),'Preserve real delivered state');row.update(status=PHASE,productionComplete=False,finalOutputsVerified=False,humanApproval=False,platformStatus='not-uploaded',nextStep=step);d.update(updatedAt=now,currentPhase=PHASE)
 cp=docs[B/'checkpoint.json'];cp.setdefault('heldNoteOperativeAliasHistory',[]).append(dict(recordedAt=now,values=dict(currentProjectCheckpoint=copy.deepcopy(cp.get('currentProjectCheckpoint')))));cp.update(phase=PHASE,nextSelectedTopicId='06.02',completedLocalReviewCount=2,currentGPUJobActive=False,ownFiniteQueueRunning=True,finalOutputsVerified=False,nextStep=step)
 continuation=docs[B/'continuation.json'];continuation.update(currentFirstStep=step,currentTopicId='06.02',nextSelectedTopicId='06.02')
 for d in(cp,continuation):d.update(currentSelectedProject=dict(path=str(P/'project.json'),sha256=hashlib.sha256(dump(project)).hexdigest()),currentSelectedCheckpoint=dict(path=str(P/'checkpoint.json'),sha256=hashlib.sha256(dump(chk)).hexdigest()))
 cp['currentProjectCheckpoint']=copy.deepcopy(cp['currentSelectedCheckpoint'])
 for p,key in((B/'batch.json','projects'),(B/'worklist.json','rows')):next(r for r in docs[p][key]if r['topicId']=='06.02')['currentCheckpoint']=copy.deepcopy(cp['currentSelectedCheckpoint'])
 for p in FILES[-2:]:
  row=docs[p][KEY];need(row.get('completedLocalReviewCount')==2 and row.get('youtubeAuthorized')is False,'Preserve shared completion/boundaries');row.update(updatedAt=now,status='two-local-final-reviews-ready;06.02-held-note-correction-active',currentTopicId='06.02',currentSelectedTopicId='06.02',nextSelectedTopicId='06.02',currentStage=PHASE,currentCheckpoint=dict(path=str(B/'checkpoint.json'),sha256=hashlib.sha256(dump(cp)).hexdigest()))
 for p,key in((B/'batch.json','projects'),(B/'worklist.json','rows')):need([r for r in read(p)[key]if r['topicId']!='06.02']==[r for r in docs[p][key]if r['topicId']!='06.02'],'Other110 rows changed')
 for p in FILES[-2:]:
  original=json.loads(before[p].decode('utf-8-sig'));need({k:v for k,v in original.items()if k!=KEY}=={k:v for k,v in docs[p].items()if k!=KEY},'Foreign shared key changed');need({k:v for k,v in original[KEY].items()if k.startswith('latest')}=={k:v for k,v in docs[p][KEY].items()if k.startswith('latest')},'Latest DELIVERED07 must remain')
 need(docs[B/'batch.json'].get('completedLocalReviewCount')==2 and docs[B/'continuation.json'].get('latestLocalDelivery')==json.loads(before[B/'continuation.json'].decode('utf-8-sig')).get('latestLocalDelivery'),'Delivery count/history changed')
 return before,{p:dump(docs[p])for p in FILES},identity

def cas(p,expected,replacement):
 need(p.read_bytes()==expected,'Concurrent edit; preserve '+str(p));tmp=p.with_name(p.name+'.held-note-'+uuid.uuid4().hex+'.tmp')
 try:
  with tmp.open('xb')as f:f.write(replacement);f.flush();os.fsync(f.fileno())
  need(p.read_bytes()==expected,'Concurrent edit before replace');os.replace(tmp,p)
 finally:
  if tmp.exists():tmp.unlink()
def main():
 q=argparse.ArgumentParser(description=__doc__);q.add_argument('--preflight',default=str(PREFLIGHT));q.add_argument('--preflight-sha256');q.add_argument('--execute',action='store_true');args=q.parse_args()
 try:
  before,after,identity=prepare(args);result=dict(ready=True,dryRun=not args.execute,phase=PHASE,worker=identity,ownedJsonFiles=[str(p)for p in FILES],completedLocalReviewCount=2,newMasterSHA256=None,latestDeliveredUnchanged=True,humanApproval=False,platformActions=[])
  if args.execute:
   actual(args);need(all(p.read_bytes()==before[p]for p in FILES),'Metadata advanced; retry without overwrite');folder=C/'06-02-held-note-progress-history'/uuid.uuid4().hex;folder.mkdir(parents=True,exist_ok=False);changed=[]
   for i,p in enumerate(FILES):(folder/(str(i)+'-'+p.name)).write_bytes(before[p])
   try:
    for p in FILES:cas(p,before[p],after[p]);changed.append(p)
    result.update(source=pin(__file__),backups=str(folder),updatedFiles=[pin(p)for p in FILES]);(folder/'receipt.json').write_bytes(dump(result))
   except Exception as error:
    for p in reversed(changed):
     if p.read_bytes()==after[p]:cas(p,after[p],before[p])
    (folder/'failed-preserved.json').write_bytes(dump(dict(error=repr(error),complete=False)));raise
  print(json.dumps(result,ensure_ascii=False));return 0
 except Exception as error:print(json.dumps(dict(ready=False,dryRun=not args.execute,reason=str(error),metadataMutationAttempted=bool(args.execute),platformActions=[]),ensure_ascii=False));return 1 if args.execute else 0
if __name__=='__main__':raise SystemExit(main())

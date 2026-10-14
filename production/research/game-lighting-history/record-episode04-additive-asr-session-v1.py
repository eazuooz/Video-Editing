from pathlib import Path
import datetime,hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
def write(p,j):
 t=p.with_name(p.name+'.writing-'+str(os.getpid()));t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
state=read(BASE/'additive-asr-execution-v1.json');i=state['actualIdentity'];p=psutil.Process(i['pid'])
if abs(p.create_time()-i['createTime'])>.1 or p.cmdline()!=i['command']:raise RuntimeError('ASR identity mismatch')
selected=read(BASE/'additive-tts-selected-execution-v2.json');hpath=ROOT/selected['researchHandoff']['path'];h=read(hpath)
if h['state']!='research_resume_verified' or h['ttsExitCode']!=0:raise RuntimeError('Research restoration not observed')
record=dict(observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),session=43451,actualIdentity=i,actualIdentityLive=True,execution=rec(BASE/'additive-asr-execution-v1.json'),status=state['status'],completedWindows=len(state['completed']),expectedWindows=48,log='projects/game-lighting-history-04/production/local/additive-asr-v1.log',cpuThreads=2,gpuJobs=0,researchHandoff=rec(hpath),researchRestoredVerified=True,original87AsrRepeated=False,wholeAsrApproved=False,independentContextsApproved=False,finalMixedAsrApproved=False,finalVideoProduced=False)
write(BASE/'additive-asr-session-v1.json',record)
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=read(cp)
c.update(updatedAt=record['observedAt'],stage='episode04-selected24-original87-byte-preserved-CPU48-window-ASR',ownedJobsRunning=[record],ownedGpuJobs=0)
c['episode04AdditiveNarration'].update(currentState='selected24-22unchanged2-retakes-all-stored-tail-pass-research-restored-CPU-ASR-running',generationComplete=True,technicalTailPassed=24,currentSelectedExecution=rec(BASE/'additive-tts-selected-execution-v2.json'),scopedRetakeExecution=rec(BASE/'additive-tail-repair-execution-v2.json'),scopedRepairSessionClosed=38924,scopedRepairSessionHistorical=c['episode04AdditiveNarration'].get('scopedRepairSession'),currentResearchHandoff=rec(hpath),currentAsrSession=record,measuredReviewAssembly=rec(BASE/'additive-unmixed-review-assembly-v1.json'),measuredUnmixedSeconds=read(BASE/'additive-unmixed-review-assembly-v1.json')['audio']['durationSeconds'],fullNewAsrApproved=False,finalMixedAsrApproved=False,finalApproved=False)
c['next']='Directly compare all24 new whole results and24 independent complete splice contexts as they finish; preserve original87 PCM. Prepare narration-timed projected2.5D scenes, relevant native intervals and tracked annotations; final timing/render/QA/upload remain pending.'
write(cp,c);print(json.dumps(dict(session=43451,pid=i['pid'],completed=len(state['completed']),gpuJobs=0)))

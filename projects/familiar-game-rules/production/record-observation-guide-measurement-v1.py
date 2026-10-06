"""Record already closed synthesis and exact new PCM lengths; measurement is not approval."""
from pathlib import Path
from datetime import datetime,timezone
import array,hashlib,json,os,time,wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
dest=BASE/'observation-guide-measurement-v1.json';assert not dest.exists()
executionPath=BASE/'observation-guide-tts-execution-v1.json';tts=read(executionPath)
assert tts['exitCode']==0 and tts['generationComplete'] and len(tts['results'])==8 and tts['actualExitObserved']
request=read(BASE/'observation-guide-tts-request-v1.json')
assert sha(BASE/'observation-guide-tts-request-v1.json')==tts['requestSha256']
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
rows=[]
for r in tts['results']:
    p=ROOT/r['path'];assert sha(p)==r['sha256']
    with wave.open(str(p),'rb') as w:
        assert w.getframerate()==24000 and w.getnchannels()==1 and w.getsampwidth()==2
        samples=w.getnframes();pcm=w.readframes(samples)
    a=array.array('h',pcm);assert samples==r['samples'] and max(abs(v) for v in a)>0
    rows.append({**r,'pcmBytesSha256':hashlib.sha256(pcm).hexdigest(),'peakInt16':max(abs(v) for v in a),'samplesChecked':True,
        'channels':1,'sampleWidthBytes':2,'technicalAsrApproved':False,'humanWholeListening':'pending','pronunciation':'pending'})
totalSamples=sum(x['samples'] for x in rows);total=totalSamples/24000
measurement=dict(schemaVersion=1,slug='familiar-game-rules',measuredAt=now(),synthesisExecution=rel(executionPath),synthesisExecutionSha256=sha(executionPath),
    measurements=rows,newGuideSamples=totalSamples,totalNewGuideSeconds=total,original11PcmSeconds=296.72,combinedUnmixedSpeechSeconds=296.72+total,
    originalSixWhiteSeconds=147.2,originalActualSpeechSeconds=149.52,overviewSeconds=24.32,allOriginalPcmAndScriptHashesMatched=True,
    perGameNewGuideSeconds={parent:sum(x['seconds'] for x in rows if x['parentScene'] in parents) for parent,parents in [('AngerFoot',['02','04']),('Gunbrella',['06']),('Pedro',['08','10'])]},
    sourceCandidateSeconds=233.467,sourceCandidateIsFinalTiming=False,additiveExplanationProposal=rel(BASE.parent/'planning/additive-explanation-proposal-v1.json'),
    finalWordActionAlignment=False,finalTimingApproved=False,bodyRatioApproved=False,technicalAsrApproved=False,finalMixedAsrApproved=False,
    endingHeuristicIsApproval=False,humanWholeListening='pending',pronunciation='pending',newGitImages=0)
save(dest,measurement)
qpath=PROOF.parent/'queue.json';q=read(qpath);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
item.update(stage='all8new-guide-PCM-measured-awaiting-new-whole-ASR',updatedAt=now(),
    observationGuideMeasurement=dict(path=rel(dest),newGuideSeconds=total,original11PcmSecondsPreserved=296.72,originalSixWhiteSecondsPreserved=147.2,combinedSpeechSeconds=296.72+total,technicalAsrApproved=False),
    nextAction='Only8newguide whole-ASR→direct text/word/end comparison→complete independent contexts. Preserve original11PCM296.72s/white147.2s. Adopt meaningful new comparisons only after currentword boundaries; final native/cue/ratio/mix/render/private pending.')
item['execution'].update(alive=False,status=tts['status'],completed=8,total=8,activeTasks=[],exitCode=0,actualExitObserved=True,sessionId=81540)
q.update(updatedAt=now(),lastProgressAt=now());save(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','execution','observationGuideMeasurement','nextAction']:d[k]=item[k]
    save(p,d)
print(json.dumps({k:measurement[k] for k in ['totalNewGuideSeconds','combinedUnmixedSpeechSeconds','originalSixWhiteSeconds','perGameNewGuideSeconds','finalTimingApproved']},ensure_ascii=False))

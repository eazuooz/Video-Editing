"""Move a verified interrupted onset into its intact paragraph; preserve every source sample."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'measured-current17-plan-v2.json';audit=R/'current17-first-onset-placement-audit-v1.json';assert not out.exists() and not audit.exists()
old=read(R/'measured-current17-plan-v1.json');plan=copy.deepcopy(old);s=next(v for v in plan['scenes'] if v['id']=='07b')
path=ROOT/s['voice'];assert sha(path)==s['audioSha256']
with wave.open(str(path),'rb') as w:
 assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
 raw=w.readframes(w.getnframes());pcm=np.frombuffer(raw,dtype='<i2').astype(float)
quiet=pcm[round(8.16*24000):round(8.26*24000)];assert np.max(np.abs(quiet))==0
cut_old=round(8.32*24000);cut_new=round(8.21*24000)
assert float(np.sqrt(np.mean(pcm[cut_old-96:cut_old+96]**2)))>2000
assert np.max(np.abs(pcm[cut_new-96:cut_new+96]))==0
first=s['parts'][0];assert first['voiceSegments'][0]['outSeconds']==8.32 and first['voiceSegments'][1]['inSeconds']==8.32
first['voiceSegments'][0]['outSeconds']=8.21;first['voiceSegments'][1].update(inSeconds=8.21,offsetFrame=984)
first['purpose']='P1 remains complete through its own8.16s repair PCM and50ms of the verified100ms zero gap. P2 begins at output984 with the rest of the zero gap and its intact onset; no speech crosses the observation pause. Red-cube words move only33ms earlier versus the previous fragment alignment; final narrated pixels remain pending.'
s['paragraphAndSentenceBoundaries'][1]=8.21
placements=[v for v in plan['voicePlacements'] if v['sceneId']=='07b']
assert placements[0]['sourceEndSample']==placements[1]['sourceStartSample']==cut_old
placements[0]['sourceEndSample']=cut_new
placements[1].update(sourceStartSample=cut_new,destinationStartSample=(s['startFrame']+984)*400)
s['voicePlacements']=placements
for part in s['parts']:
 if part['id']==first['id']:assert placements[1]['destinationStartSample']+placements[1]['sourceEndSample']-placements[1]['sourceStartSample']<=part['endFrame']*400
for sid in [v['id'] for v in plan['scenes']]:
 rows=sorted([v for v in plan['voicePlacements'] if v['sceneId']==sid],key=lambda v:v['sourceStartSample']);cursor=0
 for row in rows:assert row['sourceStartSample']==cursor;cursor=row['sourceEndSample']
 with wave.open(str(ROOT/rows[0]['voice']),'rb') as w:assert cursor==w.getnframes()
ordered=sorted(plan['voicePlacements'],key=lambda v:v['destinationStartSample'])
assert all(a['destinationStartSample']+a['sourceEndSample']-a['sourceStartSample']<=b['destinationStartSample'] for a,b in zip(ordered,ordered[1:]))
assert plan['totalFrames']==51186 and plan['actualFrames']==30280 and plan['explanationFrames']==20186 and abs(plan['ratioErrorFrames'])<=1
plan.update(schemaVersion=2,preparedAt=datetime.now(timezone.utc).isoformat(),supersedesPlan='measured-current17-plan-v1.json',supersedesPlanSha256=sha(R/'measured-current17-plan-v1.json'),sourceFirstParagraphPlacementRepaired=True,currentMixedAudioApproved=False,encodedFinalTimingApproved=False)
plan['metadataCorrections'].append('07b p1->p2 junction8.21 lies inside exact8.16..8.26 zero seam;8.32 was inside the first voiced onset. Offset984 retains full p2 onset without changing video frames or any PCM bytes.')
out.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
windows=[dict(start=t/100,end=(t+1)/100,rms=float(np.sqrt(np.mean(pcm[t*240:(t+1)*240]**2))),peak=float(np.max(np.abs(pcm[t*240:(t+1)*240])))) for t in range(810,845)]
audit.write_text(json.dumps(dict(schemaVersion=1,observedAt=plan['preparedAt'],sourcePath=s['voice'],sourceSha256=s['audioSha256'],sourceWholeAsr='first-paragraph-spliced-whole-asr-v1.json',wholeWordFirstP2='먼저8.32..8.48 approximate recognizer times; actual onset already voiced at8.30..8.32',sourceRmsWindowsDirectlyRead=windows,oldCutSeconds=8.32,oldCutRms8ms=float(np.sqrt(np.mean(pcm[cut_old-96:cut_old+96]**2))),verifiedExactZeroGap=[8.16,8.26],newCutSeconds=8.21,newCutRms8ms=0,oldMixHeld='current-mix-execution-v1.json',oldWhole17AsrActualSession=55087,oldWhole17AsrExit=0,oldWhole17AsrIsNotFinalAudioApproval=True,boundaryProposalsV1V2Held=True,newPlan=out.name,newPlanSha256=sha(out),all17OriginalPcmSamplesPreserved=True,ttsRequested=False,mediaRendered=False,finalNarrationTimedPixelsApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(newPlan=out.name,verifiedQuietCut=8.21,allSourceSamplesPreserved=True,frames=51186,oldMixHeld=True,ttsRequested=False)))

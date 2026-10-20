"""Record direct current transcript decisions and normalization/terminal evidence."""
from pathlib import Path
import hashlib,importlib.util,json,time
import numpy as np
import soundfile as sf
import psutil
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v7_direct_analysis',H/'voice-analysis.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);c=a.c
def main():
 c.validate(preserve_pcm=True);script_file=c.P/'script/revision-v7-two-part/part-01.ko.json';script=c.read(script_file);voice=c.read(H/'voice-input.json');caps=c.read(H/'caption-plan.json')
 alignment=c.read(c.O/'source-alignment.json');assert alignment['sceneCount']==21 and alignment['paragraphCount']==135 and not alignment['pending']
 _,norm=a.alignment_helpers();source={s['id']:s for s in script['scenes']};paragraphs=0
 for display,spoken in zip(script['scenes'],voice['scenes']):
  assert display['id']==spoken['id']
  for x,y in zip(display['lines'],spoken['lines']):assert norm(x)==norm(y);paragraphs+=1
 counts={};cue_count=0
 for row in caps['cues']:
  text=source[row['scene']]['lines'][row['line']-1];lo,hi=row['sourceKoOffset'],row['sourceKoEnd'];assert text[lo:hi]==row['sourceKo']
  begin=len(norm(text[:lo]));end=len(norm(text[:hi]));key=(row['scene'],row['line'])
  assert end-begin==len(norm(row['sourceKo']))and begin==counts.get(key,0);counts[key]=end;cue_count+=1
 for sid,s in source.items():
  for i,line in enumerate(s['lines'],1):assert counts[(sid,i)]==len(norm(line))
 assert paragraphs==135 and cue_count==386
 for scene in alignment['scenes']:
  starts=[v for row in scene['lines']for v in row['characterStarts']];ends=[v for row in scene['lines']for v in row['characterEnds']]
  assert all(x<=y for x,y in zip(starts,ends))and all(x<=y+1e-7 for x,y in zip(starts,starts[1:]))
  assert min(starts)>=0 and max(ends)<=scene['seconds']+.001
 normalization=dict(schemaVersion=1,part=1,displaySha256=c.sha(script_file),voiceInputSha256=c.sha(H/'voice-input.json'),captionPlanSha256=c.sha(H/'caption-plan.json'),normalizationImplementationSha256=c.sha(H/'voice-analysis.py'),sourceAlignmentSha256=c.sha(c.O/'source-alignment.json'),paragraphEqualityCount=135,cueCount=386,everyCuePrefixSubstringAdditive=True,everyParagraphComplete=True,allCharacterClocksMonotone=True,sourceScriptWordsChanged=False,rawAsrWordsChanged=False)
 c.save(c.O/'normalization-boundary-review.json',normalization)
 review=c.read(c.O/'source-asr-review.json');tts=c.read(c.O/'tts-current.json');assert review['complete']and len(review['scenes'])==21
 notes={
 'v7-a01':'Complete greeting/overview/position-versus-orientation text compared. Independent complete ending recognizes 돛을; whole-file 도치를 spelling is not retained as a content error.',
 'v7-a02':'All nine paragraphs, raft log versus separate sail, object/upright/identity frames retained. X/Y/Z versus spoken names and 뗏목/땜목 are recognition spelling differences; no internal-game coordinate claim.',
 'v7-a03':'All convention and sign limitations retained. 식의/시계 remains homophonic recognition ambiguity in the explicit calculation/convention passage; pronunciation listening remains pending, not a confirmed source error.',
 'v7-a04':'Heading positive45 and positive-Y viewpoint, moving object axes and fixed-Y preserved. 양의/양해 and 기수/기술 recognition spellings do not change the reviewed meaning; listening pending.',
 'v7-a05':'Complete local-versus-upright pitch comparison, positive20/negative pitch and example caveat retained. Duplicated long-file words return to identical57–63s timestamps; independent complete context contains the passage exactly once. Original PCM retained.',
 'v7-a06':'All six paragraphs; heading45/pitch20/bank30, current-Z axis and forward/up/right roles retained.',
 'v7-a07':'All six paragraphs; observer reversal, positive-Y versus positive-Z view directions and unchanged left-hand rule retained.',
 'v7-a08':'All seven paragraphs; forward direction versus twist, Mario Kart front/up/camera caveats and unmeasured editorial marks retained.',
 'v7-a09':'All five current paragraphs directly compared after one approved first-sentence repair. 지금까지 is present in both contextual prefix and current full-scene ASR. Original unchanged tail samples retained. No repeated text in current full-scene ASR.',
 'v7-a10':'All six paragraphs; intrinsic/extrinsic definitions and reverse-order equivalence with changed moving/fixed axes retained. No general permission to reorder.',
 'v7-a11':'All six paragraphs;30/20 example and fixed-X90/Y90 noncommutativity retained with correct endpoints.',
 'v7-a12':'All seven paragraphs; vertical-pitch yaw-versus-heading comparison, current/fixed-Y distinction and implementation caveat retained.',
 'v7-a13':'All six paragraphs; middle-angle versus final body-X distinction, proper Euler versus Tait-Bryan and gyroscope examples retained. Word-piece normalization was corrected only for equivalent canonical names.',
 'v7-a14':'All six paragraphs; conversion through matrices, coordinate-change caveat and row-vector bank/pitch/heading product retained. 규약/귀하 remains recognition ambiguity; actual pronunciation listening pending.',
 'v7-a15':'All seven paragraphs; readable inputs, separate logs/sail/hook task, no assertion of game internal Euler implementation and data-size transition retained.',
 'v7-a16':'All eight paragraphs; local three parameters,1-degree quantization,0.5-degree component error,20/20.4 example and final-orientation-error limitation retained.',
 'v7-a17':'All five paragraphs; finite inputs720/135, unrestricted matrix/normalized rotation representation limitations and valid-versus-intended result distinction retained.',
 'v7-a18':'All six paragraphs;0/360/720 and(0,135,0)=(180,45,180), endpoint-versus-path and nonmeasurement caveats retained.',
 'v7-a19':'All five paragraphs;(−180,180] heading/bank and inclusive±90 pitch, coupled canonicalization and boundary caveat retained.',
 'v7-a20':'All eight paragraphs;45/80/90 progression,positive90 h−b,negative90 h+b,30−10=20 and45 versus bank−45 retained. Long-file duplicate returns to same38–44s; complete independent context contains example once. Original PCM retained.',
 'v7-a21':'All eight paragraphs;bank0 representative,positive subtract/negative add,remaining continuity limitation,input/output distinction,raft close and next-episode path question retained.'}
 rows=[]
 for scene in review['scenes']:
  sid=scene['scene'];assert c.sha(c.R/scene['audioFile'])==scene['audioSha256']and c.sha(c.R/scene['asrFile'])==scene['asrSha256']
  rows.append(dict(scene=sid,paragraphs=len(source[sid]['lines']),audioFile=scene['audioFile'],audioSha256=scene['audioSha256'],asrFile=scene['asrFile'],asrSha256=scene['asrSha256'],expectedTextSha256=hashlib.sha256(scene['expected'].encode()).hexdigest(),fullExpectedAndRawRecognitionDirectlyRead=True,decision=notes[sid],humanListening='pending'))
 flags=[dict(scene='v7-a03',sourceRange=[68.52,78.34],expected='식의 부호',recognized='시계 부호',kind='homophonic ASR ambiguity; not confirmed wrong source word',humanListening='pending'),dict(scene='v7-a14',sourceRange=[75.64,79.94],expected='규약까지',recognized='귀하까지',kind='recognition/pronunciation ambiguity; no low-score automatic retake',humanListening='pending')]
 before=tts['scenes'][8]['originalSynthesisRecord'];after=tts['scenes'][8];energy=[]
 for kind,row in [('original',before),('repaired',after)]:
  x,rate=sf.read(c.R/row['file'],dtype='float32')
  energy.append(dict(kind=kind,sourceSha256=row['sha256'],firstWordCache=(c.read(c.O/'asr/v7-a09.json')['words']if kind=='original'else c.read(c.R/row['asrFile'])['words'])[:4],first1p5Seconds20msEnergy=[dict(start=i/rate,rmsDbfs=a.db(a.rms(x[i:i+round(.04*rate)])))for i in range(0,round(1.5*rate),round(.02*rate))]))
 c.save(c.O/'source-direct-review.json',dict(schemaVersion=1,part=1,approvedScriptSha256=c.sha(script_file),ttsCurrentSha256=c.sha(c.O/'tts-current.json'),sourceAsrReviewSha256=c.sha(c.O/'source-asr-review.json'),allCurrent21TextsCompared=True,paragraphsCompared=135,unresolvedConfirmedContentErrors=0,contentStatus='Complete current texts/claims/numbers directly compared; two pronunciation-listening flags remain.',scenes=rows,recognitionBoundaryDuplicatesResolved=['v7-a05','v7-a09-original','v7-a20'],independentContextReview=c.rel(c.O/'source-context-review.json'),independentContextReviewSha256=c.sha(c.O/'source-context-review.json'),selectedRepair=c.rel(c.O/'repair-a09-attempt3/selection.json'),selectedRepairSha256=c.sha(c.O/'repair-a09-attempt3/selection.json'),openingEnergyAndWordTimes=energy,listeningFlags=flags,numericalAndCanonicalClaimsCompared=True,normalizationReview=c.rel(c.O/'normalization-boundary-review.json'),normalizationReviewSha256=c.sha(c.O/'normalization-boundary-review.json'),humanWholeListening='pending',actualVoiceWithMovingVisualPace='pending',finalEncodedMixAsr='pending final captioned master handoff; source ASR is not final mix review'))
 handoff=c.read(c.O/'voice-handoff.json')
 handoff.update(directContentReview=c.rel(c.O/'source-direct-review.json'),directContentReviewSha256=c.sha(c.O/'source-direct-review.json'),contentReviewStatus='Current21 complete raw transcripts and135 paragraphs directly compared; no unresolved confirmed content errors; two phonetic listening flags retained.',status='Current21PCM/ASR/135paragraph clocks ready; human listening, moving pace and final encoded mix QA pending')
 c.save(c.O/'voice-handoff.json',handoff)
 execution=[]
 for file in c.O.glob('*-execution.json'):
  d=c.read(file)
  if 'returnCode'not in d:continue
  assert d['status']in ['complete','failed']
  d['state']='complete'if d['returnCode']==0 else'failed'
  d['terminalStateFinalizedFromReturnCode']=True
  d['recordedWorkerPidStillPresent']=psutil.pid_exists(d.get('workerPid',-1))
  d['terminalStateRecordedAt']=time.time();c.save(file,d)
  execution.append(dict(file=c.rel(file),sha256=c.sha(file),state=d['state'],returnCode=d['returnCode'],workerPidStillPresent=d['recordedWorkerPidStillPresent']))
 names={'voice-render.py','voice-review.py','voice-contexts.py','voice-opening-repair.py','voice-opening-repair3.py'}
 own=[]
 for proc in psutil.process_iter(['pid','cmdline']):
  if any(Path(arg).name in names for arg in proc.info['cmdline']or[]):own.append(proc.info['pid'])
 assert not own,'An owned model/coordinator remains active'
 lease=c.read(c.LEASE)if c.LEASE.exists()else None
 assert not lease or lease.get('project')!=c.P.name,'An own live/stale GPU lease remains'
 c.save(c.O/'gpu-release.json',dict(part=1,ownedModelOrCoordinatorPids=[],ownFiniteLeasesReleased=True,sharedLeasePresent=bool(lease),foreignLeaseUntouched=True,execution=execution,checkedAt=time.time(),foreignAppsClosedOrPaused=False,sourcePcmFilesPreserved=True))
 print(json.dumps(dict(alignedScenes=21,paragraphs=135,cues=386,allBoundaryChecks=True,unresolvedConfirmedContentErrors=0,listeningFlags=len(flags),ownGpuReleased=True)))
if __name__=='__main__':main()

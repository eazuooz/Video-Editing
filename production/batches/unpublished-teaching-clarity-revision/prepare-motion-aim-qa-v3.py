from pathlib import Path
import json,hashlib,subprocess
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,o):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
render=read(R/'aim-target-render-execution-v3.json')
qa=read(R/'two-target-qa-execution-v2.json')
assert render['actualExitCode']==0 and qa['actualExitCode']==0
ps="Get-CimInstance Win32_Process -Filter 'ProcessId=64628 OR ProcessId=16592' | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4"
raw=subprocess.check_output(['powershell','-NoProfile','-Command',ps],text=True).strip()
assert not raw,raw
save(R/'two-target-held-observation-v2.json',dict(schemaVersion=1,observedAt=now(),renderOuterExitCode=0,qaOuterExitCode=0,qaSessionId=20379,qaExitObservedChunk='7800a1',qaProcessAbsent=True,processAbsenceObservedChunk='4701dd',goal=dict(id='06b',cleanSamples=19,captionedSamples=19,boardsDirectlyRead=8,cleanSha256='542232598e0461d3268c03e3e1df204751aa8c213b1aad70ccb393a085d9cb08',sampleSpacingAndProjectedLandmarkReviewApproved=True,wholeMovementApproved=False,observation='All clean and captioned selected samples show separated floor label and secondary footer. Full-size f235 keeps a gap above two-line fixed captions.'),scene02=dict(status='held-direction-ray-misses-target',cleanBoardsRead=8,remainingCleanBoardsUnread=8,captionedBoardsUnread=16,fullSizeFrameRead=1860,observation='The goal-directed blue ray misses the brown target in v2. Preserve this output; use independently reviewed scene02 v3.'),all222SamplesRead=False,allFinalPixelsApproved=False,newTtsOrAsr=0))
save(R/'aim-target-render-process-closure-v3.json',dict(schemaVersion=1,observedAt=now(),actualOuterExitCode=0,sessionId=49596,pid=render['pid'],actualCreationDate=None,creationDateObservation='Process finished before CIM session receipt; creation timestamp was not observed.',actualCommand=render['commandLine'],cwd=render['cwd'],actualFfmpegExitCode=render['completed'][0]['actualFfmpegExitCode'],processAbsent=True,exitObservedChunk='892dd0',processAbsenceObservedChunk='4701dd',renderSha256=render['completed'][0]['sha256'],fullSizeFrame1860Read=True,fullSizeObservation='Blue direction reaches the brown target; the red camera has separate shake indication and the ray stays around its brown target.',allFinalPixelsApproved=False))
source=(B/'review-motion-two-targets-v2.py').read_text('utf-8')
source=source.replace('two-target-qa-v2','aim-target-qa-v3').replace('two-target-qa-execution-v2','aim-target-qa-execution-v3').replace('two-target-render-execution-v2','aim-target-render-execution-v3')
source=source.replace("len(render['completed'])==2","len(render['completed'])==1").replace('43721','49596')
start=source.index("save(R/'two-target-render-process-closure-v2.json'")
end=source.index('\nsubprocess.run',start)
source=source[:start]+"assert read(R/'aim-target-render-process-closure-v3.json')['actualOuterExitCode']==0"+source[end:]
source=source.replace('reviewing-two-target-clean-and-current-captioned-pixels','reviewing-scene02-aim-v3-clean-and-current-captioned-pixels').replace('two-target-current-captioned-samples-awaiting-direct-review','scene02-aim-v3-current-captioned-samples-awaiting-direct-review')
savepath=B/'review-motion-aim-target-v3.py'
assert not savepath.exists();savepath.write_text(source,'utf-8')
print(json.dumps(dict(prepared=True,heldV2Preserved=True,goalNoReExtraction=True,newTtsOrAsr=0)))

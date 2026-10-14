"""Prepare only two previously unused navigation windows for native/caption review."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
base=P/'review-plant-endpoints-v6.py';text=base.read_text('utf-8')
cuts=[dict(key='town-entry-navigation',source='chicory-b-roll-1',startFrame=11400,endFrameExclusive=11580,candidateSeconds=3,
 framingUpPixels=120,provisionalInsertion='generic-outline-navigation',caveat='Coarse190–192 movement after dialogue189, before current193 painting. Verify all native boundaries/ongoing motion/UI; no dialogue or idle quota.',selected=False,sourceAdoptionApproved=False,finalCueUiApproved=False,startSeconds=190,endSeconds=193),
 dict(key='interior-door-navigation',source='chicory-b-roll-1',startFrame=23040,endFrameExclusive=23160,candidateSeconds=2,
 framingUpPixels=120,provisionalInsertion='generic-outline-navigation',caveat='Coarse384–386 interior movement before dialogue387. Inspect movement/dark outlined objects and correct crop; no claim painting or house-specific geometry.',selected=False,sourceAdoptionApproved=False,finalCueUiApproved=False,startSeconds=384,endSeconds=386)]
start=text.index('cuts = [');end=text.index('protected_paths = ',start)
text=text[:start]+'cuts = '+repr(cuts)+'\nassert sum(c[\'candidateSeconds\'] for c in cuts)==5\n'+text[end:]
text=text.replace("plant-endpoints-execution-v6.json","navigation-targets-execution-v7.json").replace("preflight/plant-endpoints-v6","preflight/navigation-targets-v7")
text=text.replace("new-plant-endpoints-","new-navigation-targets-")
text=text.replace('Observe actual v5 exit and read only revised endpoints/new plant-action pixels. Reuse v4 interiors. Preserve original8PCM/32ASR and foreign lease. Measure3bridges after sufficient unique matched footage is secured; final gates remain false.',
 'Observe actual v7 exit and directly read every new navigation/caption sample. Preserve31window bankv2, all11PCM and completed3whole+3complete+2target bridge ASR. Confirm ongoing useful action before allocation; final gates remain false.')
text=text.replace('candidateSeconds=2,planCuts=cuts','candidateSeconds=5,planCuts=cuts')
text=text.replace("tts = read(BASE/'narration-tts-execution-v1.json')","tts = read(BASE/'narration-tts-execution-v1.json')\nbridge = read(BASE/'causal-bridge-tts-execution-v1.json')\nassert bridge['actualOuterExitCode']==0 and bridge['researchResumeVerified']\nassert read(BASE/'causal-bridge-targeted-voice-direct-review-v1.json')['current3WholePlus3IndependentPlus2AdaptiveContextsDirectlyCompared']")
text=text.replace("for x in tts['results']}","for x in tts['results']+bridge['results']}")
text=text.replace("ROOT/'projects/limited-color-world/planning/causal-chain-additions-v1.json']","ROOT/'projects/limited-color-world/planning/causal-chain-additions-v1.json',P/'source-action-bank-v2.json',ROOT/'projects/limited-color-world/sources/game-candidates-v2.json',BASE/'causal-bridge-targeted-voice-direct-review-v1.json']")
text=text.replace("targets = read(P/'extra-native-targets-execution-v5.json')","targets = read(P/'extra-native-targets-execution-v5.json')\n    plant=read(P/'plant-endpoints-execution-v6.json')")
text=text.replace('[prior,trimmed,extra,targets]','[prior,trimmed,extra,targets,plant]')
text=text.replace("protectedInputsAnd8PcmUnchanged=True","protectedInputsAnd11PcmUnchanged=True")
dest=P/'review-navigation-targets-v7.py';assert not dest.exists();dest.write_text(text,'utf-8')
plan=P/'prepared-navigation-targets-v7.json';assert not plan.exists()
plan.write_text(json.dumps(dict(preparedAt=datetime.now(timezone.utc).isoformat(),candidateSeconds=5,cuts=cuts,
 worker=dest.relative_to(ROOT).as_posix(),workerSha256=hashlib.sha256(dest.read_bytes()).hexdigest(),sourceBankPreserved=True,
 acquisition=0,render=0,adopted=0,finalRatioApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print('New5s/two navigation targets prepared; no source re-download/decode/ASR repeat/adoption.')

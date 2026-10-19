"""Record completed direct current-text review and measured audio evidence."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v4-clarity';OLD=P/'production/local/revision-v4'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def evidence(p):return dict(file=p.relative_to(R).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
pair=read(O/'pair-source.json');qa=read(O/'qa/audio-continuity.json');contexts=read(O/'encoded-contexts/results.json');before=read(OLD/'qa/audio-continuity.json');equiv=read(O/'audio-clarity-equivalence.json')
assert contexts['status']=='complete' and read(O/'final-mix-asr.json')['complete']
assert qa['sustainedLocalDropCandidates']==before['sustainedLocalDropCandidates'] and qa['sceneJoins']==before['sceneJoins']
assert len(qa['flaggedVoiceTransferWindows'])==1 and qa['flaggedVoiceTransferWindows']==before['flaggedVoiceTransferWindows']
assert read(OLD/'qa/flag-context-review.json')['allTechnicalVoiceTransferPassed']
r=dict(schemaVersion=4,revision='standard-game-audio-v4',reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),captionedSha256=pair['outputs']['captioned']['sha256'],directWholeEncodedTextCompared=True,unresolvedConfirmedContentErrors=0,narrationStemUnchanged=True,wholeListening='pending',noHumanListeningClaimed=True,scope='All26 scenes and full recognized text directly compared against current approved narration; only newly ambiguous complete contexts independently recognized. Exact source PCM and visual streams retained.',addedBgm=False,gameAudioTargetLufs=-23,speechPriorityGameRide=read(O/'audio-build.json')['speechPriorityGameRide'],loudness=read(O/'qa/encoded-loudness.json'),speechWindows=len(qa['windows']),sourceAsrReuse=evidence(P/'production/revision-v3/narration-review.json'),wholeEncodedAsr=evidence(O/'final-mix-asr.json'),wholeTextComparison=evidence(O/'final-mix-text-comparison.json'),independentContexts=evidence(O/'encoded-contexts/results.json'),continuity=evidence(O/'qa/audio-continuity.json'),preRepairContexts=evidence(OLD/'encoded-contexts/results.json'),equivalence=evidence(O/'audio-clarity-equivalence.json'),isolatedProjectionFlag=dict(start=823.735,end=824.135,resolved='Correlated background, not a voice-level loss. Current24kHz decoded6.4s context exactly equal to the independently measured pre-clarity context.',voiceCoefficientDb=-.06191603361379008,evidence=evidence(OLD/'qa/flag-context-review.json')),naturalDropCandidates=dict(count=111,sourceOriginEvidence=evidence(P/'production/local/revision-v3/qa/drop-context-review.json'),unchangedSourceStemAndCandidates=True,contextListening='pending'),findings=[
 'Standard original game sound restored; no separate BGM. Mario Kart source is natively silent, so no invented replacement effects.',
 'Zelda1195.55–1216.70: ordinary narration-priority game ride with300ms edges restores recognition of 길이로 and 담고 있는 정보. Approved speech PCM unchanged.',
 '07 and17 ambiguities use directly reviewed current v4 contexts verified decoded-identical in the final audio; no repeated inference.',
 '24 numerical units resolve to1/4second and3/4turn;24/26 overlap repeats are ASR stitching, resolved by current independent contexts.25 wrapPi also resolved.',
 'Retained pronunciation ambiguities 요,보간,단위축,정규화 and subjective whole listening remain pending; on-screen canonical terms unchanged.'
 ])
(H/'audio-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Recorded full current text review and audio measurements; human listening remains pending.')

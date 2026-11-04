"""Record completed sampled inspection and correct an analysis-only downmix bias."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math,statistics
P=Path(__file__).resolve().parents[1];R=P.parents[1];V=P/'production/local/render-v4'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.now(timezone.utc).isoformat();q=read(V/'final-qa/report.json')
master=q['files']['captioned']['sha256'];m=read(V/'temporal-samples/manifest.json')
assert m['masterSha256']==master
observations={
 '000':'Moving headlamp over rocks; ellipse follows illuminated ledge then clears; native motion throughout.',
 '007':'Showroom orbit changes hood/window reflections. Hood contour follows target briefly then clears. Source menu transition in first second remains visible.',
 '018':'Tower additions/orbit and wall contour remain matched. Camera-dependent appearance is not presented as a measured fixed-light test. Marks clear before the Unity continuation.',
 '027':'Brightbloom arrow attachment, plant and nearby illumination are visible. Small circle marks the plant; later climbing remains native motion.',
 '031':'Ceiling-light placement and changed room brightness remain visible. Ellipse marks the fixture briefly, without a fabricated light-intensity value.',
 '049':'Moving headlamp reveals illuminated versus dark ledge; target is followed briefly, then annotation clears at the cut.',
 '060':'Flashlight changes the rail/door patch; circle follows the illuminated area, then clears before the Unity explanation. Intentional darkness is preserved.'}
for x in m['records']:
 x.update(viewed=True,inspectionKind='agent-temporal-frame-sampling-not-continuous-playback',observations=observations[x['scene']],checkedAt=at)
 x['sheetEvidence']=[dict(path=p,sha256=sha(Path(p))) for p in x['sheets']]
m.update(checkedAt=at,totalFrames=sum(x['frames'] for x in m['records']),status='sampled-motion-targets-and-cut-clearance-inspected',humanListening=False,continuousPlaybackViewed=False)
assert m['totalFrames']==307
save(V/'temporal-samples/manifest.json',m)
bias=10*math.log10(2);paragraphs=[];suspects=[]
for f in sorted((V/'final-mix-review/paragraphs').glob('*.json')):
 d=read(f);assert d['masterSha256']==master
 windows=[dict(w,correctedProjectedVoiceGainDb=w['projectedVoiceGainDb']-bias) for w in d['localWindows']]
 vals=[w['correctedProjectedVoiceGainDb'] for w in windows]
 bad=[dict(scene=d['entry']['scene_id'],**w) for w in windows if w['correctedProjectedVoiceGainDb'] < -1]
 paragraphs.append(dict(scene=d['entry']['scene_id'],activeWindows=len(windows),medianProjectedVoiceGainDb=statistics.median(vals) if vals else None))
 suspects+=bad
assert len(paragraphs)==79
save(V/'final-mix-review/downmix-corrected-level-review.json',dict(checkedAt=at,masterSha256=master,method='Original final decode used equal-power mono, reference arithmetic mean. Subtract 10log10(2) from the unchanged measured projection gains. Raw evidence and master remain untouched.',analysisBiasDb=bias,paragraphs=paragraphs,suspectWindows=suspects,suspectInterpretation='All remaining low-projection windows coincide with game audio; projection is not an isolated perceptual loudness measure. Actual human listening remains pending.',humanListening=False,mediaChanged=False))
record=dict(id='final-v4-technical-asr-and-temporal-review',checkedAt=at,masterSha256=master,
 status='four-files-available-integrated-listening-pending',technicalEvidence=str((V/'final-qa/report.json').relative_to(R)),
 pixelEvidence=str((P/'production/local/render-v3/final-qa/sampled-visual-review.json').relative_to(R)),
 pixelReuseBasis='V3 and V4 compressed visual packets are byte-identical; only final audio was repaired. Verified in V4 technical report.',
 temporalEvidence=str((V/'temporal-samples/manifest.json').relative_to(R)),
 audioEvidence=str((V/'final-mix-review/report.json').relative_to(R)),
 correctedLevelEvidence=str((V/'final-mix-review/downmix-corrected-level-review.json').relative_to(R)),
 asrReviewNotes=['79 complete encoded paragraphs transcribed without expected-text prompting; no runaway repetitions.',
 'Common technical/homophone disagreements include 세기/색이, 계수/개수, 감쇠/감쇄, 보간/보관 and roman formula spelling. ASR alone does not prove a speech error.',
 '037 initial 지금, 042 zero/one recognition, and 058 spoken subtraction remain targeted listening items; do not silently approve them.'],
 remaining=['Actual continuous audiovisual and listening review, including three targeted ASR ambiguities','User final viewing/listening'],
 computerPlaybackAttempt=dict(status='stopped-by-tool',reason='Current browser URL could not be identified reliably; no further application control attempted.'),
 continuousPlaybackViewed=False,humanListening=False,humanReview=False,localPreviewAvailable=True,localFinalReviewReady=False)
save(V/'content-review.json',record)
ledger=read(P/'production/review-ledger.json');checks=ledger.get('checks',[])
if isinstance(checks,dict):checks[record['id']]=record
else:checks=[x for x in checks if x.get('id')!=record['id']]+[record]
ledger.update(checks=checks,updatedAt=at);save(P/'production/review-ledger.json',ledger)
print('307 viewed temporal frames; 79 corrected paragraph level records; four output candidates, listening pending')

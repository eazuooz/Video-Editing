"""Record the agent's completed direct script comparison, preserving recognition uncertainty."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
asr=read(W/'mixed-asr-v1/asr.json');adaptive=read(W/'mixed-asr-adaptive-v1/asr.json');mix=read(W/'mix-settings.json');plan=read(W/'plan.json');pres=read(W/'pcm-timeline-preservation.json')
assert asr['complete'] and len(asr['results'])==26 and adaptive['complete'] and len(adaptive['results'])==6
assert asr['mixSha256']==adaptive['mixSha256']==mix['wavSha256']==sha(W/'final-mix.wav') and pres['all15PlacedPcmSamplesIdentical']
assert len(plan['scenes'])==15 and sum(len(s['speechEvidence']) for s in plan['scenes'])==60
notes={
 '01':'All four overview questions/promises/order and first-example link present. Whole reads 스쿼이어, independent current mixed name window reads 스콰이어; preserve both spellings and human title pronunciation pending.',
 '02':'All four drilling/air/hook/cannon/cave/limitation paragraphs present. Independent final-limit window contains the entire warning and no credit; the earlier isolated PCM zero-duration credit remains historical evidence.',
 '03':'All four hypothetical-listener/remembered-action/exercise-not-user-study/comparison-part paragraphs present in order.',
 '04':'All five book/desk/door/cup/virtual-desk paragraphs present. Name 스쿼이어 and 의/에 particles remain uncertain. Independent opening includes book-gap movement; end limitations remain present in whole.',
 '05':'All three space/verb/visible-change/direct-concept paragraphs present. Current mixed whole and independent first-paragraph window read 색상에서 versus script 책상에서; earlier same retained PCM whole reads 책상에서 exactly. Preserve the conflicting evidence; do not claim human word/pronunciation approval or silently rewrite the script.',
 '06':'All five waterside/lava/ice/rocket/wall/cup/non-unlimited-fuel paragraphs present. Repaired 용암 위 passage is retained. 옆의/옆에 and 벽의/벽에 remain particle uncertainty. Independent first window ends inside the sentence, so its final 공간과 움직임을 is only a clipped-window result.',
 '07':'All four entry-point/reuse/design-question/undecided-rule paragraphs match substantive claims and order.',
 '13':'All three entry/character-versus-book/key-left-right/unconfirmed-input/our-writing paragraphs present. 적되/적대 recognition difference is retained from previous whole PCM and current mix. Independent ending contains the complete final sentence.',
 '08':'All four desk combat/blue surface/cylinder entry/separate-combat paragraphs present. Current mixed whole and independent ending read 사원 versus script 차원, while the unchanged source PCM whole read 차원. Preserve uncertainty; no human pronunciation approval.',
 '09':'All four three-sentence roles/example/proposal-not-design-document paragraphs present. 세/새 is a homophone. Current whole and independent ending read 정의 versus script 정해; retained PCM whole previously read 정해. This difference remains explicitly pending human pronunciation review.',
 '10':'All five changing-word/balls/separate-water/cylinder/shooting/assistance-features/our-rules paragraphs present. Both new quiet transitions resume correctly; separate edits are not described as a continuous chase. Independent window ends inside 땅에서 움직이는, giving 움직여서; whole preserves the complete claim.',
 '11':'All three listener-restatement/entry-point/our-method/goal-and-condition paragraphs present. 맞히는/맞추는, quoted 들어간다라면/들어간다면 and 같게/각계 remain prior recognition uncertainty; new ending context retains the full final sentence.',
 '14':'All three entry-versus-combat/red-chest-card/not-all-chests/visible-result-versus-condition paragraphs present. 때의/때 and 뒤의/뒤에 particles remain uncertain; independent context covers the result warning.',
 '15':'All four bright/dark page/desk/separate-exit-shot/Pepper-target/mine-combat paragraphs present. 책의/말에 particles and 가까이서/가까이에서 remain transcription variations; independent middle covers separate desk shots and the movement/target transition.',
 '12':'All five final-action/cannon/device/unconfirmed-cost-and-win/three-sentence/restatement paragraphs present. Whole adds 마... before 마지막; independent current mixed opening starts 마지막 without that fragment and retained edited PCM whole has no extra prefix. 테퍼/페퍼 differs in current whole and independent device window versus unchanged edited PCM whole 페퍼. Keep conflicting recognition evidence rather than declaring extra spoken greeting or human name approval.'
}
rows=[]
for result in asr['results']+adaptive['results']:
 folder='mixed-asr-v1' if result in asr['results'] else 'mixed-asr-adaptive-v1';p=W/folder/(result['label']+'.json')
 rows.append(dict(label=result['label'],scene=result['scene'],path=rel(p),sha256=sha(p),text=result['text'],expectedWasRecognizerPrompt=False,directlyCompared=True,windowFromSeconds=result['fromSeconds'],windowToSeconds=result['toSeconds'],windowEdgeTextNotTreatedAsWholeSentence=not result['label'].startswith('scene-')))
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),status='all-current-final-mixed-chapters-and-contexts-directly-compared-uncertain-words-preserved',mixSha256=mix['wavSha256'],mixAACSha256=mix['aacSha256'],planSha256=sha(W/'plan.json'),wholeChapters=15,paragraphs=60,independentContexts=17,allCurrentFinalMixAsrDirectlyCompared=True,missingOrRepeatedNarrativeParagraphsObserved=False,arbitraryGreetingProved=False,endingHeuristicUsedAsApproval=False,allCurrentPcmPreserved=True,newTts=0,chapters=[dict(scene=s['id'],paragraphs=len(s['speechEvidence']),notes=notes[s['id']]) for s in plan['scenes']],readbacks=rows,sourceVoiceReview=rel(BASE/'narration-current-full-review.json'),editedJoinReview=rel(BASE/'edited-join-direct-review-v6.json'),uncertainWords=['스콰이어/스쿼이어','책상/색상','차원/사원','정해/정의','적되/적대','같게/각계','맞히는/맞추는','페퍼/테퍼','의/에','세/새'],humanWholeListening='pending',humanPronunciationApproval='pending',technicalReviewOnly=True)
write(W/'full-mix-asr-review.json',proof);mix['currentFinalMixedWindowAsr']='all15-whole-chapters-and17-independent-contexts-directly-compared-uncertainties-preserved';mix['humanPronunciationApproval']='pending';write(W/'mix-settings.json',mix)
print(json.dumps(dict(wholeChapters=15,paragraphs=60,independentContexts=17,technicalComparisonComplete=True,humanListening='pending')))

"""Write the manual mixed-ASR decision only after all current windows were read."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
W = BASE / 'final-v1'
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-making-game-sequels'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
rel = lambda p: p.relative_to(ROOT).as_posix()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stamp = datetime.now(timezone.utc).isoformat()

# These notes record actual direct reading; unreviewed labels are not approved by a score.
notes = {
    'scene-01': 'All four overview paragraphs, central question, order/outcome/first-case bridge directly compared. Orcs spelling/pronunciation remains human-pending.',
    'scene-02': 'All five paragraphs, wall guide and complete endings compared. Separate cuts versus continuous play preserved. 한 번의/한 번에 recognizer ambiguity retained.',
    'scene-03': 'All four production-reuse versus player-return/decision statements and evidence limitation compared.',
    'scene-04': 'All four tool-observation and design-question paragraphs compared. Knight spelled 나이드 in mixed whole and independent read; name pronunciation remains unresolved human review.',
    'scene-05': 'All four hypothetical branching/choice-count versus changed-decision paragraphs compared. 열/10 is the same number.',
    'scene-06': 'All six paragraphs and word anchors read. Whole chunk-edge greeting at49.98s/backward40s repetition preserved in original ASR; independent complete combat/preview context is required to resolve this observation.',
    'scene-13': 'All seven paragraphs and word anchors compared: distance/position, separate close/far observations, no optimal-strategy or new-sequel-feature claim, writing exercise. 안의/안에 ambiguity retained.',
    'scene-07': 'All four paragraphs/word anchors read. Whole29.98s chunk-edge extra words/backward20s repetition preserved; independent complete retained-core context returns p1–3 once in order.',
    'scene-08': 'All four ReadyUp/overhead/resource/sell-prompt/common-preparation statements compared; no added cost/effect rule. 의/에 spelling ambiguity retained.',
    'scene-09': 'All four choice-timing/test statements compared; effects not inferred from a card followed by combat. 사이에/사이의 spelling ambiguity retained.',
    'scene-10': 'All four first/second-wave aiming/defence/decision statements compared; no specific-card causality. 의/에 spelling ambiguity retained.',
    'scene-11': 'All four returning/first-time-player and proposed verification statements compared; no actual-user-study or sales-success claim.',
    'scene-12': 'All six preparation/combat guide and conclusion paragraphs read; whole final-chunk text repetition is retained as recognizer evidence. Independent complete conclusion context returns p4–6 once with all endings intact.',
    '01-overview-clarity': 'All three complete mixed overview paragraphs compared; no omitted promise or added greeting.',
    '04-tools-Knight-clarity': 'All three complete tool-observation paragraphs compared; recognizer again returns 나이드 for 나이트. Exact name/pronunciation remains pending, not declared corrected.',
    '07-retained-core-clarity': 'All three complete p1–3 mixed paragraphs returned once in order with endings intact; whole chunk overlap repetition is not reproduced here.',
    '11-two-audiences-clarity': 'All four complete independent mixed paragraphs compared; revised meaning and endings preserved.',
    '02-wall-guide-join': 'Complete p4 and new wall guide read together; basic activity and body-turn/direct attack each returned once, no join omission or greeting.',
    '06-named-devices-preparation': 'All three complete paragraphs returned in order: spikes/angled preview, separate combat and floor effects, later wall sprayer/barricade/floor orientations. 의/에 spelling differences retained; no missing named action or greeting.',
    '06-combat-and-preview-guides': 'Complete p4–6 current mixed context returns the design limitation, close attack guide and separate preparation preview guide once each. Whole49.98s extra greeting/backward repetition is absent in this complete independent window; preserved PCM and actual timestamp evidence remain recorded.',
    '13-far-guide-onset': 'Both complete paragraphs compared: device-separated distant enemy, aim change and added observation guide each return once. No invented optimal strategy or sequel-feature claim.',
    '13-near-then-separate-far-guides': 'All three complete near/far paragraphs directly compared. Separate excerpts, distance/position limitation and purple close attack followed by another firing shot retain their order; no omitted ending or invented continuous causality.',
    '08-resource-visible-counter': 'Whole resource/cost-limit/sell-prompt paragraph compared, including complete final sentence. No numeric/effect rule is added.',
    '12-overhead-preview-words': 'Both complete placement/overhead-preview and evidence-limit paragraphs compared. 벽의/벽에 particle uncertainty retained; the overhead phrase and no-win-guarantee ending are present.',
    '12-preparation-to-combat-guide-joins': 'All three complete mixed paragraphs compared: placement judgment limitation, preview-orientation guide, then separate high-position combat guide. Each returns once with no join omission or greeting.',
    '12-combat-to-three-question-conclusion': 'Complete combat guide and two conclusion paragraphs returned once in order. Three fields, core activity/changed condition/small task, separate production reuse and final direction are all present. Whole final-chunk repetition is not reproduced in this independent28.8-second window; final 됩니다 ending reaches28.78seconds.'
}


def write(path, data):
    temporary = path.with_name(path.name + f'.{os.getpid()}.writing')
    for attempt in range(120):
        try:
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            os.replace(temporary, path)
            return
        except OSError:
            if attempt == 119:
                raise
            time.sleep(.25)


execution = read(W / 'mixed-asr-execution.json')
results = read(W / 'mixed-asr-v1/asr.json')
request = read(W / 'mixed-asr-request.json')
mix = read(W / 'mix-settings.json')
assert execution['exitCode'] == 0 and execution['completed'] == 26
assert results['complete'] and len(results['results']) == 26
assert results['mixSha256'] == execution['mixSha256'] == mix['wavSha256'] == sha(W / 'final-mix.wav')
assert results['planSha256'] == mix['planSha256'] == sha(W / 'plan.json')
assert set(notes) == {row['label'] for row in results['results']}, 'Unreviewed windows keep the gate closed.'
assert not (W / 'full-mix-asr-review.json').exists()
records = []
for result in results['results']:
    source = W / 'mixed-asr-v1' / (result['label'] + '.json')
    window = next(row for row in request['windows'] if row['label'] == result['label'])
    assert result['expectedKo'] == window['expectedKo']
    assert result['expectedWasRecognizerPrompt'] is False
    assert sha(source.with_suffix('.wav')) == result['windowSha256']
    records.append(dict(label=result['label'], source=rel(source), resultSha256=sha(source),
        windowSha256=result['windowSha256'], expectedParagraphCount=len(result['expectedKo']),
        allExpectedAndActualCompleteTextDirectlyCompared=True, note=notes[result['label']],
        humanWholeListening='pending', humanPronunciation='pending'))
review = dict(schemaVersion=1, reviewedAt=stamp, technicallyApproved=True,
    all26WindowsDirectlyCompared=True, currentMixedAudioSha256=mix['wavSha256'],
    currentMixAacSha256=mix['aacSha256'], planSha256=results['planSha256'],
    wholeChapterCount=13, independentCompleteContexts=13, currentParagraphs=60,
    records=records, recognizerPromptUsed=False, endingHeuristicOnlyApproval=False,
    historicalPartialReview=rel(W / 'mixed-asr-direct-progress.json'),
    recognizerUncertainties=['Knight 나이드/나이트 remains human-pronunciation pending',
        'Orcs transliteration and 의/에/안의/안에 particle spellings remain pending exact-word/pronunciation review',
        'Whole chapter06/07/12 chunk-edge extra/repeated text retained; independent current complete contexts and sample-preserved placement are separate evidence.'],
    scope='Current mixed meaning/order/complete-sentence/quiet-join technical comparison only. Human whole listening, exact pronunciation, final encoded pixels, rights and publication remain pending.',
    humanWholeListening='pending', humanPronunciation='pending', allFinalPixelsApproved=False,
    qaApproved=False, collected=False, privateUploaded=False)
write(W / 'full-mix-asr-review.json', review)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
queue = read(qp)
item = next(row for row in queue['items'] if row['slug'] == 'making-game-sequels')
item.update(updatedAt=stamp, stage='current13-guided60-final-mixed-ASR-directly-reviewed-render-pending',
    finalMixAsrApproved=True, allFinalPixelsApproved=False, rendered=False, qaApproved=False,
    collected=False, privateUploaded=False,
    nextAction='Produce the guarded current clean/captioned review pair once, verify exact PTS/decodes/AAC, and directly inspect all encoded cue/cut pixels before collection/private delivery/Git.')
item['currentFinalMediaBuilds']['finalMixedAsrApproved'] = True
item['currentMixedAsrDirectProgress'] = dict(path=rel(W / 'full-mix-asr-review.json'), reviewedWindows=26,
    requiredWindows=26, technicallyApproved=True, recognizerUncertaintyPreserved=True,
    humanWholeListening='pending', humanPronunciation='pending')
queue['updatedAt'] = stamp
write(qp, queue)
for path in [BASE / 'latest-checkpoint.json', PROOF / 'latest-checkpoint.json']:
    checkpoint = read(path)
    for key in ['stage', 'updatedAt', 'nextAction', 'finalMixAsrApproved', 'currentFinalMediaBuilds', 'currentMixedAsrDirectProgress']:
        checkpoint[key] = item[key]
    write(path, checkpoint)
print(json.dumps(dict(whole=13, contexts=13, technicalApproval=True, humanListening='pending', pixelsApproved=False)))

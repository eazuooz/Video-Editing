"""Record only windows whose complete expected/actual text and words were read."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'projects/game-lighting-history-04/production'
OUT = ROOT / 'production/research/game-lighting-history/local/part3-mixed-asr-v147'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text('utf-8-sig'))
stamp = lambda: datetime.now(timezone.utc).isoformat()
# Explicit direct-review observations, never similarity-score approval.
observations = {
 'context-original-22-3': {'paragraphs': 2, 'notes': [
  'Both complete expected/actual paragraphs and all word clocks directly compared: generated-frame UI demonstration and September2026 NBA2K27 DLSS5 release scope. No added greeting, missing sentence or backward restart.',
  'Variants retained: 위의/위에, DLSS오는/DLSSO는 and 재질의/재질이. Preview versus released-game scope remains explicit; human pronunciation pending.'
 ], 'independentCorroborationPending': False},
 'context-21-guide-post-exposure': {'paragraphs': 2, 'notes': [
  'Complete exposure-context and guide21 expected/actual paragraphs and all word clocks read. Last 따라서 sentence appears once; the whole03 chunk-edge farewell/restart is absent in this independent window.',
  '언리얼/얼리얼 variant and a small26.76 versus26.90 word-clock overlap retained. Current sample-exact PCM corroboration is still required before resolving whole03.'
 ], 'independentCorroborationPending': False},
 'context-original-22r-1': {'paragraphs': 2, 'notes': [
  'Full debugger-command-submit and frame-inspection paragraphs and all word clocks read. CPU stopped-line versus GPU completion distinction and version/platform/path conditions complete without extra greeting/repeat.',
  'Minor27.06 versus27.30 adjacent-word timestamp overlap is retained; no long backward restart. Human pronunciation pending.'
 ], 'independentCorroborationPending': False},
 'context-original-22r-2': {'paragraphs': 2, 'notes': [
  'Full capture-context and purpose paragraphs and every word clock read. DX12 method demonstration is not commercial-game lighting evidence; reflection/shadow-page/G-buffer questions complete.',
  '밖의/밖에 and numeral/spacing variants, small28.80 versus28.94 overlap retained. No extra greeting, missing/repeated paragraph or long backward restart.'
 ], 'independentCorroborationPending': False},
 'context-original-22r-4': {'paragraphs': 2, 'notes': [
  'Full engine/API/conditions and resource dimensions/format/layers/mips paragraphs and every word clock read; complete final usage-relation sentence, no added greeting or repeated passage.',
  '원인을/원인의 recognition variant retained. Human pronunciation pending.'
 ], 'independentCorroborationPending': False},
 'context-23-pre-capture-dataflow': {'paragraphs': 2, 'notes': [
  'Full capture-target-view and pre-capture-dataflow text and every word clock compared. Clear versus Draw, triangle-to-mesh/shader input/output and method-only scope all complete once.',
  '렌더독 시연에서는/랜더독션에서는 at19.56–20.52 remains a pronunciation/word-boundary recognition variant; independent result does not contain the extra 에서는 duplication in whole08. DrawInstance들, 메쉬/메시 and 쉐이더/셰이더 variants retained. Do not assert a heard syllable correction; human pronunciation pending.'
 ], 'independentCorroborationPending': False},
 'context-original-22r-7': {'paragraphs': 2, 'notes': [
  'Full G-buffer and shadow-resource paragraphs and every clock read. Normal-color visualization, encoding caveat, light-space depth comparison and cascade/page choices complete once.',
  'Expected spoken 지 버퍼 is written Z 버퍼 by this recognizer; the literal captions retain G-buffer and the separate depth paragraph remains distinct. This recognizer spelling cannot decide the ambiguous letter pronunciation; human listening pending.'
 ], 'independentCorroborationPending': False},
 'context-original-22rb-4': {'paragraphs': 2, 'notes': [
  'Full tone-transform order and producer/consumer resource dependency paragraphs plus every word clock read. Engine-specific order and prepared-diagram versus actual-capture limitations complete once.',
  '톤 매핑/톤 맵핑 orthographic variant retained; no extra greeting, omission or backward restart.'
 ], 'independentCorroborationPending': False},
 'context-original-conclusion-5': {'paragraphs': 2, 'notes': [
  'Full conclusions4/5 and every word clock directly read: sampling/cache/reconstruction cost and final viewer questions complete once through final 있습니다.',
  'No additional greeting or backward restart; this window corroborates the ending only, not the whole11 obscured conclusion3.'
 ], 'independentCorroborationPending': False},
 'context-focus-later-settings': {'paragraphs': 2, 'notes': [
  'Full focus-error-isolation and later-settings paragraphs and all word clocks read. Same box placement, near/far regions and cause-isolation statements complete once. The whole07 fake farewell/60s restart is absent.',
  '번진/던진 and 뒤의/뒤에 recognition variants and25.40 versus25.56 clock overlap retained. Sample-exact current PCM corroboration and human pronunciation remain separate requirements.'
 ], 'independentCorroborationPending': False},
 'context-capture-target-view': {'paragraphs': 2, 'notes': [
  'Full resource dimensions and target-view paragraphs and all word clocks read. Clear versus Draw selection, blue triangle output and transition to vertex/shader input complete once.',
  '드로 인스턴스드/드로 인스턴스들 and 꼭짓점/꼭지점, 셰이더/쉐이더 spellings plus26.98 versus27.14 overlap retained; no extra greeting or long backward restart.'
 ], 'independentCorroborationPending': False},
 'whole-10': {'paragraphs': 9, 'notes': [
  'All nine complete expected/actual paragraphs, endings and all word timestamps directly read. Reflection/volume/temporal/tone passes, producer-consumer dependencies and upload budgets versus frame/performance measurement remain in order.',
  'No added greeting or backward chunk restart. Raw replacement character 안�니다 at84.44–85.12s is retained for expected 안 됩니다. Dedicated resource-upload context is prepared and not yet executed; no claim of source PCM corruption.',
  'Variants retained: 캡처/캡쳐, 톤 매핑/톤 맵핑, 뒤의/뒤에, 셰이더/쉐이더. Human pronunciation remains pending.'
 ], 'independentCorroborationPending': True},
 'whole-11': {'paragraphs': 6, 'notes': [
  'All complete expected and actual text and every word timestamp directly read. Inspection recording and conclusions1/2/4/5 occur completely; the first half of conclusion3 is obscured in this recognizer result.',
  'At49.98s the chunked recognizer emits many zero-duration repetitions of 화면에 남겨주시기 바랍니다. It then resumes at52.60s in 표현을 보는지. This is not asserted to be a real repeated waveform or missing source audio.',
  'New conclusion-inspection context includes complete conclusions2/3/4 for independent current-mix comparison. Retain thin/얇은 versus 얄은 recognition variant and human pronunciation pending.'
 ], 'independentCorroborationPending': True},
 'context-part3-overview': {'paragraphs': 1, 'notes': [
  'Full expected/actual overview and all timestamps directly read. Complete viewer question, episode order, displayed versus calculated frames and reconstruction responsibility occur without extra greeting/repetition.',
  'Independent result spells 맡는 as 맞는 like whole01; human pronunciation remains pending. This context corroborates overview content only, not final pixels or the rest of the mixed audio.'
 ], 'independentCorroborationPending': False},
 'whole-01': {'paragraphs': 9, 'notes': [
  'All complete paragraphs and endings were read in order. No omitted/repeated paragraph or additional greeting in this window.',
  'Recognition variants retained: 맡는/맞는, 위의/위에, DLSS오/DLSSO, 재질의/재질이, 세 영상/새 영상, 켜짐/켜진.',
  'Small stride word-clock overlaps were observed; no long backward restart. Independent overview and human pronunciation remain pending.'
 ], 'independentCorroborationPending': True},
 'whole-02': {'paragraphs': 7, 'notes': [
  'All seven paragraphs, four-game surface distinctions and complete last sentence directly compared.',
  'Recognition variants retained: 앞의 빗속/앞에 빛속, 앞의/앞에, 이 번/2번 and spoken year/numeral formatting.',
  'No added greeting or repeated paragraph. Native red/teal markers require the separately prepared visual repair; transcript review does not approve pixels.'
 ], 'independentCorroborationPending': False},
 'whole-03': {'paragraphs': 8, 'notes': [
  'All expected and actual text and every word timestamp directly read. All eight expected paragraphs occur, including the complete final 따라서 sentence.',
  'Recognition variants retained: 홀 안입니다/홀 아닙니다, 화면은/하면은, 프레임 안의/안에, 언리얼/얼리얼, 배치/매치.',
  'At 129.90–129.98 s chunk edge, recognizer appends 다음 영상에서 만나요 with zero-duration words, then restarts at 120.00 s and repeats the already recognized editor sentence. This is not asserted to be repeated PCM or a real greeting.',
  'Pending independent context-21-guide-post-exposure covers the full exposure-context paragraph and the next original guide in the current mix; compare it and current PCM before resolving the chunk artifact.'
 ], 'independentCorroborationPending': True},
 'whole-04': {'paragraphs': 8, 'notes': [
  'All eight full paragraphs, every word timestamp and all endings directly compared; exposure settings, histogram/log scale, camera-condition limits and bloom versus indirect light are preserved.',
  'No missing/repeated paragraph or unrequested greeting. Minor particle variants 뒤의/뒤에 and 표면의/표면에 remain recorded; spacing and numeral representation do not remove content.',
  'Current independent exposure context remains pending for the adjacent whole-03 chunk-edge artifact; this whole-04 result does not resolve that earlier artifact by itself.'
 ], 'independentCorroborationPending': False},
 'whole-05': {'paragraphs': 7, 'notes': [
  'All seven expected/actual paragraphs and every timestamp directly read. Color/tone, fixed observation face, lookup setup and the final complete sentence occur in order without an added greeting or repeated paragraph.',
  'Recognizer output preserves a replacement character at 41.60–42.62 s in 구�해보세요; do not alter the raw result or call this evidence of corrupt PCM. Expected text is 구분해 보세요.',
  'Variants retained: 남아 있는데/남아있는데, 게임 안의/안에, 앞의/앞에, 포스트 프로세스 블렌더블/Post Process Blendable and 블렌드/Blender. Current PCM binding and the previously reviewed literal guide are separate evidence; human pronunciation remains pending.'
 ], 'independentCorroborationPending': False},
 'whole-06': {'paragraphs': 6, 'notes': [
  'All six full expected/actual paragraphs and word timestamps directly read. Lookup-table role, focus/blur distinction, old bokeh limits, diagnostic legend and transition width are preserved through the complete final sentence.',
  'At 29.84–29.98 s chunk edge, zero-duration 영상에서/만나요 is appended, followed by a restart at 20.00 s repeating the previous role/focus sentences. Retain the raw result; this is not treated as evidence of a real extra greeting or repeated waveform.',
  'Recognition variants: 색띠/색디, 엘유티/LUT, 피사계/피삭의, 오른쪽의/오른쪽에, 화면에/화면의. The term and chunk artifact need targeted independent complete current-mix corroboration before final approval.'
 ], 'independentCorroborationPending': True},
 'whole-07': {'paragraphs': 9, 'notes': [
  'All nine expected/actual paragraphs, complete endings and every word timestamp directly read. Focus, camera conditions, linear/display transforms and CPU submission versus GPU completion remain present in order.',
  'At 69.86–69.98 s the chunked recognizer adds 시청해주셔서 감사합니다 with a zero-duration final word, then restarts at 60.00 s and repeats the earlier focus-settings sentence. This is not asserted to be a real greeting or repeated PCM.',
  'Independent context-focus-later-settings covers the complete paragraph around the artifact and remains pending. Variants retained: 상자의/상자에, 뒤의/뒤에, 비교에서도/비교해서도, 표시용/표시형, 기하/기아, 지금까지 네 게임/끝까지 넷게임. Human pronunciation remains pending.'
 ], 'independentCorroborationPending': True},
 'whole-08': {'paragraphs': 8, 'notes': [
  'All eight full expected/actual paragraphs and every timestamp read. Capture context, comparison purpose, Clear versus Draw, engine/API conditions, resource dimensions/mips and shader data flow are present through the complete final sentence.',
  'No extra greeting or long backward timestamp restart. Variants retained: 화면 밖의/밖에, 드로 인스턴스드/Draw Instance들, 메시/메쉬, 렌더독 시연에서는/랜더독션에서는에서는 at 123.36–124.30 s. The last term needs the pending independent complete pre-capture context; do not infer an actual duplicate syllable from this recognizer spelling.',
  'Self-made DX12 capture is explicitly a scoped frame-inspection method demonstration, not evidence of a commercial game lighting pipeline.'
 ], 'independentCorroborationPending': True},
 'whole-09': {'paragraphs': 8, 'notes': [
  'All eight full expected/actual paragraphs and every word timestamp directly read. Vertex versus pixel stage, returned color, projected depth, G-buffer visualization, shadow space, page pools and resource dependency limits are present through the final complete sentence.',
  'No added greeting, omitted full paragraph or long backward restart. Technical-word/particle variants preserved: 뒤의/뒤에, 렌더독 시연/렌더독 시, 리버스드 지/g, 가까움과 멂의 값 관계/가까움 과 머데 갑 관계 at 71.14–73.42 s, 언리얼/얼리얼 and 루멘의 방사휘도/룸앤의 방사위도.',
  'The newly prepared, unexecuted depth-and-gbuffer independent current-mix context covers the complete depth and G-buffer paragraphs. Final pronunciation is still pending human listening; recognizer spellings do not prove corrupt source PCM.'
 ], 'independentCorroborationPending': True},
}
target = P / 'part3-final-mixed-asr-direct-progress-v147.json'
progress = read(target) if target.exists() else {
 'schemaVersion': 1, 'records': [], 'allWholeAndIndependentTextsDirectlyCompared': False,
 'finalMixedAsrApproved': False, 'humanWholeListening': 'pending',
 'humanPronunciation': 'pending', 'automaticApproval': False,
}
execution = read(P / 'part3-final-mixed-asr-execution-v147.json')
for label, observation in observations.items():
 source = OUT / (label + '.json'); result = read(source)
 existing = next((r for r in progress['records'] if r['label'] == label), None)
 if existing:
  assert existing['resultSha256'] == sha(source)
  continue
 assert len(result['window']['expectedKo']) == observation['paragraphs']
 progress['records'].append({
  'label': label, 'resultPath': source.relative_to(ROOT).as_posix(),
  'resultSha256': sha(source), 'reviewedAt': stamp(),
  'directFullExpectedAndActualTextRead': True, 'allWordTimestampsRead': True,
  'paragraphIds': result['window']['paragraphIds'], 'notes': observation['notes'],
  'independentCorroborationPending': observation['independentCorroborationPending'],
  'finalContentApproval': False,
 })
progress.update(updatedAt=stamp(), currentMixSha256=execution['mixSha256'],
                planSha256=execution['planSha256'], directlyReadCount=len(progress['records']),
                expectedWindowCount=execution['total'])
temp = target.with_name(target.name + '.writing-' + str(os.getpid()))
temp.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + '\n', 'utf-8')
os.replace(temp, target)
print(json.dumps({'directlyRead': len(progress['records']), 'total': execution['total'], 'approved': False}))

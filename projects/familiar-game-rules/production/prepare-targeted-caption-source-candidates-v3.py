"""Record the directly read still trials and prepare reversible targeted fixes.

No PCM, original scripts, timeline durations, source intervals or final gates change.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, re
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()
norm = lambda t: ''.join(c for c in t if c.isalnum())
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 48)

trial_path = PROOF / 'targeted-framing-trials-v2.json'
trial = read(trial_path)
assert trial['boardCount'] == 15 and trial['imageCount'] == 90
assert read(ROOT / trial['inputReview'])['allInputBoardsDirectlyRead']
for row in trial['boards'] + trial['tiles']:
    assert sha(ROOT / row['path']) == row['sha256']

notes = [
    'Q1110/1139/1168: bottom120 raises the market player and umbrella above the fixed caption. The observed main shot remains in frame. Complete excerpt motion pending.',
    'Q1199/1285: market player and upper wire tool remain within bottom120 in these stills. Z1663: upper lift player visible, lower targets remain close to the caption. Do not treat all lift targets as solved.',
    'Z1686/1709: lift player remains visible; lower enemy bodies are still partly obscured. Z1756: grounded player/explosion clearer after bottom120. Lift cut03 remains unresolved.',
    'Z1777/1816: grounded tool/body clearer after bottom120; upper scaffold retained. Z2820: the main player is already left of the native caption; retain earlier 2805/2821 concerns for motion review instead of declaring all boss frames obstructed.',
    'B1470/1477/1530: boss player/tool raised above or beside the caption with upper barrel retained. Complete boss movement pending.',
    'B1596: airborne umbrella and boss barrel in frame. B2220/2279: junkyard player and nearby actions clearer after bottom120. Complete movement pending.',
    'B2386: grounded tool clearer after bottom120. B3480/3510: player and main barrel retained, but upper-right arm/projectile trajectory can leave the crop. That context needs complete motion review.',
    'B3540: left airborne player and boss barrel remain visible. C300/309: market player feet lifted above the fixed caption after bottom120.',
    'C319: clearer after bottom120. P1217: zipline tool approaches the upper crop edge; lower central enemy still partly behind the caption. P1334: upper player clear while lower feet remain obscured. Preserve native Pedro framing.',
    'P2261/2340: bottom120 clips the upper airborne actor at2340. Reject a blanket crop for this vertical sequence. P2548: some lower figures remain masked even after cropping.',
    'P2641/2700: partly hidden lower bodies and preserved upper-route context favor native framing. P4395: upper active aiming is visible in both versions, while some lower prospective targets remain obscured. Do not sacrifice upper space for peripheral feet.',
    'P4614: lower prospective feet overlap both versions. P5658/5707: bottom120 can clip upper target heads. Reject whole10-part2 crop; trial narrower semantic captions on native composition.',
    'P5880: upper yellow target head clipped after bottom120. P6216/6251: active upper red focus clear in native; lower blue prospective feet remain partly hidden. Preserve upper active context.',
    'H2256: lower feet clearer with bottom120, but H2466 clips the airborne player/head. Reject the whole18 crop. H3045: lower feet clearer but complete upper jump/descent context must remain.',
    'H3075: lower feet clearer after bottom120. H1865: upper-right target partly clipped by the crop. H1943: explosion briefly masks action in both versions. Reject a blanket19 crop and retain native upper route.',
]
review_path = PROOF / 'targeted-framing-direct-review-v2.json'
review = dict(schemaVersion=1, slug='familiar-game-rules', reviewedAt=now(), evidence=rel(trial_path),
              evidenceSha256=sha(trial_path), boards=[dict(index=b['index'], path=b['path'], sha256=b['sha256'],
              tileIndices=b['tileIndices'], directlyRead=True, notes=notes[b['index']-1]) for b in trial['boards']],
              all15BoardsDirectlyRead=True, all90TilesDirectlyRead=True, sampleComparisons=45,
              allSourceMotionReviewed=False, allFinalCaptionPixelsReviewed=False, finalTimelineAdopted=False,
              humanListeningPronunciation='pending', newGitImages=0,
              scope='Direct still comparisons only; explicit unresolved active/peripheral targets retained. No blanket crop or gate approval.')
if review_path.exists():
    previous=read(review_path)
    assert previous['evidenceSha256']==sha(trial_path) and previous['all90TilesDirectlyRead']
    assert [b['notes'] for b in previous['boards']]==notes
else:
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n', 'utf-8')

caption_path = BASE / 'word-caption-candidate-v2/captions.json'
caption = read(caption_path)
tail_path = BASE / 'current-independent-asr-v1/10-complete-tail.json'
tail = read(tail_path)
assert tail['startSeconds'] == 19.48
anchors = {'이런':20.52, '실행하며':22.00, '수':23.52, '확인해':25.24}
for word, t in anchors.items():
    assert any(w['text'].strip().rstrip('.,') == word and abs(tail['startSeconds']+w['timestamp'][0]-t)<1e-8 for w in tail['words'])
target = BASE / 'word-caption-candidate-v3'
assert not target.exists()
v3 = copy.deepcopy(caption)
old = {r['index']:r for r in caption['ko']}
rows=[]
splits={221:[('자신의 설계도',None,20.52),('이런 동작',20.52,None)],
        222:[('조합을 하나씩',None,22.00),('실행하며,',22.00,None)],
        223:[('목표를 고를',None,23.52),('수 있는지와',23.52,None)],
        224:[('안내가 맞는지를',None,25.24),('확인해 보세요.',25.24,old[225]['sourceSpeechEnd'])]}
for row in caption['ko']:
    if row['index']==225:continue
    if row['index'] not in splits:
        rows.append(copy.deepcopy(row));continue
    for text,a,z in splits[row['index']]:
        item=copy.deepcopy(row)
        a=row['sourceSpeechStart'] if a is None else a
        z=row['sourceSpeechEnd'] if z is None else z
        offset=row['startSeconds']-row['sourceSpeechStart']
        item.update(ko=text,lines=[text],sourceSpeechStart=a,sourceSpeechEnd=z,startSeconds=a+offset,
                    endSeconds=z+offset,textWidthPx=font.getlength(text), historicalCueIndices=[row['index']] + ([225] if text=='확인해 보세요.' else []),
                    boundaryEvidence=rel(tail_path),boundaryEvidenceSha256=sha(tail_path),
                    timingApproved=False,pixelsApproved=False)
        assert z>a and font.getlength(text)<=620
        rows.append(item)
assert len(rows)==253
assert norm(' '.join(r['ko'] for r in rows)) == norm(' '.join(r['ko'] for r in caption['ko']))
for i,row in enumerate(rows,1):row['index']=i
for left,right in zip(rows,rows[1:]):assert left['endSeconds']<=right['startSeconds']+1e-8
v3.update(preparedAt=now(), ko=rows,koCueCount=len(rows),baselineCaption=rel(caption_path),baselineCaptionSha256=sha(caption_path),
          status='targeted-semantic-splits-candidate-only',newAsrJobs=0,sourceActionAlignmentApproved=False,allCuePixelsReviewed=False,
          finalTimingApproved=False,finalTimelineAdopted=False,all70LiteralParagraphsPreserved=True,
          scope='Only221–225 split/merge into8 narrower cues at current independent complete-tail word boundaries. All words, outer ranges, all70 paragraphs, PCM, EN and timeline preserved. Direct pixels/motion/timing pending.')
v3['corrections'].append(dict(kind='native-upper-route-preserving-narrower-cues',historicalCues=[221,222,223,224,225],
                            independentEvidence=rel(tail_path),independentEvidenceSha256=sha(tail_path),
                            exactAnchors=anchors,captionCenter=[960,970],fontPx=48,sourceCropChanged=False,audioChanged=False,
                            readingDurationSecondsForClosingCue=old[225]['sourceSpeechEnd']-25.24,
                            outerCueRangeSeconds=[old[221]['startSeconds'],old[225]['endSeconds']],requiresDirectPixelMotionTimingReview=True))
target.mkdir()
def stamp(t):
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
(target/'candidate.ko.srt').write_text('\n\n'.join(f'{r["index"]}\n{stamp(r["startSeconds"])} --> {stamp(r["endSeconds"])}\n{r["ko"]}' for r in rows)+'\n','utf-8')
(target/'candidate.en.srt').write_bytes((caption_path.parent/'candidate.en.srt').read_bytes())
v3['englishSrtByteExactFromV2']=sha(target/'candidate.en.srt')==sha(caption_path.parent/'candidate.en.srt')
(target/'captions.json').write_text(json.dumps(v3,ensure_ascii=False,indent=2)+'\n','utf-8')

source_path=BASE/'word-action-source-candidate-v1.json'
source=read(source_path);candidate=copy.deepcopy(source)
crop_ids=['06-part1-cut02','14-cut01','06-part2-cut03','15-cut02','06-part3-cut01','06-part3-cut04','06-part3-cut07']
for p in candidate['pieces']:
    for cut in p['selectedSourceCuts']:
        if cut['id'] in crop_ids:
            cut.update(sourceCrop=[160,180,1600,900],framingMode='targeted-bottom120-candidate',
                       framingEvidence=rel(review_path),framingEvidenceSha256=sha(review_path),
                       sourceAndCaptionPixelsReviewed=False,completeMotionReviewed=False,wordActionAlignmentApproved=False)
candidate.update(preparedAt=now(),status='targeted7-Gunbrella-crops-and-native-Pedro-cue-splits-candidate-only',
                 baselineCandidate=rel(source_path),baselineCandidateSha256=sha(source_path),
                 captionCandidate=rel(target/'captions.json'),captionCandidateSha256=sha(target/'captions.json'),
                 ko=copy.deepcopy(rows),en=copy.deepcopy(v3['en']),targetedCropIds=crop_ids,
                 targetedFramingDirectReview=rel(review_path),targetedFramingDirectReviewSha256=sha(review_path),
                 allSourceSegmentPixelsReviewed=False,allSourceMotionReviewed=False,allFinalCaptionPixelsReviewed=False,
                 finalWordActionAlignment=False,finalTimingApproved=False,bodyRatioApproved=False,finalTimelineAdopted=False,
                 scope='Reversible7 targeted Gunbrella crops only; native Pedro/Hype framing retained. Source intervals, timeline,70 paragraphs, PCM and EN unchanged. All modified literal samples and complete motion need direct review.')
candidate['unresolved'].append('Lower lift enemies06-part1-cut03 remain partly masked; upper lift/player visibility alone is insufficient. Targeted crop/semantic remedy pending.')
candidate['unresolved'].append('06-part3-cut07 upper boss projectile/arm context needs complete motion review before targeted crop adoption.')
dest=BASE/'word-action-source-candidate-v2.json'
assert not dest.exists();dest.write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n','utf-8')
assert candidate['finalFrameBudget']==source['finalFrameBudget']==23570
assert len([c for p in candidate['pieces'] for c in p['selectedSourceCuts']])==78
print(json.dumps(dict(reviewedBoards=15,reviewedTiles=90,koCues=len(rows),enCues=len(v3['en']),targetedCropCount=len(crop_ids),
                      englishByteExact=v3['englishSrtByteExactFromV2'],paragraphs=70,timelineFrames=23570,approved=False)))

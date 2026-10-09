"""Seal the actually read nominal source boards without adopting footage."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def main():
    names = [('tetris-classic-official', 312, 52, '8271e3dd4e6e3e0a13046471c553516f432f0fcdd767a840f01fcb3bb776c946'),
             ('tetris-modern-official', 328, 55, 'c14d1d3034ce1585768119b6f957b7d0fc492b0afde286f0a677f43516d584d9')]
    rows = []
    for name, count, boards, source_hash in names:
        base = ROOT/'shared/output/presenting-game-scores/source-review-v1'/name
        ep = base/'execution.json'
        e = json.loads(ep.read_text(encoding='utf-8'))
        assert e['exitCode'] == e['wholeDecodeExit'] == 0
        assert e['samples'] == count and len(e['boards']) == boards
        assert e['sha256'] == source_hash == sha(Path(e['rawPath']))
        for b in e['boards']:
            assert sha(Path(b['path'])) == b['sha256']
            for x in b['entries']:
                assert sha(Path(x['path'])) == x['sha256']
        p = json.loads((base/'probe.json').read_text())['streams'][0]
        rows.append(dict(name=name, sourceSha256=source_hash,
                         execution=str(ep.relative_to(ROOT)).replace('\\','/'),
                         executionSha256=sha(ep), technicalExit=0, wholeDecodeExit=0,
                         reviewedBoardNumbers=list(range(1,boards+1)),
                         reviewedNominalSampleCount=count, allListedBoardPixelsDirectlyRead=True,
                         allListedNominalSamplePixelsDirectlyRead=True, allListedHashesMatched=True,
                         nativeVideoDuration=p['duration'], nativeFrameRate=p['avg_frame_rate'],
                         nativeTimeBase=p['time_base'], nativeFrameCount=int(p['nb_frames']),
                         footageAdopted=False, sourceAudioSelected=False, rastersGit=False))
    proof = dict(schemaVersion=2, slug='presenting-game-scores', reviewedAt=datetime.now(timezone.utc).isoformat(),
                 reviewScope='All 107 source observation boards and all 640 nominal half-second samples were directly read. These are source observations, not final encoded pixels.',
                 samplingCaveat='fps=2 labels index*0.5+0.25 are nominal observations, not verified native frame PTS or approved edit boundaries.',
                 officialChain=['https://www.tetriseffect.game/connected/media/',
                                'https://drive.google.com/drive/folders/1FWJA2z2jyqHi-Q5aO0X8Zsroi6vzMUIe',
                                'https://drive.google.com/drive/u/0/folders/1LyBkTx4u-6cNnS1dIYmsKx6UWysop0F0'],
                 recordingOwner='Enhance Games official press kit B-roll',
                 rights=dict(policy='https://www.tetriseffect.game/support/',
                             scope='Official recording acquisition and free original-commentary review. General game streaming/recording guidance is not treated as blanket permission for unrelated third-party recordings.',
                             originalMusicExcluded=True, sourceAudioSelected=False, finalPublicApproval=False),
                 allNativeFramesDirectlyReviewed=False, wholeContinuousPlaybackDirectlyWatched=False,
                 sourceIntervalsApproved=False, footageAdopted=False, newProjectCreated=False,
                 newScriptTtsOrMotionCanvasCreated=False, sources=rows,
                 observations={
                    'classic': [
                       {'nominalSeconds':'0-21', 'visible':'Active pieces, separate LINES and SCORE, signed opponent difference. Drop points can change while line count stays fixed.', 'limit':'Do not infer exact scoring formula.'},
                       {'nominalSeconds':'21.25-23.25', 'visible':'Left LINES 004 and score rise to 1315; right later LINES 001 and score 141.', 'limit':'Native-frame order and exact in/out still require review.'},
                       {'nominalSeconds':'61.25-82.75', 'visible':'Repeated actual placements and line clears; right reaches LINES 11, score1361, level01 while left LINES09/level00.', 'connection':'Quantity, evaluated score and pace are different measures.'},
                       {'nominalSeconds':'90.25-98.75', 'visible':'Both reach LINES12 with unequal scores; later both LINES13 show2602/1610 and signed gap992.', 'connection':'Equal quantity does not mean equal evaluated score.'},
                       {'nominalSeconds':'114.25-137.75', 'visible':'Both LINES19 scores3195/2530; later left LINES27/10453 versus right28/9955.', 'connection':'Compare named measures within the same mode and units, without declaring a best strategy.'},
                       {'nominalSeconds':'139.75-155.75', 'visible':'Left PLEASE WAIT, then WIN/LOSE, results and avatar EXP, ending black.', 'decision':'Waiting and static results are excluded from actual-play quota.'}
                    ],
                    'modern': [
                       {'nominalSeconds':'0-17.25', 'visible':'Friend-match ready menu, handicap, fade and countdown.', 'decision':'Exclude from actual-play quota.'},
                       {'nominalSeconds':'18.25-34.75', 'visible':'Active placements and scores rising with LINES0.', 'connection':'Score can count actions other than completed lines.'},
                       {'nominalSeconds':'35.75-41.25', 'visible':'T-SPIN DOUBLE/BACK-TO-BACK labels, right LINES2/1704 then4/3617; left LINES3/1142.', 'connection':'A labeled evaluation helps explain why a larger line count need not lead the score.'},
                       {'nominalSeconds':'49.75-67', 'visible':'T-SPIN, TETRIS and BACK-TO-BACK feedback; both later cross speed-level thresholds.', 'limit':'Feedback is observed; exact hidden weights and optimal play are not inferred.'},
                       {'nominalSeconds':'97.25', 'visible':'Both LINES27 with scores14096/17016 and gap2920.', 'connection':'Quantity and weighted evaluation need distinct labels.'},
                       {'nominalSeconds':'114.75-119.75', 'visible':'Left behind by5231, then T-SPIN DOUBLE/BACK-TO-BACK changes lead to+141 despite fewer lines; right later leads again.', 'connection':'Signed score difference gives a reference and changes meaning as play continues.'},
                       {'nominalSeconds':'125.25-148.75', 'visible':'Active placements/line clears and large score jumps. Camera tilts and particles alter bottom UI geometry.', 'limit':'Fixed caption margin requires exact source/crop/overlay review.'},
                       {'nominalSeconds':'149.75-164.197', 'visible':'Left topped-out/LOSE; right continues briefly then WIN; static scores31003/39589, per-line average688/842, rankD, black at163.75.', 'decision':'End/wait/result/EXP screens excluded from actual-play quota; no causal winner claim from selected earlier montage.'}
                    ]},
                 next='Verify normal-speed continuous actions, native PTS and exact selected boundaries/fixed-caption UI before game-candidates adoption. Recheck current duplicate input digest before project creation.',
                 researchGpuStopped=False, researchProcessManipulated=False, rasterGitAdditions=0)
    out=HERE/'tetris-source-direct-review-v2.json'
    assert not out.exists(), 'Preserve existing review proof'
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':str(out.relative_to(ROOT)), 'sha256':sha(out), 'boardsRead':107,'nominalSamplesRead':640,'adopted':False}))

if __name__ == '__main__':
    main()

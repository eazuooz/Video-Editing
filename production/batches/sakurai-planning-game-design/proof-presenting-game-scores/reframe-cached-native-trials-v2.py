"""Reuse native samples to test fixed captions; never regenerate source extraction."""
import hashlib, json, os, time
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[4]
PR = Path(__file__).parent
OLD = ROOT / 'shared/output/presenting-game-scores/native-cut-trials-v1'
OUT = ROOT / 'shared/output/presenting-game-scores/native-framing-v2'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def save(p, d): Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    prior = json.loads((OLD/'execution-resume-v1.json').read_text(encoding='utf-8'))
    assert prior['exitCode'] == 0 and prior['boardCount'] == 50
    for board in prior['boards']:
        assert sha(board['path']) == board['sha256']
        for entry in board['entries']:
            assert sha(entry['path']) == entry['sha256']
    review = dict(schemaVersion=1, reviewedAt=now(), execution=str(OLD/'execution-resume-v1.json'),
        executionSha256=sha(OLD/'execution-resume-v1.json'), reviewedBoards=list(range(1,51)),
        reviewedOverlaySamples=295, directlyReadAllListedBoards=True, allListedHashesMatched=True,
        scope='Native source cut trials with placeholder captions; neither actual narration cues nor final encoded pixels.',
        findings=[
            'Uncropped and crop-y120 zoom trials both obscure portions of bottom Tetris player names/WINS. Neither framing is adopted.',
            'Classic first native frame f0 is black. Reject original start0; f50 at2.0s is directly observed active play.',
            'Classic equal line counts12/13/19 coexist with different scores; signed differences update during play. No exact scoring formula or optimal strategy inferred.',
            'Modern T-SPIN DOUBLE/BACK-TO-BACK and line/score changes are visible. At f3455 PTS3458455, left29lines/19919 and right32lines/19778 give left+141; later the lead changes again.',
            'Modern late camera angle/particles change UI geometry. Native trial ends before observed top-out/wait/results.',
            'Balatro11.4-18.9 trial ends in greyscale game-over transition. That ending is excluded, and captions cover lower cards/options in wider shots. No continuous17s adoption.',
            'Balatro closeups show four A cards and then, in a different sequence, Five of a Kind lvl5, chips/mult count-up. They do not establish an optimal strategy or one continuous run.',
            'Ballionaire f965 is a wipe and f2027 is a vending/unlock screen; reject those exact trial endings and do not count them as actual play.',
            'Ballionaire remains held because the Raw Fury functional product link condition needs compatibility with the user public-credit preference; no rights assumption.'
        ], sourceIntervalsApproved=False, footageAdopted=False, allFinalPixelsReviewed=False,
        wholeContinuousPlaybackDirectlyWatched=False, allNativeFramesDirectlyReviewed=False,
        researchStopped=False, rasterGitAdditions=0)
    assert not (PR/'native-cut-trials-direct-review-v1.json').exists()
    save(PR/'native-cut-trials-direct-review-v1.json', review)
    assert not OUT.exists(), 'Preserve existing framing; read checkpoint instead'
    OUT.mkdir(parents=True)
    state=dict(schemaVersion=2, startedAt=now(), pid=os.getpid(), processCreatedEpoch=time.time(),
        stage='reframing-cached-native-samples', cpuThreads=1, gpu=0, exitCode=None,
        sourceExtractionRepeated=False, sourceDecodeRepeated=False,
        variant='shift-y120-same-frame-blur-fill', foregroundCrop=[0,120,1920,1080],
        foregroundPosition=[0,0], foregroundScale=1, bottomFill='same source frame Gaussian blur radius24; bottom120px only',
        fixedCaptionCenter=[960,970], box=[153,897,1767,1043], shadow=[167,911,1781,1057],
        footageAdopted=False, sourceIntervalsApproved=False, allFinalPixelsReviewed=False, rastersGit=False,
        sources=[], images=[], boards=[])
    ep=OUT/'execution.json'; save(ep,state)
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
    label=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
    try:
        for src in prior['sources']:
            if src['name'] not in ['classic','modern']: continue
            state['sources'].append({k:src[k] for k in ['name','rawPath','rawSha256','ptsPath','ptsSha256','cuts']})
            for row in src['samples']:
                assert sha(row['rawPath']) == row['rawSha256']
                im=Image.open(row['rawPath']).convert('RGB')
                assert im.size == (1920,1080)
                pic=im.filter(ImageFilter.GaussianBlur(24))
                pic.paste(im.crop((0,120,1920,1080)),(0,0))
                draw=ImageDraw.Draw(pic)
                draw.rectangle((167,911,1781,1057),fill='#073c32')
                draw.rectangle((153,897,1767,1043),fill='white',outline='#161b18',width=3)
                for text,y in [('점수와 지운 줄 수는 서로 다른 기준입니다.',939),('지금 비교하는 값과 단위를 함께 확인하세요.',1001)]:
                    draw.text((960,y),text,font=font,fill='#080b09',anchor='mm')
                dest=OUT/f"{src['name']}-{row['frame']:06}.jpg"
                pic.save(dest,quality=94)
                state['images'].append(dict(path=str(dest),sha256=sha(dest),source=src['name'],**row))
            save(ep,state)
        for start in range(0,len(state['images']),6):
            board=Image.new('RGB',(1920,1683),'#151515'); draw=ImageDraw.Draw(board)
            entries=state['images'][start:start+6]
            for j,row in enumerate(entries):
                im=Image.open(row['path']);im.thumbnail((948,533))
                x=j%2*960+6;y=j//2*561+28;board.paste(im,(x,y))
                draw.text((x,y-26),f"{row['source']} shift-y120 f{row['frame']} PTS{row['pts']}",fill='white',font=label)
            dest=OUT/f'board-{start//6+1:03}.jpg';board.save(dest,quality=94)
            state['boards'].append(dict(path=str(dest),sha256=sha(dest),entries=entries))
        state.update(stage='cached-framing-ready-direct-review-pending',finishedAt=now(),exitCode=0,
            sampleCount=len(state['images']),boardCount=len(state['boards']))
        save(ep,state)
        print(json.dumps(dict(exit=0,samples=len(state['images']),boards=len(state['boards']),adopted=False)))
    except BaseException as e:
        state.update(stage='cached-framing-failed',finishedAt=now(),exitCode=1,error=repr(e));save(ep,state);raise

if __name__=='__main__': main()

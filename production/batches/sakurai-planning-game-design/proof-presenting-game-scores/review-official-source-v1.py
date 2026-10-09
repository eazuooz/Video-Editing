"""Single CPU source verification and local-only observation boards; no adoption gate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
FF = Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
FP = FF.with_name('ffprobe.exe')

def stamp():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--url', required=True)
    a = ap.parse_args()
    source = Path(a.source).resolve()
    raw = ROOT/'shared/assets/presenting-game-scores/raw'/source.name
    out = ROOT/'shared/output/presenting-game-scores/source-review-v1'/a.name
    if out.exists():
        raise RuntimeError('Existing source review preserved; do not rerun completed job')
    out.mkdir(parents=True)
    raw.parent.mkdir(parents=True, exist_ok=True)
    h = sha(source)
    if raw.exists():
        assert sha(raw) == h, 'Do not overwrite a different source'
    else:
        shutil.copy2(source, raw)
    assert sha(raw) == h
    state = {'schemaVersion':1,'stage':'source-review-running','startedAt':stamp(),
             'pid':os.getpid(),'processCreatedEpoch':time.time(),'command':a.__dict__,
             'cpuThreads':2,'gpu':0,'sourcePath':str(source),'rawPath':str(raw),
             'sourceUrl':a.url,'sha256':h,'bytes':raw.stat().st_size,
             'sourcePreserved':True,'sourceAudioSelected':False,'directPixelsReviewed':False,
             'footageAdopted':False,'rightsFinalPublicApproval':False,'rastersGit':False}
    sp = out/'execution.json'
    def save():
        sp.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    save()
    try:
        p = subprocess.run([str(FP),'-v','error','-show_streams','-show_format','-of','json',str(raw)],capture_output=True,text=True,check=True)
        probe = json.loads(p.stdout)
        (out/'probe.json').write_text(json.dumps(probe, indent=2)+'\n',encoding='utf-8')
        duration = float(probe['format']['duration'])
        with (out/'whole-decode.log').open('w',encoding='utf-8') as log:
            d = subprocess.run([str(FF),'-nostdin','-v','error','-threads','2','-i',str(raw),'-map','0:v:0','-map','0:a?','-f','null','-'],stdout=log,stderr=log)
        state['wholeDecodeExit'] = d.returncode
        assert d.returncode == 0
        frames = out/'frames'
        frames.mkdir()
        with (out/'sampling.log').open('w',encoding='utf-8') as log:
            s = subprocess.run([str(FF),'-nostdin','-v','error','-threads','2','-i',str(raw),'-an','-vf','fps=2','-threads','2','-q:v','2',str(frames/'source-%04d.jpg')],stdout=log,stderr=log)
        assert s.returncode == 0
        imgs = sorted(frames.glob('*.jpg'))
        font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf',24)
        boards=[]
        for start in range(0,len(imgs),6):
            board=Image.new('RGB',(1920,1683),'#1a1a1a')
            draw=ImageDraw.Draw(board)
            entries=[]
            for j, path in enumerate(imgs[start:start+6]):
                sample=(start+j)*0.5+0.25
                im=Image.open(path).convert('RGB')
                im.thumbnail((948,533))
                x=(j%2)*960+6;y=(j//2)*561+28
                board.paste(im,(x,y))
                draw.text((x,y-27),f'{start+j+1:03d}  sample {sample:.2f}s',fill='white',font=font)
                entries.append({'index':start+j+1,'samplingTime':sample,'path':str(path),'sha256':sha(path)})
            bp=out/f'board-{start//6+1:03d}.jpg'
            board.save(bp,quality=94)
            boards.append({'path':str(bp),'sha256':sha(bp),'entries':entries})
        state.update(stage='source-technical-review-complete-direct-review-pending',
                     durationSeconds=duration,samples=len(imgs),boards=boards,finishedAt=stamp(),exitCode=0)
        save()
        print(json.dumps({'exit':0,'source':str(raw),'sha256':h,'duration':duration,'samples':len(imgs),'boards':len(boards),'directPixelsReviewed':False}))
    except BaseException as e:
        state.update(stage='source-review-failed',error=repr(e),finishedAt=stamp(),exitCode=1)
        save()
        raise

if __name__=='__main__':
    main()

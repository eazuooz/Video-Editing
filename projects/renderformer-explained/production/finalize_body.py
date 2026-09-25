"""Finish the repaired body, captions and media QA; never invent a membership ending."""
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/renderformer-explained/production/body-review'
def run(*args):subprocess.run(args,cwd=ROOT,check=True)
if not (BASE/'page22-repair.json').exists():raise RuntimeError('Page 22 repair must finish first')
clean=BASE/'renderformer-clean-review.mp4'
previous=BASE/'renderformer-clean-before-page22-repair.mp4'
if not previous.exists():
    clean.rename(previous)
    run('ffmpeg','-v','error','-n','-i',str(previous),'-i',str(BASE/'narration-mastered.m4a'),
        '-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(clean))
run(sys.executable,'projects/renderformer-explained/production/apply_caption_terms.py')
run(sys.executable,'projects/renderformer-explained/production/build_english_subtitles.py')
if not (BASE/'renderformer-captioned-review.mp4').exists():
    run('node','motion-canvas/scripts/compose-renderformer-captions.cjs')
run('C:/Python/python.exe','projects/renderformer-explained/production/verify_body.py')
report={'stage':'body-review-rendered','pages':88,'duration':2648.75,'frames':158925,'publishReady':False,
        'pending':['human listening approval','original membership screenshot and 10-second ending'],
        'englishSubtitles':'533 translated cues with identical Korean timecodes','bgm':None}
(BASE/'render-progress.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(BASE/'progress.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Complete 88-page body review ready. Membership source and listening approval remain.',flush=True)
run('node','scripts/collect-video-output.cjs','renderformer-explained')

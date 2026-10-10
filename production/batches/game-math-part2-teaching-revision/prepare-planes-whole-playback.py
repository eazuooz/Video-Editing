"""Expose the current completed captioned file at native speed; no approval."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('slug',choices=['game-math-plane-distances-v2','game-math-triangle-addresses-v2']);a=p.parse_args()
P=ROOT/'projects'/a.slug;m=json.loads((P/'project.json').read_text(encoding='utf8'));t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'));src=ROOT/m['paths']['videoBurnedCaptions']
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(src)],text=True,creationflags=subprocess.CREATE_NO_WINDOW));v=next(s for s in info['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==t['frames'] and v['r_frame_rate']=='60/1'
sha=hashlib.sha256(src.read_bytes()).hexdigest();O=ROOT/'shared/output/game-math-part2-teaching-revision';target=O/(a.slug+'.captioned.mp4')
if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest()!=sha:shutil.copy2(src,target)
template=(O/'game-math-lines-circles-v2-review.html').read_text(encoding='utf8')
template=template.replace('game-math-lines-circles-v2',a.slug).replace('직선·경계','평면·삼각형 좌표')
import re
template=re.sub(r'[0-9a-f]{64}',sha,template)
(O/(a.slug+'-review.html')).write_text(template,encoding='utf8')
print(json.dumps({'slug':a.slug,'sha256':sha,'seconds':t['seconds'],'page':f'http://127.0.0.1:9261/{a.slug}-review.html','actualViewingComplete':False}))

"""Make a complete1080p60 H.264 copy within the connected Drive upload limit.

Preserves the validated high-bitrate master. Promotion/QA is explicit; this
script does not upload, overwrite the canonical output, or approve the copy.
"""
from pathlib import Path
import json,subprocess,hashlib,datetime
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
O=ROOT/'shared/output'/SLUG
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
control=read(ROOT/'shared/publishing/video-production-control.json')
assert control['selectedVideo']==SLUG
source=ROOT/'shared/output/motion-canvas'/f'{SLUG}-subtitled.mp4'
integrity=read(O/'encoded-integrity.json')
assert sha(source)==integrity['outputs'][1]['sha256']
target=O/'drive-optimized-v1.mp4';assert not target.exists()
args=['ffmpeg','-hide_banner','-v','warning','-n','-i',str(source),'-map','0:v:0','-map','0:a:0',
      '-c:v','h264_nvenc','-preset','p7','-tune','hq','-rc','vbr','-multipass','fullres',
      '-b:v','2500k','-maxrate','10M','-bufsize','20M','-rc-lookahead','32',
      '-spatial-aq','1','-temporal-aq','1','-aq-strength','8','-bf','3','-b_ref_mode','middle',
      '-fps_mode','passthrough','-frames:v',str(integrity['outputs'][1]['frames']),
      '-c:a','copy','-movflags','+faststart','-progress',str(O/'drive-optimization-progress.txt'),str(target)]
recipe={'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':source.relative_to(ROOT).as_posix(),'sourceSha256':sha(source),'args':args,'reason':'Connector512MiB limit; web file chooser stayed at upload starting and was closed. Original high-bitrate master preserved.','sampleReview':{'diagram42sSsim':.998974,'game30sSsim':.947827,'directSampleFramesReviewed':True,'sampleBitrate':2400000,'finalBitrate':2500000},'status':'encoding; not yet QA approved'}
(O/'drive-optimization.json').write_text(json.dumps(recipe,indent=2)+'\n',encoding='utf-8')
with (O/'drive-optimization.log').open('wb') as log:subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
assert target.stat().st_size<536870912,'Do not upload an oversized file'
recipe.update(status='encoded; current-output QA pending',completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),target=target.relative_to(ROOT).as_posix(),sha256=sha(target),bytes=target.stat().st_size)
(O/'drive-optimization.json').write_text(json.dumps(recipe,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'bytes':target.stat().st_size,'sha256':recipe['sha256'],'status':recipe['status']}))

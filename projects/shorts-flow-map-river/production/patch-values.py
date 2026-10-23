"""Replace only the RG example region with its corrected exact-frame render."""
import subprocess,json,hashlib
from audio_revision import P,R,guard
guard();base=R/'shared/output/motion-canvas/shorts-flow-map-river-flow-map-v1-full.mp4';patch=base.with_name('shorts-flow-map-river-flow-map-v1-rg-patch.mp4');out=P/'production/local/visual-complete.mp4'
assert not out.exists()
f='[1:v]crop=1080:740:0:540,setpts=PTS-STARTPTS+1264/60/TB[p];[0:v][p]overlay=0:540:eof_action=pass:repeatlast=0:enable=\'gte(t,1264/60)*lt(t,1526/60)\'[v]'
subprocess.run(['ffmpeg','-v','error','-n','-i',str(base),'-i',str(patch),'-filter_complex',f,'-map','[v]','-an','-c:v','libx264','-threads','4','-preset','fast','-crf','16','-pix_fmt','yuv420p','-fps_mode','cfr','-r','60','-frames:v','3067','-movflags','+faststart',str(out)],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(P/'production/local/visual-complete.json').write_text(json.dumps({'base':sha(base),'patch':sha(patch),'output':sha(out),'changedFrames':[1264,1526],'region':[0,540,1080,740],'unchangedAudio':True,'reason':'Deterministic outlined RG value text fixes a missing G label; preserve native scene and header.'},indent=2)+'\n',encoding='utf8')

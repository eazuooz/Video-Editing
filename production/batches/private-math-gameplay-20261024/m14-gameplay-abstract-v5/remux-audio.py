"""Apply the prepared lecture mix to the selected, still-unreviewed masters."""
from pathlib import Path
import importlib.util
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base',B.parent/'render-patches.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
slug='game-math-polygon-partition-v2';P=R/'projects'/slug;H=P/'production/gameplay-abstract-v5';O=P/'production/local/gameplay-abstract-v5';D=R/'output'/f'{slug}-gameplay-abstract-v5'
c=m.read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations']['m14-gameplay-abstract-v5']
assert c['status']=='active' and c['renderAuthorized'] and not c['uploadAuthorized']
out=m.read(H/'outputs.json');assert out['status']=='encoded-qa-pending'
plan=m.read(H/'plan.json')
for kind in ['clean','captioned']:
 file=D/f'{slug}.{kind}.mp4';temp=D/f'{slug}.{kind}.audio-repair.mp4'
 m.ff(['-i',file,'-i',O/'final-mix.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar',48000,'-movflags','+faststart',temp],O/f'audio-repair-{kind}.log',O)
 before=next(s for s in m.probe(file)['streams'] if s['codec_type']=='video');after=next(s for s in m.probe(temp)['streams'] if s['codec_type']=='video')
 assert before['nb_frames']==after['nb_frames']==str(plan['totalFrames'])
 temp.replace(file)
for e in out['outputs']:
 f=R/e['path'];e.update(bytes=f.stat().st_size,sha256=m.sha(f))
out['introSourceAudio']='Excluded mixed trailer music; original body mix retained.'
m.save(H/'outputs.json',out)
print('Both video streams copied unchanged; narration-only abstract mix applied.')

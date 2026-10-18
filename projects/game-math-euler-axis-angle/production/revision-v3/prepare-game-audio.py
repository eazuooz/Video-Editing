"""Measure and attenuate locked source cuts; reused by the final audio mix."""
from pathlib import Path
import importlib.util
p=Path(__file__).with_name('build-audio.py');s=importlib.util.spec_from_file_location('audio',p);a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
assert a.read(a.R/'shared/publishing/video-production-control.json')['selectedVideo']==a.P.name
plan=a.read(a.P/'sources/cut-plan-v3.json');media={v['id']:v for v in a.read(a.P/'sources/media-revision-v3.json')['sources']};cache=a.O/'game-audio';cache.mkdir(exist_ok=True)
for sid,scene in plan['scenes'].items():
 if sid=='23':continue
 source=plan['sources'][scene['sourceId']];digest=a.sha(a.R/source['file']);assert digest==media[scene['sourceId']]['downloadedSha256']
 for i,(start,end) in enumerate(scene['ranges'],1):
  frames=round(end*60)-round(start*60);c=dict(id=f'{sid}-cut-{i:02}',sourceSha256=digest,sourceStart=start,sourceFile=source['file'],frames=frames,seconds=frames/60)
  _,info=a.quiet_game_cut(c,cache);print(c['id'],round(info['gainDb'],2),'dB attenuation',flush=True)

"""Final narration-timed ASS from observed projected landmarks, never world angles."""
from pathlib import Path
import hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
spec=importlib.util.spec_from_file_location('screen_overlay_renderer',B/'render-quaternion-track-drafts-v3.py')
renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
def stem(slot):return {'trailmakers-JvTCVUEc1ZE':'trail','space-engineers-XvpNC9lkLwQ':'gear-v3','besiege-uWKEJ92486U':'besiege'}[slot['cut']['sourceId']]
def track_sha(slot):
 return [hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/(stem(slot)+'-screen-track.json'),B/'render-quaternion-track-drafts-v3.py',Path(__file__)]]
def crop_filter(slot,segment):
 crop=segment.get('crop') or {'trail':[360,340,1200,674],'besiege':[320,90,1440,810]}[stem(slot)]
 x,y,w,h=crop
 return f'crop={w}:{h}:{x}:{y},scale=1920:1080:flags=lanczos,setsar=1,fps=60'
def write_overlay(slug,ident):
 timeline=read(ROOT/f'projects/{slug}/production/timeline.json');slot=next(s for s in timeline['scenes'] if s['id']==ident)
 assert slot['classification']=='actual' and not slot['preservedOriginal']
 track=read(R/(stem(slot)+'-screen-track.json'));assert slot['frames']<=len(track['frames'])
 reveal=slot.get('annotationReveal',{});red=reveal.get('redAt',slot['lineStarts'][0]);blue=reveal.get('blueAt',red)
 # An inserted observation pause can fall after an imprecise raw-ASR word
 # onset. Prefer the audited actual final-AAC cue for this visual layer.
 overrides=R/'final-aac-annotation-reveal.json'
 if overrides.exists():
  selected=read(overrides).get(ident)
  if selected:
   assert selected['voiceSha256']==slot['voiceSha256']
   red=selected.get('redAt',red);blue=selected.get('blueAt',blue)
 path=ROOT/f'shared/output/{slug}/overlays/{ident}.ass';path.parent.mkdir(parents=True,exist_ok=True)
 return renderer.write_overlay(stem(slot),target=path,red_at=red,blue_at=blue)

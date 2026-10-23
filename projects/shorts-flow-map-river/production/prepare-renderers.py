"""Create this project's finite render wrappers from the proven local pipeline."""
from pathlib import Path
import json
from audio_revision import P,R,guard
guard();old=R/'projects/shorts-normal-map-illusion/production'
def transform(t):
 return t.replace('shorts-normal-map-illusion','shorts-flow-map-river').replace('normal-map-v3-spatial-normals','flow-map-v1').replace('audio-v2','audio').replace('final-v3','final')
t=transform((old/'render-visual.cjs').read_text(encoding='utf8'))
a=t.index("const capture=");b=t.index("const mode=",a)
t=t[:a]+"const capture=read(path.join(local,'capture-full/success.json'));\nif(!control.shortsDirectSelection?.fullProductionAuthorized||capture.frames!==timing.frames)throw Error('Finite native capture incomplete');\n"+t[b:]
t=t.replace("'v3-spatial-normals-full-v1'","'flow-map-v1-full'")
(P/'production/render-visual.cjs').write_text(t,encoding='utf8')
t=transform((old/'render-preflight.cjs').read_text(encoding='utf8'))
t=t.replace("const finalInputs=process.argv[4]==='final';","const finalInputs=true;")
(P/'production/render-preflight.cjs').write_text(t,encoding='utf8')
t=transform((old/'finish-video.py').read_text(encoding='utf8'))
a=t.index('    # Visual-onlyv3:');b=t.index('    points=sorted',a);t=t[:a]+t[b:]
a=t.index("scope='Changed");b=t.index("'))",a)
t=t[:a]+"scope='All cue midpoints, every section join and sampled motion states at native and mobile size. Moving playback separately recorded."+t[b:]
(P/'production/finish-video.py').write_text(t,encoding='utf8')
timing=json.loads((P/'production/visual-timing.json').read_text(encoding='utf8'))
meta=json.loads((R/'motion-canvas/src/projects/shorts-normal-map-illusion/project.meta').read_text(encoding='utf8'))
meta['shared']['range']=[0,timing['durationSeconds']]
(R/'motion-canvas/src/projects'/P.name/'project.meta').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf8')

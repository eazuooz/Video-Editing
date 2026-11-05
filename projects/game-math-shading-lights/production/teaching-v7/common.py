import hashlib
import json
import sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
PROJECT=BASE.parents[1]
ROOT=PROJECT.parents[1]
WORK=PROJECT/'production/local/render-v7'
OUT=ROOT/'output'/(PROJECT.name+'-render-v7')
V6=ROOT/'output'/(PROJECT.name+'-render-v6')
V6WORK=WORK.parent/'render-v6'
VOICE=WORK/'speech'
for folder in [WORK,VOICE,OUT]:folder.mkdir(parents=True,exist_ok=True)
sys.path.append(str(PROJECT/'production/terms-v6'))
import build as v6
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):
    with open(p,'rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def make_voice():
    from narration import LESSONS
    control=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
    assert control['productionAllowedNow'] and PROJECT.name in control['projectSlugs']
    manifest=read(PROJECT/'production/tts-manifest.json')
    for lang,idx,key in [('ko',0,'script'),('en',1,'scriptEn')]:
        dest=VOICE/('script.'+lang+'.json')
        write(dest,dict(slug=PROJECT.name,scenes=[dict(id=f'{i:03}',title=v6.TITLES[i][1],lines=[' '.join(x[idx] for x in clauses)]) for i,clauses in LESSONS.items()]))
        manifest['paths'][key]=dest.relative_to(ROOT).as_posix()
    manifest['tts'].update(outputDir=VOICE.relative_to(ROOT).as_posix(),status='new-meaning-first-paragraphs')
    manifest['tts'].pop('generatedPcmSha256',None)
    write(VOICE/'manifest.json',manifest)
if __name__=='__main__':make_voice()

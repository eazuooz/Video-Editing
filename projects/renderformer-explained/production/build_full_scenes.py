"""Generate 88 independent editable scenes and immutable source page assets.
layout-project is explicitly a silent visual QA reel, never the finished video.
The narrated project is generated only by the measured-audio assembler.
"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT/'projects/renderformer-explained'
MC = ROOT/'motion-canvas/src/projects/renderformer-explained/full'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def main():
    manifest = json.loads((PROJECT/'project.json').read_text(encoding='utf-8'))
    source = Path(manifest['sourceDocument']['path'])
    if hashlib.sha256(source.read_bytes()).hexdigest() != manifest['sourceDocument']['sha256']:
        raise RuntimeError('Source PDF changed: review required.')
    script = json.loads((PROJECT/'script/narration.ko.json').read_text(encoding='utf-8'))
    overlays = json.loads((PROJECT/'production/slide-overlays.json').read_text(encoding='utf-8'))
    assets = MC/'assets'
    assets.mkdir(parents=True, exist_ok=True)
    images = sorted(assets.glob('page-*.png'))
    if len(images) != 88:
        subprocess.run(['C:/texlive/2025/bin/windows/pdftoppm.exe','-scale-to','2560',
                        '-png',str(source),str(assets/'page')],check=True)
    if len(list(assets.glob('page-*.png'))) != 88:
        raise RuntimeError('Missing source page raster.')
    write(MC/'overlays.generated.json',json.dumps(overlays,ensure_ascii=False,indent=2)+'\n')
    write(MC/'pages.generated.ts','// Generated from immutable 88-page PDF.\n'+
          '\n'.join(f"import p{i:02} from './assets/page-{i:02}.png';" for i in range(1,89))+
          '\nexport const pages = ['+','.join(f'p{i:02}' for i in range(1,89))+'];\n')
    timing={'kind':'silent-layout-review-only','fps':60,'duration':440,'totalFrames':26400,
            'scenes':[{'id':s['id'],'sourcePage':s['sourcePage'],'title':s['title'],
                       'firstFrame':i*300,'frames':300,'duration':5,'cues':[]}
                      for i,s in enumerate(script['scenes'])]}
    write(MC/'layout.generated.json',json.dumps(timing,ensure_ascii=False,indent=2)+'\n')
    imports=[]
    for s in script['scenes']:
        sid=s['id']
        write(MC/f'layout/page{sid}.tsx',
              "import {makeScene2D} from '@motion-canvas/2d';\nimport {lectureSlide} from '../slide';\n"+
              "import timing from '../layout.generated.json';\n"+
              f"export default makeScene2D(function* (view) {{yield* lectureSlide(view,timing.scenes[{int(sid)-1}],false);}});\n")
        imports.append(f"import page{sid} from './layout/page{sid}?scene';")
    write(MC/'layout-project.ts',"import {makeProject} from '@motion-canvas/core';\n"+
          '\n'.join(imports)+"\nexport default makeProject({name:'RenderFormer — 무음 화면 검수본', scenes:["+
          ','.join(f"page{s['id']}" for s in script['scenes'])+"]});\n")
    print('Created 88 independent source-page scenes; layout review only, no invented speech timing.')


if __name__=='__main__':main()

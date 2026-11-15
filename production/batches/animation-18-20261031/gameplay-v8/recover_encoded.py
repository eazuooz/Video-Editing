"""Verification-only recovery: never re-encode an already completed own master."""
from common import *
import ast,inspect
import render

def main(ep):
 e=next(e for e in read(HERE/'plan.json')['episodes'] if e['id']==ep);render.guard(ep)
 folder=WORK/ep;dest=OUTPUT/ep;audio=read(folder/'audio.json');frames=audio['frames']
 files={r['kind']:Path(r['path']) for r in e['baselineFiles']}
 clean=dest/files['clean.mp4'].name;captioned=dest/files['captioned.mp4'].name
 assert clean.is_file() and captioned.is_file() and not clean.with_suffix('.partial.mp4').exists()
 tree=ast.parse(inspect.getsource(render.render_episode));body=tree.body[0].body
 start=next(i for i,n in enumerate(body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='result' for t in n.targets))
 scope=dict(vars(render),e=e,ep=ep,folder=folder,dest=dest,audio=audio,changes=audio['changes'],frames=frames,files=files,clean=clean,captioned=captioned,spans=e['replacementSpans'])
 exec(compile(ast.Module(body=body[start:],type_ignores=[]),str(HERE/'render.py'),'exec'),scope)
 save(folder/'verification-recovery.json',dict(reason='Preserve completed masters; balanced FFmpeg select expression fixes frame-extraction failure.',reencoded=False,updatedAt=stamp()))
if __name__=='__main__':
 import sys
 main(sys.argv[1])

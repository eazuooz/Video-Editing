"""Register actual sprite-gen cuts to each source sheet's fixed cell origin.

This changes placement only, not pose pixels or individual pose scale.
The tool's per-cell bbox centering is undone, preserving the source motion.
"""
from pathlib import Path
from PIL import Image
import json, hashlib, shutil

ROOT=Path(__file__).resolve().parents[4]
P=ROOT/'projects/ai-2d-game-assets'
OUT=ROOT/'sites/yamyam-cartographers-room/dist/assets/motions'
OUT.mkdir(parents=True,exist_ok=True)
specs=[('walk','walk-eight','hero-walk-eight-source.png'),('sit','sit-eight','hero-sit-eight-source.png'),('book','book-eight-v2','hero-book-eight-source-v2.png'),('look','look-eight','hero-look-eight-source.png')]
records=[]
for prefix,folder,source in specs:
    base=P/'production/local/room-v2'/folder
    sheet=Image.open(P/'assets/local/room-v2'/source).convert('RGBA')
    report=json.loads((base/f'{prefix}-slice-sheet.json').read_text())
    s=report['factor']
    for i in range(8):
        cell=sheet.crop(((i%4)*384,(i//4)*512,(i%4+1)*384,(i//4+1)*512))
        mask=cell.getchannel('A').point(lambda a:255 if a>=128 else 0)
        bb=mask.getbbox()
        src=Image.open(base/f'{prefix}-{i:02}.png').convert('RGBA')
        dx=round(((bb[0]+bb[2])/2-192)*s)
        dy=round((bb[3]-480)*s)
        dst=Image.new('RGBA',(128,176))
        dst.alpha_composite(src,(dx,dy))
        path=OUT/f'{prefix}-{i:02}.png';dst.save(path)
        records.append({'file':path.relative_to(ROOT).as_posix(),'source':source,'frame':i,'sourceBox':bb,'toolFactor':s,'registrationTranslation':[dx,dy],'anchor':[64,166],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})

def clip(prefix,ids,fps=8,loop=False):
    return {'frames':[f'motions/{prefix}-{i:02}.png' for i in ids],'canvas':[128,176],'anchor':[64,166],'gameScale':.75,'fps':fps,'loop':loop}
clips={
 'walk-right':clip('walk',range(8),10,True),
 'sit-down':clip('sit',range(8),6.4),
 'sit-idle':clip('sit',[7],1,True),
 'look-enter':clip('look',range(8),6.4),
 'look-idle':clip('look',[7],1,True),
 'book-take':clip('book',range(8),3.2),
 'book-read':clip('book',[7],1,True),
 'book-return':clip('book',list(range(7,-1,-1)),3.2),
 'map-open':clip('book',range(4,8),2.67),
 'map-read':clip('book',[7],1,True)
}
manifest={'version':2,'clips':clips,'registration':'Shared source-cell root (192,480), same per-sheet scale, no per-frame bbox recentering','visualQa':'8-frame source sequences inspected; game contact and moving playback still require integration QA','knownIssues':['walk near/far continuity needs in-game motion review'],'contactHints':{'sit-idle':{'hip':[54,114],'feet':[78,168]},'look-idle':{'sillHand':[89,74],'facing':'right/back; horizontally flip whole sequence for a window to screen-left'}}}
(OUT.parent/'motions.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'production/room-v2/motion-registration.json').write_text(json.dumps({'sourceCanvas':[1536,1024],'sourceCell':[384,512],'sourceAnchor':[192,480],'records':records,'manifest':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(records),'manifest':str(OUT.parent/'motions.json')},ensure_ascii=False))

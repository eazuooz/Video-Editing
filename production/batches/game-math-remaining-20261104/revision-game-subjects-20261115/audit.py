"""Inventory every current scene; extracted pictures are evidence, not approval."""
import sys,json,subprocess,io,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OLD=HERE.parent/'revision-teaching-sync-20261115'
sys.path.insert(0,str(OLD));from render_revision import FF

def main():
    inv=json.loads((OLD/'inventory.json').read_text())['episodes'];rows=[]
    out=HERE/'local/audit';out.mkdir(exist_ok=True)
    for e in inv:
        epout=out/e['id'];epout.mkdir(exist_ok=True)
        master=ROOT/'output'/f"{e['slug']}-teaching-sync-v2"/f"{e['slug']}.captioned.mp4"
        ep=[]
        for s in e['scenes']:
            t=(s['start']+s['end'])/2;p=epout/f"{s['scene']}.jpg"
            if not p.exists():
                data=subprocess.check_output([str(FF),'-v','error','-threads','1','-ss',str(t),'-i',str(master),'-frames:v','1','-vf','scale=400:225','-threads','1','-f','image2pipe','-c:v','mjpeg','-'])
                p.write_bytes(data)
            teaching=s.get('currentTeaching') or {};m=teaching.get('motion',{});steps=teaching.get('steps',[])
            row=dict(episode=e['id'],scene=s['scene'],start=s['start'],end=s['end'],time=t,picture=str(p),speech=s['speech'],originalGame=s.get('originalGame'),diagramMode=teaching.get('diagramMode'),motionSubject=m.get('subjectKind','robot' if m else None),modelKinds=sorted(set(str(x.get('model',{}).get('picture',x.get('model',{}).get('mode'))) for x in steps)),status='pending-actual-picture-review')
            ep.append(row)
        for i in range(0,len(ep),24):
            board=Image.new('RGB',(1600,250*((len(ep[i:i+24])+3)//4)),(8,8,8));draw=ImageDraw.Draw(board)
            for j,r in enumerate(ep[i:i+24]):
                x=(j%4)*400;y=(j//4)*250;board.paste(Image.open(r['picture']),(x,y));draw.text((x+5,y+229),f"{e['id']}/{r['scene']} @ {r['time']:.2f}",fill='white')
            board.save(epout/f'board-{i//24+1:02}.jpg',quality=95)
        rows.extend(ep);print(e['id'],len(ep),'scenes extracted; semantic decisions pending',flush=True)
    (HERE/'scene-audit.json').write_text(json.dumps(dict(scope=[e['id'] for e in inv],rows=rows,actualVisualReview=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()

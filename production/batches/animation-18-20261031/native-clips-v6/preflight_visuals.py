"""Sample every revised comparison and its simultaneous stages before full rendering."""
import subprocess
from pathlib import Path

from PIL import Image,ImageDraw
from prepare import HERE,ROOT,WORK,read,save
from native_visuals import REPAIR,draw
from render_replacements import old


def main():
    plan={r['id']:r for r in read(HERE/'plan.json')['episodes']}
    folder=WORK/'configuration-preflight';folder.mkdir(parents=True,exist_ok=True)
    records=[];pending=[]
    for ep,keys in REPAIR.items():
        old.EPISODES={ep:keys}
        spans_all=old.classify(ep,read(HERE.parent/'contrast-v5/local/explanation-assembly'/ep/'edl.json'))
        prior=ROOT/next(f['path'] for f in plan[ep]['baseline']['files'] if f['kind']=='captioned.mp4')
        for key in sorted(keys):
            spans=[s for s in spans_all if s['reference']['key']==key]
            if not spans:continue
            span=max(spans,key=lambda s:s['end']-s['start'])
            at=(span['start']+span['end'])/120
            raw=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-threads','1','-ss',str(at),
                '-i',str(prior),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
            caption=Image.frombytes('RGB',(1920,1080),raw).crop((0,900,1920,1080))
            try:
                for mode,n in (('compare',85),('stages',179)):
                    image=draw(ep,key,n,mode)
                    image.paste(caption,(0,900))
                    path=folder/(ep+'-'+key+'-'+mode+'.png');image.save(path)
                    image.resize((375,211),Image.Resampling.LANCZOS).save(path.with_name(path.stem+'-375.png'))
                    records.append({'episode':ep,'key':key,'mode':mode,'frame':n,'file':str(path),
                                    'captionSourceAt':at,'captionScope':'Prior actual caption strip for clearance; changed speech captions are verified after encoding.'})
            except (FileNotFoundError,AssertionError) as error:
                pending.append({'episode':ep,'key':key,'reason':str(error)})
    for page in range((len(records)+11)//12):
        group=records[page*12:page*12+12]
        canvas=Image.new('RGB',(1500,720),'#080c0a');pen=ImageDraw.Draw(canvas)
        for j,row in enumerate(group):
            x,y=(j%4)*375,(j//4)*240
            with Image.open(row['file']) as image:canvas.paste(image.resize((375,211)),(x,y+25))
            pen.text((x+5,y+3),row['episode']+' / '+row['key']+' / '+row['mode'],fill='white')
        canvas.save(folder/f'contact-{page+1:02}.jpg')
    save(folder/'manifest.json',{'samples':records,'pending':pending,'configurationReviewed':False,
                               'finalEncodedInspectionRequired':True})
    print(len(records),'preflight samples;',len(pending),'native inputs pending.',flush=True)


if __name__=='__main__':main()

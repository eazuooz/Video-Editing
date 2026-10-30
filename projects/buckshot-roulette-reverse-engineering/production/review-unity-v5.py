"""Build indexed contact sheets of actual Unity or encoded capture frames."""
from pathlib import Path
import json,argparse,hashlib,math
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];OUT=P/'production/local/unity-v5'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fingerprint');args=ap.parse_args()
    fingerprint=args.fingerprint or read(OUT/'build.json')['fingerprint']
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',19)
    spec=read(P/'production/unity-workflow-v5-cues.json');index=[]
    dest=OUT/'review'/fingerprint[:8];dest.mkdir(parents=True,exist_ok=True)
    for entry in spec['entries']:
        folder=OUT/entry['id']/('preflight-'+fingerprint[:8]);images=sorted(folder.glob('frame-*.png'))
        for n in range(0,len(images),12):
            batch=images[n:n+12];sheet=Image.new('RGB',(1440,math.ceil(len(batch)/3)*300),'#141414');draw=ImageDraw.Draw(sheet)
            for i,path in enumerate(batch):
                thumb=Image.open(path).convert('RGB');thumb.thumbnail((480,270));x=(i%3)*480;y=(i//3)*300
                sheet.paste(thumb,(x,y));draw.text((x+8,y+273),entry['mode']+' / '+path.stem,font=font,fill='white')
            output=dest/(entry['id']+'-'+str(n//12+1)+'.jpg');sheet.save(output,quality=93)
            index.append({'id':entry['id'],'page':str(output),'frames':[int(x.stem.split('-')[-1]) for x in batch],'sourcePaths':[str(x) for x in batch]})
    (dest/'index.json').write_text(json.dumps({'fingerprint':fingerprint,'pages':index},indent=2)+'\n')
    print(json.dumps({'directory':str(dest),'pages':len(index),'frames':sum(len(x['frames']) for x in index)}))
if __name__=='__main__':main()

"""Sample each changed source range with the actual newly encoded caption strip."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw

from prepare import WORK,read,save
from sample_final_outputs import frame
from finish_episode import sha


def main(ep):
    review=read(WORK/ep/'native-picture-review.json')
    source=Path(review['pictures']['captioned.mp4']['path'])
    assert sha(source)==review['pictures']['captioned.mp4']['sha256']
    spans=read(WORK/ep/'new-pictures/manifest.json')['spans']
    folder=WORK/ep/'encoded-native-review';folder.mkdir(parents=True,exist_ok=True)
    samples=[]
    for key in dict.fromkeys(s['reference']['key'] for s in spans):
        group=[s for s in spans if s['reference']['key']==key]
        selected=max(group,key=lambda s:s['end']-s['start'])
        for j,u in enumerate((.15,.48,.85)):
            n=selected['start']+round((selected['end']-selected['start']-1)*u)
            picture=frame(source,n)
            path=folder/(key+'-'+str(j)+'.png');picture.save(path)
            picture.resize((375,211),Image.Resampling.LANCZOS).save(path.with_name(path.stem+'-375.png'))
            samples.append({'key':key,'frame':n,'file':str(path),'sha256':sha(path)})
    for page in range((len(samples)+11)//12):
        canvas=Image.new('RGB',(1500,720),'#080c0a');pen=ImageDraw.Draw(canvas)
        for j,row in enumerate(samples[page*12:page*12+12]):
            x,y=(j%4)*375,(j//4)*240
            with Image.open(row['file']) as image:canvas.paste(image.resize((375,211)),(x,y+25))
            pen.text((x+5,y+3),ep+' / '+row['key']+' / '+str(row['frame'])+'F',fill='white')
        canvas.save(folder/f'contact-{page+1:02}.jpg')
    save(folder/'samples.json',{'episode':ep,'captionedBodySha256':review['pictures']['captioned.mp4']['sha256'],
        'samples':samples,'visualReviewPending':True,'humanReviewed':False})
    print(ep,'encoded native-body samples ready for inspection.',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('episode');main(p.parse_args().episode)

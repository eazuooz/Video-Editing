"""Inspect final encoded scene changes and verify the reserved caption area."""
from pathlib import Path
import json, subprocess, hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1]; L=P/'production/local/v1'; OUT=L/'visuals'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    movie=L/'body.mp4';plan=load(L/'timeline.json');samples={}
    for scene in plan['scenes']:
        first=scene['startFrame'];length=scene['frames']
        for j,beat in enumerate(scene['sentences']):
            t=(beat['start']+beat['end'])/2
            samples[first+min(length-1,round(t*60))]=f"{scene['id']}.{j+1}"
        samples[first]=scene['id']+' first';samples[first+length-1]=scene['id']+' last'
    selected=sorted(samples)
    expr='select='+'+'.join('eq(n\\,'+str(f)+')' for f in selected)+',scale=375:211:flags=lanczos'
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(movie),'-vf',expr,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'])
    pixels=np.frombuffer(raw,dtype=np.uint8).reshape(-1,211,375,3)
    assert len(pixels)==len(selected),(len(pixels),len(selected))
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',14)
    clear=int(pixels[:,177:,:,:].max());assert clear<=9,clear
    coverage=[]
    for page_start in range(0,len(selected),12):
        sheet=Image.new('RGB',(375*3,238*4),'#192020');draw=ImageDraw.Draw(sheet)
        for j,frame in enumerate(selected[page_start:page_start+12]):
            im=Image.fromarray(pixels[page_start+j]);x=j%3*375;y=j//3*238
            sheet.paste(im,(x,y));draw.text((x+5,y+212),f'{samples[frame]}  |  frame {frame}',font=font,fill='white')
            lit=float((pixels[page_start+j,:170,:,:].max(axis=2)>40).mean())
            assert lit>.012,(samples[frame],lit)
            coverage.append({'id':samples[frame],'bodyFrame':frame,'litContentShare':round(lit,4)})
        sheet.save(OUT/f'body-review-{page_start//12+1:02}.jpg',quality=92)
    result={'dimensions':[1920,1080],'mobileWidth':375,'samples':coverage,
       'coverage':'first, last and each spoken sentence midpoint',
       'decodedStream':'single sequential ffmpeg decode through EOF',
       'captionAreaCheck':'below 900px, every sampled frame','maxDecodedRgbInCaptionArea':clear,
       'humanRealtimeReview':'pending'}
    (OUT/'encoded-body-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{len(selected)} encoded samples; caption area maximum {clear}.')
if __name__=='__main__':main()

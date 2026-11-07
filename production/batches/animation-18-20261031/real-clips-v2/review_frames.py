"""Extract small decoded captioned frames at all changed/retained study cues."""
from pathlib import Path
import json,subprocess,sys,io
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
plan=read(H/'revision-plan.json')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
for ep in sys.argv[1:]:
    row=next(r for r in plan['episodes'] if r['id']==ep);p=R/'projects'/row['slug'];old=p/'production'/row['baselineRevision']
    new=p/'production/local/real-clips-v2';receipt=new/'verification.json'
    if receipt.is_file():
        data=read(receipt);cuts=data['changedCuts'];master=new/'captioned.mp4';dest=new/'qa'
    else:
        timeline=read(old/'edit-plan-final.json');visual=read(old/'visual-plan.json');seen=set();cuts=[]
        for c in timeline['cuts']:
            if c['key'] in visual['rigs'] and c['key'] not in seen:cuts.append(c);seen.add(c['key'])
        master=p/'production/local'/row['baselineRevision']/'delivery/output'/row['slug']/(row['slug']+'.captioned.mp4');dest=B/'local/real-clips-v2'/'retained-qa'/ep
    dest.mkdir(parents=True,exist_ok=True);samples=[]
    for c in cuts:
        start=c.get('start',c.get('startFrame',0));offset=min(c['frames']-1,max(45,int(c['frames']*.4)))
        time=(start+offset)/60
        blob=subprocess.check_output(['ffmpeg','-v','error','-threads','2','-ss',str(time),'-i',str(master),'-frames:v','1','-vf','scale=375:-2','-f','image2pipe','-c:v','png','-'])
        samples.append((c,time,Image.open(io.BytesIO(blob)).convert('RGB')))
    for page in range((len(samples)+17)//18):
        selected=samples[page*18:(page+1)*18];canvas=Image.new('RGB',(1125,250*((len(selected)+2)//3)),'#18211d');d=ImageDraw.Draw(canvas)
        for i,(c,t,im) in enumerate(selected):
            x=i%3*375;y=i//3*250;d.text((x+5,y+4),ep+' '+str(c.get('key',c.get('id',c.get('paragraph'))))+' '+f'{t:.2f}s',font=font,fill='white');canvas.paste(im,(x,y+32))
        canvas.save(dest/f'mobile-review-{page+1:02}.jpg',quality=92)
    (dest/'samples.json').write_text(json.dumps([dict(cut=c,time=t) for c,t,_ in samples],ensure_ascii=False,indent=2),'utf-8')
    print(ep,len(samples),'decoded review samples',flush=True)

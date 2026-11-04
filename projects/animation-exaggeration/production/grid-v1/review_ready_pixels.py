"""Extract current completed-cut pixels with real captions at their global times."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
import audio_pipeline as ap
import video_pipeline as vp
H=Path(__file__).resolve().parent
L=H.parent/'local/grid-v1'
O=L/'qa/ready-cuts-v1'

def main():
    plan=ap.read(H/'edit-plan.json');ass=L/'edit/captions.ko.ass'
    cuts=[c for c in plan['cuts'] if c['kind']=='independent-gameplay' or c.get('explanationMode')=='source-frame-analysis']
    O.mkdir(parents=True,exist_ok=True)
    rows=[]
    for c in cuts:
        src=L/'edit'/f'{c["id"]}.mp4'
        assert src.is_file(),src
        for label,n in [('first',0),('middle',(c['frames']-1)//2),('last',c['frames']-1)]:
            t=(c['startFrame']+n)/60;dst=O/f'{c["id"]}-{label}.png'
            vf=f'select=eq(n\\,{n}),setpts={t:.9f}/TB,ass='+vp.filter_path(ass)
            subprocess.run([vp.binary('ffmpeg'),'-hide_banner','-v','error','-nostdin','-y',
                '-threads','2','-filter_threads','1','-i',str(src),'-vf',vf,'-frames:v','1',
                '-fps_mode','passthrough','-threads','1',str(dst)],check=True)
            rows.append({'cut':c['id'],'sample':label,'globalTime':t,'image':ap.artifact(dst),'source':ap.artifact(src)})
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
    sheets=[]
    for start in range(0,len(rows),12):
        subset=rows[start:start+12];sheet=Image.new('RGB',(1125,259*4),'#151515');d=ImageDraw.Draw(sheet)
        for i,row in enumerate(subset):
            x=i%3*375;y=i//3*259
            im=Image.open(ap.repo_path(row['image']['path'])).convert('RGB').resize((375,211),Image.Resampling.LANCZOS)
            sheet.paste(im,(x,y));d.text((x+4,y+215),f"{row['cut']} {row['sample']} {row['globalTime']:.3f}s",font=font,fill='white')
        target=O/f'contact-{start//12+1:02}.jpg';sheet.save(target,quality=94);sheets.append(ap.artifact(target))
    ap.save(O/'manifest.json',{'episode':'A02','status':'extracted-pixels-not-yet-reviewed',
        'captionAss':ap.artifact(ass),'rows':rows,'contactSheets':sheets,
        'scope':'Eight encoded cuts first/middle/last with current exact global-time ASS. Not final master, no audio/motion claim.'})
    print('24 ready-cut captioned frames extracted; inspect two375px contact sheets.')
if __name__=='__main__':main()

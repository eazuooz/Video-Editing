"""Reproducible FHD explanation plate from a verified actual video frame.

The unchanged source frame and its exact crop/fit are retained as provenance.
This clip is an explanation still, never native gameplay or an isolated model.
Timed editorial arrows/labels are applied later by video_pipeline.
"""
import argparse, hashlib, json, math, subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import audio_pipeline as ap

H=Path(__file__).resolve().parent
R=H.parents[3]
LOCAL=H.parent/'local/grid-v1'
FONT=Path('C:/Windows/Fonts/malgun.ttf')

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--spec',required=True,type=Path)
 a=parser.parse_args();s=ap.read(a.spec)
 ap.require_authorized('video-cuts')
 source=ap.repo_path(s['sourceFile'])
 assert ap.sha(source)==s['sourceSha256'],'Source bytes changed'
 out=ap.current_local_output(s['outputDir'])
 out.relative_to(LOCAL.resolve())
 frames=int(s['frames']);assert frames>0
 input_id=ap.canonical_signature({'spec':s,'scriptSha256':ap.sha(Path(__file__)),'fontSha256':ap.sha(FONT)})
 receipt=out/'explanation-render.json'
 if receipt.exists():
  old=ap.read(receipt);assert old['inputSignature']==input_id,'Preserve previous render'
  assert ap.sha(ap.repo_path(old['movie']['path']))==old['movie']['sha256']
  print('Reusing identical still '+str(out));return
 assert not out.exists(),'Preserve unregistered/partial output; use a new directory'
 out.mkdir(parents=True)
 frame=out/'source-frame.png';plate=out/'explanation-plate.png';movie=out/'explanation.mp4'
 t=float(s['frameTimeSeconds']);assert t>=0
 ap.run_ff(['-ss',f'{t:.9f}','-i',source,'-frames:v',1,frame],out/'source-frame.log')
 original=Image.open(frame).convert('RGB');w,h=original.size
 assert min(w,h)>=1080 and max(w,h)>=1920,'Actual source must be FHD'
 picture=original
 crop=s.get('crop')
 if crop is not None:
  x,y,cw,ch=map(int,crop);assert x>=0 and y>=0 and cw>0 and ch>0 and x+cw<=w and y+ch<=h
  picture=picture.crop((x,y,x+cw,y+ch))
 canvas=Image.new('RGB',(1920,1080),'#ECEEED');draw=ImageDraw.Draw(canvas)
 for x in range(0,1920,42):draw.line((x,160,x,900),fill='#D0D5D5',width=2)
 for y in range(170,901,42):draw.line((0,y,1920,y),fill='#D0D5D5',width=2)
 for x in range(0,1920,168):draw.line((x,160,x,900),fill='#ADB7BA',width=3)
 draw.rectangle((0,0,1920,159),fill='#0B1515')
 draw.rectangle((0,900,1920,1080),fill='#0B1515')
 title=s.get('title','동작을 자세히 보기')
 font=ImageFont.truetype(str(FONT),54)
 assert draw.textlength(title,font=font)<1420,'Title too long at actual size'
 draw.text((70,65),title,font=font,fill='#E9CD79',anchor='lm')
 if s.get('contextLabel'):
  small=ImageFont.truetype(str(FONT),34)
  assert draw.textlength(s['contextLabel'],font=small)<1750
  draw.text((70,125),s['contextLabel'],font=small,fill='#F0F2F0',anchor='lm')
 viewport=s.get('viewport',[320,180,1280,720]);x,y,vw,vh=map(int,viewport)
 assert x>=0 and y>=160 and x+vw<=1920 and y+vh<=900
 scale=min(vw/picture.width,vh/picture.height)
 size=(round(picture.width*scale),round(picture.height*scale))
 fit=[x+(vw-size[0])//2,y+(vh-size[1])//2,*size]
 canvas.paste(picture.resize(size,Image.Resampling.LANCZOS),fit[:2])
 draw.rectangle((fit[0]-2,fit[1]-2,fit[0]+fit[2]+1,fit[1]+fit[3]+1),outline='#708486',width=2)
 canvas.save(plate)
 ap.run_ff(['-loop','1','-framerate',60,'-i',plate,'-frames:v',frames,
            '-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p',
            '-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','17',
            '-g','60','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',
            '-movflags','+faststart',movie],out/'encode.log')
 probe=json.loads(subprocess.check_output([ap.tool('ffprobe'),'-v','error','-count_frames','-show_streams','-of','json',str(movie)]))['streams'][0]
 assert int(probe['nb_read_frames'])==frames and probe['width']==1920 and probe['height']==1080 and probe['r_frame_rate']=='60/1'
 data={'status':'complete','kind':'annotated-still','inputSignature':input_id,
       'episode':'A01','slug':'animation-assigning','revision':'grid-v1',
       'completed':frames,'frames':frames,'fps':60,'width':1920,'height':1080,'movie':ap.artifact(movie),
       'sourceImage':ap.artifact(frame),'imageOutput':ap.artifact(plate),
       'sourceVideo':{'path':ap.relative(source),'sha256':ap.sha(source),'frameTimeSeconds':t,'decodedWidth':w,'decodedHeight':h},
       'layout':{'crop':crop,'viewport':viewport,'actualFit':fit,'background':'animation-grid','preserveAspectRatio':True,'captionProtectedRect':[150,892,1784,1060]},
       'classification':'explanation','sourcePixelsModifiedBeyondCropFit':False,
       'nativeGameplay':False,'foregroundExtraction':False,'timedAnnotations':'applied by final cut compositor',
       'createdAt':ap.now()}
 ap.save(receipt,data);print('COMPLETE '+str(receipt),flush=True)

if __name__=='__main__':main()

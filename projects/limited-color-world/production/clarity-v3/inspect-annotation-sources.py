"""Bounded, exact-frame source inspection for new editorial marks; no edits to video."""
from pathlib import Path
import json,subprocess,math
from PIL import Image,ImageDraw,ImageFont
import audio_pipeline as a
import video_pipeline as v
H=Path(__file__).resolve().parent

def main():
 a.require_authorized('bounded-source-annotation-inspection')
 plan=a.read(H/'edit-plan.draft.json');sources={c['source']:c for c in plan['cuts'] if c['kind']=='independent-gameplay'}
 root=H/'evidence/annotation-sources-v1'
 if root.exists():raise FileExistsError('Preserve existing source inspection')
 root.mkdir(parents=True)
 specs=[('wonder-before',[8+i*.5 for i in range(17)]+[22+i*.5 for i in range(17)]),('wonder-block-cc',[15+i*.5 for i in range(9)]),('wonder-after',[3+i*.5 for i in range(15)])]
 records=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17)
 for key,times in specs:
  c=sources[key];source=a.repo_path(c['sourceFile']);assert a.sha(source)==c['sourceSha256']
  info=v.video_stream(source);fps=float(v.Fraction(info['avg_frame_rate']));indices=sorted({round(t*fps) for t in times})
  dest=root/key;dest.mkdir()
  expr='+'.join(f'eq(n\\,{n})' for n in indices)
  cmd=[a.tool('ffmpeg'),'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(source),'-vf','select='+expr,'-fps_mode','vfr','-q:v','2','-n',str(dest/'%04d.jpg')]
  done=subprocess.run(cmd,capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));(dest/'decode.log').write_bytes(done.stderr)
  if done.returncode:raise RuntimeError(done.stderr.decode('utf8','replace'))
  files=sorted(dest.glob('*.jpg'));assert len(files)==len(indices)
  rows=[{'frame':n,'seconds':n/fps,'path':a.relative(p)} for n,p in zip(indices,files)]
  sheets=[]
  for start in range(0,len(rows),12):
   subset=rows[start:start+12];im=Image.new('RGB',(1200,math.ceil(len(subset)/3)*251),'#171717');draw=ImageDraw.Draw(im)
   for i,row in enumerate(subset):
    x,y=i%3*400,i//3*251;pic=Image.open(a.repo_path(row['path']));assert pic.size==(1920,1080)
    im.paste(pic.resize((400,225),Image.Resampling.LANCZOS),(x,y+26));draw.text((x+4,y+3),f"{key} {row['seconds']:.3f}s f{row['frame']}",font=font,fill='white')
   sheet=dest/f'sheet-{start//12+1:02d}.jpg';im.save(sheet,quality=94);sheets.append(a.relative(sheet))
  records.append({'source':key,'sourceFile':c['sourceFile'],'sourceSha256':c['sourceSha256'],'fps':info['avg_frame_rate'],'frames':rows,'sheets':sheets})
 a.save(root/'evidence.json',{'status':'extracted-not-viewed','method':'exact decoded source frame index; source bytes unchanged','records':records})
 print('Bounded annotation frames extracted; direct review pending')
if __name__=='__main__':main()

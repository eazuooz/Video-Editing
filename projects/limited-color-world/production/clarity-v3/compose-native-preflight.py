"""Compose actual measured native preflight states, brand UI and final timed captions."""
from pathlib import Path
import argparse,json,subprocess,math
from PIL import Image,ImageDraw,ImageFont
import audio_pipeline as a
import ui_compositor as ui
import video_pipeline as v
H=Path(__file__).resolve().parent
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cut',required=True);ap.add_argument('--native-revision',default='measured-v1');ap.add_argument('--output-revision',default='v1');args=ap.parse_args()
 a.require_authorized('measured-native-ui-caption-preflight')
 plan=a.read(H/'edit-plan.draft.json');cut=next(c for c in plan['cuts'] if c['id']==args.cut);cue=next(x for x in a.read(H/'unity-cues.json')['cuts'] if x['cutId']==args.cut)
 photos=cut['variant'] in ui.PHOTO_VARIANTS;native=a.LOCAL/'preflight'/args.native_revision/args.cut
 if photos:
  n=cut['frames'];sample={0,n//4,n//2,3*n//4,n-1}
  for row in cue.get('cues',[]):sample.update(round(t*60) for t in [row['start'],(row['start']+row['end'])/2,row['end']] if 0<=round(t*60)<n)
  samples=[(f,None) for f in sorted(sample)];nativeProof=None
 else:
  done=a.read(native/'preflight-success.json');assert done['status']=='complete' and done['cutId']==args.cut and done['frames']==cut['frames']
  samples=[(int(p.stem.split('-')[-1]),p) for p in sorted(native.glob('frame-*.png'))];nativeProof=a.artifact(native/'preflight-success.json')
 root=a.LOCAL/'preflight-composited'/args.output_revision/args.cut;root.mkdir(parents=True,exist_ok=False);rows=[];ass=a.LOCAL/'edit/captions.ko.ass'
 for frame,source in samples:
  state=ui.picture_state(cue,frame/60,cut['frames']);overlay,bounds=ui.render_ui(state)
  if source:
   image=Image.open(source).convert('RGBA');assert image.size==(1920,1080);image.alpha_composite(overlay)
  else:image=overlay
  raw=root/f'ui-{frame:05d}.png';image.convert('RGB').save(raw);target=root/f'captioned-{frame:05d}.png';globalFrame=cut['startFrame']+frame
  graph=f'setpts=PTS+{globalFrame}/60/TB,ass='+v.filter_path(ass)
  process=subprocess.run([a.tool('ffmpeg'),'-hide_banner','-nostdin','-v','error','-threads','1','-i',str(raw),'-vf',graph,'-frames:v','1','-n',str(target)],capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  if process.returncode:raise RuntimeError(process.stderr.decode('utf8','replace'))
  rows.append({'localFrame':frame,'globalFrame':globalFrame,'sourceNative':a.artifact(source) if source else None,'output':a.artifact(target),'state':state,'bounds':bounds})
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14);sheets=[]
 for start in range(0,len(rows),12):
  part=rows[start:start+12];sheet=Image.new('RGB',(1125,math.ceil(len(part)/3)*235),'#171717');draw=ImageDraw.Draw(sheet)
  for i,row in enumerate(part):
   x,y=i%3*375,i//3*235;pic=Image.open(a.repo_path(row['output']['path']));sheet.paste(pic.resize((375,211),Image.Resampling.LANCZOS),(x,y+23));draw.text((x+4,y+2),f"{args.cut} f{row['localFrame']} / {row['globalFrame']/60:.3f}s",font=font,fill='white')
  dest=root/f'mobile-{start//12+1:02d}.jpg';sheet.save(dest,quality=95);sheets.append(a.artifact(dest))
 a.save(root/'proof.json',{'status':'generated-not-viewed','cut':cut,'cueFile':a.artifact(H/'unity-cues.json'),'uiSource':a.artifact(Path(ui.__file__)),'actualCaptionAss':a.artifact(ass),'nativeProof':nativeProof,'frames':rows,'mobileSheets':sheets,'wholeHumanReview':'pending','fullEncodedMaster':'not yet produced'})
 print(f'{args.cut}: {len(rows)} actual native/UI/caption states +375px sheets; direct viewing pending')
if __name__=='__main__':main()

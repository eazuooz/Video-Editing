"""Two bounded still proofs: inspected native grayscale world plus measured UI/captions."""
from pathlib import Path
import subprocess,json
from PIL import Image
import audio_pipeline as a
import ui_compositor as ui
import video_pipeline as v
H=Path(__file__).resolve().parent
def main():
 a.require_authorized('bounded-ui-caption-proof')
 plan=a.read(H/'edit-plan.draft.json');cue={x['cutId']:x for x in a.read(H/'unity-cues.draft.json')['cuts']};root=H/'evidence/ui-proof-v1';root.mkdir(exist_ok=False)
 native=a.LOCAL/'preflight/native-v2/forest-gray/frame-00719.png';assert native.is_file()
 records=[]
 for cid,name in [('c024','forest-gray'),('c012','official-filter-on')]:
  cut=next(x for x in plan['cuts'] if x['id']==cid);frame=cut['frames']-60;globalFrame=cut['startFrame']+frame
  state=ui.picture_state(cue[cid],frame/60,cut['frames']);overlay,bounds=ui.render_ui(state)
  if cid=='c024':
   background=Image.open(native).convert('RGBA');assert background.size==(1920,1080);background.alpha_composite(overlay)
  else:background=overlay
  raw=root/(name+'-ui.png');background.convert('RGB').save(raw)
  target=root/(name+'-captioned.png');ass=a.LOCAL/'edit/captions.ko.ass'
  graph=f'setpts=PTS+{globalFrame}/60/TB,ass='+v.filter_path(ass)
  result=subprocess.run([a.tool('ffmpeg'),'-hide_banner','-nostdin','-v','error','-threads','1','-i',str(raw),'-vf',graph,'-frames:v','1','-n',str(target)],capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  (root/(name+'.log')).write_bytes(result.stderr)
  if result.returncode:raise RuntimeError(result.stderr.decode('utf8','replace'))
  image=Image.open(target);image.resize((375,211),Image.Resampling.LANCZOS).save(root/(name+'-375.png'))
  records.append({'cutId':cid,'globalFrame':globalFrame,'state':state,'bounds':bounds,'nativeWorld':a.artifact(native) if cid=='c024' else None,'actualCaptionAss':a.artifact(ass),'proof':a.artifact(target),'sameWorldState':'fully grayscale representative; measured final cut capture still pending' if cid=='c024' else 'official screenshot; no native world required'})
 a.save(root/'proof.json',{'status':'created-not-viewed','scope':'bounded still feasibility, not final moving master approval','records':records})
 print('Two native/UI/actual-caption still proofs generated')
if __name__=='__main__':main()

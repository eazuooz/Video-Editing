"""One-frame previews of actual source, editorial marks and current fixed captions."""
from pathlib import Path
import json,subprocess,hashlib
from PIL import Image
import video_pipeline as v
ROOT=Path(__file__).resolve().parents[4];PROJECT=Path(__file__).resolve().parents[2];SLUG=PROJECT.name;LOCAL=PROJECT/'production/local/batch-v1'
plan=json.loads((Path(__file__).parent/'edit-plan.json').read_text('utf-8'))
ids=['01-01-1','02-04-1','03-05-1','07-01-1'] if SLUG=='kind-to-beginners' else ['01-01-1','03-03-1','05-03-1']
output=LOCAL/'inspection/gameplay-preview';output.mkdir(parents=True,exist_ok=True)
for cid in ids:
 c=next(x for x in plan['cuts'] if x['id']==cid);focus=next((x for x in c.get('marks',[]) if x['id']!='game-name'),None)
 t=(focus['t0']+focus['t1'])/2 if focus else c['frames']/120;t=min(t,c['frames']/60-.05)
 ass,_=v.annotations(c,plan);mark=output/(cid+'.ass');mark.write_text(ass,'utf-8')
 global_t=c['startFrame']/60+t;vf=f"scale=1564:880:flags=lanczos,setsar=1,pad=1920:1080:178:0:black,setpts=PTS-STARTPTS+{t}/TB,ass="+v.filter_path(mark)+f",setpts=PTS-STARTPTS+{global_t}/TB,ass="+v.filter_path(LOCAL/'edit/captions.ko.ass')
 target=output/(cid+'.jpg')
 subprocess.run(['ffmpeg','-y','-v','error','-threads','1','-ss',str(c['sourceStart']+t),'-i',str(ROOT/c['sourceFile']),'-filter_threads','1','-vf',vf,'-frames:v','1',str(target)],check=True)
 im=Image.open(target);im.resize((375,211),Image.Resampling.LANCZOS).save(output/(cid+'-375.jpg'))
 (output/(cid+'.json')).write_text(json.dumps({'cut':cid,'globalTime':global_t,'editPlanSha256':hashlib.sha256((Path(__file__).parent/'edit-plan.json').read_bytes()).hexdigest(),'captionsSha256':hashlib.sha256((LOCAL/'edit/captions.ko.ass').read_bytes()).hexdigest(),'imageSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'scope':'single current native source frame with actual current marks/captions; not whole moving-video review'},ensure_ascii=False,indent=2),'utf-8')
 print(cid,round(global_t,3),flush=True)

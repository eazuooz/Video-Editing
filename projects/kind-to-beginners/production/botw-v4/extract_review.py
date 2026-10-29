"""Bounded CPU final pixels, preserving every generated version."""
from pathlib import Path
import hashlib,json,subprocess
from PIL import Image,ImageDraw
from audio_pipeline import tool
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;P=HERE.parents[1];LOCAL=P/'production/local/botw-v4'
def main():
 plan=json.loads((HERE/'edit-plan.json').read_text('utf-8'));movie=LOCAL/'edit/kind-to-beginners-captioned.mp4';out=LOCAL/'qa/final-v1'
 cue={c['id']:c for c in json.loads((HERE/'unity-cues.json').read_text('utf-8'))['cuts']}
 captions=json.loads((LOCAL/'edit/captions.json').read_text('utf-8'))['cues']
 out.mkdir(parents=True,exist_ok=True);rows=[];sheet=[]
 for cut in plan['cuts']:
  states=[.08,.35,.68,.94]if cut['kind']=='explanation'else[.2,.7]
  frames={min(cut['endFrame']-1,cut['startFrame']+round(cut['frames']*q)) for q in states}
  # Every final clause is represented in an actual encoded frame, in addition
  # to the mechanism/action states below. No extra video or audio generation.
  for caption in captions:
   center=round((caption['start']+caption['end'])*30)
   if cut['startFrame']<=center<cut['endFrame']:frames.add(center)
  if cut['kind']=='independent-gameplay':
   frames.add(min(cut['endFrame']-1,cut['startFrame']+45)) # visible speech-led annotation interval
   for mark in cut.get('marks',[]):
    middle=(mark['t0']+mark['t1'])/2
    frames.add(min(cut['endFrame']-1,cut['startFrame']+round(middle*60)))
  if cut['id'] in ['04-06','05-01','05-02','06-02','06-06','07-02','07-04','07-06']:
   for t in cue[cut['id']]['phaseSeconds']:
    for delta in [-3,9]:
     frames.add(max(cut['startFrame'],min(cut['endFrame']-1,cut['startFrame']+round(t*60)+delta)))
  for idx,frame in enumerate(sorted(frames)):
   f=out/f"{cut['id']}-{idx}.jpg"
   if not f.exists():subprocess.run([tool('ffmpeg'),'-v','error','-threads','2','-ss',str(frame/60),'-i',str(movie),'-frames:v','1','-q:v','2','-threads','2',str(f)],check=True)
   im=Image.open(f).convert('RGB');im.thumbnail((375,211));tile=Image.new('RGB',(395,250),'#131313');tile.paste(im,(10,28));ImageDraw.Draw(tile).text((10,8),f"{cut['id']} | frame {frame}",fill='white');sheet.append(tile)
   rows.append({'cut':cut['id'],'frame':frame,'ptsSeconds':frame/60,'kind':cut['kind'],'captionCues':[c['cue'] for c in captions if c['start']<=frame/60<c['end']], 'image':str(f.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'viewed':False})
 for n in range(0,len(sheet),12):
  board=Image.new('RGB',(395*3,250*4),'black')
  for i,tile in enumerate(sheet[n:n+12]):board.paste(tile,((i%3)*395,(i//3)*250))
  board.save(out/f'board-{n//12+1:02d}.jpg',quality=94)
 (out/'index.json').write_text(json.dumps({'status':'extracted-not-yet-viewed','movie':str(movie.relative_to(ROOT)).replace('\\','/'),'frames':rows},ensure_ascii=False,indent=2)+'\n','utf-8')
 print('Extracted',len(rows),'bounded final states; actual viewing remains separate.')
if __name__=='__main__':main()

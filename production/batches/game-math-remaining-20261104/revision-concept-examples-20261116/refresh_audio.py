"""New-excerpt-only audio correction; copy every picture and retain first-pass files."""
import shutil,subprocess
from pathlib import Path
from render import *
def vcl(p):return ff(['-i',p,'-map','0:v:0','-an','-c','copy','-bsf:v','filter_units=remove_types=6|7|8|9','-f','hash','-hash','sha256','-'],capture=True).decode().strip()
def main():
 rp=HERE/'deliveries/M31.json';d=read(rp)
 if d.get('recorderCommentarySeparated'):return
 save(HERE/'local/M31-before-source-commentary-removal.json',d)
 p=WORK/'audio-refresh/M31';p.mkdir(parents=True,exist_ok=True);audio=combined_audio(d,p,read(HERE/'sources.json'))
 backing=Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingOutputs/game-math-concept-examples-20261116/M31/audio-cleaned';backing.mkdir(parents=True,exist_ok=True)
 link=OUT/'M31/media';assert link.resolve().is_relative_to((OUT/'M31').resolve()) if not link.exists() else link.resolve()==backing.resolve()
 if not link.exists():
  quote=lambda x:"'"+str(x).replace("'","''")+"'"
  subprocess.run(['powershell','-NoProfile','-NonInteractive','-Command',f'New-Item -ItemType Junction -Path {quote(link)} -Target {quote(backing)} | Out-Null'],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 files={};qa=[]
 for kind in ('clean','captioned'):
  previous=d['files'][kind]['path'];target=link/(d['slug']+'.'+kind+'.mp4')
  ff(['-i',previous,'-i',audio,'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',target],p,'remux-'+kind)
  expected=vcl(previous);assert vcl(target)==expected;assert int(video(target)['nb_frames'])==d['frames'];grid=packet_grid(target,d['frames'])
  ff(['-threads','2','-v','error','-xerror','-i',target,'-map','0:v','-map','0:a','-f','null','-'],p,'decode-'+kind)
  files[kind]=dict(path=str(target),sha256=sha(target));qa.append(dict(kind=kind,fullDecode=True,clock=grid,videoPicturesByteIdenticalToFirstPass=True,videoVclHash=expected))
 for lang in ('ko','en'):
  target=link/(d['slug']+'.'+lang+'.srt');shutil.copy2(d['files'][lang]['path'],target);files[lang]=dict(path=str(target),sha256=sha(target))
 d.update(files=files,qa=qa,workDir=str(p),recorderCommentarySeparated=True,audioCorrectionScope='Only the three newly inserted real-game excerpts. All accepted main-lesson audio remains unchanged.',status='encoded-final-visual-and-audio-boundary-review-pending');save(rp,d)
 print('M31 new game-excerpt commentary removed; all video pictures preserved',flush=True)
if __name__=='__main__':main()

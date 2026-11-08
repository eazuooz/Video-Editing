"""Assemble a separate review version on C; never replace the previous master."""
from pathlib import Path
import json,subprocess,hashlib
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/room-v3';OLD=P/'production/local';OUT=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v3/video');F=OUT/'final';F.mkdir(exist_ok=True)
control=json.loads((R/'shared/publishing/video-production-control.json').read_text('utf-8-sig'));assert control['ai2dRoomRevision20261108']['fullLocalVideoRevisionAuthorized']
tm=json.loads((L/'timeline.json').read_text('utf8'));replaced=['17','18','19','22','26','28'];files=[P/'assets/local/intro.mp4'];entries=[]
for row in tm['scenes']:
 changed=not row['id'].isdigit() or row['id'] in replaced;f=(OUT if changed else OLD)/'visual'/f"scene-{row['id']}.mp4";assert f.exists(),f
 rec=json.loads(f.with_suffix('.mp4.json').read_text('utf8'));assert rec['frames']==row['frames'],row['id']
 files.append(f);entries.append({'id':row['id'],'path':str(f),'newVisual':changed,'frames':row['frames']})
files.append(P/'assets/local/outro.mp4');concat=OUT/'concat.txt';concat.write_text('\n'.join("file '"+f.as_posix().replace("'","'\\''")+"'" for f in files),'utf8')
def run(cmd):subprocess.run(list(map(str,cmd)),cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
clean=F/'ai-2d-game-assets.room-v3.clean.mp4';cap=F/'ai-2d-game-assets.room-v3.captioned.mp4'
if not clean.exists():run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',concat,'-i',OUT/'final-mix.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',clean])
# Copy-mux -shortest can discard the final reordered B frames despite equal
# planned stream durations. Preserve every input frame and verify before ASS.
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(clean)],text=True))
assert int(probe['streams'][0]['nb_frames'])==tm['frames'],probe
if not cap.exists():
 ass=(L/'captions.ko.ass').relative_to(R).as_posix();run(['ffmpeg','-hide_banner','-loglevel','error','-i',clean,'-vf',f"ass='{ass}'",'-c:v','libx264','-preset','veryfast','-crf','18','-threads','3','-c:a','copy','-movflags','+faststart',cap])
record={'duration':tm['duration'],'frames':tm['frames'],'sources':entries,'previousMasterPreserved':True,'files':[{'file':str(f),'bytes':f.stat().st_size,'sha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest()} for f in [clean,cap]],'humanReview':False,'uploaded':False}
(H/'assembly.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');print('Assembled',tm['duration'])

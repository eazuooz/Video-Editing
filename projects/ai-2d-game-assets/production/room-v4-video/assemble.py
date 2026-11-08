"""Mux the changed visuals and one additive passage into separate v4 files."""
from pathlib import Path
import json,subprocess,hashlib
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/room-v4-video';O=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v4-video/video');F=O/'final'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert read(H/'authorization.json')['renderAuthorized']
tm=read(L/'timeline.json');plan=read(H/'revision-plan.json');changed=set(plan['replaceVisualIds'])|{'W36'};before={s['id']:s for s in read(H.parent/'room-v3/assembly.json')['sources']};sources=[];files=[P/'assets/local/intro.mp4']
gameSha=sha(O.parent/'site-snapshot/game.js')
for row in tm['scenes']:
 f=O/'visual'/f"scene-{row['id']}.mp4" if row['id'] in changed else Path(before[row['id']]['path'])
 meta=read(f.with_suffix('.mp4.json'));assert meta['frames']==row['frames'],row['id']
 if row['id'] in changed:assert meta['gameSourceSha256']==gameSha,row['id']
 files.append(f);sources.append({'id':row['id'],'path':str(f),'sha256':sha(f),'frames':row['frames'],'changed':row['id'] in changed,'gameSourceSha256':meta.get('gameSourceSha256')})
files.append(P/'assets/local/outro.mp4');concat=O/'concat.txt';concat.write_text('\n'.join("file '"+f.as_posix().replace("'","'\\''")+"'" for f in files),'utf8')
def run(args):subprocess.run(list(map(str,args)),cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
clean=F/'ai-2d-game-assets.room-v4-video.clean.mp4';captioned=F/'ai-2d-game-assets.room-v4-video.captioned.mp4'
if not clean.exists():run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',concat,'-i',O/'final-mix.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',clean])
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(clean)],text=True));assert int(probe['streams'][0]['nb_frames'])==tm['frames'],probe
if not captioned.exists():
 ass=(L/'captions.ko.ass').relative_to(R).as_posix();run(['ffmpeg','-hide_banner','-loglevel','error','-i',clean,'-vf',f"ass='{ass}'",'-c:v','libx264','-preset','veryfast','-crf','18','-threads','3','-c:a','copy','-movflags','+faststart','-progress',O/'encode-progress.txt',captioned])
(H/'assembly.json').write_text(json.dumps({'revision':'room-v4-video','duration':tm['duration'],'frames':tm['frames'],'sources':sources,'sameSiteSourceSha256':gameSha,'oldMastersPreserved':True,'old51PcmSamplesPreserved':True,'newPassages':1,'newVisualScenes':len(changed),'files':[{'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size} for f in [clean,captioned]],'uploaded':False,'userReview':False},ensure_ascii=False,indent=2),'utf8')
print('Assembled',tm['duration'],tm['frames'],flush=True)

"""Compose narration-paced real captures with film graphics; resumes by input hashes."""
from pathlib import Path
import json,hashlib,math,subprocess,time,argparse
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local/full-video-v3';V=L/'visual';V.mkdir(parents=True,exist_ok=True)
rows=json.loads((P/'script/narration.ko.json').read_text('utf-8'))['scenes']
MOTION={1: ('living-room-v9', 0, 20), 6: ('living-room-v9', 37, 8), 11: ('living-room-v9', 20, 11), 12: ('living-room-v9', 37, 8), 13: ('living-room-v9/walk-source', 0, 12), 16: ('living-room-v9/walk-source', 0, 12), 17: ('living-room-v9', 33, 12), 18: ('living-room-v9', 12, 8), 19: ('web-final-v6', 32, 7), 20: ('living-room-v9', 68, 6), 21: ('final-activities-v7', 26, 7), 22: ('living-room-v9', 61, 7), 28: ('living-room-v9', 68, 6), 29: ('living-room-v9', 53, 8), 30: ('living-room-v9', 45, 8)}
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
def render(row):
 import soundfile as sf
 f=L/'narration/chunks'/(row['id']+'-scene.wav')
 if not f.exists():return False
 duration=sf.info(f).duration;frames=math.ceil((duration+(.28 if row['id']!='28' else 0))*60)
 if row['id']=='28':frames=max(frames,600)
 seconds=frames/60
 n=int(row['id']);board=L/'boards'/(row['id']+'.png');out=V/('scene-'+row['id']+'.mp4');receipt=out.with_suffix('.json');sig={'narration':sha(f),'board':sha(board),'frames':frames,'renderer':'ai-tool-tutorial-compositor-v3'}
 if out.exists() and receipt.exists() and json.loads(receipt.read_text())['inputs']==sig:return True
 base=['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-framerate','60','-i',board]
 n=int(row['id']);fil='';source=None
 if n in MOTION and n not in (23,24,26):
  folder,start,length=MOTION[n];source=P/'production/local'/folder/'unity-native-clean.mp4'
  cache=L/'clips'/f"{folder.replace('/', '-')}-{start}-{length}.mp4";cache.parent.mkdir(exist_ok=True)
  if not cache.exists():run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',start,'-i',source,'-t',length,'-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2',cache])
  base+=['-stream_loop','-1','-i',cache]
  enable=f":enable='gte(t,{seconds*.5})'" if n in (2,6,13) else ''
  fil='[1:v]scale=1120:630,setsar=1[v];[0:v][v]overlay=76:216:shortest=1'+enable+',format=yuv420p[out]'
 elif n==27:
  folder,start,length=('living-room-v9',33,12) if n==17 else ('living-room-v9',0,20);source=P/'production/local'/folder/'unity-native-clean.mp4'
  cache=L/'clips'/f'pair-{n}.mp4';cache.parent.mkdir(exist_ok=True)
  if not cache.exists():run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',start,'-i',source,'-t',length,'-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2',cache])
  base+=['-stream_loop','-1','-i',cache];fil='[1:v]scale=850:478,setsar=1[v];[0:v][v]overlay=994:260:shortest=1,format=yuv420p[out]'
 if fil:base+=['-filter_complex',fil,'-map','[out]']
 else:base+=['-vf','format=yuv420p']
 temp=out.with_name(out.stem+'.partial.mp4')
 run(base+['-frames:v',frames,'-r','60','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','3','-movflags','+faststart',temp]);temp.replace(out)
 receipt.write_text(json.dumps({'inputs':sig,'frames':frames,'duration':seconds,'source':str(source) if source else 'Own images / independent diagram'},ensure_ascii=False,indent=2)+'\n','utf-8');print('Rendered',row['id'],frames,flush=True);return True
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--watch',action='store_true');parser.add_argument('--skip-scenes',default='');args=parser.parse_args();selected=[r for r in rows if r['id'] not in args.skip_scenes.split(',')]
 while True:
  done=all([render(r) for r in selected])
  if done or not args.watch:break
  time.sleep(8)

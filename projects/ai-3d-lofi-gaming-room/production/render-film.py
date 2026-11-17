"""Compose narration-paced real captures with film graphics; resumes by input hashes."""
from pathlib import Path
import json,hashlib,math,subprocess,time,argparse
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local/full-video-v1';V=L/'visual';V.mkdir(parents=True,exist_ok=True)
rows=json.loads((P/'script/narration.ko.json').read_text('utf-8'))['scenes']
MOTION={1:('web-final-v6',0,18),2:('unity-sample-v1',0,12),6:('web-final-v6',10,8),9:('web-final-v6',10,8),11:('web-final-v6',0,18),12:('atmosphere-v3',15,9),13:('nature-v2',0,12),16:('web-final-v6',0,8),18:('hearth-v4',24,10),19:('web-final-v6',32,7),20:('web-final-v6',18,14),21:('hearth-v4',40,10),22:('hearth-v4',50,8),23:('web-final-v6',10,8),24:('web-final-v6',0,18),25:('web-final-v6',0,18),26:('web-final-v6',0,18),28:('web-final-v6',0,18)}
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
def render(row):
 import soundfile as sf
 f=L/'narration/chunks'/(row['id']+'-scene.wav')
 if not f.exists():return False
 duration=sf.info(f).duration;frames=math.ceil((duration+(.28 if row['id']!='28' else 0))*60);seconds=frames/60
 board=L/'boards'/(row['id']+'.png');out=V/('scene-'+row['id']+'.mp4');receipt=out.with_suffix('.json');sig={'narration':sha(f),'board':sha(board),'frames':frames,'renderer':'actual-room-compositor-v1'}
 if out.exists() and receipt.exists() and json.loads(receipt.read_text())['inputs']==sig:return True
 base=['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-framerate','60','-i',board]
 n=int(row['id']);fil='';source=None
 if n in MOTION and n not in (23,24,26):
  folder,start,length=MOTION[n];source=P/'production/local'/folder/'unity-native-clean.mp4'
  cache=L/'clips'/f'{folder}-{start}-{length}.mp4';cache.parent.mkdir(exist_ok=True)
  if not cache.exists():run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',start,'-i',source,'-t',length,'-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2',cache])
  base+=['-stream_loop','-1','-i',cache]
  enable=f":enable='gte(t,{seconds*.5})'" if n in (6,13) else ''
  fil='[1:v]scale=1120:630,setsar=1[v];[0:v][v]overlay=76:216:shortest=1'+enable+',format=yuv420p[out]'
 elif n in (4,17,27):
  folder,start,length=('web-final-v6',5,10) if n==17 else ('web-final-v6',0,18);source=P/'production/local'/folder/'unity-native-clean.mp4'
  cache=L/'clips'/f'pair-{n}.mp4';cache.parent.mkdir(exist_ok=True)
  if not cache.exists():run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',start,'-i',source,'-t',length,'-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2',cache])
  base+=['-stream_loop','-1','-i',cache];fil='[1:v]scale=850:478,setsar=1[v];[0:v][v]overlay=994:260:shortest=1,format=yuv420p[out]'
 if fil:base+=['-filter_complex',fil,'-map','[out]']
 else:base+=['-vf','format=yuv420p']
 temp=out.with_name(out.stem+'.partial.mp4')
 run(base+['-frames:v',frames,'-r','60','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','3','-movflags','+faststart',temp]);temp.replace(out)
 receipt.write_text(json.dumps({'inputs':sig,'frames':frames,'duration':seconds,'source':str(source) if source else 'Own images / independent diagram'},ensure_ascii=False,indent=2)+'\n','utf-8');print('Rendered',row['id'],frames,flush=True);return True
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--watch',action='store_true');args=parser.parse_args()
 while True:
  done=all([render(r) for r in rows])
  if done or not args.watch:break
  time.sleep(8)

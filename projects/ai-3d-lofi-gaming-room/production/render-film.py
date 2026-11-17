"""Compose narration-paced real captures with film graphics; resumes by input hashes."""
from pathlib import Path
import json,hashlib,math,subprocess,time,argparse
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local/full-video-v5';V=L/'visual';V.mkdir(parents=True,exist_ok=True)
rows=json.loads((P/'script/narration.ko.json').read_text('utf-8'))['scenes']
MOTION={1: ('living-room-v11', 0, 20), 6: ('living-room-v11', 37, 8), 11: ('living-room-v11', 20, 11), 12: ('living-room-v11', 37, 8), 13: ('living-room-v11/walk-source', 0, 12), 16: ('living-room-v11/walk-source', 0, 12), 17: ('living-room-v11', 26, 19), 18: ('living-room-v11/sofa-entry', 3, 21), 19: ('web-final-v6', 32, 7), 20: ('living-room-v11', 84, 6), 21: ('final-activities-v7', 26, 7), 22: ('living-room-v11', 77, 7), 28: ('living-room-v11', 84, 6), 29: ('living-room-v11', 69, 8), 30: ('living-room-v11', 45, 24)}
DELAYED={6,11,13,30}
END_HOLD={17,18,30}
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)

def cached_clip(source,start,length,name):
 cache=L/'clips'/(name+'.mp4');cache.parent.mkdir(exist_ok=True)
 receipt=cache.with_suffix('.inputs.json')
 inputs={'sourceSha256':sha(source),'start':start,'length':length,'encoder':'libx264-crf18-60fps-v1'}
 if not cache.exists() or not receipt.exists() or json.loads(receipt.read_text('utf-8'))!=inputs:
  temp=cache.with_name(cache.stem+'.partial.mp4')
  run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',start,'-i',source,'-t',length,'-an','-c:v','libx264','-preset','veryfast','-crf','18','-r','60','-threads','2',temp])
  temp.replace(cache);receipt.write_text(json.dumps(inputs,indent=2)+'\n','utf-8')
 return cache,inputs
def render(row):
 import soundfile as sf
 f=L/'narration/chunks'/(row['id']+'-scene.wav')
 if not f.exists():return False
 duration=sf.info(f).duration;frames=math.ceil((duration+(.28 if row['id']!='28' else 0))*60)
 if row['id']=='28':frames=max(frames,600)
 seconds=frames/60
 n=int(row['id']);board=L/'boards'/(row['id']+'.png');out=V/('scene-'+row['id']+'.mp4');receipt=out.with_suffix('.json');sig={'narration':sha(f),'board':sha(board),'frames':frames,'renderer':'ai-tool-tutorial-compositor-v5.1'}
 base=['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-framerate','60','-i',board]
 n=int(row['id']);fil='';source=None
 if n in MOTION and n not in (23,24,26):
  folder,start,length=MOTION[n];source=P/'production/local'/folder/'unity-native-clean.mp4'
  cache,clip_inputs=cached_clip(source,start,length,f"{folder.replace('/', '-')}-{start}-{length}")
  delay=(frames//2)/60 if n in DELAYED else 0
  sig.update(clip=clip_inputs,placementStartSeconds=delay,repeat=n not in END_HOLD,endObservationHold=n in END_HOLD)
  base+=['-i',cache] if n in END_HOLD else ['-stream_loop','-1','-i',cache]
  enable=f":enable='gte(t,{delay})'" if delay else ''
  padding=f',tpad=stop_mode=clone:stop_duration={seconds}' if n in END_HOLD else ''
  video='[1:v]scale=1120:630,setsar=1'+padding+f',setpts=PTS-STARTPTS+{delay}/TB[v];'
  fil=video+'[0:v][v]overlay=76:216:eof_action=repeat'+enable+',format=yuv420p[out]'
  if n==30:
   base+=['-loop','1','-framerate','60','-i',L/'assets/tripo-cat.png']
   sig['toolImageSha256']=sha(L/'assets/tripo-cat.png')
   fil=f"[2:v]scale=1120:630,setsar=1[tool];[0:v][tool]overlay=76:216:enable='between(t,8,{delay})'[board];"+video+f"[board][v]overlay=76:216:eof_action=repeat:enable='gte(t,{delay})',format=yuv420p[out]"
 elif n==27:
  folder,start,length=('living-room-v11',0,20);source=P/'production/local'/folder/'unity-native-clean.mp4'
  cache,clip_inputs=cached_clip(source,start,length,f'pair-{n}');sig['clip']=clip_inputs
  base+=['-stream_loop','-1','-i',cache];fil='[1:v]scale=850:478,setsar=1[v];[0:v][v]overlay=994:260:shortest=1,format=yuv420p[out]'
 if out.exists() and receipt.exists() and json.loads(receipt.read_text('utf-8'))['inputs']==sig:return True
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

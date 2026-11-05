"""One finite production run for the explicitly requested remaining animation reviews; no publishing."""
from pathlib import Path
import sys,json,subprocess,time
B=Path(__file__).resolve().parent;R=B.parents[2];PYC=Path(sys.executable)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def run(args,log):
 with log.open('wb') as f:rc=subprocess.call([PYC,'-X','utf8','-u',*map(str,args)],cwd=R,stdout=f,stderr=f)
 if rc:raise RuntimeError(str(log)+'\n'+log.read_text('utf-8',errors='replace')[-1700:])
def wait(files):
 while not all(p.is_file() for p in files):time.sleep(10)
def produce(e,resume='voice'):
 ep=f'A{e:02}';batch=read(B/'batch.json');assert ep in batch['episodeIds'] and batch['productionAuthorized'] and not batch['youtubeAuthorized']
 row=next(x for x in read(R/'shared/publishing/video-worklist.json')['rows'] if x['id']==ep);p=R/'projects'/row['slug'];h=p/'production/series-v1';l=p/'production/local/series-v1'
 if (h/'checkpoint.json').is_file():return
 wait([h/'production-binding.json',h/'visual-plan.json',h/'make_poses.py'])
 if resume=='voice' and e==6:wait([l/'voice/narration.asr-review.json',*[l/(k+'.mp4') for k in read(h/'visual-plan.json')['rigs']]])
 elif resume=='voice':
  # Voice work owns its shared hardware handoff. CPU pose authoring may run during its inference.
  with (l/'queue-voice.log').open('wb') as f:
   voice=subprocess.Popen([PYC,'-X','utf8','-u',B/'render_voice.py',ep],cwd=R,stdout=f,stderr=f)
   try:run([h/'make_poses.py'],l/'queue-poses.log')
   finally:rc=voice.wait()
   if rc:raise RuntimeError(str(l/'queue-voice.log'))
  if not all((l/(k+'.mp4')).is_file() for k in read(h/'visual-plan.json')['rigs']):
   run([B/'native/capture_studies.py',ep],l/'queue-capture.log')
 modes=('voice','timing','mix','picture','verify','readback')
 for mode in modes[max(1,modes.index(resume)):-1]:
  run([B/'assemble_episode.py',ep,mode],l/f'queue-{mode}.log')
 run([B/'readback.py',row['slug'],'series-v1'],l/'queue-final-audio.log')
 print('Local review collected:',ep,flush=True)
if __name__=='__main__':
 first=int(sys.argv[1]);last=int(sys.argv[2]);assert 6<=first<=last<=18
 first_stage=sys.argv[3] if len(sys.argv)>3 else 'voice'
 for n in range(first,last+1):produce(n,first_stage if n==first else 'voice')

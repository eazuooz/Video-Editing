"""CPU-only finite Manim clip batch with exact receipts and alpha endpoints."""
from pathlib import Path
import os,json,hashlib,subprocess,argparse,time
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v6/math'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def run(cmd,log,env=None):
 with log.open('wb') as f:q=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
 if q.returncode:raise RuntimeError(log.read_text(encoding='utf8',errors='replace')[-3500:])
def selected():
 c=read(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized']
def main():
 a=argparse.ArgumentParser();a.add_argument('--beat',action='append');args=a.parse_args();selected();plan=read(H/'screen-plan.json');outputs=[]
 O.mkdir(parents=True,exist_ok=True)
 env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',CUDA_VISIBLE_DEVICES='')
 for scene in plan['scenes']:
  for beat in scene['beats']:
   key=beat['id']
   if beat['renderer']!='Manim' or (args.beat and key not in args.beat):continue
   selected();work=O/key;work.mkdir(exist_ok=True);receipt=work/'output.json'
   signature={'spec':beat['demonstration'],'sourceSha256':sha(H/'math-clips.py'),'fps':60,'resolution':[1920,1080],'engine':'Manim Cairo alpha qtrle; CPU-only'}
   sig=hashlib.sha256(json.dumps(signature,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
   if receipt.exists():
    done=read(receipt)
    if done['signature']==sig and all((R/f['file']).exists() and sha(R/f['file'])==f['sha256'] for f in done['files']):outputs.append(done);print('Cached',key,flush=True);continue
   localenv={**env,'V6_BEAT':key};cmd=[str(R/'manim/.venv/Scripts/python.exe'),'-m','manim','--renderer','cairo','--format','mov','-t','-r','1920,1080','--fps','60','--media_dir',str(work/'manim'),'-o',key,str(H/'math-clips.py'),'FiniteMathBeat']
   print('Render finite math',key,flush=True);run(cmd,work/'render.log',localenv)
   files=list((work/'manim').rglob(key+'.mov'));assert len(files)==1,files;clip=files[0]
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(clip)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');assert(v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1');frames=int(v['nb_frames']);assert frames>1
   first=work/'first.png';last=work/'last.png'
   for index,dest in [(0,first),(frames-1,last)]:
    run(['ffmpeg','-v','warning','-y','-i',str(clip),'-vf',f'select=eq(n\\,{index})','-frames:v','1','-fps_mode','passthrough','-pix_fmt','rgba',str(dest)],work/('endpoint-'+str(index)+'.log'))
   row={'id':key,'signature':sig,'clipFile':clip.relative_to(R).as_posix(),'firstFrame':first.relative_to(R).as_posix(),'lastFrame':last.relative_to(R).as_posix(),'durationFrames':frames,'seconds':frames/60,'renderer':'Manim0.20.1/Cairo; authored transparent diagram','sourceKind':'illustrative mathematical calculation','files':[{'file':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in [clip,first,last]],'newVoiceChanged':False,'movingFinalReview':'pending composite captions and same-testbed background'}
   save(receipt,row);outputs.append(row);save(O/'outputs.json',{'outputs':outputs,'renderedAt':time.time()});print('Completed',key,frames,'frames',flush=True)
 save(O/'outputs.json',{'outputs':outputs,'renderedAt':time.time()})
if __name__=='__main__':main()

"""CPU-only finite Manim clip batch with exact receipts and alpha endpoints."""
from pathlib import Path
import os,json,hashlib,subprocess,argparse,time,ast
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v6/math'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def run(cmd,log,env=None):
 with log.open('wb') as f:q=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
 if q.returncode:raise RuntimeError(log.read_text(encoding='utf8',errors='replace')[-3500:])
def selected():
 c=read(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']==P.name and c['newProductionAuthorization']['fullProductionAuthorized']
def base_helpers(source):
 tree=ast.parse(Path(source).read_text(encoding='utf8'));colors={'INK','MUTED','RULE','GOLD','TEAL','ORANGE','RED','GREEN','PURPLE','PANEL'}
 nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['tx','rowgroup'] or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in colors for t in n.targets)]
 return hashlib.sha256('\n'.join(ast.dump(n,include_attributes=False) for n in nodes).encode()).hexdigest()
def signature_for(beat):
 module='math-prerequisites.py' if beat['demonstration'].get('module')=='prerequisites' else 'math-clips.py'
 signature={'spec':beat['demonstration'],'sourceSha256':sha(H/module),'fps':60,'resolution':[1920,1080],'engine':'Manim Cairo alpha qtrle; CPU-only'}
 if module=='math-prerequisites.py':signature['baseHelpersSha256']=base_helpers(H/'math-clips.py')
 return hashlib.sha256(json.dumps(signature,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--beat',action='append');args=a.parse_args();selected();plan=read(H/'screen-plan.json');outputs={};order=[b['id'] for s in plan['scenes'] for b in s['beats'] if b['renderer']=='Manim']
 if args.beat:assert set(args.beat)<=set(order),'Unknown mathematical beat'
 O.mkdir(parents=True,exist_ok=True)
 env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',CUDA_VISIBLE_DEVICES='')
 for scene in plan['scenes']:
  for beat in scene['beats']:
   if beat['renderer']!='Manim':continue
   receipt=O/beat['id']/'output.json'
   if receipt.exists():
    done=read(receipt)
    if done['signature']==signature_for(beat) and all((R/f['file']).exists() and sha(R/f['file'])==f['sha256'] for f in done['files']):outputs[beat['id']]=done
 def manifest():save(O/'outputs.json',{'outputs':[outputs[key] for key in order if key in outputs],'renderedAt':time.time(),'complete':len(outputs)==len(order),'expected':len(order)})
 for scene in plan['scenes']:
  for beat in scene['beats']:
   key=beat['id']
   if beat['renderer']!='Manim' or (args.beat and key not in args.beat):continue
   selected();work=O/key;work.mkdir(exist_ok=True);receipt=work/'output.json'
   module='math-prerequisites.py' if beat['demonstration'].get('module')=='prerequisites' else 'math-clips.py';klass='FinitePrerequisite' if module=='math-prerequisites.py' else 'FiniteMathBeat'
   sig=signature_for(beat)
   if key in outputs:print('Cached',key,flush=True);continue
   localenv={**env,'V6_BEAT':key};cmd=[str(R/'manim/.venv/Scripts/python.exe'),'-m','manim','--renderer','cairo','--format','mov','-t','-r','1920,1080','--fps','60','--media_dir',str(work/'manim'),'-o',key,str(H/module),klass]
   print('Render finite math',key,flush=True);run(cmd,work/'render.log',localenv)
   files=list((work/'manim').rglob(key+'.mov'));assert len(files)==1,files;clip=files[0]
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(clip)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');assert(v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1');frames=int(v['nb_frames']);assert frames>1
   first=work/'first.png';last=work/'last.png'
   for index,dest in [(0,first),(frames-1,last)]:
    run(['ffmpeg','-v','warning','-y','-i',str(clip),'-vf',f'select=eq(n\\,{index})','-frames:v','1','-fps_mode','passthrough','-pix_fmt','rgba',str(dest)],work/('endpoint-'+str(index)+'.log'))
   row={'id':key,'signature':sig,'clipFile':clip.relative_to(R).as_posix(),'firstFrame':first.relative_to(R).as_posix(),'lastFrame':last.relative_to(R).as_posix(),'durationFrames':frames,'seconds':frames/60,'renderer':'Manim0.20.1/Cairo; authored transparent diagram','sourceKind':'illustrative mathematical calculation','files':[{'file':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in [clip,first,last]],'newVoiceChanged':False,'movingFinalReview':'pending composite captions and same-testbed background'}
   save(receipt,row);outputs[key]=row;manifest();print('Completed',key,frames,'frames',flush=True)
 manifest()
if __name__=='__main__':main()

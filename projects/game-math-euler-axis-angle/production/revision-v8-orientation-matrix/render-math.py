"""Explicit finite CPU-only Manim batch, serially invoked by root."""
from pathlib import Path
import importlib.util,json,os,subprocess
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
TASKS=[('rows','세 축을 행으로 모으기','m04',2,181),('transpose','행과 열을 교환','m05',3,181),('weighted','축을 따라가고 더하기','m04',4,241),('dcm','아홉 칸의 방향코사인','m08',2,181),('composition','공간을 연결하는 곱셈','m09',5,181),('storage','1초 동안 저장한 자세','m10',3,181)]
def main():
 c.authorized();out=c.O/'math';out.mkdir(parents=True,exist_ok=True);records=[]
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONUTF8='1')
 for key,title,sid,line,frames in TASKS:
  c.authorized();folder=out/key;folder.mkdir(exist_ok=True);log=folder/'render.log'
  cmd=[str(c.R/'manim/.venv/Scripts/python.exe'),'-m','manim','--renderer','cairo','--format','mp4','-r','800,700','--fps','60','--media_dir',str(folder),'-o',key,str(H/'matrix-manim.py'),'MatrixAction']
  with log.open('wb') as f:
   result=subprocess.run(cmd,cwd=c.R,env=dict(env,V8_MATH_ACTION=key,V8_MATH_TITLE=title),stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
  if result.returncode:raise RuntimeError(log.read_text(encoding='utf8',errors='replace')[-3500:])
  file=next(folder.rglob(key+'.mp4'));v=c.probe(file)['streams'][0];assert int(v['nb_frames'])==frames and v['r_frame_rate']=='60/1'
  records.append(dict(key=key,scene=sid,line=line,file=c.rel(file),sha256=c.sha(file),frames=frames,fps=60,dimensions=[800,700],sourceKind='authored exact matrix calculation',phases=[[i,min(i+60,frames-1)]for i in range(0,frames-1,60)]))
  c.save(H/'math-manifest.json',dict(source=c.rel(H/'matrix-manim.py'),sourceSha256=c.sha(H/'matrix-manim.py'),records=records,complete=len(records)==len(TASKS)))
  print(key,frames,flush=True)
if __name__=='__main__':main()

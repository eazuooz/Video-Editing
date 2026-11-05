"""Capture the selected studies offscreen in a separate worker; never focus the user's editor."""
from pathlib import Path
import subprocess,json,shutil,sys,os
H=Path(__file__).resolve().parent;R=H.parents[3];batch=H.parent
ep=sys.argv[1];work=json.loads((R/'shared/publishing/video-worklist.json').read_text(encoding='utf-8-sig'));row=next(x for x in work['rows'] if x['id']==ep)
assert ep in json.loads((batch/'batch.json').read_text('utf-8'))['episodeIds']
P=R/'projects'/row['slug'];L=P/'production/local/series-v1';W=L/'unreal-worker';src=R/'GameAnimationSample'
job=json.loads((L/'study-job.json').read_text('utf-8'));assert job['episode']==ep
exe=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe')
template=R/'projects/animation-assigning/production/local/unreal-kit-v2/unreal-worker'
descriptor=W/(ep+'Worker.uproject');(W/'Content').mkdir(parents=True,exist_ok=True);(W/'Config').mkdir(exist_ok=True)
shutil.copyfile(template/'A01Worker.uproject',descriptor);shutil.copyfile(template/'Config/DefaultEngine.ini',W/'Config/DefaultEngine.ini')
for folder in (src/'Content').iterdir():
 if not folder.is_dir() or folder.name=='YamyamAnimationSeries':continue
 dst=W/'Content'/folder.name
 if not dst.exists():
  q=lambda p:"'"+str(p).replace("'","''")+"'"
  subprocess.run(['powershell','-NoProfile','-Command','New-Item -ItemType Junction -Path '+q(dst)+' -Target '+q(folder)+' | Out-Null'],check=True)
 assert dst.resolve()==folder.resolve()
(W/'build-job.json').write_text(json.dumps(dict(job,local=str(L))),encoding='utf-8')
def run(args,name):
 with (L/(name+'.log')).open('wb') as log:
  subprocess.run([exe,descriptor,*args,'-unattended','-nosound','-nosplash','-NoLiveCoding','-abslog='+str(L/(name+'.engine.log'))],stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
error=L/'stage-error.txt'
if error.exists():error.rename(L/('stage-error-'+str(error.stat().st_mtime_ns)+'.txt'))
run(['-run=pythonscript','-script='+str(H/'build_level.py'),'-nullrhi'],'stage-build')
if error.exists():raise RuntimeError(error.read_text('utf-8'))
for key in job['keys']:
 meta=json.loads((L/(key+'-build.json')).read_text());folder=L/'frames'/key
 if len(list(folder.glob('*.png')))!=meta['frames']:
  run([meta['level'],'-game','-LevelSequence='+meta['sequence'],'-MoviePipelineConfig='+meta['config'],'-RenderOffscreen','-NoScreenMessages','-NoLoadingScreen','-notexturestreaming','-resx=1920','-resy=1080'],'render-'+key)
 assert len(list(folder.glob('*.png')))==meta['frames'],key
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-i',str(folder/'%06d.png'),'-frames:v',str(meta['frames']),'-c:v','h264_nvenc','-preset','p4','-cq','17','-b:v','0','-pix_fmt','yuv420p',str(L/(key+'.mp4'))],check=True)
 print('Rendered',key,flush=True)
shutil.copytree(W/'Content/YamyamAnimationSeries'/ep,src/'Content/YamyamAnimationSeries'/ep,dirs_exist_ok=True)

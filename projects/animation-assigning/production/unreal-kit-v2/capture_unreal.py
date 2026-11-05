"""Create an isolated GAS editor worker, render native plates and retain editable assets."""
from pathlib import Path
import subprocess,json,shutil,hashlib
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/unreal-kit-v2';W=L/'unreal-worker';U=L/'unreal'
EXE=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe')
src=R/'GameAnimationSample';descriptor=W/'A01Worker.uproject';owned='/Game/YamyamA01/assigning_v2'
def check():
 grant=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))['scopedProductionAuthorizations']['animation-assigning-unreal-kit-v2'];assert grant['renderAuthorized']
def run(args,label):
 with (U/(label+'.stdout')).open('wb') as f:
  subprocess.run([EXE,descriptor,*args,'-unattended','-nosound','-nosplash','-NoLiveCoding','-abslog='+str(U/(label+'.log'))],stdout=f,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
check();U.mkdir(parents=True,exist_ok=True);(W/'Content').mkdir(parents=True,exist_ok=True)
template=R/'projects/animation-exaggeration/production/local/fighters-v4-kula-lili/unreal-worker'
d=json.loads((template/'A02Worker.uproject').read_text(encoding='utf-8'));d['Description']='A01 animation direction studies using Game Animation Sample';descriptor.write_text(json.dumps(d,indent=2),encoding='utf-8')
(W/'Config').mkdir(exist_ok=True);shutil.copy2(template/'Config/DefaultEngine.ini',W/'Config/DefaultEngine.ini')
for f in (src/'Content').iterdir():
 if not f.is_dir() or f.name.startswith('Yamyam'):continue
 junction=W/'Content'/f.name
 if not junction.exists():
  quote=lambda x:"'"+str(x).replace("'","''")+"'"
  subprocess.run(['powershell','-NoProfile','-Command','New-Item -ItemType Junction -Path '+quote(junction)+' -Target '+quote(f)+' | Out-Null'],check=True)
 assert junction.resolve()==f.resolve()
jobs=json.loads((H/'stage-plan.json').read_text(encoding='utf-8'))['stages']
fingerprint=hashlib.sha256((H/'build_stages.py').read_bytes()+(H/'stage-plan.json').read_bytes()).hexdigest()
stamp=U/'stage-source.sha256'
if not stamp.exists() or stamp.read_text()!=fingerprint:
 run(['-run=pythonscript','-script='+str(H/'build_stages.py'),'-nullrhi'],'build-locked')
 assert not (U/'error.txt').exists(),(U/'error.txt').read_text()
 stamp.write_text(fingerprint)
for key in jobs:
 check();j=json.loads((U/(key+'-build.json')).read_text());assert j['level'].startswith(owned+'/')
 centered=key in ('stop','turn')
 imgs=U/('final-renders' if centered else 'locked-renders')/key;target=U/(key+('-final.mp4' if centered else '-inplace.mp4'))
 if target.exists() and int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','default=nw=1:nk=1',str(target)]))==j['frames']:continue
 if not list(imgs.glob('*.png')):
  run([j['level'],'-game','-LevelSequence='+j['sequence'],'-MoviePipelineConfig='+j['captureConfig'],'-RenderOffscreen','-NoScreenMessages','-NoLoadingScreen','-notexturestreaming','-resx=1920','-resy=1080'],'render-'+key)
 frames=sorted(imgs.glob('*.png'));assert len(frames)==j['frames'],(key,len(frames),j['frames'])
 start=int(frames[0].stem);subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-start_number',str(start),'-i',str(imgs/'%06d.png'),'-frames:v',str(j['frames']),'-c:v','h264_nvenc','-preset','p5','-cq','17','-b:v','0','-pix_fmt','yuv420p',str(target)],check=True)
 print('Captured',key,j['frames'],flush=True)
output=src/'Content/YamyamA01/assigning_v2';shutil.copytree(W/'Content/YamyamA01/assigning_v2',output,dirs_exist_ok=True)
assets=[{'path':f.relative_to(R).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(output.rglob('*')) if f.is_file()]
(H/'native-assets.json').write_text(json.dumps({'engine':'5.8','captures':list(jobs),'files':assets},indent=2)+'\n',encoding='utf-8')

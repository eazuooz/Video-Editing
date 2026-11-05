"""Use the isolated project and licensed local library; save editable scene + actual WARP renders."""
from build import HERE,ROOT,MEDIA,WORK,sha,save
import os,shutil,subprocess as sp
from pathlib import Path
src=ROOT/'unity/VideoEditing/Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack'
project=MEDIA/'unity-capture';folder=project/'Assets/VideoScenes/FeedbackRTS'
models=folder/'Models';models.mkdir(exist_ok=True,parents=True);(folder/'Editor').mkdir(exist_ok=True)
links=[]
for f in [src/'FBX Unity'/f'{m}.fbx' for m in ['Tank_1_A','Tank_2_A','Jeep_A','Heli_1_A','Turret_1_A','Hangar_1_A']]+[src/'Textures/Military Atlas.png']:
    shutil.copyfile(f,models/f.name);links.append(dict(source=f.relative_to(ROOT).as_posix(),sha256=sha(f),imported=(models/f.name).relative_to(project).as_posix()))
for f,d in [('CommandReplay.cs',folder),('ReplayCapture.cs',folder/'Editor')]:shutil.copyfile(HERE/f,d/f)
target=WORK/'unity-rts-layout2';env=dict(os.environ,YAMYAM_REPLAY_FRAMES=str(target));target.mkdir(exist_ok=True)
exe='C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe'
if not (target/'renderer.txt').exists():
    sp.run([exe,'-batchmode','-force-d3d11','-force-driver-type-warp','-job-worker-count','2','-projectPath',str(project),'-executeMethod','ReplayCapture.Run','-logFile',str(WORK/'unity-layout2.log')],env=env,check=True,creationflags=sp.CREATE_NO_WINDOW)
assert (target/'record/state.csv').read_bytes()==(target/'replay/state.csv').read_bytes()!=(target/'patch/state.csv').read_bytes()
for k in ['record','replay','patch']:assert len(list((target/k).glob('*.jpg')))==195
save(HERE/'unity-source.json',dict(scene=str(folder/'ReplaySquad.unity'),sceneSHA256=sha(folder/'ReplaySquad.unity'),editor='6000.6.0f1',softwareDevice=(target/'renderer.txt').read_text(),renderer='Built-in / orthographic',captures='1080x548 window, 30 fps, 60 simulation ticks/s',seed=42,orders=[dict(tick=120,action='move'),dict(tick=240,action='attack')],inputs=links,traces={k:sha(target/k/'state.csv') for k in ['record','replay','patch']},fullEditableProject=str(project)))

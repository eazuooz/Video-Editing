"""Record the actual imported rattan scene with existing native motion via Unity MCP."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,shutil,time

H=Path(__file__).resolve().parent;R=H.parents[2];L=H/'local/living-room-v11'
spec=importlib.util.spec_from_file_location('unity_client',H/'unity-mcp-client.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def call(tool,args=None):
    path,result=m.call(tool,args or {},180)
    body=result.get('result',{})
    assert not body.get('isError'),body
    text='\n'.join(c.get('text','') for c in body.get('content',[]))
    assert not text.startswith('Error:'),text
    return text

def play():
    call('eval',{'code':'UnityEditor.EditorApplication.isPlaying=false;return "stop";'})
    call('eval',{'code':'UnityEditor.SceneManagement.EditorSceneManager.OpenScene("Assets/LofiRoom/Scenes/LofiRattanRoomV11.unity");UnityEditor.EditorApplication.isPlaying=true;return "play";'})

def capture(folder,command,frames):
    destination=L/folder
    assert not (destination/'unity-native-clean.mp4').exists(),f'Preserve existing capture: {destination}'
    began=time.time();print('Starting',command,flush=True)
    call(command,{'ffmpeg':shutil.which('ffmpeg')})
    result=destination/'capture-result.json';last=-1
    while not result.exists() or result.stat().st_mtime<began:
        progress=destination/'capture-progress.json'
        if progress.exists():
            row=json.loads(progress.read_text('utf-8'));frame=row.get('frame',0)
            if frame//600!=last:print(command,frame,'/',frames,flush=True);last=frame//600
        assert time.time()-began<1200,command
        time.sleep(3)
    row=json.loads(result.read_text('utf-8'))
    assert row['frames']==frames and row['exitCode']==0,row
    print('Finished',command,flush=True)
    return row

play();walk=capture('walk-source','lofi_tutorial_walk_record',720)
play();entry=capture('sofa-entry','lofi_sofa_entry_record',1440)
# Entry ends in the settled reading pose. Preserve it for the first wide shot.
feature=capture('','lofi_living_record',5400)
call('eval',{'code':'UnityEditor.EditorApplication.isPlaying=false;return "stop";'})
sources=['Runtime/LofiSofaReading.cs','Runtime/LofiSleepingCatBreath.cs','Runtime/LofiLivingCapture.cs','Runtime/LofiSofaEntryCapture.cs','Scenes/LofiRattanRoomV11.unity']
record={'recordedAtKst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'transport':'official project-scoped Unity CLI MCP','fps':60,'dimensions':[1920,1080],'captures':{'walk':walk,'sofaEntry':entry,'features':feature},'inputs':[{'path':'unity/LofiGamingRoomWeb/Assets/LofiRoom/'+name,'sha256':hashlib.sha256((R/'unity/LofiGamingRoomWeb/Assets/LofiRoom'/name).read_bytes()).hexdigest()} for name in sources],'furnitureImport':'production/rattan-v11-import.json','nativeContacts':'Existing licensed native body/reading-arm clips, fitted IK; no replacement body rig','humanFinalReview':False}
(H/'rattan-v11-capture-record.json').write_text(json.dumps(record,indent=2)+'\n','utf-8')
print('All three actual rattan captures complete; Editor left in edit mode.',flush=True)

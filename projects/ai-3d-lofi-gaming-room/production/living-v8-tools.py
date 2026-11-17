"""Use the official scoped Unity MCP; never control the user's other Editor."""
from pathlib import Path
import importlib.util,json,sys
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('lofi_mcp',H/'unity-mcp-client.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
actions={
 'play':'UnityEditor.EditorApplication.isPlaying=true;return "play";',
 'stop':'UnityEditor.EditorApplication.isPlaying=false;return "stopped";',
 'refresh':'UnityEditor.AssetDatabase.Refresh();return "refreshed";',
 'read':'UnityEngine.Object.FindAnyObjectByType<Yamyam.LofiRoom.LofiRoomSample>().ReadBook();return "read";',
 'metrics':'''var r=UnityEngine.Object.FindAnyObjectByType<Yamyam.LofiRoom.LofiRoomSample>();var l=r.GetComponent<Yamyam.LofiRoom.LofiLivingRoom>();var p=r.GetComponent<Yamyam.LofiRoom.LofiPlaylist>();return Newtonsoft.Json.JsonConvert.SerializeObject(new{phase=r.activities.phase,busy=r.activities.busy,seated=r.activities.seated,reclined=l.reclined,hips=r.actor.GetBoneTransform(UnityEngine.HumanBodyBones.Hips).position.ToString("F3"),head=r.actor.GetBoneTransform(UnityEngine.HumanBodyBones.Head).position.ToString("F3"),leftFoot=r.actor.GetBoneTransform(UnityEngine.HumanBodyBones.LeftFoot).position.ToString("F3"),rightHand=r.actor.GetBoneTransform(UnityEngine.HumanBodyBones.RightHand).position.ToString("F3"),l.cushionWeight,l.bookWeight,l.raining,track=p.index,title=p.Title,playing=p.source.isPlaying,loaded=p.source.clip.loadState.ToString()});''',
 'preview':'''var r=UnityEngine.Object.FindAnyObjectByType<Yamyam.LofiRoom.LofiRoomSample>();r.CameraRoom();r.showControls=false;r.SetNight(true);var c=r.roomCamera;var t=new UnityEngine.RenderTexture(1920,1080,24);var p=new UnityEngine.Texture2D(1920,1080,UnityEngine.TextureFormat.RGB24,false);c.targetTexture=t;c.Render();UnityEngine.RenderTexture.active=t;p.ReadPixels(new UnityEngine.Rect(0,0,1920,1080),0,0);p.Apply();System.IO.File.WriteAllBytes("projects/ai-3d-lofi-gaming-room/production/local/living-room-v8/preview.png",p.EncodeToPNG());c.targetTexture=null;UnityEngine.RenderTexture.active=null;UnityEngine.Object.DestroyImmediate(t);UnityEngine.Object.DestroyImmediate(p);return "preview";'''
}
if __name__=='__main__':
 a=sys.argv[1]
 if a in actions:
  code=actions[a].replace('"projects/ai-3d-lofi-gaming-room/production/local/living-room-v8/preview.png"','"'+(H/'local/living-room-v8/preview.png').as_posix()+'"');tool,args='eval',{'code':code}
 else:tool,args=a,json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
 path,result=m.call(tool,args,180);print(json.dumps({'record':str(path),'result':result},ensure_ascii=True)[:12000])

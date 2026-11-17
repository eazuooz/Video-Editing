"""Official project-scoped MCP plus deterministic native contact inspection."""
from pathlib import Path
import importlib.util,json,sys
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('client',H/'unity-mcp-client.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
common='var r=UnityEngine.Object.FindAnyObjectByType<Yamyam.LofiRoom.LofiRoomSample>();var l=r.GetComponent<Yamyam.LofiRoom.LofiLivingRoom>();'
actions={
 'refresh':'UnityEditor.AssetDatabase.Refresh();return "refreshed";',
 'play':'UnityEditor.SceneManagement.EditorSceneManager.OpenScene("Assets/LofiRoom/Scenes/LofiLivingRoomV9.unity");UnityEditor.EditorApplication.isPlaying=true;return "play requested";',
 'stop':'UnityEditor.EditorApplication.isPlaying=false;return "stop requested";',
 'read':common+'r.ReadBook();return "read requested";',
 'metrics':common+'return Newtonsoft.Json.JsonConvert.SerializeObject(new {phase=r.activities.phase, book=r.activities.book.position.ToString("F3"), bookNormal=r.activities.book.up.ToString("F3"), bones=System.Enum.GetValues(typeof(UnityEngine.HumanBodyBones)).Cast<UnityEngine.HumanBodyBones>().Where(b=>b==UnityEngine.HumanBodyBones.Head||b==UnityEngine.HumanBodyBones.Chest||b==UnityEngine.HumanBodyBones.LeftHand||b==UnityEngine.HumanBodyBones.RightHand||b==UnityEngine.HumanBodyBones.LeftLowerArm||b==UnityEngine.HumanBodyBones.RightLowerArm).Select(b=>new {name=b.ToString(),position=r.actor.GetBoneTransform(b).position.ToString("F3")})});',
 'exit':'UnityEditor.EditorApplication.Exit(0);return "owned editor closing";'
}
def preview(name):
 base=common+'r.showControls=false;r.SetNight(true);var c=r.roomCamera;'
 if name=='cat':base+='var p=new UnityEngine.Vector3(3.5f,1.25f,-2f);c.transform.SetPositionAndRotation(p,UnityEngine.Quaternion.LookRotation(new UnityEngine.Vector3(2.15f,.26f,-.5f)-p));c.orthographicSize=.55f;'
 else:
  pos='new UnityEngine.Vector3(2.2f,1.8f,-3.1f)' if name=='book' else 'new UnityEngine.Vector3(-2.4f,1.9f,-1.7f)'
  base+='var p='+pos+';var centre=r.activities.book.position;c.transform.SetPositionAndRotation(p,UnityEngine.Quaternion.LookRotation(centre-p));c.orthographicSize=.75f;'
 out=(H/'local/living-room-v9'/('contact-'+name+'.png')).as_posix()
 return base+'var t=new UnityEngine.RenderTexture(1920,1080,24);var image=new UnityEngine.Texture2D(1920,1080,UnityEngine.TextureFormat.RGB24,false);c.targetTexture=t;c.Render();UnityEngine.RenderTexture.active=t;image.ReadPixels(new UnityEngine.Rect(0,0,1920,1080),0,0);image.Apply();System.IO.File.WriteAllBytes("'+out+'",image.EncodeToPNG());c.targetTexture=null;UnityEngine.RenderTexture.active=null;UnityEngine.Object.DestroyImmediate(t);UnityEngine.Object.DestroyImmediate(image);return "'+out+'";'
if __name__=='__main__':
 (H/'local/living-room-v9').mkdir(parents=True,exist_ok=True)
 a=sys.argv[1]
 if a in ('cat','book','reverse'):tool,args='eval',{'code':preview(a)}
 elif a in actions:tool,args='eval',{'code':actions[a]}
 elif a=='code':tool,args='eval',{'code':Path(sys.argv[2]).read_text('utf-8')}
 else:tool,args=a,json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
 path,result=m.call(tool,args,180);print(json.dumps({'record':str(path),'result':result},ensure_ascii=True)[:12000])

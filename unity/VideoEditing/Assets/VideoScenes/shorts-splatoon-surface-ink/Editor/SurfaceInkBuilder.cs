using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Yamyam.Video.SurfaceInk.Editor
{
    public static class SurfaceInkBuilder
    {
        const string Root="Assets/VideoScenes/shorts-splatoon-surface-ink";
        [MenuItem("Yamyam/Selected Shorts/Build Surface Ink Lessons")]
        public static void Build()
        {
            // Invoke only after the project-level scope/resource preflight permits Unity.
            string[] names={"01-SurfaceSheet","02-Collision","03-UVAddress","04-StampFloorWall","05-AdjacentPatch","06-CameraOrbit"};
            var existingScenes=new System.Collections.Generic.List<string>();
            foreach(string name in names)
            {
                string path=Root+"/Scenes/"+name+".unity";
                if(File.Exists(path))existingScenes.Add(path);
            }
            // Check every destination before creating folders, assets or scenes.
            if(existingScenes.Count>0)
                throw new IOException("Preserve existing scenes; choose a revision before rebuilding: "+string.Join(", ",existingScenes));
            var previousActive=SceneManager.GetActiveScene();
            Directory.CreateDirectory(Root+"/Generated");Directory.CreateDirectory(Root+"/Scenes");
            var shader=Shader.Find("Yamyam/SurfaceInkLesson");
            if(!shader)throw new System.InvalidOperationException("Surface ink shader has not imported.");
            Material material=AssetDatabase.LoadAssetAtPath<Material>(Root+"/Generated/Paint.mat");
            if(!material){material=new Material(shader);AssetDatabase.CreateAsset(material,Root+"/Generated/Paint.mat");}
            for(int stage=0;stage<names.Length;stage++)
            {
                string path=Root+"/Scenes/"+names[stage]+".unity";
                var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);
                try
                {
                if(SceneManager.GetActiveScene()!=scene && !EditorSceneManager.SetActiveScene(scene))
                    throw new System.InvalidOperationException("Could not activate generated scene. valid="+scene.IsValid()+" loaded="+scene.isLoaded+" handle="+scene.handle);
                var host=new GameObject("Surface paint principle — independently authored");
                var demo=host.AddComponent<SurfaceInkDemo>();demo.stage=stage;demo.paintMaterial=material;
                demo.generatedRoot=host.transform;
                demo.floorRenderer=Quad("Floor",new Vector3(-2,0,-2),Vector3.right*4,Vector3.forward*4,true,host.transform,material);
                demo.wallRenderer=Quad("Wall",new Vector3(-2,0,2),Vector3.right*4,Vector3.up*4,true,host.transform,material);
                demo.sheetRenderer=Quad("Live paint texture",new Vector3(-1.3f,4.5f,1),Vector3.right*2.6f,Vector3.up*2.6f,false,host.transform,material);
                demo.impactGuide=Line("Actual collision ray",host.transform,Color.green);
                demo.mappingGuide=Line("Same point on texture",host.transform,Color.yellow);
                var dot=GameObject.CreatePrimitive(PrimitiveType.Sphere);dot.name="Hit position";dot.transform.SetParent(host.transform);dot.transform.localScale=Vector3.one*.09f;
                Object.DestroyImmediate(dot.GetComponent<Collider>());demo.contactMarker=dot.transform;
                var camera=new GameObject("Lesson Camera").AddComponent<Camera>();camera.transform.SetParent(host.transform);
                camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=Color.black;camera.fieldOfView=44;camera.aspect=9f/16f;
                demo.lessonCamera=camera;camera.transform.position=new Vector3(0,6.5f,-15);camera.transform.LookAt(new Vector3(0,3,1));
                // Runtime textures are generated from actual hits when capture calls ApplyFrame.
                if(!EditorSceneManager.SaveScene(scene,path))
                    throw new IOException("Could not save the generated lesson scene: "+path);
                }
                finally
                {
                    // Never unload, save or discard an unrelated open/dirty scene.
                    if(previousActive.IsValid() && previousActive.isLoaded)
                        SceneManager.SetActiveScene(previousActive);
                    if(scene.IsValid() && scene.isLoaded)
                        EditorSceneManager.CloseScene(scene,true);
                }
            }
            // CreateAsset persists each newly created asset. Do not SaveAssets here:
            // that would also save unrelated dirty assets in the user's project.
        }
        static MeshRenderer Quad(string name,Vector3 corner,Vector3 u,Vector3 v,bool collide,Transform parent,Material material)
        {
            string asset=Root+"/Generated/"+name.Replace(" ","-")+".asset";
            var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(asset);
            if(!mesh){mesh=new Mesh{name=name,vertices=new[]{corner,corner+u,corner+u+v,corner+v},uv=new[]{Vector2.zero,Vector2.right,Vector2.one,Vector2.up},triangles=new[]{0,2,1,0,3,2}};mesh.RecalculateNormals();mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,asset);}
            var go=new GameObject(name);go.transform.SetParent(parent);go.AddComponent<MeshFilter>().sharedMesh=mesh;
            var render=go.AddComponent<MeshRenderer>();render.sharedMaterial=material;
            if(collide)go.AddComponent<MeshCollider>().sharedMesh=mesh;
            return render;
        }
        static LineRenderer Line(string name,Transform parent,Color color)
        {
            var go=new GameObject(name);go.transform.SetParent(parent);var l=go.AddComponent<LineRenderer>();
            l.positionCount=2;l.startWidth=l.endWidth=.025f;l.startColor=l.endColor=color;
            string path=Root+"/Generated/"+name.Replace(" ","-")+".mat";
            var mat=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(!mat){mat=new Material(Shader.Find("Universal Render Pipeline/Unlit"));mat.SetColor("_BaseColor",color);AssetDatabase.CreateAsset(mat,path);}
            l.sharedMaterial=mat;
            l.enabled=false;return l;
        }
    }
}

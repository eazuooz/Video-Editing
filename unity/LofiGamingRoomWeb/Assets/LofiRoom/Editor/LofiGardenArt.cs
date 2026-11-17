using System.Linq;
using UnityEngine;
using UnityEditor;
using Yamyam.LofiRoom;

public static class LofiGardenArt
{
    public static void Apply(LofiRoomSample room,string root)
    {
        // Keep the seat contact height, but reveal the seated head and shoulders.
        var back=GameObject.Find("reading chair back");
        back.transform.position=new Vector3(1,.665f,.57f);
        back.transform.localScale=new Vector3(.82f,.48f,.82f);
        // Lower the display and shorten its stand; the desk and hands stay put.
        foreach(var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Where(x=>x.name.StartsWith("iMac ")||x.name=="quiet work line"))
        {
            if(r.name=="iMac low stand foot")continue;
            if(r.name=="iMac slim stand")
            {r.transform.position+=Vector3.down*.065f;r.transform.localScale=new Vector3(1,.57f,1);}
            else r.transform.position+=Vector3.down*.13f;
        }
        var hair=room.actor.GetComponent<LofiHairMotion>();
        hair.breezeStrength=4.2f;hair.restoringStrength=.65f;hair.maximumSway=.12f;hair.maximumAngle=43;
        var leaves=AssetDatabase.LoadAssetAtPath<Material>(root+"/Materials/living-leaf.mat");
        leaves.SetFloat("_WindStrength",.085f);EditorUtility.SetDirty(leaves);
        var outside=GameObject.Find("night outside");
        // Bring the panorama close to the actual opening so the thick frame
        // cannot occlude the moon through orthographic parallax.
        outside.transform.position=new Vector3(-1.8f,1.78f,2.395f);
        // The rounded box uses face-dependent UVs; use an upright XY panorama
        // instead so trees, sky and moon remain correctly oriented.
        var panorama=new Mesh{name="Upright forest window"};
        panorama.vertices=new[]{new Vector3(-.95f,-.975f,0),new Vector3(.95f,-.975f,0),new Vector3(-.95f,.975f,0),new Vector3(.95f,.975f,0)};
        panorama.uv=new[]{Vector2.zero,Vector2.right,Vector2.up,Vector2.one};panorama.triangles=new[]{0,2,1,1,2,3};panorama.RecalculateNormals();panorama.RecalculateBounds();
        AssetDatabase.CreateAsset(panorama,root+"/Meshes/forest-window-plane.asset");outside.GetComponent<MeshFilter>().sharedMesh=panorama;
        var forest=new Material(Shader.Find("Yamyam/Forest Window"));
        forest.SetFloat("_DayAmount",0);
        AssetDatabase.CreateAsset(forest,root+"/Materials/forest-window.mat");
        outside.GetComponent<Renderer>().sharedMaterial=forest;
        outside.GetComponent<Renderer>().shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;
        room.atmosphere.outsideMaterial=forest;
        room.memo=room.gameObject.AddComponent<LofiMemo>();
        room.gameObject.AddComponent<LofiWebBridge>();
    }
}

using UnityEngine;
namespace Yamyam.OriginalTechTwelve.Sand {
    public class SandLesson:MonoBehaviour {
        public string mode="smooth-surface";
        public Material material;public Texture2D averaged,preserved;
        public Camera duneView,detailView;
        public bool livePlayback=true;public float elapsed;public SandState current;
        void Update(){if(livePlayback){elapsed=(elapsed+Time.deltaTime)%12;Apply(elapsed);}}
        public void Apply(float t){
            current=SandModel.Sample(mode,t);material.SetFloat("_Grain",current.grain);material.SetFloat("_Glitter",current.glitter);material.SetFloat("_ViewGlitter",current.viewGlitter);material.SetFloat("_GrazingMask",current.grazingMask);material.SetFloat("_Broad",current.broad);
            material.SetTexture("_GrainTex",current.preserveMipDistribution?preserved:averaged);
            duneView.transform.position=new Vector3(current.cameraX,current.cameraY,current.cameraZ);duneView.transform.LookAt(new Vector3(0,.2f,1));
            detailView.transform.position=new Vector3(current.cameraX*.25f,1.7f,-4);detailView.transform.LookAt(new Vector3(0,.2f,0));
        }
    }
}

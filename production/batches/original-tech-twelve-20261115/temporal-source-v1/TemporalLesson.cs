using UnityEngine;
namespace Yamyam.OriginalTechTwelve.Temporal {
    public class TemporalLesson:MonoBehaviour {
        public string mode="no-aa";public Camera fullView,detailView;public Transform occluder;public bool livePlayback=true;public float elapsed;public TemporalState current;
        void Update(){if(livePlayback){elapsed=(elapsed+Time.deltaTime)%12;Apply(elapsed);}}
        public void Apply(float t){current=TemporalSceneModel.Sample(mode,t);occluder.position=new Vector3(current.cubeX,1.5f,-.7f);foreach(var c in new[]{fullView,detailView}){c.transform.position=new Vector3(current.cameraX,1.65f,-7);c.transform.LookAt(new Vector3(0,1.5f,1));}}
    }
}

using UnityEngine;
namespace Yamyam.OriginalTechTwelve.Camera {
    public class CameraLesson:MonoBehaviour {
        public string mode="follow";
        public Transform hero,rigIndicator;
        public UnityEngine.Camera playerView,observerView;
        public LineRenderer viewLine,orbitTrail;
        public AnimationClip walk,idle;
        public bool livePlayback=true;
        public float elapsed;
        public CameraState current;
        void Update(){if(livePlayback){elapsed=(elapsed+Time.deltaTime)%12;Apply(elapsed);}}
        public void Apply(float t){
            current=CameraModel.Sample(mode,t);
            var anim=mode=="follow"?walk:idle;
            if(anim)anim.SampleAnimation(hero.gameObject,t%anim.length);
            hero.position=new Vector3(current.heroX,0,current.heroZ);
            hero.rotation=mode=="follow"?Quaternion.Euler(0,90,0):Quaternion.identity;
            playerView.transform.position=new Vector3(current.cameraX,current.cameraY,current.cameraZ);
            playerView.transform.LookAt(new Vector3(current.lookX,current.lookY,current.lookZ));
            playerView.fieldOfView=current.fieldOfView;
            rigIndicator.position=playerView.transform.position;
            rigIndicator.rotation=playerView.transform.rotation;
            viewLine.SetPosition(0,rigIndicator.position);
            viewLine.SetPosition(1,new Vector3(current.lookX,current.lookY,current.lookZ));
            for(int i=0;i<65;i++){
                float angle=Mathf.Lerp(-55,55,i/64f)*Mathf.Deg2Rad;
                orbitTrail.SetPosition(i,new Vector3(current.heroX+6*Mathf.Sin(angle),.03f,-6*Mathf.Cos(angle)));
            }
            orbitTrail.enabled=mode=="orbit"||mode=="orbit-limit";
        }
    }
}

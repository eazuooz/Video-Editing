using UnityEngine;
namespace Yamyam.OriginalTechTwelve.Placement {
    public class PlacementLesson:MonoBehaviour {
        public string mode="all-candidates";
        public Camera forestView,mapView;
        public Transform[] trees,dots,grass;
        public bool livePlayback=true;public float elapsed;public PlacementState current;
        public void Initialize(){current=PlacementModel.Build(mode);Apply(0);}
        void Start(){Initialize();}
        void Update(){if(livePlayback){elapsed=(elapsed+Time.deltaTime)%12;Apply(elapsed);}}
        public void Apply(float t){
            if(current==null)current=PlacementModel.Build(mode);
            bool reveal=t>=3;
            for(int i=0;i<trees.Length;i++){trees[i].gameObject.SetActive(reveal&&current.points[i].accepted);dots[i].gameObject.SetActive(!reveal||!current.points[i].accepted);}
            foreach(var g in grass)g.gameObject.SetActive(reveal&&current.secondLayer);
            float angle=Mathf.Lerp(-12,12,Mathf.Clamp01(t/12))*Mathf.Deg2Rad;
            forestView.transform.position=new Vector3(17*Mathf.Sin(angle)+7,12,-17*Mathf.Cos(angle));forestView.transform.LookAt(new Vector3(0,1,0));
        }
    }
}

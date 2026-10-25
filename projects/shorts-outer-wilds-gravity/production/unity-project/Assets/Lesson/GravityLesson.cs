using UnityEngine;
using System.Collections.Generic;

namespace YamyamCoding.GravityLesson {
// Numeric values are a teaching model. They are not extracted Outer Wilds constants.
[ExecuteAlways]
public sealed class Demo : MonoBehaviour {
    [Range(0,1)] public float previewPhase;
    float previousPreview=-1;
    void Update(){if(redPath!=null&&greenPath!=null&&previewPhase!=previousPreview)Tick(previewPhase);}
    public Camera observer; public Transform redBall,greenBall; public LineRenderer redTrail,greenTrail;
    public float radius=2, surfaceGravity=2.5f, launchSpeed=3.5f;
    public float redDistance,greenDistance; public bool greenReturned;
    Vector3[] redPath,greenPath;
    void OnEnable(){if(redBall&&greenBall){redPath=Simulate(2,-4);greenPath=Simulate(1,4);}}
    public static Demo Build(){
        var d=new GameObject("Gravity falloff — one-variable comparison").AddComponent<Demo>();
        d.observer=new GameObject("Observer camera").AddComponent<Camera>();d.observer.transform.position=new Vector3(0,2,-30);d.observer.transform.LookAt(new Vector3(0,2,0));d.observer.orthographic=true;d.observer.orthographicSize=8.4f;d.observer.clearFlags=CameraClearFlags.SolidColor;d.observer.backgroundColor=Color.black;
        RenderSettings.ambientLight=new Color(.5f,.5f,.5f);var light=new GameObject("Key light").AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.3f;light.transform.rotation=Quaternion.Euler(40,-30,0);
        for(int k=0;k<2;k++){
            float x=k==0?-4:4;var planet=GameObject.CreatePrimitive(PrimitiveType.Sphere);planet.name=k==0?"Reference planet — inverse square":"Comparison planet — slower falloff";planet.transform.position=new Vector3(x,-3,0);planet.transform.localScale=Vector3.one*4;planet.GetComponent<Renderer>().sharedMaterial=Mat("Rock",new Color(.22f,.35f,.38f));
            // Landmarks make rotation and surface position legible; no vendor asset required.
            for(int j=0;j<18;j++){float a=j*2*Mathf.PI/18;var p=GameObject.CreatePrimitive(PrimitiveType.Cube);p.name="Surface marker";p.transform.position=new Vector3(x+Mathf.Sin(a)*2,-3+Mathf.Cos(a)*2,0);p.transform.localScale=new Vector3(.12f,.28f,.16f);p.transform.rotation=Quaternion.Euler(0,0,-a*Mathf.Rad2Deg);p.GetComponent<Renderer>().sharedMaterial=Mat("Marker",new Color(.55f,.67f,.51f));}
            var ball=GameObject.CreatePrimitive(PrimitiveType.Sphere);ball.transform.localScale=Vector3.one*.32f;ball.GetComponent<Renderer>().sharedMaterial=Mat("Probe",k==0?new Color(.95f,.3f,.3f):new Color(.4f,.95f,.6f));if(k==0)d.redBall=ball.transform;else d.greenBall=ball.transform;
            var line=new GameObject("Computed trajectory").AddComponent<LineRenderer>();line.sharedMaterial=new Material(Shader.Find("Sprites/Default"));line.startColor=line.endColor=k==0?new Color(.95f,.3f,.3f):new Color(.4f,.95f,.6f);line.startWidth=line.endWidth=.055f;if(k==0)d.redTrail=line;else d.greenTrail=line;
        }
        d.redPath=d.Simulate(2,-4);d.greenPath=d.Simulate(1,4);d.Tick(0);return d;
    }
    Vector3[] Simulate(float exponent,float x){
        var p=new List<Vector3>();float r=radius,v=launchSpeed;const float dt=1f/240;int frames=60*14;
        for(int f=0;f<frames;f++){p.Add(new Vector3(x,-3+r,0));for(int sub=0;sub<4;sub++){v-=surfaceGravity*Mathf.Pow(radius/r,exponent)*dt;r+=v*dt;if(r<radius){r=radius;v=0;}}}return p.ToArray();
    }
    public void Tick(float phase){previewPhase=previousPreview=Mathf.Clamp01(phase);int n=Mathf.Clamp(Mathf.RoundToInt(Mathf.Clamp01(phase)*(redPath.Length-1)),0,redPath.Length-1);redBall.position=redPath[n];greenBall.position=greenPath[n];redDistance=redBall.position.y+3;greenDistance=greenBall.position.y+3;greenReturned=n>5&&greenDistance<=radius+.001f;
        Trace(redTrail,redPath,n);Trace(greenTrail,greenPath,n);
    }
    static void Trace(LineRenderer line,Vector3[] all,int n){line.positionCount=n+1;for(int i=0;i<=n;i++)line.SetPosition(i,all[i]);}
    static Material Mat(string name,Color c){var m=new Material(Shader.Find("Standard"));m.name=name;m.color=c;m.SetFloat("_Glossiness",.03f);return m;}
}
}

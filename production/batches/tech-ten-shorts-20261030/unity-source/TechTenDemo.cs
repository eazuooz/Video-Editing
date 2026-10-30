using System;
using System.Collections.Generic;
using UnityEngine;

namespace Yamyam.TechTen {
 // Small, independently authored teaching implementations. Never commercial debug data.
 public sealed partial class TechTenDemo:MonoBehaviour {
  public string topic; public int stage; public float elapsed;
  public string actionKind=""; public float actionStartSeconds, actionResumeSeconds;
  public TextMesh[] valueLabels;
  public Camera shot,contactCamera; public Transform[] actors,props; public LineRenderer[] lines;
  public Material[] effects; public MeshFilter dynamicSurface; public AnimationClip walk;
  public float lastFillNormalY, lastMaskEnabled, lastGap, lastRopeLength;
  public int firedCount; public bool collisionBypassed;
  float[] snow; Vector3[] baseVertices; int snowFrame=-1;
  RenderTexture contactTarget;Texture2D contactPixels;
  Vector3[] ropeNow,ropeOld;int ropeFrame=-1;
  float[] nextShot,lastShot;System.Random[] shotRandom;int marineFrame=-1;
  static readonly Color Teal=new Color(.32f,.86f,.77f),Yellow=new Color(1,.81f,.25f);
  public void Sample(float seconds) {
   elapsed=seconds;
   switch(topic) {
    case "alyx-liquid-shader": Bottle(); break;
    case "batman-origins-snow-below-camera": Snow(); break;
    case "sea-of-thieves-water-masking": Water(); break;
    case "uncharted3-fixed-plane-scrolling-desert": Plane(); break;
    case "uncharted4-taut-rope-fallback": Rope(); break;
    case "starcraft-worker-mineral-walk": Workers(); break;
    case "starcraft2-marine-random-firing-delay": Marines(); break;
   }
  }
  void Bottle() {
   float angle=Mathf.Sin(elapsed*.9f)*52;
   for(int i=0;i<actors.Length;i++) {
    var b=actors[i];b.rotation=Quaternion.Euler(0,0,angle);
    bool horizontal=stage!=0 && (stage!=2||i==1);
    Vector3 normal=horizontal?Vector3.up:b.up;
    effects[i*2].SetFloat("_ClipEnabled",1);
    effects[i*2].SetVector("_Plane",new Vector4(normal.x,normal.y,normal.z,-Vector3.Dot(normal,b.position)));
    props[i].position=b.position;props[i].rotation=Quaternion.FromToRotation(Vector3.forward,normal);
    effects[i*2+1].SetMatrix("_WorldToBottle",b.worldToLocalMatrix);
    if(lines.Length>i){var l=lines[i];l.enabled=stage>0;l.SetPositions(new[]{b.position-Vector3.right*.8f,b.position+Vector3.right*.8f});}
    lastFillNormalY=normal.y;
   }
  }
  void Snow() {
   var mesh=dynamicSurface.mesh;
   if(baseVertices==null){baseVertices=mesh.vertices;snow=new float[baseVertices.Length];}
   if(!contactTarget){contactTarget=new RenderTexture(194,98,24,RenderTextureFormat.ARGB32);contactTarget.Create();contactPixels=new Texture2D(194,98,TextureFormat.RGB24,false);contactCamera.targetTexture=contactTarget;contactCamera.SetReplacementShader(Shader.Find("Yamyam/TechTen/ContactCapture"),"");}
   // Only the thin slice at the surface is captured, not the whole boot.
   contactCamera.transform.position=new Vector3(0,-.8f,0);contactCamera.nearClipPlane=.915f;contactCamera.farClipPlane=.97f;
   int now=Mathf.FloorToInt(elapsed*60);
   if(now<snowFrame){Array.Clear(snow,0,snow.Length);snowFrame=-1;}
   for(int f=snowFrame+1;f<=now;f++) {
    float t=f/60f;float travel=Mathf.Repeat(t*1.1f,12);float x=Mathf.PingPong(t*1.1f,6)-3;actors[0].position=new Vector3(x,.12f,0);if(walk)walk.SampleAnimation(actors[0].gameObject,t%walk.length);actors[0].rotation=Quaternion.Euler(0,travel<6?90:-90,0);
    contactCamera.Render();var previous=RenderTexture.active;RenderTexture.active=contactTarget;contactPixels.ReadPixels(new Rect(0,0,194,98),0,0);contactPixels.Apply();RenderTexture.active=previous;
    // Looking upward with +Z as screen-up makes screen-right point toward -X.
    bool accumulate=stage>0 && !(actionKind=="accumulation-toggle"&&t>=actionStartSeconds&&t<actionResumeSeconds);
    for(int n=0;n<snow.Length;n++){Vector3 v=baseVertices[n];float u=(4-v.x)/8,uv=(v.z+2)/4;float mask=contactPixels.GetPixelBilinear(u,uv).r;snow[n]=accumulate?Mathf.Max(snow[n],mask*.12f):mask*.12f;}
   }
   snowFrame=now;
   Vector3[] vertices=new Vector3[baseVertices.Length];
   for(int i=0;i<vertices.Length;i++){vertices[i]=baseVertices[i];vertices[i].y-=snow[i];}
   mesh.vertices=vertices;mesh.RecalculateNormals();mesh.RecalculateBounds();
   float px=Mathf.PingPong(elapsed*1.1f,6)-3;actors[0].position=new Vector3(px,.12f,0);
   if(walk)walk.SampleAnimation(actors[0].gameObject,elapsed%walk.length);actors[0].rotation=Quaternion.Euler(0,Mathf.Repeat(elapsed*1.1f,12)<6?90:-90,0);
   // Real isolated orthographic ankle-slab camera; accumulate its contact mask.
   if(props.Length>0)props[0].gameObject.SetActive(stage==1);
   if(effects!=null&&effects.Length==2)dynamicSurface.GetComponent<Renderer>().sharedMaterial=effects[stage==1?1:0];
   if(stage==1){foreach(var r in FindObjectsByType<Renderer>(FindObjectsSortMode.None))if(r.name=="Dark teaching stage"||r.name.StartsWith("GridX")||r.name.StartsWith("GridZ"))r.enabled=false;shot.transform.position=new Vector3(7,3,-8);shot.transform.LookAt(new Vector3(0,.2f,0));}
   foreach(var line in lines)line.enabled=stage==1;
   lastGap=Max(snow);
  }
  static float Max(float[] a){float r=0;foreach(float x in a)r=Mathf.Max(r,x);return r;}
  void Water() {
   float actionTime=elapsed-actionStartSeconds;
   bool enabled=stage>0&&(actionKind!="mask-on"||actionTime>=0);effects[0].SetFloat("_WaterMask",enabled?1:0);lastMaskEnabled=enabled?1:0;
   float wave=Mathf.Sin(elapsed*1.4f)*.055f;props[0].position=new Vector3(0,.67f+wave,0);
   props[1].gameObject.SetActive(stage==2);if(stage==2)props[1].position=new Vector3(0,Mathf.Lerp(.08f,.56f,Mathf.Clamp01((actionKind=="flood-rise"?actionTime:elapsed)/5)),0);
   for(int i=0;i<lines.Length;i++){lines[i].enabled=stage>0;}
   // The mask is the sole changed condition: retain identical framing for A/B.
   shot.transform.position=new Vector3(6,6,-9);shot.transform.LookAt(new Vector3(0,.5f,0));
  }
  void Plane() {
   PlaneSample();
  }
  void Rope() {
   Vector3 a=new Vector3(-3,2,-.75f),b=RopeEnd(elapsed);
   actors[0].position=a;actors[1].position=b;
   var path=WrappedPath(a,b,.78f);lastRopeLength=0;
   for(int i=1;i<path.Count;i++)lastRopeLength+=Vector3.Distance(path[i-1],path[i]);
   lines[0].positionCount=path.Count;lines[0].SetPositions(path.ToArray());lines[0].enabled=stage>0;
   const int count=40;int frame=Mathf.FloorToInt(elapsed*60);
   bool risk=actionKind=="rope-risk",fallback=actionKind=="rope-fallback";
   int actionFrame=Mathf.CeilToInt(actionStartSeconds*60-.00001f);
   if(ropeNow==null||frame<ropeFrame){ropeFrame=-1;ropeNow=new Vector3[count];ropeOld=new Vector3[count];var initial=fallback?new List<Vector3>{a,RopeEnd(0)}:WrappedPath(a,RopeEnd(0),.8f);for(int i=0;i<count;i++){ropeNow[i]=Along(initial,i/(count-1f));ropeOld[i]=ropeNow[i];}}
   for(int f=ropeFrame+1;f<=frame;f++){
    Vector3 end=RopeEnd(f/60f);
    // Deliberate teaching failure, then our simple restoration from the parallel
    // collision-safe route. This is not the undisclosed commercial recovery code.
    if((risk||fallback)&&f==actionFrame){var reset=risk?new List<Vector3>{a,end}:WrappedPath(a,end,.8f);for(int i=0;i<count;i++){ropeNow[i]=Along(reset,i/(count-1f));ropeOld[i]=ropeNow[i];}}
    bool allowPenetration=(risk&&f>=actionFrame)||(fallback&&f<actionFrame);
    for(int i=1;i<count-1;i++){Vector3 prev=ropeNow[i];ropeNow[i]+=(ropeNow[i]-ropeOld[i])*.992f+Vector3.down*(9.81f/3600);ropeOld[i]=prev;}
    for(int pass=0;pass<28;pass++){
     ropeNow[0]=a;ropeNow[count-1]=end;
     for(int i=1;i<count;i++){Vector3 delta=ropeNow[i]-ropeNow[i-1];float d=delta.magnitude;Vector3 adjust=delta*(1-(8.0f/(count-1))/Mathf.Max(d,.0001f))*.5f;if(i>1)ropeNow[i-1]+=adjust;if(i<count-1)ropeNow[i]-=adjust;}
     for(int i=1;i<count-1;i++){Vector3 p=ropeNow[i];if(!allowPenetration&&Mathf.Abs(p.x)<.8f&&Mathf.Abs(p.z)<.8f){if(.8f-Mathf.Abs(p.x)<.8f-Mathf.Abs(p.z))p.x=(p.x<0?-1:1)*.8f;else p.z=(p.z<=0?-1:1)*.8f;}p.y=Mathf.Max(p.y,.08f);ropeNow[i]=p;}
    }
   }
   ropeFrame=frame;lines[1].positionCount=count;lines[1].SetPositions(ropeNow);
   for(int i=0;i<props.Length;i++){props[i].gameObject.SetActive(stage==0);props[i].position=ropeNow[i];}
  }
  Vector3 RopeEnd(float seconds){
   // The disclosed parallel system preserves a collision-safe wrapped route.
   // It is not evidence of an endpoint-distance clamp in the commercial game.
   return new Vector3(3,2,Mathf.Lerp(-.75f,1.7f,.5f+.5f*Mathf.Sin(seconds*.7f)));
  }
  static List<Vector3> WrappedPath(Vector3 a,Vector3 b,float radius) {
   // This testbed has endpoints on opposite sides of one square pillar. Keep
   // the lower winding established at the first frame, rather than jumping to
   // another side when the shortest path changes. Both corner offsets lie
   // outside the real collider footprint (.75 units).
   float leftZ=Mathf.Lerp(a.z,b.z,(-radius-a.x)/(b.x-a.x));
   float rightZ=Mathf.Lerp(a.z,b.z,(radius-a.x)/(b.x-a.x));
   if(Mathf.Max(leftZ,rightZ)<=-radius||Mathf.Min(leftZ,rightZ)>=radius)return new List<Vector3>{a,b};
   return new List<Vector3>{a,new Vector3(-radius,2,-radius),new Vector3(radius,2,-radius),b};
  }
  static Vector3 Along(List<Vector3> p,float u){float len=0;for(int i=1;i<p.Count;i++)len+=Vector3.Distance(p[i-1],p[i]);float d=u*len;for(int i=1;i<p.Count;i++){float l=Vector3.Distance(p[i-1],p[i]);if(d<=l)return Vector3.Lerp(p[i-1],p[i],d/Mathf.Max(l,.0001f));d-=l;}return p[p.Count-1];}
  void Workers() {
   if(stage==2){
    float stop=actionKind=="stop-scatter"?actionStartSeconds:1.5f;float spread=Mathf.SmoothStep(0,1,Mathf.Clamp01((elapsed-stop)/1.2f));collisionBypassed=elapsed<stop;
    for(int i=0;i<actors.Length;i++){float a=i*Mathf.PI*2/actors.Length;actors[i].position=Vector3.Lerp(new Vector3((i-1.5f)*.05f,0,0),new Vector3(Mathf.Cos(a),0,Mathf.Sin(a))*.9f,spread);}
   }else{
    collisionBypassed=stage>0&&(actionKind!="harvest-on"||elapsed>=actionStartSeconds);float x=Mathf.Lerp(-3,3,Mathf.Clamp01(elapsed/5));
    if(actionKind=="harvest-on"&&collisionBypassed)x=Mathf.Min(3,-.72f+(elapsed-actionStartSeconds)*1.2f);
    for(int i=1;i<actors.Length;i++)actors[i].position=new Vector3(0,0,(i-2)*.9f);
    if(!collisionBypassed)for(int i=1;i<actors.Length;i++)if(Mathf.Abs(actors[i].position.z)<.72f)x=Mathf.Min(x,actors[i].position.x-.72f);
    actors[0].position=new Vector3(x,0,0);
   }
   lines[0].enabled=collisionBypassed;lines[0].SetPositions(new[]{actors[0].position+Vector3.up*.9f,new Vector3(3,.1f,0)});
   // State-controlled stop/pass is a deliberately one-dimensional collision illustration.
  }
  void Marines() {
   int frame=Mathf.FloorToInt(elapsed*60);
   if(nextShot==null||frame<marineFrame){marineFrame=-1;nextShot=new float[actors.Length];lastShot=new float[actors.Length];shotRandom=new System.Random[actors.Length];for(int i=0;i<actors.Length;i++){lastShot[i]=-10;shotRandom[i]=new System.Random(1000+i);}}
   for(int f=marineFrame+1;f<=frame;f++)for(int i=0;i<actors.Length;i++)if(f/60f>=nextShot[i]){bool vary=stage!=0&&(stage!=2||i%4>=2);lastShot[i]=nextShot[i];float jitter=(float)(shotRandom[i].NextDouble()*2-1)*.02f;if(f==0&&i==2)jitter=-.02f;if(f==0&&i==3)jitter=.02f;nextShot[i]=lastShot[i]+1f+(vary?jitter:0);}
   marineFrame=frame;
   firedCount=0;
   for(int i=0;i<actors.Length;i++) {
    bool vary=stage!=0 && (stage!=2||i%4>=2);
    float period=nextShot[i]-lastShot[i],local=elapsed-lastShot[i];bool flash=local<.07f;
    props[i].gameObject.SetActive(flash);if(flash)firedCount++;
    float recoil=flash?-.04f:0;actors[i].localPosition=new Vector3((i%4-1.5f)*1.15f,0,(i/4-1)*1.25f+recoil);
    if(lines.Length>i){lines[i].enabled=stage>0;lines[i].SetPositions(new[]{actors[i].position+Vector3.up*1.3f,actors[i].position+Vector3.up*(1.3f+local/period*.65f)});}
   }
   if(valueLabels!=null)for(int i=0;i<valueLabels.Length;i++){int actorIndex=new[]{0,2,3}[i];var label=valueLabels[i];label.gameObject.SetActive(stage==2);label.text=(nextShot[actorIndex]-lastShot[actorIndex]).ToString("F2",System.Globalization.CultureInfo.InvariantCulture)+" s";label.transform.position=actors[actorIndex].position+Vector3.up*2.1f;label.transform.rotation=shot.transform.rotation;}
   // Seeded per-shot jitter demonstrates desynchronization; these are illustrative parameters, not measured SC2 values.
  }
 }
}

using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

using YamyamCoding.GameMath.EulerAxisAngle.V6;
namespace YamyamCoding.GameMath.EulerAxisAngle.V7
{
    [Serializable] public class V6PoseKey
    {
        public float t;
        public Vector3 value, position;
        public Vector3 scale = Vector3.one;
    }
    [Serializable] public class V6RotationStep
    {
        public string space = "upright";
        public Vector3 axis = Vector3.up;
        public float degrees, start, end = 1;
    }
    [Serializable] public class V6Program
    {
        public string kind = "euler";
        public Vector3 initialEuler;
        public V6PoseKey[] keys;
        public V6RotationStep[] steps;
        public bool linear;
        public Vector3 axis;
        public bool hasAxis;
    }
    [Serializable] public class V6Shot
    {
        public string sceneId, id, model = "aircraft", activeAxis = "none";
        public bool pair, axes = true, gimbals;
        public V6Program a, b;
        public float motionSeconds = 5;
        public Vector3 cameraPosition = new Vector3(7,4.5f,8);
        public Vector3 cameraEndPosition;
        public bool moveCamera;
        public Vector3 customAxis = Vector3.up;
        public float arcDegrees = 90;
    }
    [Serializable] public class V6Catalog { public V6Shot[] shots; }

    /// <summary>Independent V6 testbed. Detailed geometry is reused as source,
    /// rebuilt in native +Z-forward coordinates, never relabeled V5 pixels.
    /// All matrix/anchor values are left-handed ROW object-to-upright.</summary>
    public sealed class EulerV7PanelScene : MonoBehaviour
    {
        public string sceneId="v6-01", selectedShotId="v6-01.B01";
        public TextAsset shotCatalog;
        [Range(0,1)] public float normalizedTime;
        public bool playInRuntime;
        public Color background=new Color32(8,11,13,255);
        public V6Shot shot;
        [SerializeField] private Transform generated, aircraftA, aircraftB, fixedA, fixedB;
        [SerializeField] private Camera captureCamera;
        public Camera SceneCamera=>captureCamera;
        public Matrix4x4 RowA{get;private set;}=Matrix4x4.identity;
        public Matrix4x4 RowB{get;private set;}=Matrix4x4.identity;
        private readonly List<Material> ownedMaterials=new List<Material>();
        private readonly Dictionary<string,Material> materialCache=new Dictionary<string,Material>();
        private readonly List<Mesh> ownedMeshes=new List<Mesh>();
        [SerializeField] private List<AxisLabel> labels=new List<AxisLabel>();
        [SerializeField] private Transform headingRing,pitchRing,bankRing,activeGuide,axisAngleA,axisAngleB;
        [SerializeField] private LineRenderer activeArc,axisAngleArcA,axisAngleArcB;
        private float started;
        private Vector3 focusA,focusB;
        private static readonly Color AxisX=new Color32(239,90,99,255);
        private static readonly Color AxisY=new Color32(108,206,142,255);
        private static readonly Color AxisZ=new Color32(115,172,245,255);
        public const int Width=1920,Height=1080,Fps=60;
        private float BodyAxisLength=>shot.pair?2.35f:2.7f;
        private float UprightAxisLength=>shot.pair?2.30f:2.65f;
        [Serializable] private class AxisLabel { public string name; public TextMesh text; public TextMesh[] outline; public LineRenderer leader; public Transform frame; public Vector3 endpoint; public Vector2 pixel; }

        private void Start()
        {
            started=Time.time;
            if(shot==null||shot.a==null)LoadShot(selectedShotId);
            if(generated==null||captureCamera==null||aircraftA==null)Build();
            Evaluate(normalizedTime);
        }
        private void Update()
        {if(playInRuntime&&shot!=null)Evaluate(Mathf.Clamp01((Time.time-started)/Mathf.Max(.1f,shot.motionSeconds)));}
        public void LoadShot(string id)
        {
            if(shotCatalog==null)throw new InvalidOperationException("V6 shot catalog is required.");
            var c=JsonUtility.FromJson<V6Catalog>(shotCatalog.text);
            shot=Array.Find(c.shots,s=>s.id==id);
            if(shot==null)throw new InvalidOperationException("Unknown V6 shot "+id);
            selectedShotId=id;sceneId=shot.sceneId;
        }
        [ContextMenu("Load selected V6 shot and rebuild")]
        public void LoadSelectedAndBuild(){LoadShot(selectedShotId);Build();}
        public void PrimeTextGeometry()
        {
            // The first exported frame must use the same measured glyph size
            // as subsequent frames. This runs only in explicit Editor capture.
            RenderTexture previous=captureCamera.targetTexture;
            RenderTexture temporary=null;
            if(previous==null){temporary=RenderTexture.GetTemporary(16,9,24);captureCamera.targetTexture=temporary;}
            captureCamera.Render();Evaluate(normalizedTime);
            captureCamera.targetTexture=previous;
            if(temporary!=null)RenderTexture.ReleaseTemporary(temporary);
        }
        [ContextMenu("Build V6 editable testbed")]
        public void Build()
        {
            if(shot==null||shot.a==null)LoadShot(selectedShotId);
            ClearOwned();
            generated=NewObject("Generated V6 testbed",transform);
            captureCamera=NewObject("1920x1080 60fps orthographic camera",generated).gameObject.AddComponent<Camera>();
            captureCamera.clearFlags=CameraClearFlags.SolidColor;captureCamera.backgroundColor=background;
            captureCamera.orthographic=true;captureCamera.orthographicSize=shot.pair?4.25f:3.95f;
            captureCamera.aspect=Width/(float)Height;captureCamera.nearClipPlane=.05f;captureCamera.farClipPlane=80;
            captureCamera.allowHDR=false;captureCamera.allowMSAA=true;
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.38f,.41f,.45f);RenderSettings.ambientIntensity=.6f;RenderSettings.reflectionIntensity=0;
            SetCamera(shot.cameraPosition);
            var key=NewObject("Key light",generated).gameObject.AddComponent<Light>();
            key.type=LightType.Directional;key.intensity=1.05f;key.transform.rotation=Quaternion.Euler(38,-27,0);key.shadows=LightShadows.None;
            var fill=NewObject("Fill light",generated).gameObject.AddComponent<Light>();
            fill.type=LightType.Directional;fill.intensity=.55f;fill.transform.rotation=Quaternion.Euler(325,145,0);fill.shadows=LightShadows.None;
            Transform l,r,e,u;
            aircraftA=BuildModel("Aircraft A",out l,out r,out e,out u);
            if(shot.pair)aircraftB=BuildModel("Aircraft B",out l,out r,out e,out u);
            fixedA=NewObject("A upright frame; origin follows object",generated);BuildFrame(fixedA,UprightAxisLength,true);
            if(shot.pair){fixedB=NewObject("B upright frame; origin follows object",generated);BuildFrame(fixedB,UprightAxisLength,true);}
            fixedA.gameObject.SetActive(shot.axes);if(fixedB!=null)fixedB.gameObject.SetActive(shot.axes);
            if(shot.gimbals)
            {
                headingRing=NewObject("Heading ring; upright Y",generated);BuildRing(headingRing,Vector3.up,2.35f,AxisY,.025f);
                pitchRing=NewObject("Pitch ring; after heading X",generated);BuildRing(pitchRing,Vector3.right,2.12f,AxisX,.025f);
                bankRing=NewObject("Bank ring; after heading and pitch Z",generated);BuildRing(bankRing,Vector3.forward,1.90f,AxisZ,.025f);
            }
            if(shot.activeAxis!="none"&&!shot.a.hasAxis)
            {
                activeGuide=NewObject("Active rotation guide",generated);
                activeArc=NewObject("Progressive positive-angle arc",activeGuide).gameObject.AddComponent<LineRenderer>();
                activeArc.useWorldSpace=false;activeArc.widthMultiplier=.045f;activeArc.sharedMaterial=MakeMaterial(new Color32(243,154,75,255),true);
                activeArc.numCapVertices=4;activeArc.numCornerVertices=4;
            }
            if(shot.a!=null&&shot.a.hasAxis)axisAngleA=BuildAxisAngleGuide("A",shot.a,out axisAngleArcA);
            if(shot.pair&&shot.b!=null&&shot.b.hasAxis)axisAngleB=BuildAxisAngleGuide("B",shot.b,out axisAngleArcB);
            // Old small labels/leaders are omitted, never painted over geometry.
            Evaluate(normalizedTime);
        }
        private Transform BuildAxisAngleGuide(string name,V6Program program,out LineRenderer arc)
        {
            var guide=NewObject(name+" explicit signed axis-angle axis",generated);
            BuildArrow(guide,Vector3.zero,program.axis.normalized*(shot.pair?2.25f:2.6f),new Color32(243,154,75,255),.05f);
            arc=NewObject(name+" actual signed-angle arc",guide).gameObject.AddComponent<LineRenderer>();
            arc.useWorldSpace=false;arc.widthMultiplier=.035f;arc.sharedMaterial=MakeMaterial(new Color32(243,154,75,255),true);arc.numCapVertices=4;arc.numCornerVertices=4;return guide;
        }
        private static void UpdateAxisAngleArc(LineRenderer arc,V6Program program,float t)
        {
            if(arc==null)return;
            Vector3 o,s,v;Program(program,t,out o,out s,out v);Vector3 n=program.axis.normalized;
            float angle=Vector3.Dot(v,n)*Mathf.Rad2Deg;Vector3 u=Radial(n,Vector3.forward);
            const int count=97;arc.positionCount=count;
            for(int i=0;i<count;i++)arc.SetPosition(i,EulerV6Math.RowMultiply(u,EulerV6Math.AxisAngle(n,angle*i/(count-1)))*1.85f);
        }
        private static Vector3 Radial(Vector3 normal,Vector3 preferred)
        {
            Vector3 u=Vector3.ProjectOnPlane(preferred,normal);
            if(u.sqrMagnitude<1e-7f)u=Vector3.ProjectOnPlane(Vector3.up,normal);
            if(u.sqrMagnitude<1e-7f)u=Vector3.ProjectOnPlane(Vector3.right,normal);
            return u.normalized;
        }
        private Transform BuildModel(string name,out Transform l,out Transform r,out Transform e,out Transform u)
        {
            if(shot.model=="sail"||shot.model=="hook"||shot.model=="log")
            {
                l=r=e=u=null;return BuildMatchedObject(name);
            }
            if(shot.model=="wheel")
            {
                l=r=e=u=null;Transform t=NewObject(name,generated);
                Lathe("Rubber tire with central axle",t,new[]{-.18f,-.15f,.15f,.18f},new[]{1.38f,1.48f,1.48f,1.38f},new Color32(45,50,58,255));
                BuildRing(t,Vector3.forward,1.23f,new Color32(220,224,229,255),.09f);
                for(int i=0;i<8;i++){float a=i*Mathf.PI/4;Segment("Visible wheel spoke",t,Vector3.zero,new Vector3(Mathf.Cos(a),Mathf.Sin(a),0)*1.20f,Color.gray,.055f);}
                Ellipsoid("Axle",t,Vector3.zero,new Vector3(.32f,.32f,.45f),new Color32(244,188,51,255));
                Ellipsoid("Tracked rim mark",t,new Vector3(0,1.25f,.20f),new Vector3(.20f,.20f,.10f),new Color32(244,188,51,255));if(shot.axes)BuildFrame(t,BodyAxisLength,false);return t;
            }
            if(shot.model=="top")
            {
                l=r=e=u=null;Transform t=NewObject(name,generated);Transform shape=NewObject("Spinning top",t);
                Lathe("Tapered spinning-top body",shape,new[]{-1.35f,-.70f,-.10f,.15f,.35f,.60f},new[]{.03f,.35f,1.1f,1.15f,.80f,.18f},new Color32(244,188,51,255));
                shape.localRotation=Quaternion.AngleAxis(-90,Vector3.right);
                Segment("Recognizable top stem",t,new Vector3(0,.5f,0),new Vector3(0,1.4f,0),new Color32(37,49,64,255),.12f);
                Ellipsoid("Tracked top rim mark",t,new Vector3(.9f,.15f,0),new Vector3(.16f,.15f,.16f),new Color32(37,49,64,255));if(shot.axes)BuildFrame(t,BodyAxisLength,false);return t;
            }
            return BuildAircraft(name,Vector3.zero,out l,out r,out e,out u);
        }
        // Generic independently authored lesson objects. Their controlled angles
        // are not reconstructed Zelda engine values or extracted game assets.
        [SerializeField] private Transform matchedReference;
        private Transform BuildMatchedObject(string name)
        {
            Transform root=NewObject(name+" independent matched object",generated);
            Color wood=new Color32(134,88,49,255),dark=new Color32(68,44,29,255);
            Color rope=new Color32(205,177,124,255),cloth=new Color32(238,229,201,255);
            if(shot.model=="sail")
            {
                Segment("Separate wooden mast",root,new Vector3(0,-1.62f,0),new Vector3(0,1.62f,0),wood,.085f);
                Segment("Upper crossbar",root,new Vector3(-1.00f,1.12f,0),new Vector3(1.00f,1.12f,0),wood,.060f);
                Segment("Lower crossbar",root,new Vector3(-.94f,-.92f,0),new Vector3(.94f,-.92f,0),wood,.055f);
                const int cols=10,rows=12;
                var vertices=new List<Vector3>();var triangles=new List<int>();
                for(int y=0;y<=rows;y++)for(int x=0;x<=cols;x++)
                {
                    float u=x/(float)cols,v=y/(float)rows;
                    float width=Mathf.Lerp(.90f,.96f,v);
                    vertices.Add(new Vector3((u*2-1)*width,Mathf.Lerp(-.91f,1.10f,v),.04f+.28f*Mathf.Sin(u*Mathf.PI)*Mathf.Sin(v*Mathf.PI)));
                }
                // Separate back vertices retain proper opposing normals;
                // reverse triangles sharing front vertices would cancel them.
                int layer=vertices.Count;for(int i=0;i<layer;i++)vertices.Add(vertices[i]);
                for(int y=0;y<rows;y++)for(int x=0;x<cols;x++)
                {
                    int i=y*(cols+1)+x,j=i+cols+1;
                    triangles.AddRange(new[]{i,i+1,j,i+1,j+1,j,j+layer,i+1+layer,i+layer,j+layer,j+1+layer,i+1+layer});
                }
                CreateMesh("Curved cloth, visible from both sides",root,vertices.ToArray(),triangles.ToArray(),cloth);
                for(int side=-1;side<=1;side+=2)
                {
                    Segment("Tension rope",root,new Vector3(side*.98f,1.12f,.02f),new Vector3(side*.92f,-.92f,.02f),rope,.017f);
                    Segment("Mast supporting rope",root,new Vector3(0,1.57f,0),new Vector3(side*.95f,-.92f,.02f),rope,.014f);
                }
                for(int i=0;i<4;i++)
                {
                    float yy=i<2?1.12f:-.92f;
                    BuildRingAt(root,new Vector3(0,yy+(i%2)*.065f,0),Vector3.up,.105f,rope,.014f);
                }
                Ellipsoid("Mast base socket",root,new Vector3(0,-1.55f,0),new Vector3(.22f,.18f,.22f),dark);
            }
            else if(shot.model=="log")
            {
                BuildTimber(root,wood,dark,rope);
                matchedReference=NewObject("Stationary neighbor timber; independent of the manipulated log",generated);
                BuildTimber(matchedReference,new Color32(103,76,48,255),dark,rope);
            }
            else
            {
                Color steel=new Color32(183,194,204,255),edge=new Color32(101,120,135,255);
                // The opening is deliberately asymmetric, so changing its
                // orientation is visible instead of rotating a featureless ring.
                const int count=36;
                for(int i=0;i<count;i++)
                {
                    float a=Mathf.Lerp(-.20f*Mathf.PI,1.20f*Mathf.PI,i/(float)count);
                    float b=Mathf.Lerp(-.20f*Mathf.PI,1.20f*Mathf.PI,(i+1)/(float)count);
                    Segment("Open curved metal hook",root,new Vector3(Mathf.Cos(a)*.80f,Mathf.Sin(a)*.80f,0),new Vector3(Mathf.Cos(b)*.80f,Mathf.Sin(b)*.80f,0),steel,.11f);
                }
                Segment("Hook neck",root,new Vector3(-.65f,-.47f,0),new Vector3(-.65f,-1.4f,0),steel,.12f);
                Ellipsoid("Thick hook mount",root,new Vector3(-.65f,-1.4f,0),new Vector3(.52f,.27f,.40f),edge);
                for(float z=-.16f;z<=.17f;z+=.32f)Ellipsoid("Mount fastener",root,new Vector3(-.65f,-1.26f,z),new Vector3(.10f,.11f,.10f),steel);
                Ellipsoid("Visible open tip",root,new Vector3(Mathf.Cos(-.20f*Mathf.PI)*.80f,Mathf.Sin(-.20f*Mathf.PI)*.80f,0),new Vector3(.19f,.19f,.19f),edge);
            }
            if(shot.axes)BuildFrame(root,BodyAxisLength,false);
            return root;
        }
        private void BuildTimber(Transform root,Color wood,Color dark,Color rope)
        {
            Segment("Recognizable cylindrical timber",root,new Vector3(-1.5f,0,0),new Vector3(1.5f,0,0),wood,.32f);
            for(int side=-1;side<=1;side+=2)
            {
                Vector3 center=new Vector3(side*1.505f,0,0);
                BuildRingAt(root,center,Vector3.right,.24f,rope,.014f);
                BuildRingAt(root,center,Vector3.right,.13f,dark,.012f);
            }
            for(int i=0;i<9;i++)
            {
                float a=i*Mathf.PI*2/9;Vector3 q=new Vector3(0,Mathf.Cos(a),Mathf.Sin(a))*.324f;
                Segment("Lengthwise bark groove",root,q+Vector3.left*1.4f,q+Vector3.right*1.4f,dark,.014f);
            }
            foreach(float x in new[]{-.92f,.92f})BuildRingAt(root,new Vector3(x,0,0),Vector3.right,.34f,rope,.026f);
        }
        private void BuildRingAt(Transform parent,Vector3 center,Vector3 normal,float radius,Color color,float thickness)
        {
            Transform holder=NewObject("Functional ring / rope tie",parent);
            holder.localPosition=EulerV6Math.ToUnity(center);
            BuildRing(holder,normal,radius,color,thickness);
        }

        private void SetCamera(Vector3 pos)
        {captureCamera.transform.position=pos;captureCamera.transform.LookAt(new Vector3(0,-.15f,0),Vector3.up);}
        private static float Progress(float t,float a,float b,bool linear)
        {float v=Mathf.InverseLerp(a,b,t);return linear?v:v*v*(3-2*v);}
        private static Matrix4x4 Program(V6Program p,float t,out Vector3 offset,out Vector3 scale,out Vector3 value)
        {
            offset=Vector3.zero;scale=Vector3.one;value=Vector3.zero;
            if(p==null)return Matrix4x4.identity;
            if(p.keys!=null&&p.keys.Length>0)
            {
                V6PoseKey left=p.keys[0],right=left;
                for(int i=1;i<p.keys.Length;i++){right=p.keys[i];if(t<=right.t)break;left=right;}
                float u=right.t<=left.t?0:Progress(t,left.t,right.t,p.linear);
                value=Vector3.LerpUnclamped(left.value,right.value,u);offset=Vector3.LerpUnclamped(left.position,right.position,u);scale=Vector3.LerpUnclamped(left.scale,right.scale,u);
            }
            if(p.kind=="rotvec")return EulerV6Math.RotationVector(value);
            if(p.kind=="sequence")
            {
                Matrix4x4 result=EulerV6Math.HPB(p.initialEuler);
                if(p.steps!=null)foreach(var step in p.steps)
                {
                    Matrix4x4 delta=EulerV6Math.AxisAngle(step.axis,step.degrees*Progress(t,step.start,step.end,p.linear));
                    result=step.space=="body"?delta*result:result*delta;
                }
                return result;
            }
            return EulerV6Math.HPB(value);
        }
        public void Evaluate(float t)
        {
            normalizedTime=Mathf.Clamp01(t);if(shot==null||captureCamera==null)return;
            if(shot.moveCamera)SetCamera(Vector3.Lerp(shot.cameraPosition,shot.cameraEndPosition,Progress(t,0,1,false)));
            float depth=captureCamera.WorldToViewportPoint(Vector3.zero).z;
            focusA=captureCamera.ViewportToWorldPoint(new Vector3((shot.pair?535:650)/1920f,1-500/1080f,depth));
            focusB=captureCamera.ViewportToWorldPoint(new Vector3(1350/1920f,1-500/1080f,depth));
            Vector3 off,scale,value;RowA=Program(shot.a,t,out off,out scale,out value);
            aircraftA.position=focusA+off;aircraftA.rotation=EulerV6Math.UnityRotation(RowA);aircraftA.localScale=scale*(shot.pair?.78f:1f);
            if(matchedReference!=null){matchedReference.position=focusA+EulerV6Math.ToUnity(new Vector3(0,0,.68f));matchedReference.rotation=Quaternion.identity;}
            fixedA.position=aircraftA.position;fixedA.localScale=Vector3.one*(shot.pair?.78f:1f);
            if(aircraftB!=null){RowB=Program(shot.b,t,out off,out scale,out value);aircraftB.position=focusB+off;aircraftB.rotation=EulerV6Math.UnityRotation(RowB);aircraftB.localScale=scale*.78f;fixedB.position=aircraftB.position;fixedB.localScale=Vector3.one*.78f;}
            if(axisAngleA!=null){axisAngleA.position=aircraftA.position;axisAngleA.localScale=Vector3.one*(shot.pair?.78f:1f);}
            if(axisAngleB!=null){axisAngleB.position=aircraftB.position;axisAngleB.localScale=Vector3.one*.78f;}
            UpdateAxisAngleArc(axisAngleArcA,shot.a,t);UpdateAxisAngleArc(axisAngleArcB,shot.b,t);
            if(headingRing!=null)
            {
                Vector3 v;Program(shot.a,t,out off,out scale,out v);
                headingRing.position=pitchRing.position=bankRing.position=aircraftA.position;
                headingRing.localScale=pitchRing.localScale=bankRing.localScale=Vector3.one*(shot.pair?.78f:1f);
                pitchRing.rotation=EulerV6Math.UnityRotation(EulerV6Math.Ry(v.x));
                bankRing.rotation=EulerV6Math.UnityRotation(EulerV6Math.Rx(v.y)*EulerV6Math.Ry(v.x));
            }
            UpdateArc(t);UpdateLabels();
        }
        private void BuildFrame(Transform parent,float length,bool dashed)
        {
            Vector3[] axes={Vector3.right,Vector3.up,Vector3.forward};Color[] colors={AxisX,AxisY,AxisZ};
            for(int i=0;i<3;i++)
            {
                var axis=NewObject((dashed?"Upright ":"Body ")+"XYZ"[i],parent);
                if(dashed){for(int j=0;j<12;j++)Segment("Dashed axis",axis,axes[i]*(length*j/12f),axes[i]*(length*(j+.55f)/12f),colors[i],.014f);BuildArrow(axis,axes[i]*(length-.32f),axes[i]*length,colors[i],.018f);}
                else BuildArrow(axis,Vector3.zero,axes[i]*length,colors[i],.035f);
            }
        }
        private void UpdateArc(float t)
        {
            if(activeArc==null)return;
            Vector3 n=shot.customAxis;
            if(shot.activeAxis=="bodyX")n=EulerV6Math.RowMultiply(Vector3.right,RowA);
            if(shot.activeAxis=="bodyY")n=EulerV6Math.RowMultiply(Vector3.up,RowA);
            if(shot.activeAxis=="bodyZ")n=EulerV6Math.RowMultiply(Vector3.forward,RowA);
            if(shot.activeAxis=="uprightY")n=Vector3.up;
            if(shot.activeAxis=="pitchX")
            {
                Vector3 o,s,v;Program(shot.a,t,out o,out s,out v);
                n=EulerV6Math.RowMultiply(Vector3.right,EulerV6Math.Ry(shot.a.kind=="sequence"?shot.a.initialEuler.x:v.x));
            }
            n.Normalize();
            activeGuide.position=aircraftA.position;
            Vector3 offset,scale,value;Program(shot.a,t,out offset,out scale,out value);
            Vector3 preferred=Vector3.forward;
            if(shot.activeAxis=="pitchX")preferred=EulerV6Math.RowMultiply(Vector3.forward,EulerV6Math.Ry(value.x));
            if(shot.activeAxis=="bodyZ"&&shot.a.kind=="euler")preferred=EulerV6Math.RowMultiply(Vector3.up,EulerV6Math.Rx(value.y)*EulerV6Math.Ry(value.x));
            Vector3 u=Radial(n,preferred);
            float actualAngle=shot.arcDegrees*Mathf.Clamp01(t);
            if(shot.a.kind=="euler")actualAngle=shot.activeAxis=="uprightY"?value.x:shot.activeAxis=="pitchX"?value.y:shot.activeAxis=="bodyZ"?value.z:actualAngle;
            int count=72;activeArc.positionCount=count;
            for(int i=0;i<count;i++)activeArc.SetPosition(i,EulerV6Math.RowMultiply(u,EulerV6Math.AxisAngle(n,actualAngle*i/(count-1)))*2.25f);
        }
        private void CreateAxisLabels()
        {
            labels.Clear();if(!shot.axes)return;
            AddLabels("a",aircraftA,fixedA,shot.pair?new Vector2(190,285):new Vector2(190,290),shot.pair?new Vector2(790,285):new Vector2(950,290));
            if(aircraftB!=null)AddLabels("b",aircraftB,fixedB,new Vector2(1070,285),new Vector2(1680,285));
        }
        private void AddLabels(string prefix,Transform body,Transform upright,Vector2 left,Vector2 right)
        {
            Color[] colors={AxisX,AxisY,AxisZ};Vector3[] axes={Vector3.right,Vector3.up,Vector3.forward};
            for(int i=0;i<3;i++)for(int k=0;k<2;k++)
            {
                string text=(k==0?"upright ":"object ")+"XYZ"[i];var go=NewObject(prefix+" "+text,generated);
                TextMesh tm=go.gameObject.AddComponent<TextMesh>();tm.text=text;tm.fontSize=80;tm.characterSize=.10f;tm.anchor=TextAnchor.MiddleCenter;tm.alignment=TextAlignment.Center;tm.color=colors[i];
                tm.font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");go.GetComponent<MeshRenderer>().sharedMaterial=tm.font.material;
                tm.font.RequestCharactersInTexture(text,tm.fontSize,FontStyle.Normal);
                var outline=new TextMesh[8];
                for(int j=0;j<outline.Length;j++)
                {
                    var child=NewObject("Thin readability outline "+j,go).gameObject.AddComponent<TextMesh>();
                    child.text=text;child.fontSize=tm.fontSize;child.characterSize=tm.characterSize;child.anchor=tm.anchor;child.alignment=tm.alignment;child.font=tm.font;child.color=background;child.GetComponent<MeshRenderer>().sharedMaterial=tm.font.material;outline[j]=child;
                }
                var leader=NewObject("Leader to "+prefix+" "+text,generated).gameObject.AddComponent<LineRenderer>();leader.useWorldSpace=true;leader.positionCount=2;leader.widthMultiplier=.012f;leader.sharedMaterial=MakeMaterial(colors[i],true);
                labels.Add(new AxisLabel{name=prefix+"."+(k==0?"upright":"body")+"XYZ"[i],text=tm,outline=outline,leader=leader,frame=k==0?upright:body,endpoint=axes[i]*(k==0?UprightAxisLength:BodyAxisLength),pixel=(k==0?left:right)+new Vector2(0,i*150)});
            }
        }
        private void UpdateLabels()
        {
            foreach(var l in labels)
            {
                float depth=5f;
                Vector3 pos=captureCamera.ViewportToWorldPoint(new Vector3(l.pixel.x/Width,1-l.pixel.y/Height,depth));
                l.text.transform.position=pos;l.text.transform.rotation=captureCamera.transform.rotation;
                // Camera-facing guides are annotations, not measured physical objects.
                float desiredHeight=shot.pair?32:36;
                var renderer=l.text.GetComponent<Renderer>();float h=renderer.localBounds.size.y;
                if(h>1e-5f)l.text.transform.localScale=Vector3.one*(desiredHeight*(captureCamera.orthographicSize*2/Height)/h);
                if(l.outline!=null)
                {
                    float pixelWorld=captureCamera.orthographicSize*2/Height/l.text.transform.localScale.x;
                    for(int i=0;i<l.outline.Length;i++){float a=i*Mathf.PI/4;l.outline[i].transform.localPosition=new Vector3(Mathf.Cos(a)*2.4f*pixelWorld,Mathf.Sin(a)*2.4f*pixelWorld,.02f/l.text.transform.localScale.x);}
                }
                Vector3 target=l.frame.TransformPoint(l.endpoint);Vector3 vp=captureCamera.WorldToViewportPoint(target);
                Vector3 projected=captureCamera.ViewportToWorldPoint(new Vector3(vp.x,vp.y,depth));
                l.leader.SetPosition(0,pos);l.leader.SetPosition(1,projected);
                l.leader.enabled=vp.z>0&&vp.x>=0&&vp.x<=1&&vp.y>=0&&vp.y<=1;
            }
        }
        [Serializable] public class Anchor {public string name;public Vector3 pixelTopLeft,positionInUpright,positionInScene;public bool inFrame;}
        [Serializable] public class FrameState
        {
            public string sceneId,shotId,handedness="left",vectorConvention="row",transform="object-to-upright";
            public string anchorSpace="positionInUpright removes the object origin and uniform presentation scale; positionInScene includes presentation placement",occlusion="Geometry uses real camera depth; leader/label is editorial overlay. No detector measurement.";
            public int frame,width=Width,height=Height,fps=Fps;public float normalizedTime,clipTimeSeconds,exampleTimeSeconds=-1;
            public bool hasEulerParametersA,hasEulerParametersB,hasRotationVectorA,hasRotationVectorB;
            public Vector3 eulerDegreesA,eulerDegreesB,rotationVectorRadiansA,rotationVectorRadiansB;
            public float[] rowMatrixA,rowMatrixB;public Anchor[] anchors;
        }
        public FrameState State(int frame,float t)
        {
            var all=new List<Anchor>();AddAnchors(all,"a",aircraftA,fixedA);if(aircraftB!=null)AddAnchors(all,"b",aircraftB,fixedB);
            Vector3 o,s,va,vb;Program(shot.a,t,out o,out s,out va);Program(shot.b,t,out o,out s,out vb);
            return new FrameState{sceneId=sceneId,shotId=shot.id,frame=frame,normalizedTime=t,clipTimeSeconds=frame/60f,exampleTimeSeconds=shot.model=="wheel"?t:-1,
                hasEulerParametersA=shot.a.kind=="euler",hasEulerParametersB=shot.b!=null&&shot.b.kind=="euler",hasRotationVectorA=shot.a.kind=="rotvec",hasRotationVectorB=shot.b!=null&&shot.b.kind=="rotvec",
                eulerDegreesA=shot.a.kind=="euler"?va:Vector3.zero,eulerDegreesB=shot.b!=null&&shot.b.kind=="euler"?vb:Vector3.zero,rotationVectorRadiansA=shot.a.kind=="rotvec"?va:Vector3.zero,rotationVectorRadiansB=shot.b!=null&&shot.b.kind=="rotvec"?vb:Vector3.zero,
                rowMatrixA=Flatten(RowA),rowMatrixB=Flatten(RowB),anchors=all.ToArray()};
        }
        private void AddAnchors(List<Anchor> list,string prefix,Transform body,Transform upright)
        {
            AddAnchor(list,prefix+".origin",body.position,body);AddAnchor(list,prefix+(shot.model=="aircraft"?".nose":".frontProbe"),body.TransformPoint(new Vector3(0,0,2.1f)),body);AddAnchor(list,prefix+".up",body.TransformPoint(Vector3.up),body);
            if(prefix=="a"&&matchedReference!=null){AddAnchor(list,"a.referenceOrigin",matchedReference.position,body);AddAnchor(list,"a.referenceEndA",matchedReference.TransformPoint(Vector3.left*1.5f),body);AddAnchor(list,"a.referenceEndB",matchedReference.TransformPoint(Vector3.right*1.5f),body);AddAnchor(list,"a.referenceUp",matchedReference.TransformPoint(Vector3.up*.34f),body);AddAnchor(list,"a.referenceDown",matchedReference.TransformPoint(Vector3.down*.34f),body);}
            if(prefix=="a"&&(shot.model=="sail"||shot.model=="log"||shot.model=="hook")){bool found=false;Bounds bounds=new Bounds();foreach(Renderer rr in generated.GetComponentsInChildren<Renderer>(true)){if(!rr.enabled||!rr.gameObject.activeInHierarchy)continue;if(!found){bounds=rr.bounds;found=true;}else bounds.Encapsulate(rr.bounds);}if(found){int corner=0;for(int x=-1;x<=1;x+=2)for(int y=-1;y<=1;y+=2)for(int z=-1;z<=1;z+=2)AddAnchor(list,"a.geometryCorner"+(corner++),bounds.center+Vector3.Scale(bounds.extents,new Vector3(x,y,z)),body);}}
            Vector3[] axes={Vector3.right,Vector3.up,Vector3.forward};
            for(int i=0;i<3;i++){AddAnchor(list,prefix+".body"+"XYZ"[i],body.TransformPoint(axes[i]*BodyAxisLength),body);AddAnchor(list,prefix+".upright"+"XYZ"[i],upright.TransformPoint(axes[i]*UprightAxisLength),body);}
        }
        private void AddAnchor(List<Anchor> list,string name,Vector3 p,Transform body)
        {Vector3 v=captureCamera.WorldToViewportPoint(p);list.Add(new Anchor{name=name,pixelTopLeft=new Vector3(v.x*Width,(1-v.y)*Height,v.z),positionInScene=p,positionInUpright=(p-body.position)/body.localScale.x,inFrame=v.z>0&&v.x>=0&&v.x<=1&&v.y>=0&&v.y<=1});}
        private static float[] Flatten(Matrix4x4 r)
        {float[] a=new float[9];for(int i=0;i<3;i++)for(int j=0;j<3;j++)a[i*3+j]=r[i,j];return a;}
        private static bool UsesSrp()=>GraphicsSettings.currentRenderPipeline!=null||GraphicsSettings.defaultRenderPipeline!=null||QualitySettings.renderPipeline!=null;
        private void ClearOwned()
        {
            if(generated!=null)DestroyOwnedObject(generated.gameObject);
            foreach(var m in ownedMeshes)if(m!=null)DestroyOwnedObject(m);
            foreach(var m in ownedMaterials)if(m!=null)DestroyOwnedObject(m);
            ownedMeshes.Clear();ownedMaterials.Clear();materialCache.Clear();labels.Clear();aircraftA=aircraftB=fixedA=fixedB=headingRing=pitchRing=bankRing=activeGuide=axisAngleA=axisAngleB=null;
            activeArc=axisAngleArcA=axisAngleArcB=null;
        }

        private Transform BuildAircraft(string label, Vector3 mathPosition, out Transform leftAileron,
            out Transform rightAileron, out Transform elevator, out Transform rudder)
        {
            Transform root = NewObject(label, generated);
            root.localPosition = EulerV6Math.ToUnity(mathPosition);
            Color fuselage = new Color32(244, 188, 51, 255);
            Color ivory = new Color32(220, 224, 229, 255);
            Color dark = new Color32(37, 49, 64, 255);
            Color canopy = new Color32(44, 72, 89, 255);
            float[] z = { -2.08f, -1.70f, -1.1f, -.5f, .25f, .85f, 1.45f, 1.86f, 2.08f };
            float[] r = { .04f, .13f, .22f, .28f, .31f, .29f, .21f, .10f, .025f };
            Lathe("Tapered rounded fuselage", root, z, r, fuselage);
            Ellipsoid("Dark cockpit canopy", root, new Vector3(0f, .27f, .45f), new Vector3(.43f, .30f, .93f), canopy);
            Ellipsoid("Cockpit rear frame", root, new Vector3(0f, .28f, .04f), new Vector3(.45f, .32f, .045f), dark);
            Ellipsoid("Nose cone", root, new Vector3(0f, 0f, 1.84f), new Vector3(.23f, .23f, .42f), dark);
            // Each wing has a tapered planform and actual thickness, not a cuboid.
            Wing("Port main wing", root, new[] { new Vector2(-.20f, .52f), new Vector2(-2.22f, -.10f),
                new Vector2(-2.12f, -.51f), new Vector2(-.21f, -.35f) }, .02f, .09f, ivory);
            Wing("Starboard main wing", root, new[] { new Vector2(.20f, .52f), new Vector2(.21f, -.35f),
                new Vector2(2.12f, -.51f), new Vector2(2.22f, -.10f) }, .02f, .09f, ivory);
            Wing("Port yellow wing-tip", root, new[] { new Vector2(-1.98f, -.03f), new Vector2(-2.22f, -.10f),
                new Vector2(-2.12f, -.51f), new Vector2(-1.96f, -.49f) }, .078f, .035f, fuselage);
            Wing("Starboard yellow wing-tip", root, new[] { new Vector2(1.98f, -.03f), new Vector2(1.96f, -.49f),
                new Vector2(2.12f, -.51f), new Vector2(2.22f, -.10f) }, .078f, .035f, fuselage);
            leftAileron = NewObject("Port hinged aileron", root);
            leftAileron.localPosition = EulerV6Math.ToUnity(new Vector3(-1.35f, .03f, -.36f));
            Wing("Port aileron panel", leftAileron, new[] { new Vector2(-.60f, 0f), new Vector2(.55f, .04f),
                new Vector2(.55f, -.12f), new Vector2(-.57f, -.15f) }, 0f, .065f, dark);
            rightAileron = NewObject("Starboard hinged aileron", root);
            rightAileron.localPosition = EulerV6Math.ToUnity(new Vector3(1.35f, .03f, -.36f));
            Wing("Starboard aileron panel", rightAileron, new[] { new Vector2(-.55f, .04f), new Vector2(.60f, 0f),
                new Vector2(.57f, -.15f), new Vector2(-.55f, -.12f) }, 0f, .065f, dark);
            Wing("Tailplane", root, new[] { new Vector2(-1.00f, -1.62f), new Vector2(-.12f, -1.35f),
                new Vector2(.12f, -1.35f), new Vector2(1.00f, -1.62f), new Vector2(.89f, -1.88f),
                new Vector2(-.89f, -1.88f) }, .14f, .065f, ivory);
            elevator = NewObject("Hinged elevator", root);
            elevator.localPosition = EulerV6Math.ToUnity(new Vector3(0f, .14f, -1.76f));
            Wing("Elevator trailing surface", elevator, new[] { new Vector2(-.87f, 0f), new Vector2(.87f, 0f),
                new Vector2(.81f, -.18f), new Vector2(-.81f, -.18f) }, 0f, .055f, fuselage);
            Fin("Vertical tail fin", root, new[] { new Vector2(.14f, -1.16f), new Vector2(.93f, -1.58f),
                new Vector2(.83f, -1.88f), new Vector2(.12f, -1.95f) }, .07f, ivory);
            rudder = NewObject("Hinged rudder", root);
            rudder.localPosition = EulerV6Math.ToUnity(new Vector3(0f, .15f, -1.80f));
            Fin("Rudder trailing surface", rudder, new[] { new Vector2(0f, 0f), new Vector2(.65f, .02f),
                new Vector2(.57f, -.15f), new Vector2(0f, -.15f) }, .075f, fuselage);
            Ellipsoid("Engine exhaust port", root, new Vector3(0f, .0f, -2.035f), new Vector3(.105f, .105f, .07f), dark);
            Ellipsoid("Visible engine intake", root, new Vector3(0f, -.17f, 1.10f), new Vector3(.24f, .11f, .37f), dark);
            // Seams and cabin frame give readable articulated construction at mobile size.
            Segment("Canopy center frame", root, new Vector3(0f, .422f, .14f), new Vector3(0f, .422f, .70f), dark, .022f);
            Segment("Port wing root seam", root, new Vector3(-.30f, .09f, .46f), new Vector3(-.30f, .09f, -.33f), dark, .015f);
            Segment("Starboard wing root seam", root, new Vector3(.30f, .09f, .46f), new Vector3(.30f, .09f, -.33f), dark, .015f);
            if (shot.axes)
            {
                Transform axes = NewObject("Moving body axes", root);
                BuildAxes(axes, BodyAxisLength, .038f, 1f);
            }
            return root;
        }

        private void Lathe(string label, Transform parent, float[] zs, float[] radii, Color color)
        {
            const int sides = 32;
            var verts = new List<Vector3>(); var tris = new List<int>();
            for (int k = 0; k < zs.Length; k++) for (int j = 0; j < sides; j++)
            {
                float a = j * Mathf.PI * 2f / sides;
                verts.Add(new Vector3(Mathf.Cos(a) * radii[k], Mathf.Sin(a) * radii[k] * .85f, zs[k]));
            }
            for (int k = 0; k < zs.Length - 1; k++) for (int j = 0; j < sides; j++)
            {
                int i = k * sides + j, n = k * sides + (j + 1) % sides;
                tris.AddRange(new[] { i, n, i + sides, n, n + sides, i + sides });
            }
            CreateMesh(label, parent, verts.ToArray(), tris.ToArray(), color);
        }
        private void Wing(string label, Transform parent, Vector2[] xz, float y, float thickness, Color color)
        {
            var verts = new Vector3[xz.Length * 2]; var tris = new List<int>(); int n = xz.Length;
            for (int i = 0; i < n; i++)
            {
                verts[i] = new Vector3(xz[i].x, y + thickness * .5f, xz[i].y);
                verts[i + n] = new Vector3(xz[i].x, y - thickness * .5f, xz[i].y);
            }
            for (int i = 1; i < n - 1; i++) tris.AddRange(new[] { 0, i + 1, i, n, n + i, n + i + 1 });
            for (int i = 0; i < n; i++) { int j = (i + 1) % n; tris.AddRange(new[] { i, i + n, j, j, i + n, j + n }); }
            CreateMesh(label, parent, verts, tris.ToArray(), color);
        }
        private void Fin(string label, Transform parent, Vector2[] yz, float width, Color color)
        {
            var v = new Vector3[yz.Length * 2]; var t = new List<int>(); int n = yz.Length;
            for (int i = 0; i < n; i++) { v[i] = new Vector3(-width * .5f, yz[i].x, yz[i].y); v[i + n] = new Vector3(width * .5f, yz[i].x, yz[i].y); }
            for (int i = 1; i < n - 1; i++) t.AddRange(new[] { 0, i + 1, i, n, n + i, n + i + 1 });
            for (int i = 0; i < n; i++) { int j = (i + 1) % n; t.AddRange(new[] { i, j, i + n, j, j + n, i + n }); }
            CreateMesh(label, parent, v, t.ToArray(), color);
        }
        private void CreateMesh(string label, Transform parent, Vector3[] mathVerts, int[] mathTriangles, Color color)
        {
            var mesh = new Mesh { name = label + " self-authored mesh" };
            // V6 geometry is rebuilt directly in native +Z-forward coordinates; no reflection.
            for (int i = 0; i < mathVerts.Length; i++) mathVerts[i] = EulerV6Math.ToUnity(mathVerts[i]);
mesh.vertices = mathVerts; mesh.triangles = mathTriangles; mesh.RecalculateNormals(); mesh.RecalculateBounds();
            ownedMeshes.Add(mesh);
            Transform obj = NewObject(label, parent);
            obj.gameObject.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = obj.gameObject.AddComponent<MeshRenderer>(); renderer.sharedMaterial = MakeMaterial(color, false);
            renderer.shadowCastingMode = ShadowCastingMode.Off; renderer.receiveShadows = false;
        }
        private void Ellipsoid(string label, Transform parent, Vector3 mathCenter, Vector3 dimensions, Color color)
        {
            GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Sphere); obj.name = label;
            obj.transform.SetParent(parent, false); obj.transform.localPosition = EulerV6Math.ToUnity(mathCenter);
            obj.transform.localScale = dimensions;
            var collider = obj.GetComponent<Collider>(); if (collider != null) DestroyOwnedObject(collider);
            var renderer = obj.GetComponent<MeshRenderer>(); renderer.sharedMaterial = MakeMaterial(color, false);
            renderer.shadowCastingMode = ShadowCastingMode.Off; renderer.receiveShadows = false;
        }
        private void BuildAxes(Transform parent, float length, float radius, float strength)
        {
            BuildArrow(parent, Vector3.zero, Vector3.right * length, Color.Lerp(Color.white, AxisX, strength), radius);
            BuildArrow(parent, Vector3.zero, Vector3.up * length, Color.Lerp(Color.white, AxisY, strength), radius);
            BuildArrow(parent, Vector3.zero, Vector3.forward * length, Color.Lerp(Color.white, AxisZ, strength), radius);
        }
        private void BuildArrow(Transform parent, Vector3 start, Vector3 end, Color color, float radius)
        {
            Vector3 d = (end - start).normalized;
            Segment("Axis shaft", parent, start, end - d * .23f, color, radius);
            const int sides = 20;
            var verts = new Vector3[sides + 2]; var tris = new List<int>();
            Vector3 u = Vector3.Cross(d, Mathf.Abs(d.y) < .9f ? Vector3.up : Vector3.right).normalized;
            Vector3 v = Vector3.Cross(d, u); Vector3 basePoint = end - d * .23f;
            verts[0] = end; verts[sides + 1] = basePoint;
            for (int i = 0; i < sides; i++)
            {
                float a = i * Mathf.PI * 2f / sides;
                verts[i + 1] = basePoint + (u * Mathf.Cos(a) + v * Mathf.Sin(a)) * radius * 3.4f;
            }
            for (int i = 0; i < sides; i++) { int next = (i + 1) % sides + 1; tris.AddRange(new[] { 0, i + 1, next, sides + 1, next, i + 1 }); }
            CreateMesh("Arrow head", parent, verts, tris.ToArray(), color);
        }
        private void Segment(string label, Transform parent, Vector3 start, Vector3 end, Color color, float radius)
        {
            GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder); obj.name = label;
            obj.transform.SetParent(parent, false);
            Vector3 a = EulerV6Math.ToUnity(start), b = EulerV6Math.ToUnity(end);
            obj.transform.localPosition = (a + b) * .5f;
            obj.transform.localRotation = Quaternion.FromToRotation(Vector3.up, (b - a).normalized);
            obj.transform.localScale = new Vector3(radius * 2f, Vector3.Distance(a, b) * .5f, radius * 2f);
            var collider = obj.GetComponent<Collider>(); if (collider != null) DestroyOwnedObject(collider);
            var renderer = obj.GetComponent<MeshRenderer>(); renderer.sharedMaterial = MakeMaterial(color, true);
            renderer.shadowCastingMode = ShadowCastingMode.Off; renderer.receiveShadows = false;
        }
        private void BuildRing(Transform parent, Vector3 normal, float radius, Color color, float tubeRadius)
        {
            Vector3 u = Vector3.Cross(normal, Vector3.forward).normalized;
            if (u.sqrMagnitude < .5f) u = Vector3.right;
            Vector3 v = Vector3.Cross(normal, u).normalized;
            const int count = 96;
            for (int i = 0; i < count; i++)
            {
                float a = i * Mathf.PI * 2f / count, b = (i + 1) * Mathf.PI * 2f / count;
                Segment("Ring arc", parent, (u * Mathf.Cos(a) + v * Mathf.Sin(a)) * radius,
                    (u * Mathf.Cos(b) + v * Mathf.Sin(b)) * radius, color, tubeRadius);
            }
        }
        private Material MakeMaterial(Color color, bool unlit)
        {
            bool srp = UsesSrp();
            string cacheKey = ColorUtility.ToHtmlStringRGBA(color) + "-" + unlit + "-" + srp;
            if (materialCache.TryGetValue(cacheKey, out Material existing)) return existing;
            Shader shader = Shader.Find(srp ? (unlit ? "Universal Render Pipeline/Unlit" : "Universal Render Pipeline/Lit")
                : (unlit ? "Unlit/Color" : "Standard"));
            if (shader == null) shader = Shader.Find("Sprites/Default");
            Material material = new Material(shader) { name = "M04 owned " + ColorUtility.ToHtmlStringRGB(color) };
            material.color = color;
            if (material.HasProperty("_BaseColor")) material.SetColor("_BaseColor", color);
            if (material.HasProperty("_Smoothness")) material.SetFloat("_Smoothness", .22f);
            if (material.HasProperty("_Glossiness")) material.SetFloat("_Glossiness", .22f);
            if (material.HasProperty("_Metallic")) material.SetFloat("_Metallic", 0f);
            // Procedural surfaces are double-sided for stable authoring and interior visibility.
            if (material.HasProperty("_Cull")) material.SetFloat("_Cull", 0f);
            ownedMaterials.Add(material); materialCache[cacheKey] = material; return material;
        }
        private static Transform NewObject(string name, Transform parent)
        { var obj = new GameObject(name); obj.transform.SetParent(parent, false); return obj.transform; }
        private static void DestroyOwnedObject(UnityEngine.Object obj)
        { if (Application.isPlaying) UnityEngine.Object.Destroy(obj); else UnityEngine.Object.DestroyImmediate(obj); }

    }
}

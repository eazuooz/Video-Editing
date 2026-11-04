using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.MathMotion {
    [Serializable] public class MotionShot {
        public string beatId="UNBOUND",englishTerm="Velocity",koreanTerm="속도",meaning="위치가 시간에 따라 변하는 비율";
        public MotionParameters parameters=new MotionParameters();
        public double startTime=0,endTime=3,secantH=.5;
        public string timeUnit="min",positionUnit="fur";
        public string axisConvention="x 오른쪽 / y 위 / +z 화면 밖 (오른손 도식)";
        public bool positiveYIsDown=false,termExpanded=true;
        public float worldUnitsPerModelUnit=.65f,velocityArrowScale=.3f,accelerationArrowScale=.15f;
        public Vector3 worldOrigin=new Vector3(-6,0,0);
        public bool showVelocity=true,showAcceleration=false,showRadius=false,showSecant=false;
        public bool showVelocityGraph=true,showAccelerationGraph=false;
        public bool showRiemann=false;
        public int riemannCount=6;
        public double riemannDuration=2.4,riemannAcceleration=32,riemannV0=0;
        public bool graphY=false;
        public double positionMin=-2,positionMax=9,velocityMin=-3,velocityMax=7,accelerationMin=-5,accelerationMax=2;
    }
    // No Update, wall-clock time, looping, physics stepping, rendering or file writes.
    // The parent renderer must call Evaluate with an approved, speech-bound cue time.
    public sealed class MotionTeachingStage:MonoBehaviour {
        public MotionShot shot=new MotionShot();
        public GameObject subjectPrefab;
        public Font koreanFont; // Load from local OS dynamically; never vendor a font file.
        public Camera stageCamera;
        public Transform subjectAnchor;
        public bool built;
        readonly List<GameObject> generated=new List<GameObject>();
        readonly List<LineRenderer> lines=new List<LineRenderer>();
        int lineCursor;
        Text term,kind,values,details,coordinateLabel,positionTitle,velocityTitle,accelerationTitle,velocityCallout,accelerationCallout,radiusCallout;
        Canvas canvas;
        Material lineMaterial;
        static readonly Color White=new Color(.961f,.961f,.961f),Yellow=new Color(.910f,.812f,.514f),Teal=new Color(.451f,.780f,.761f),Red=new Color(.937f,.522f,.522f),Green=new Color(.643f,.776f,.627f),Muted=new Color(.722f,.722f,.722f);
        public void Build() {
            if(built)return;
            if(subjectPrefab==null)throw new InvalidOperationException("Assign a rights-verified recognizable prefab. No generic cube or silent substitute is created.");
            if(koreanFont==null)throw new InvalidOperationException("Supply a local dynamic Korean font; do not distribute its original font file.");
            if(stageCamera==null) {
                GameObject c=Own(new GameObject("MotionLabCamera"));stageCamera=c.AddComponent<Camera>();
                stageCamera.transform.position=new Vector3(0,2,-20);stageCamera.transform.rotation=Quaternion.identity;
                stageCamera.orthographic=true;stageCamera.orthographicSize=5.625f;stageCamera.clearFlags=CameraClearFlags.SolidColor;stageCamera.backgroundColor=Color.black;
                stageCamera.nearClipPlane=.1f;stageCamera.farClipPlane=80;
            }
            var shader=Shader.Find("Universal Render Pipeline/Unlit")??Shader.Find("Unlit/Color");
            if(shader==null)throw new InvalidOperationException("No compatible unlit shader; preserve pipeline and supply one explicitly.");
            lineMaterial=new Material(shader){name="YamyamMotionLines"};
            GameObject anchor=Own(new GameObject("TrackedObjectAnchor"));subjectAnchor=anchor.transform;
            var subject=Instantiate(subjectPrefab,subjectAnchor);subject.name="LicensedSubject_Instance";
            subject.transform.localPosition=Vector3.zero;
            // Preserve vendor original materials/rig. Parent renderer must select compatible materials.
            Bounds bounds=new Bounds(subject.transform.position,Vector3.zero);bool first=true;
            foreach(var renderer in subject.GetComponentsInChildren<Renderer>()) { if(first){bounds=renderer.bounds;first=false;}else bounds.Encapsulate(renderer.bounds); }
            if(first||bounds.size.magnitude<1e-6f)throw new InvalidOperationException("The selected prefab has no visible renderer bounds.");
            float scale=.95f/Mathf.Max(bounds.size.x,bounds.size.y,bounds.size.z);subject.transform.localScale*=scale;
            // Its tracked point is the visible bounds centre; a labelled marker makes this explicit.
            subject.transform.localPosition-=bounds.center*scale;
            var light=Own(new GameObject("MotionLabKey")).AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.3f;light.transform.rotation=Quaternion.Euler(35,-25,0);
            GameObject ui=Own(new GameObject("MotionLabLabels"));canvas=ui.AddComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=stageCamera;canvas.planeDistance=1;
            var scaler=ui.AddComponent<CanvasScaler>();scaler.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;scaler.referenceResolution=new Vector2(1920,1080);
            term=Label("Term",new Rect(88,45,1050,145),40,Yellow);
            kind=Label("SourceKind",new Rect(1200,55,620,100),32,Muted);
            values=Label("ModelValues",new Rect(92,730,920,130),32,White);
            details=Label("LiveCalculation",new Rect(1090,760,750,110),28,White);
            coordinateLabel=Label("CoordinateConvention",new Rect(92,195,1000,42),26,Muted);
            positionTitle=Label("GraphPosition",new Rect(1120,225,620,42),30,Yellow);
            velocityTitle=Label("GraphVelocity",new Rect(1120,390,620,42),30,Teal);
            accelerationTitle=Label("GraphAcceleration",new Rect(1120,555,620,42),30,Red);
            velocityCallout=Label("VelocityArrowLabel",new Rect(0,0,380,44),28,Teal);
            accelerationCallout=Label("AccelerationArrowLabel",new Rect(0,0,380,44),28,Red);
            radiusCallout=Label("RadiusArrowLabel",new Rect(0,0,300,44),28,Yellow);
            built=true;
        }
        GameObject Own(GameObject go){go.transform.SetParent(transform,false);generated.Add(go);return go;}
        Text Label(string id,Rect pixelRect,int size,Color color) {
            GameObject go=new GameObject(id);go.transform.SetParent(canvas.transform,false);var rt=go.AddComponent<RectTransform>();rt.anchorMin=rt.anchorMax=new Vector2(0,1);rt.pivot=new Vector2(0,1);rt.anchoredPosition=new Vector2(pixelRect.x,-pixelRect.y);rt.sizeDelta=new Vector2(pixelRect.width,pixelRect.height);
            Text t=go.AddComponent<Text>();t.font=koreanFont;t.fontSize=size;t.color=color;t.horizontalOverflow=HorizontalWrapMode.Wrap;t.verticalOverflow=VerticalWrapMode.Truncate;t.supportRichText=false;return t;
        }
        // Reflection from mathematical RH coordinates to the Unity display's z direction.
        public static Vector3 ToUnity(DVec v)=>new Vector3((float)v.x,(float)v.y,(float)-v.z);
        Vector3 DisplayVector(DVec p){Vector3 v=ToUnity(p);if(shot.positiveYIsDown)v.y=-v.y;return v;}
        Vector3 Position(DVec p)=>shot.worldOrigin+DisplayVector(p)*shot.worldUnitsPerModelUnit;
        LineRenderer Line(Color color,float width) {
            LineRenderer r;
            if(lineCursor<lines.Count)r=lines[lineCursor];else {var go=Own(new GameObject("MotionGuide_"+lines.Count));r=go.AddComponent<LineRenderer>();r.useWorldSpace=true;r.sharedMaterial=lineMaterial;r.numCapVertices=4;r.numCornerVertices=4;lines.Add(r);}
            lineCursor++;r.gameObject.SetActive(true);r.startColor=r.endColor=Color.white;r.startWidth=r.endWidth=width;r.alignment=LineAlignment.View;
            var props=new MaterialPropertyBlock();props.SetColor("_BaseColor",color);props.SetColor("_Color",color);r.SetPropertyBlock(props);return r;
        }
        void Poly(IList<Vector3> points,Color color,float width=.025f) {if(points.Count<2)return;var l=Line(color,width);l.positionCount=points.Count;for(int i=0;i<points.Count;i++)l.SetPosition(i,points[i]);}
        void Arrow(Vector3 from,Vector3 delta,Color color) {
            if(delta.sqrMagnitude<1e-10f)return;
            Vector3 end=from+delta;Poly(new[]{from,end},color,.045f);
            Vector3 d=delta.normalized,s=Vector3.Cross(d,stageCamera.transform.forward);if(s.sqrMagnitude<1e-8f)s=stageCamera.transform.right;s.Normalize();
            float head=Mathf.Min(.22f,delta.magnitude*.28f);Poly(new[]{end-d*head+s*head*.5f,end,end-d*head-s*head*.5f},color,.045f);
        }
        void PlaceCallout(Text label,Vector3 world,string text,bool visible) {
            Vector3 v=stageCamera.WorldToViewportPoint(world);float px=v.x*1920,py=(1-v.y)*1080;
            bool safe=visible&&v.z>0&&px>=85&&px<=700&&py>=245&&py<=680;
            label.gameObject.SetActive(safe);if(!safe)return;
            label.rectTransform.anchoredPosition=new Vector2(px+14,-py);label.text=text;
        }
        Vector3 Plot(double t,double value,double lo,double hi,float yBase) {
            double u=(t-shot.startTime)/(shot.endTime-shot.startTime);float x=1.8f+(float)u*6.5f;
            float y=yBase+(float)((value-lo)/(hi-lo))*1.2f;return new Vector3(x,y,-2);
        }
        void Graph(Func<MotionState,double> value,double lo,double hi,float yBase,Color color,double current,bool derivative) {
            if(hi<=lo||shot.endTime<=shot.startTime)throw new InvalidOperationException("Graph range must increase.");
            Poly(new[]{new Vector3(1.8f,yBase,-2),new Vector3(8.3f,yBase,-2)},Muted*.6f,.012f);
            List<Vector3> part=new List<Vector3>();
            for(int i=0;i<=180;i++) {
                double t=shot.startTime+(shot.endTime-shot.startTime)*i/180.0;
                if(i>0&&derivative&&shot.parameters.kind==MotionKind.PiecewiseExercise){double previous=shot.startTime+(shot.endTime-shot.startTime)*(i-1)/180.0;foreach(double join in new[]{2.0,4.0,7.0})if(previous<join&&t>=join){Poly(part,color);part.Clear();}}
                var s=MotionMathModel.Sample(shot.parameters,t);double v=value(s);
                bool valid=(!derivative||s.velocityDefined)&&v>=lo&&v<=hi;
                // Never clamp out-of-range values into a false plateau or connect undefined joins.
                if(!valid) {Poly(part,color);part.Clear();continue;}
                part.Add(Plot(t,v,lo,hi,yBase));
            }
            Poly(part,color);
            float cursorX=Plot(current,lo,lo,hi,yBase).x;
            Poly(new[]{new Vector3(cursorX,yBase,-2.05f),new Vector3(cursorX,yBase+1.2f,-2.05f)},White*.65f,.015f);
        }
        public void Evaluate(double normalizedCue) {
            if(!built)Build();
            if(normalizedCue<0||normalizedCue>1)throw new ArgumentOutOfRangeException(nameof(normalizedCue),"No modulo looping or silent clamping.");
            lineCursor=0;double t=shot.startTime+(shot.endTime-shot.startTime)*normalizedCue;var state=MotionMathModel.Sample(shot.parameters,t);Vector3 at=Position(state.position);subjectAnchor.position=at;
            term.fontSize=shot.termExpanded?40:34;
            term.text=shot.termExpanded?shot.englishTerm+"\n"+shot.koreanTerm+"\n"+shot.meaning:shot.englishTerm+" · "+shot.koreanTerm+"\n"+shot.meaning;
            coordinateLabel.text="해설용 운동 모형 · "+shot.axisConvention;
            string component=shot.graphY?"y":"x";
            positionTitle.text="위치 "+component+"(t)";velocityTitle.text="속도 v"+component+"(t)";accelerationTitle.text="가속도 a"+component+"(t)";
            velocityTitle.gameObject.SetActive(shot.showVelocityGraph);accelerationTitle.gameObject.SetActive(shot.showAccelerationGraph);
            kind.text="현재 화면: 우리 구현\n해설용 해석 운동 모형 · 게임 실측 아님";
            var path=new List<Vector3>();for(int i=0;i<=160;i++){double pt=shot.startTime+(shot.endTime-shot.startTime)*i/160.0;path.Add(Position(MotionMathModel.Sample(shot.parameters,pt).position));}Poly(path,Muted*.45f,.018f);
            if(shot.showVelocity&&state.velocityDefined)Arrow(at,DisplayVector(state.velocity)*shot.velocityArrowScale,Teal);
            if(shot.showAcceleration&&state.accelerationDefined)Arrow(at,DisplayVector(state.acceleration)*shot.accelerationArrowScale,Red);
            if(shot.showRadius)Arrow(Position(shot.parameters.origin),at-Position(shot.parameters.origin),Yellow);
            PlaceCallout(velocityCallout,at+DisplayVector(state.velocity)*shot.velocityArrowScale,"v  |v|="+state.velocity.Length.ToString("0.00"),shot.showVelocity&&state.velocityDefined);
            PlaceCallout(accelerationCallout,at+DisplayVector(state.acceleration)*shot.accelerationArrowScale,"a  |a|="+state.acceleration.Length.ToString("0.00"),shot.showAcceleration&&state.accelerationDefined);
            PlaceCallout(radiusCallout,Vector3.Lerp(Position(shot.parameters.origin),at,.5f),"r = "+(state.position-shot.parameters.origin).Length.ToString("0.00"),shot.showRadius);
            if(shot.showSecant){var q=MotionMathModel.Sample(shot.parameters,t+shot.secantH);Poly(new[]{at,Position(q.position)},Green,.035f);}
            Func<MotionState,double> p=s=>shot.graphY?s.position.y:s.position.x,v=s=>shot.graphY?s.velocity.y:s.velocity.x,a=s=>shot.graphY?s.acceleration.y:s.acceleration.x;
            Graph(p,shot.positionMin,shot.positionMax,3.3f,Yellow,t,false);
            if(shot.showVelocityGraph)Graph(v,shot.velocityMin,shot.velocityMax,1.6f,Teal,t,true);
            if(shot.showAccelerationGraph)Graph(a,shot.accelerationMin,shot.accelerationMax,-.1f,Red,t,true);
            values.text="t = "+t.ToString("0.000")+" "+shot.timeUnit+"   "+component+" = "+p(state).ToString("0.000")+" "+shot.positionUnit;
            if(shot.showVelocityGraph)values.text+="\n"+(state.velocityDefined?"v"+component+" = "+v(state).ToString("0.000")+" "+shot.positionUnit+"/"+shot.timeUnit:"v = 정의되지 않음 (구간 경계)");
            if(shot.showAccelerationGraph)values.text+="   "+(state.accelerationDefined?"a"+component+" = "+a(state).ToString("0.000")+" "+shot.positionUnit+"/"+shot.timeUnit+"²":"a = 정의되지 않음");
            details.text=shot.showSecant?"Δt = "+shot.secantH.ToString("0.000")+"\n평균 속도 = "+(shot.graphY?MotionMathModel.SecantVelocity(shot.parameters,t,shot.secantH).y:MotionMathModel.SecantVelocity(shot.parameters,t,shot.secantH).x).ToString("0.000"):
                shot.parameters.kind==MotionKind.Circle?"r = "+shot.parameters.radius.ToString("0.00")+"   ω = "+shot.parameters.omega.ToString("0.00")+" rad/s\n|v| = "+state.velocity.Length.ToString("0.000")+"   |a| = "+state.acceleration.Length.ToString("0.000"):"값은 현재 해설 모형에서 직접 계산\n화살표 축척은 장면 안에서 고정";
            if(shot.showRiemann)RiemannOverlay();
            for(int i=lineCursor;i<lines.Count;i++)lines[i].gameObject.SetActive(false);
        }
        void RiemannOverlay() {
            if(shot.riemannCount<=0||shot.riemannDuration<=0)throw new InvalidOperationException("Riemann settings must be positive.");
            double sourceV=shot.graphY?shot.parameters.velocity.y:shot.parameters.velocity.x,sourceA=shot.graphY?shot.parameters.acceleration.y:shot.parameters.acceleration.x;
            if(shot.parameters.kind!=MotionKind.ConstantAcceleration||Math.Abs(sourceV-shot.riemannV0)>1e-9||Math.Abs(sourceA-shot.riemannAcceleration)>1e-9||Math.Abs(shot.startTime)>1e-9||Math.Abs(shot.endTime-shot.riemannDuration)>1e-9)
                throw new InvalidOperationException("Rectangle values must describe the same analytic velocity, time domain and component as the graph.");
            double dt=shot.riemannDuration/shot.riemannCount;
            for(int k=0;k<shot.riemannCount;k++) {
                double time=k*dt,height=shot.riemannV0+shot.riemannAcceleration*time;
                // Overlay belongs to the velocity plot, using the same real axes and units.
                if(height<shot.velocityMin||height>shot.velocityMax)continue;
                Poly(new[]{Plot(time,0,shot.velocityMin,shot.velocityMax,1.6f),Plot(time,height,shot.velocityMin,shot.velocityMax,1.6f),Plot(time+dt,height,shot.velocityMin,shot.velocityMax,1.6f),Plot(time+dt,0,shot.velocityMin,shot.velocityMax,1.6f)},Yellow,.022f);
            }
            double sum=MotionMathModel.LeftRiemannLinear(shot.riemannV0,shot.riemannAcceleration,shot.riemannDuration,shot.riemannCount);
            double exact=shot.riemannV0*shot.riemannDuration+.5*shot.riemannAcceleration*shot.riemannDuration*shot.riemannDuration;
            details.text="왼쪽 끝 "+shot.riemannCount+"분할 · Δt = "+dt.ToString("0.00")+"\n합 = "+sum.ToString("0.00")+"   정확한 변위 = "+exact.ToString("0.00");
        }
    }
}

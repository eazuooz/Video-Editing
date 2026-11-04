using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.MathMechanics {
    public enum MechanicsPicture {FreeBody,FreeSlide,Incline,GravityPair,Jump,FreeFall,Spring,SpringComparison,ControlStep,FirstOrder,HorizontalForce,ForcePair,ReferenceFrames,ContactArea}
    [Serializable] public class MechanicsShot {
        public string id="UNBOUND",english="Newton's Second Law",korean="뉴턴의 제2법칙",meaning="받는 힘을 모아 가속도를 구한다";
        public MechanicsPicture picture=MechanicsPicture.FreeBody;
        public double mass=2,gravity=9.8,forceX=6,opposingForce=2,muStatic=.5,muKinetic=.3;
        public double angleRadians=0,initialVelocity=4,slideDeceleration=2,jumpHeight=2,apexSeconds=.4;
        public double k=16,c=4,x0=1,v0=0,target=0,dt=.1,lambda=2,timeStart=0,timeEnd=3;
        public double gravityMassA=3,gravityMassB=5,gravityDistance=2;
        public double secondaryMass=4,frameVelocity=0,frameAcceleration=0,contactArea=1;
        public bool showObserverFrame=false,showReaction=false,kineticContact=false;
        public string subjectKind="box",secondaryKind="box",bodyLabel="선택한 물체",otherLabel="비교 물체";
        public bool showSupport=true,showFriction=false,showNet=true,showVelocity=true,showAcceleration=true,showEquation=true;
        public float worldScale=1,forceScale=.10f,velocityScale=.23f,accelerationScale=.06f;
        public string equation="ΣF = m a",condition="일정한 질량 · 관성 기준계";
    }
    // Deterministic teaching renderer. Values are computed by our analytic model,
    // never labelled as measurements of any commercial game or Unity solver.
    public sealed partial class MechanicsTeachingStage:MonoBehaviour {
        public MechanicsShot shot=new MechanicsShot();
        public GameObject objectPrefab,secondaryPrefab;
        public Font koreanFont;
        public Camera observer;
        public bool built;
        Transform body,other,third;
        Canvas canvas;
        Text term,kind,caption,formula,numbers,conditions;
        readonly List<LineRenderer> guides=new List<LineRenderer>();
        readonly List<Text> tags=new List<Text>();
        int lineCount,tagCount;
        Material guideMaterial;
        static readonly Color White=new Color(.96f,.96f,.96f),Yellow=new Color(.91f,.812f,.514f),Teal=new Color(.451f,.78f,.761f),Red=new Color(.937f,.522f,.522f),Green=new Color(.643f,.776f,.627f),Muted=new Color(.68f,.72f,.72f);
        GameObject Own(string name){var go=new GameObject(name);go.transform.SetParent(transform,false);return go;}
        Transform Subject(GameObject prefab,string name) {
            if(prefab==null)throw new InvalidOperationException("Select an inspected, licensed subject asset; no generic substitute.");
            var root=Own(name).transform;var obj=Instantiate(prefab,root);obj.name="LicensedSubject";
            bool first=true;Bounds bounds=new Bounds();foreach(var r in obj.GetComponentsInChildren<Renderer>()){if(first){bounds=r.bounds;first=false;}else bounds.Encapsulate(r.bounds);}
            if(first||bounds.size.magnitude<1e-6f)throw new InvalidOperationException("Subject has no visible geometry");
            float scale=1.2f/Mathf.Max(bounds.size.x,bounds.size.y,bounds.size.z);obj.transform.localScale*=scale;obj.transform.localPosition-=bounds.center*scale;
            return root;
        }
        public void Build() {
            if(built)return;if(koreanFont==null)throw new InvalidOperationException("Supply local OS font without redistribution");
            if(observer==null){observer=Own("MechanicsObserver").AddComponent<Camera>();observer.transform.position=new Vector3(0,0,-20);observer.transform.rotation=Quaternion.identity;observer.orthographic=true;observer.orthographicSize=5.625f;observer.clearFlags=CameraClearFlags.SolidColor;observer.backgroundColor=Color.black;observer.farClipPlane=70;}
            var shader=Shader.Find("Universal Render Pipeline/Unlit")??Shader.Find("Unlit/Color");if(shader==null)throw new InvalidOperationException("Missing compatible line shader");guideMaterial=new Material(shader);
            body=Subject(objectPrefab,"SelectedBody");other=Subject(secondaryPrefab??objectPrefab,"ComparisonBody");third=Subject(objectPrefab,"ThirdComparisonBody");
            var key=Own("Key").AddComponent<Light>();key.type=LightType.Directional;key.intensity=1.4f;key.transform.rotation=Quaternion.Euler(35,-25,0);
            canvas=Own("MechanicsLabels").AddComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=observer;canvas.planeDistance=1;
            var scaler=canvas.gameObject.AddComponent<CanvasScaler>();scaler.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;scaler.referenceResolution=new Vector2(1920,1080);
            term=TextAt("Term",new Rect(78,45,1110,145),40,Yellow);
            kind=TextAt("Kind",new Rect(1240,55,600,110),32,Muted);
            caption=TextAt("ModelBasis",new Rect(78,205,1040,80),30,Muted);
            formula=TextAt("Formula",new Rect(1120,280,700,185),39,Yellow);
            numbers=TextAt("Numbers",new Rect(1120,475,700,230),35,White);
            conditions=TextAt("Conditions",new Rect(1100,735,740,125),29,Muted);
            built=true;
        }
        Text TextAt(string name,Rect r,int size,Color color){var go=new GameObject(name);go.transform.SetParent(canvas.transform,false);var rt=go.AddComponent<RectTransform>();rt.anchorMin=rt.anchorMax=new Vector2(0,1);rt.pivot=new Vector2(0,1);rt.anchoredPosition=new Vector2(r.x,-r.y);rt.sizeDelta=new Vector2(r.width,r.height);var t=go.AddComponent<Text>();t.font=koreanFont;t.fontSize=size;t.color=color;t.supportRichText=false;t.horizontalOverflow=HorizontalWrapMode.Wrap;t.verticalOverflow=VerticalWrapMode.Truncate;return t;}
        void Line(IList<Vector3> pts,Color color,float width=.035f) {
            if(pts.Count<2)return;LineRenderer line;
            if(lineCount==guides.Count){line=Own("Guide"+lineCount).AddComponent<LineRenderer>();line.sharedMaterial=guideMaterial;line.numCapVertices=5;line.numCornerVertices=4;guides.Add(line);}else line=guides[lineCount];
            lineCount++;line.gameObject.SetActive(true);line.useWorldSpace=true;line.positionCount=pts.Count;line.startWidth=line.endWidth=width;line.startColor=line.endColor=Color.white;
            var props=new MaterialPropertyBlock();props.SetColor("_BaseColor",color);props.SetColor("_Color",color);line.SetPropertyBlock(props);for(int i=0;i<pts.Count;i++)line.SetPosition(i,pts[i]);
        }
        void Tag(Vector3 at,string text,Color color) {
            Text tag;if(tagCount==tags.Count){tag=TextAt("ArrowName"+tagCount,new Rect(0,0,380,82),30,color);tags.Add(tag);}else tag=tags[tagCount];tagCount++;
            var point=observer.WorldToViewportPoint(at);float x=point.x*1920,y=(1-point.y)*1080;
            bool safe=point.z>0&&x>=55&&x<=740&&y>=290&&y<=760;tag.gameObject.SetActive(safe);if(!safe)return;
            tag.color=color;tag.text=text;tag.rectTransform.anchoredPosition=new Vector2(x+12,-y);
        }
        void Arrow(Vector3 origin,Vector3 vector,Color color,string label="") {
            if(vector.sqrMagnitude<1e-10f)return;var end=origin+vector;Line(new[]{origin,end},color,.055f);
            var direction=vector.normalized;var side=Vector3.Cross(direction,observer.transform.forward);if(side.sqrMagnitude<1e-10f)side=observer.transform.right;side.Normalize();float h=Mathf.Min(.23f,vector.magnitude*.3f);Line(new[]{end-direction*h+side*h*.45f,end,end-direction*h-side*h*.45f},color,.055f);
            if(label!="")Tag(end,label,color);
        }
        static Vector3 U(MVec v)=>new Vector3((float)v.x,(float)v.y,(float)-v.z);
        static string N(double v)=>v.ToString("0.###",System.Globalization.CultureInfo.InvariantCulture);
        Vector3 Origin=>new Vector3(-4.7f,.1f,0);
        void Floor(float angle) {Vector3 tangent=new Vector3(Mathf.Cos(angle),Mathf.Sin(angle),0);Vector3 center=Origin+new Vector3(0,-.65f,.2f);Line(new[]{center-tangent*4,center+tangent*4},Muted,.05f);}
        void SpringCoil(Vector3 fixedEnd,Vector3 movingEnd,Color color) {
            Vector3 delta=movingEnd-fixedEnd,axis=delta.normalized;var side=Vector3.Cross(axis,Vector3.forward).normalized;var pts=new List<Vector3>{fixedEnd};
            for(int i=0;i<=160;i++){float u=i/160f,t=u*Mathf.PI*20;pts.Add(Vector3.Lerp(fixedEnd,movingEnd,.08f+.84f*u)+side*Mathf.Sin(t)*.17f+Vector3.forward*Mathf.Cos(t)*.17f);}
            pts.Add(movingEnd);Line(pts,color,.045f);Line(new[]{fixedEnd+Vector3.up*.4f,fixedEnd-Vector3.up*.4f},White,.06f);
        }
        void SpringGraph(double current) {
            Vector3 a=new Vector3(-8,-2.9f,-.6f),b=new Vector3(-1,-2.9f,-.6f);Line(new[]{a,b},Muted,.018f);
            var pts=new List<Vector3>();for(int i=0;i<=180;i++){double t=shot.timeStart+(shot.timeEnd-shot.timeStart)*i/180;double value=MechanicsMathModel.Spring(shot.mass,shot.k,shot.c,shot.x0,shot.v0,t).x;pts.Add(new Vector3(-8+7*i/180f,-2.9f+(float)value,-.6f));}Line(pts,Teal,.03f);
            float cx=-8+7*(float)((current-shot.timeStart)/(shot.timeEnd-shot.timeStart));Line(new[]{new Vector3(cx,-4,-.65f),new Vector3(cx,-1.8f,-.65f)},Yellow,.02f);
        }
        public void Evaluate(double normalizedTime) {
            if(!built)Build();if(normalizedTime<0||normalizedTime>1||double.IsNaN(normalizedTime))throw new ArgumentOutOfRangeException(nameof(normalizedTime));
            if(shot.timeEnd<=shot.timeStart)throw new InvalidOperationException("Increasing model time required");
            lineCount=tagCount=0;other.gameObject.SetActive(false);third.gameObject.SetActive(false);body.rotation=Quaternion.identity;body.position=Origin;
            double t=shot.timeStart+(shot.timeEnd-shot.timeStart)*normalizedTime;
            term.text=shot.english+"\n"+shot.korean+"\n"+shot.meaning;kind.text="현재 화면: 우리 구현\n해설용 역학 모형 · 게임 실측 아님";
            caption.text="오른쪽 +x · 위쪽 +y · 시간 s · 거리 m\n화살표는 표시한 물체가 받는 힘";
            formula.text=shot.showEquation?shot.equation:"";conditions.text=shot.condition;numbers.text="t = "+N(t)+" s";
            switch(shot.picture) {
                case MechanicsPicture.FreeBody:case MechanicsPicture.Incline: {
                    double angle=shot.picture==MechanicsPicture.Incline?shot.angleRadians:0;Floor((float)angle);body.rotation=Quaternion.Euler(0,0,(float)(angle*180/Math.PI));
                    MVec gravity=new MVec(0,-shot.mass*shot.gravity),external=gravity+new MVec(shot.forceX-shot.opposingForce),normal=new MVec(-Math.Sin(angle),Math.Cos(angle));
                    MVec slip=shot.kineticContact?new MVec(Math.Cos(angle),Math.Sin(angle))*shot.initialVelocity:new MVec();
                    var f=MechanicsMathModel.SupportedFriction(external,normal,slip,shot.showFriction?shot.muStatic:0,shot.showFriction?shot.muKinetic:0);MVec net=shot.showSupport?f.net:external;
                    Vector3 at=body.position+new Vector3(0,0,-1);Arrow(at,U(gravity)*shot.forceScale,Red,"중력 m g");
                    if(shot.showSupport)Arrow(at,U(normal*f.normal)*shot.forceScale,Green,"수직항력 N");
                    Arrow(at+Vector3.up*.2f,Vector3.right*(float)shot.forceX*shot.forceScale,Teal,"미는 힘");Arrow(at-Vector3.up*.2f,Vector3.left*(float)shot.opposingForce*shot.forceScale,Yellow,"반대쪽 힘");
                    if(shot.showFriction)Arrow(at+Vector3.down*.35f,U(f.friction)*shot.forceScale,Yellow,f.sticking?"정지 마찰":"운동 마찰");
                    if(shot.showNet)Arrow(at+Vector3.down*1.2f,U(net)*shot.forceScale,White,"알짜힘 ΣF");
                    numbers.text+="\nm = "+N(shot.mass)+" kg\nN = "+N(f.normal)+" N";
                    if(shot.showFriction)numbers.text+="\n정지 한도 = "+N(f.maximumStatic)+" N\n현재 마찰 = "+N(f.friction.Length)+" N";
                    numbers.text+="\n|ΣF| = "+N(net.Length)+" N";
                    break;
                }
                case MechanicsPicture.FreeSlide: {
                    Floor(0);var s=MechanicsMathModel.FreeSlide(shot.initialVelocity,shot.slideDeceleration,t);body.position=Origin+Vector3.right*((float)s.x*shot.worldScale-2);
                    if(shot.showVelocity)Arrow(body.position,U(new MVec(s.v))*shot.velocityScale,Teal,"속도 v");if(shot.showAcceleration)Arrow(body.position+Vector3.up*.6f,U(new MVec(s.a*shot.mass))*shot.forceScale,Yellow,"마찰력");
                    numbers.text+="\nx = "+N(s.x)+" m\nv = "+N(s.v)+" m/s\na = "+N(s.a)+" m/s²";break;
                }
                case MechanicsPicture.Jump: {
                    Floor(0);var s=MechanicsMathModel.DesignedJump(shot.jumpHeight,shot.apexSeconds,t);body.position=Origin+Vector3.up*((float)s.x*shot.worldScale-.3f);
                    Arrow(body.position,Vector3.up*(float)s.v*shot.velocityScale,Teal,"속도 v");Arrow(body.position+Vector3.right*.6f,Vector3.up*(float)s.a*shot.accelerationScale,Red,"가속도 a");numbers.text+="\ny = "+N(s.x)+" m\nv = "+N(s.v)+" m/s\na = "+N(s.a)+" m/s²";break;
                }
                case MechanicsPicture.GravityPair: {
                    other.gameObject.SetActive(true);float d=(float)shot.gravityDistance*shot.worldScale;body.position=Origin+Vector3.left*d/2;other.position=Origin+Vector3.right*d/2;
                    double f=MechanicsMathModel.PairGravity(shot.gravityMassA,shot.gravityMassB,new MVec(shot.gravityDistance)).Length;
                    double baseline=MechanicsMathModel.PairGravity(shot.gravityMassA,shot.gravityMassB,new MVec(1)).Length;float length=(float)(f/baseline)*3;
                    Arrow(body.position,Vector3.right*length,Teal,"A가 받는 힘");Arrow(other.position,Vector3.left*length,Red,"B가 받는 힘");
                    numbers.text+="\nr = "+N(shot.gravityDistance)+" m\nF = "+f.ToString("0.00E+0")+" N\n1 m일 때 대비 = "+N(f/baseline);conditions.text+="\n화살표 길이는 1 m 기준 상대값";break;
                }
                case MechanicsPicture.FreeFall: {
                    other.gameObject.SetActive(true);float drop=(float)(-.5*shot.gravity*t*t)*shot.worldScale;
                    body.position=Origin+new Vector3(-1,drop,0);other.position=Origin+new Vector3(1,drop,0);
                    Arrow(body.position,Vector3.down*(float)shot.gravity*shot.accelerationScale,Red,"같은 가속도 g");Arrow(other.position,Vector3.down*(float)shot.gravity*shot.accelerationScale,Red);
                    numbers.text+="\na물체 = a기준계 = −"+N(shot.gravity)+" m/s²\n상대 가속도 = 0\n두 물체의 상대 위치 유지";break;
                }
                case MechanicsPicture.Spring:case MechanicsPicture.SpringComparison: {
                    var s=MechanicsMathModel.Spring(shot.mass,shot.k,shot.c,shot.x0,shot.v0,t);body.position=Origin+Vector3.right*(float)s.x*shot.worldScale;
                    SpringCoil(Origin+Vector3.left*3,body.position+Vector3.left*.6f,White);
                    Arrow(body.position+Vector3.up*.7f,Vector3.right*(float)(-shot.k*s.x)*shot.forceScale,Teal,"복원력 −k x");Arrow(body.position+Vector3.down*.7f,Vector3.right*(float)(-shot.c*s.v)*shot.forceScale,Yellow,"감쇠력 −c v");
                    numbers.text+="\nx = "+N(s.x)+" m\nv = "+N(s.v)+" m/s\nω₀ = "+N(MechanicsMathModel.NaturalFrequency(shot.mass,shot.k))+" rad/s\nζ = "+N(MechanicsMathModel.DampingRatio(shot.mass,shot.k,shot.c));
                    SpringGraph(t);
                    if(shot.picture==MechanicsPicture.SpringComparison){other.gameObject.SetActive(true);third.gameObject.SetActive(true);double w=MechanicsMathModel.NaturalFrequency(shot.mass,shot.k);var critical=MechanicsMathModel.Spring(shot.mass,shot.k,2*shot.mass*w,shot.x0,shot.v0,t);var over=MechanicsMathModel.Spring(shot.mass,shot.k,4*shot.mass*w,shot.x0,shot.v0,t);other.position=Origin+new Vector3((float)critical.x*shot.worldScale,1.25f,0);third.position=Origin+new Vector3((float)over.x*shot.worldScale,-1.25f,0);Tag(other.position+Vector3.right*.7f,"ζ = 1",Green);Tag(third.position+Vector3.right*.7f,"ζ = 2",Yellow);}
                    break;
                }
                case MechanicsPicture.ControlStep: {
                    int steps=(int)Math.Floor(t/shot.dt+1e-8);var s=new ScalarState(shot.x0,shot.v0,0);for(int i=0;i<steps;i++)s=MechanicsMathModel.SemiImplicitSpring(s,shot.target,shot.k,shot.c,shot.dt);
                    body.position=Origin+Vector3.right*(float)s.x*shot.worldScale;Line(new[]{Origin+new Vector3((float)shot.target*shot.worldScale,-1,0),Origin+new Vector3((float)shot.target*shot.worldScale,1,0)},Green,.035f);
                    numbers.text="계산 단계 = "+steps+"\nΔt = "+N(shot.dt)+" s\nx = "+N(s.x)+"\nv = "+N(s.v)+"\na = "+N(s.a);break;
                }
                case MechanicsPicture.FirstOrder: {
                    double value=MechanicsMathModel.FirstOrderLag(shot.x0,shot.target,shot.lambda,t);body.position=Origin+Vector3.right*(float)value*shot.worldScale;
                    Line(new[]{Origin+new Vector3((float)shot.target*shot.worldScale,-1,0),Origin+new Vector3((float)shot.target*shot.worldScale,1,0)},Green,.035f);numbers.text+="\nλ = "+N(shot.lambda)+"\n현재 = "+N(value)+"\n목표 = "+N(shot.target);break;
                }
                default: ApplyAdditionalPicture(t);break;
            }
            for(int i=lineCount;i<guides.Count;i++)guides[i].gameObject.SetActive(false);for(int i=tagCount;i<tags.Count;i++)tags[i].gameObject.SetActive(false);
        }
        public void SetSourceStep(string equation,string meaning){formula.text=equation;conditions.text=meaning;}
    }
}

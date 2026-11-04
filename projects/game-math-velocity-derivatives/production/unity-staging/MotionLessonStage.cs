using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.MathMotion {
    [Serializable] public class MotionStep {
        public string anchor,formula,meaning;
        public double modelFrom,modelTo,secantH=.5;
        public bool showSecant,showTangent;
        public MotionShot motionOverride;
    }
    [Serializable] public class MotionLessonShot {
        public string beatId="UNBOUND";
        public string diagramMode="";
        public MotionShot motion=new MotionShot();
        public MotionStep[] steps=Array.Empty<MotionStep>();
        public double durationSeconds;
        public double[] stepSeconds=Array.Empty<double>(),stepPositions=Array.Empty<double>();
    }
    // Same analytic stage throughout a source paragraph. Formula changes and
    // movement follow one speech remapping; no separate animation clock.
    [ExecuteAlways] public sealed class MotionLessonStage:MonoBehaviour {
        public MotionLessonShot shot=new MotionLessonShot();
        public GameObject subjectPrefab;public Font koreanFont;public Camera stageCamera;
        [NonSerialized] public MotionTeachingStage movement;
        readonly List<UnityEngine.Object> owned=new List<UnityEngine.Object>();
        readonly List<LineRenderer> guides=new List<LineRenderer>();int guideCursor;
        Material guideMaterial;Text diagramLabel;
        public double previewSeconds;
        [ContextMenu("Preview saved teaching time")] public void PreviewAtTime(){Evaluate(previewSeconds);}
        void OnEnable(){koreanFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",42);foreach(var label in GetComponentsInChildren<Text>(true))label.font=koreanFont;}
        public void RememberMaterial(Material material){owned.Add(material);}
        public void Build(){
            if(movement!=null)return;
            if(shot.steps.Length==0)throw new InvalidOperationException("Explicit source-linked teaching steps required.");
            while(transform.childCount>0)DestroyImmediate(transform.GetChild(0).gameObject);
            guides.Clear();owned.Clear();guideCursor=0;
            var child=new GameObject("SharedAnalyticMotionStage");child.transform.SetParent(transform,false);
            movement=child.AddComponent<MotionTeachingStage>();movement.shot=shot.motion;movement.subjectPrefab=subjectPrefab;movement.koreanFont=koreanFont;movement.Build();stageCamera=movement.stageCamera;
            owned.Add(movement.GuideMaterial);
            guideMaterial=new Material(Shader.Find("Universal Render Pipeline/Unlit"));guideMaterial.SetColor("_BaseColor",Color.white);owned.Add(guideMaterial);
            var canvas=movement.GetComponentInChildren<Canvas>();var label=new GameObject("DiagramCaption");label.transform.SetParent(canvas.transform,false);var rt=label.AddComponent<RectTransform>();rt.anchorMin=rt.anchorMax=rt.pivot=new Vector2(0,1);rt.anchoredPosition=new Vector2(1120,-665);rt.sizeDelta=new Vector2(700,145);diagramLabel=label.AddComponent<Text>();diagramLabel.font=koreanFont;diagramLabel.fontSize=40;diagramLabel.color=new Color(.96f,.96f,.96f);diagramLabel.horizontalOverflow=HorizontalWrapMode.Wrap;diagramLabel.verticalOverflow=VerticalWrapMode.Truncate;
        }
        public void Evaluate(double cueSeconds){
            if(shot.durationSeconds<=0)throw new InvalidOperationException("An actual duration or labelled preview duration is required.");
            double u=Math.Max(0,Math.Min(1,cueSeconds/shot.durationSeconds));
            if(shot.stepSeconds.Length>0){
                var times=shot.stepSeconds;var values=shot.stepPositions;
                if(times.Length<2||values.Length!=times.Length||Math.Abs(times[0])>1e-8||Math.Abs(times[times.Length-1]-shot.durationSeconds)>.001||Math.Abs(values[0])>1e-8||Math.Abs(values[values.Length-1]-1)>1e-8)throw new InvalidOperationException("Incomplete speech map.");
                for(int i=1;i<times.Length;i++){
                    if(times[i]<=times[i-1]||values[i]<values[i-1]||double.IsNaN(times[i])||double.IsNaN(values[i]))throw new InvalidOperationException("Invalid speech map.");
                    if(cueSeconds>=times[i-1])u=values[i-1]+(values[i]-values[i-1])*Math.Max(0,Math.Min(1,(cueSeconds-times[i-1])/(times[i]-times[i-1])));
                }
            }
            EvaluateNormalized(u,cueSeconds<3);
        }
        public void EvaluateNormalized(double u,bool expanded=true){
            if(movement==null)Build();
            if(u<0||u>1||double.IsNaN(u))throw new ArgumentOutOfRangeException(nameof(u));
            int index=Math.Min(shot.steps.Length-1,(int)(u*shot.steps.Length));double fraction=Math.Min(1,u*shot.steps.Length-index);
            var step=shot.steps[index];movement.shot=step.motionOverride??shot.motion;double time=step.modelFrom+(step.modelTo-step.modelFrom)*fraction;
            if(time<movement.shot.startTime-1e-8||time>movement.shot.endTime+1e-8)throw new InvalidOperationException("Model cue outside plotted domain.");
            movement.shot.termExpanded=expanded;movement.shot.secantH=step.secantH;movement.shot.showSecant=step.showSecant;movement.shot.showTangent=step.showTangent;
            movement.Evaluate((time-movement.shot.startTime)/(movement.shot.endTime-movement.shot.startTime));
            movement.SetExplanation(step.formula,step.meaning);
            Diagram(index,fraction,time);
        }
        void Path(Color c,params Vector3[] p){LineRenderer line;if(guideCursor==guides.Count){var go=new GameObject("SourceDiagramGuide"+guideCursor);go.transform.SetParent(transform,false);line=go.AddComponent<LineRenderer>();line.sharedMaterial=guideMaterial;line.useWorldSpace=true;line.numCapVertices=5;guides.Add(line);}else line=guides[guideCursor];guideCursor++;line.gameObject.SetActive(true);line.startWidth=line.endWidth=.045f;line.positionCount=p.Length;line.SetPositions(p);var props=new MaterialPropertyBlock();props.SetColor("_BaseColor",c);line.SetPropertyBlock(props);}
        void DiagramArrow(Color color,Vector3 start,Vector3 end){Path(color,start,end);var direction=(end-start).normalized;var side=Vector3.Cross(direction,Vector3.forward).normalized;Path(color,end-direction*.2f+side*.11f,end,end-direction*.2f-side*.11f);}
        void Ring(Color color,Vector3 centre,float radius=.10f){var p=new Vector3[33];for(int i=0;i<p.Length;i++){float a=i*Mathf.PI*2/32;p[i]=centre+new Vector3(Mathf.Cos(a),Mathf.Sin(a),0)*radius;}Path(color,p);}
        void Diagram(int step,double phase,double time){
            guideCursor=0;diagramLabel.text="";var yellow=new Color(.91f,.812f,.514f);var teal=new Color(.451f,.78f,.761f);var red=new Color(.937f,.522f,.522f);Vector3 o=new Vector3(3,1.3f,-.3f);
            string mode=shot.diagramMode;
            if(mode=="units"||mode=="length-conversion"||mode=="speed-conversion"){
                if(mode=="units"){
                    int dimensions=step==0?2:3;var q=Quaternion.Euler(22,-28,0);var pts=new Vector3[8];for(int i=0;i<8;i++)pts[i]=o+q*new Vector3((i&1)*2,(i>>1&1)*2,(i>>2&1)*2);
                    int[,] edges={{0,1},{0,2},{1,3},{2,3},{0,4},{1,5},{2,6},{3,7},{4,5},{4,6},{5,7},{6,7}};
                    if(step<2){for(int i=0;i<(dimensions==2?4:12);i++)Path(i<4?yellow:teal,pts[edges[i,0]],pts[edges[i,1]]);diagramLabel.text=dimensions==2?"1 m × 1 m → 1 m²\n길이 둘을 곱한 넓이":"1 m × 1 m × 1 m → 1 m³\n길이 셋을 곱한 부피";}
                    else {Path(yellow,o+Vector3.up,o+Vector3.up+Vector3.right*4);Path(teal,o,o+Vector3.right*4);diagramLabel.text="속도: m/s\n가속도: (m/s)/s = m/s²";}
                }else{
                    Vector3 a=o+Vector3.left*.9f,b=o+Vector3.right*3.5f;Path(yellow,a,b);Path(yellow,a+Vector3.up*.15f,a-Vector3.up*.15f);Path(yellow,b+Vector3.up*.15f,b-Vector3.up*.15f);
                    for(int i=0;i<=10;i++){var point=Vector3.Lerp(a,b,i/10f);Path(teal,point+Vector3.down*.7f,point+Vector3.down*(i%5==0?1.05f:.9f));}
                    Path(teal,a+Vector3.down*.7f,b+Vector3.down*.7f);
                    diagramLabel.text=mode=="length-conversion"?"14.57 m = 약 47.80 ft\n물리적 길이는 같습니다":"188 km/h = 약 171.33 ft/s\n동일한 운동 · 서로 다른 눈금";
                }
            }else if(mode=="frequency"){
                var p=new Vector3[129];for(int i=0;i<p.Length;i++){double t=i/32.0;p[i]=new Vector3(1.8f+(float)t*1.5f,2.0f+(float)Math.Sin(2*Math.PI*t)*.65f,-.3f);}Path(teal,p);
                float current=1.8f+(float)Math.Min(4,time)*1.5f;Path(yellow,new Vector3(current,1.1f,-.5f),new Vector3(current,2.9f,-.5f));diagramLabel.text="진동 주기: 1초\n모형 시간 "+time.ToString("0.00")+" s · 1 Hz";
            }else if(mode=="point-coordinate"){
                Path(yellow,o,o+Vector3.right*2.7f);Path(teal,o,o+Vector3.up*2.2f);Path(red,o,o+new Vector3(-1,-.8f,0));diagramLabel.text="같은 추적점 p = (x, y, z)\nx 가로 · y 세로 · z 깊이";
            }else if(mode=="mass-weight"){
                float length=1.1f+(float)phase*1.1f;var tip=o-Vector3.up*length;Path(red,o+Vector3.up*.8f,tip);Path(red,tip+new Vector3(-.18f,.3f,0),tip,tip+new Vector3(.18f,.3f,0));diagramLabel.text="질량 m은 그대로\n중력 g가 달라지면 W=mg 변화";
            }else if(mode=="unit-dimensions"){
                Path(yellow,new Vector3(2,2.3f,0),new Vector3(7,2.3f,0));Path(teal,new Vector3(2,1.3f,0),new Vector3(7,1.3f,0));Path(red,new Vector3(2,.3f,0),new Vector3(7,.3f,0));diagramLabel.text="L : 길이   T : 시간   M : 질량\n속도 L/T · 가속도 L/T²";
            }else if(mode=="sampled-path"){
                var curve=new Vector3[81];for(int i=0;i<curve.Length;i++){float t=i*.05f;curve[i]=new Vector3(1.8f+t*1.5f,1+(-t*t+6*t-1)*.16f,0);}Path(teal,curve);
                for(int i=0;i<=8;i++){float t=i*.5f;var p=new Vector3(1.8f+t*1.5f,1+(-t*t+6*t-1)*.16f,-.2f);Path(yellow,p+Vector3.left*.08f,p+Vector3.right*.08f);Path(yellow,p+Vector3.down*.08f,p+Vector3.up*.08f);}
                diagramLabel.text="연속 경로 + 일정 간격의 표본\nΔt가 계산 간격입니다";
            }else if(mode=="relative-motion"){
                float[] lengths={3,.6f,3.6f};for(int i=0;i<3;i++){var a=new Vector3(2,3-i,0);var b=a+Vector3.right*lengths[i];var c=i==0?yellow:i==1?teal:red;Path(c,a,b);Path(c,b+new Vector3(-.2f,.12f,0),b,b+new Vector3(-.2f,-.12f,0));}
                diagramLabel.text="기차 10 + 안에서 걷기 2\n지면에서 12 m/s\n회전하지 않는 같은 기준축";
            }else if(mode=="function-flow"){
                for(int i=0;i<3;i++){var p=new Vector3(2.5f+2*i,2,0);var ring=new Vector3[33];for(int k=0;k<ring.Length;k++){float angle=k*Mathf.PI*2/32;ring[k]=p+new Vector3(Mathf.Cos(angle),Mathf.Sin(angle),0)*.45f;}Path(i==1?yellow:teal,ring);if(i<2){var from=p+Vector3.right*.45f;var to=p+Vector3.right*1.55f;Path(teal,from,to);Path(teal,to+new Vector3(-.2f,.1f,0),to,to+new Vector3(-.2f,-.1f,0));}}
                diagramLabel.text="입력 → 함수의 값 → 변화율\n미분 기호는 관계를 읽는 표기";
            }else if(mode=="accumulation"){
                var a=new Vector3(3.3f,.5f,0);Path(yellow,a+Vector3.up*3,a,a+Vector3.right*2,a+new Vector3(2,3,0));
                if(step==0){float height=.3f+(float)phase*2.3f;Path(teal,a+Vector3.up*height,a+new Vector3(2,height,0));diagramLabel.text="물 높이 h(t)가 쌓입니다\nh′(t)는 높이가 쌓이는 빠르기";}
                else {int count=4+(int)(phase*8);for(int i=0;i<count;i++){var p=a+new Vector3(.35f+(i%3)*.55f,.35f+(i/3)*.65f,-.1f);Path(teal,p+Vector3.left*.06f,p+Vector3.right*.06f);}diagramLabel.text="T·V 일정인 이상기체 모형\n기체의 양 n ↑ → 압력 P ↑";}
            }else if(mode=="circle-difference"){
                bool shrinking=shot.motion.koreanTerm!="속도 벡터의 차이";
                double delta=shrinking?.8*(1-phase)+.015*phase:.8;
                var centre=new Vector3(3.8f,2.9f,0);float radius=1.4f;var p0=centre+Vector3.right*radius;var p1=centre+new Vector3((float)Math.Cos(delta),(float)Math.Sin(delta),0)*radius;
                Ring(teal,centre,radius);Path(yellow,centre,p0,p1,centre);var arc=new Vector3[41];for(int i=0;i<arc.Length;i++){double a=delta*i/40;arc[i]=centre+new Vector3((float)Math.Cos(a),(float)Math.Sin(a),-.1f)*radius;}Path(red,arc);
                var basePoint=new Vector3(6.9f,1.1f,0);var v1=Vector3.up*1.8f;var v2=new Vector3(-(float)Math.Sin(delta),(float)Math.Cos(delta),0)*1.8f;
                DiagramArrow(teal,basePoint,basePoint+v1);DiagramArrow(yellow,basePoint,basePoint+v2);DiagramArrow(red,basePoint+v1,basePoint+v2);
                double chord=4*Math.Sin(delta/2),length=2*delta;
                diagramLabel.text="r=2, |v|=2, Δt="+delta.ToString("0.000")+"s\n현="+chord.ToString("0.000")+" · 호="+length.ToString("0.000")+"m\n빨강: Δv (같은 출발점에서 비교)";
            }else if(mode=="circle-values"){
                var model=movement.shot.parameters;double speed=Math.Abs(model.radius*model.omega),acc=model.radius*model.omega*model.omega;
                var centre=new Vector3(4.6f,2.5f,0);float radius=(float)(model.radius*.19);Ring(teal,centre,radius);double angle=model.omega*time;var at=centre+new Vector3((float)Math.Cos(angle),(float)Math.Sin(angle),0)*radius;Ring(yellow,at);
                DiagramArrow(red,at,at+(centre-at).normalized*(float)(acc*.018));
                diagramLabel.text="s="+speed.ToString("0")+" m/s · r="+model.radius.ToString("0")+" m\na="+acc.ToString("0")+" m/s²\n빨강 화살표 축척 고정";
            }else if(mode=="earth-latitude"||mode=="orbital-radius"){
                var centre=new Vector3(4.8f,2.6f,0);float earth=1.6f;Ring(teal,centre,earth);Path(teal,centre+Vector3.up*2,centre-Vector3.up*2);
                if(mode=="earth-latitude"){
                    double latitude=step==0?0:phase*Math.PI*.46;float y=(float)Math.Sin(latitude)*earth,rad=(float)Math.Cos(latitude)*earth;Path(yellow,centre+Vector3.up*y,centre+new Vector3(rad,y,0));Ring(yellow,centre+new Vector3(rad,y,0));
                    diagramLabel.text="위도="+(latitude*180/Math.PI).ToString("0")+"°\n자전 반지름=R cos(위도)\n지구 중심이 아닌 자전축까지 거리";
                }else{
                    float orbit=earth*(6711f/6371);Ring(yellow,centre,orbit);double angle=phase*Math.PI*2;var satellite=centre+new Vector3((float)Math.Cos(angle),(float)Math.Sin(angle),0)*orbit;Ring(yellow,satellite,.08f);Path(red,centre,satellite);
                    diagramLabel.text="R=6371 km, h=340 km\nr=R+h=6711 km\n반지름 비율은 실제 예제대로";
                }
            }else if(mode=="rotating-frame"){
                var centre=new Vector3(4.4f,2.5f,0);Ring(teal,centre,1.45f);var at=centre+Vector3.right*1.45f;Ring(yellow,at);DiagramArrow(teal,at,at+Vector3.up*1.5f);
                DiagramArrow(step==0?red:yellow,at,at+Vector3.right*(step==0?-1.2f:1.2f));
                diagramLabel.text=step==0?"지면 기준: 청록은 순간 속도\n빨강은 실제 안쪽 가속도":"차와 함께 도는 좌표계\n노랑: 바깥쪽 원심 관성력\n두 좌표계의 힘을 합치지 않습니다";
            }else if(mode=="rotation-axis"||mode=="shared-angular"){
                var centre=new Vector3(4.6f,2.4f,0);Ring(teal,centre,1.5f);double angle=movement.shot.parameters.omega*time;var radial=new Vector3((float)Math.Cos(angle),(float)Math.Sin(angle),0);
                if(mode=="rotation-axis"){
                    var at=centre+radial*1.5f;DiagramArrow(yellow,centre,at);DiagramArrow(teal,at,at+new Vector3(-radial.y,radial.x,0));Ring(red,centre,.2f);Ring(red,centre,.04f);
                    diagramLabel.text="축 ω⃗: 화면 밖 ⊙\n노랑 r⃗ · 청록 v=ω⃗×r⃗\n오른손 좌표 약속의 해설 도식";
                }else{
                    Ring(teal,centre,.75f);for(int k=1;k<=2;k++){var at=centre+radial*.75f*k;Ring(yellow,at);DiagramArrow(k==1?teal:red,at,at+new Vector3(-radial.y,radial.x,0)*.5f*k);}
                    diagramLabel.text="같은 시간에 같은 각도 회전\nr 2배 → 접선 속력 2배\n각속도는 두 점에서 같습니다";
                }
            }else if(mode=="unobserved-axis"){
                var origin=new Vector3(3,1.5f,0);float parallel=(float)phase*3;DiagramArrow(yellow,origin,origin+Vector3.right*2);DiagramArrow(teal,origin+Vector3.right*2,origin+new Vector3(2,2,0));DiagramArrow(red,origin+Vector3.up*2.5f,origin+new Vector3(parallel,2.5f,0));
                diagramLabel.text="r⃗=(2,0,0), ω⃗=("+parallel.ToString("0.0")+",0,3)\nv=ω⃗×r⃗=(0,6,0)\n빨강 평행 성분을 바꿔도 v는 같음";
            }else if(mode=="viewpoint-angular"){
                var centre=new Vector3(4.8f,1.4f,0);float x=-3+6*(float)phase;var at=centre+new Vector3(x,1.3f,0);Path(teal,centre+new Vector3(-3,1.3f,0),centre+new Vector3(3,1.3f,0));Ring(yellow,at);Ring(red,centre,.12f);Path(yellow,centre,at);DiagramArrow(teal,at,at+Vector3.right*.8f);
                double angular=1.3/(x*x+1.3*1.3);diagramLabel.text="고정점에서 본 직선 이동\n|v|=1 m/s · 거리 y=1.3 m\n|ω관측|="+angular.ToString("0.000")+" rad/s";
            }else if(mode=="pressure-units"){
                var a=new Vector3(3.5f,1.3f,0);Path(yellow,a,a+Vector3.right*2.3f,a+new Vector3(2.3f,2.3f,0),a+Vector3.up*2.3f,a);DiagramArrow(red,a+new Vector3(1.15f,3,0),a+new Vector3(1.15f,1.2f,0));
                diagramLabel.text="1 in²=(0.0254 m)²\n힘 1 lbf=4.448221615 N\n같은 압력을 다른 단위로 표시";
            }else if(mode=="arrival-roots"){
                var origin=new Vector3(2,1,0);var curve=new Vector3[81];for(int k=0;k<curve.Length;k++){float t=2*k/80f;curve[k]=origin+new Vector3(t*3,(4*t-2*t*t),0);}Path(teal,curve);
                float target=step==0?2.6f:step==1?2:1.5f;Path(yellow,origin+Vector3.up*target,origin+new Vector3(6,target,0));if(step==1)Ring(red,origin+new Vector3(3,2,0),.14f);if(step==2){Ring(red,origin+new Vector3(1.5f,1.5f,0),.14f);Ring(red,origin+new Vector3(4.5f,1.5f,0),.14f);}
                diagramLabel.text=step==0?"목표 높이 2.6m > 최대 2m\n교점 없음 · 판별식 < 0":step==1?"목표 높이 2m\n정점에서 한 번 접함 · 판별식 = 0":"목표 높이 1.5m\n두 시간 후보 · 판별식 > 0";
            }else if(mode=="complex-unit-circle"){
                var centre=new Vector3(4.8f,2.5f,0);float scale=1.55f;Ring(teal,centre,scale);Path(yellow,centre-Vector3.right*1.9f,centre+Vector3.right*1.9f);Path(red,centre-Vector3.up*1.9f,centre+Vector3.up*1.9f);var at=centre+new Vector3((float)Math.Cos(time),(float)Math.Sin(time),0)*scale;Ring(yellow,at);Path(teal,centre,at,new Vector3(at.x,centre.y,0));
                diagramLabel.text="가로: 실수 cos x · 세로: 허수 sin x\nx="+time.ToString("0.00")+" rad\ncos²x+sin²x=1";
            }else if(mode=="jump-target"||mode=="launch-components"||mode=="range-comparison"||mode=="gravity-projection"){
                var origin=new Vector3(2,-.3f,0);Func<double,double,Vector3> point=(x,y)=>origin+new Vector3((float)x*.9f,(float)y*.9f,0);
                if(mode=="range-comparison"){
                    // Same angle and gravity; speed doubled means both the
                    // flight duration and horizontal velocity are doubled.
                    for(int variant=0;variant<2;variant++){
                        double speed=variant==0?1:2,finish=2*speed;var p=new Vector3[81];
                        for(int k=0;k<p.Length;k++){double t=finish*k/80.0;p[k]=new Vector3(2+(float)(3*speed*t)*.24f,.5f+(float)(4*speed*t-2*t*t)*.24f,0);}Path(variant==0?teal:yellow,p);
                        double current=phase*finish;Ring(variant==0?teal:yellow,new Vector3(2+(float)(3*speed*current)*.24f,.5f+(float)(4*speed*current-2*current*current)*.24f,0));
                    }
                    diagramLabel.text="해설 모형 · R: 6 m → 24 m\n같은 각도·중력·착지 높이";
                }else if(mode=="gravity-projection"){
                    Vector3 centre=new Vector3(4.5f,2,0),g=new Vector3(.6f,-.8f,0),d=new Vector3(2,1,0),projection=g*Vector3.Dot(d,g);
                    DiagramArrow(red,centre,centre+g*2);DiagramArrow(yellow,centre,centre+d);DiagramArrow(teal,centre,centre+projection);Path(teal,centre+d,centre+projection);
                    diagramLabel.text="빨강: 가속도 방향\n노랑: 목표 변위 · 청록: 투영\n후보 시간 → 전체 위치 확인";
                }else{
                    var p=new Vector3[81];for(int k=0;k<p.Length;k++){double t=2*k/80.0;p[k]=point(3*t,4*t-2*t*t);}Path(teal,p);
                    double tNow=2*phase;var at=point(3*tNow,4*tNow-2*tNow*tNow);Ring(yellow,at);
                    if(mode=="launch-components"){
                        var v0=origin+new Vector3(3,4,0)*.55f;DiagramArrow(yellow,origin,v0);DiagramArrow(teal,origin,origin+Vector3.right*1.65f);DiagramArrow(red,origin+Vector3.right*1.65f,v0);
                        diagramLabel.text="노랑: 초기 속도 벡터\n청록: 수평 · 빨강: 수직 성분";
                    }else{
                        float h=1.5f;Path(yellow,point(0,h),point(6,h));Ring(yellow,point(1.5,h),.14f);Ring(yellow,point(4.5,h),.14f);
                        var target=point(4,h);Path(red,target+new Vector3(-.13f,-.13f,0),target+new Vector3(.13f,.13f,0));Path(red,target+new Vector3(-.13f,.13f,0),target+new Vector3(.13f,-.13f,0));
                        diagramLabel.text="y=1.5m: t=0.5 또는 1.5s\nx=1.5 또는 4.5m\n목표 (4,1.5)m에는 적중하지 않음";
                    }
                }
            }else if(mode=="flow-accumulation"){
                var origin=new Vector3(3,.2f,0);Path(yellow,origin+Vector3.up*3,origin,origin+Vector3.right*3,origin+new Vector3(3,3,0));
                if(step==0){float length=(float)phase*3;Path(teal,origin+new Vector3(0,1,0),origin+new Vector3(length,1,0),origin+new Vector3(length,1.8f,0),origin+new Vector3(0,1.8f,0));DiagramArrow(teal,origin+Vector3.up*2.4f,origin+new Vector3(2.4f,2.4f,0));diagramLabel.text="천: 공급 속도 → 통과한 길이\n해설용 일정 속도 모형";}
                else {float height=step==1?.2f+(float)phase*2.3f:2.5f-(float)phase*2.3f;Path(teal,origin+Vector3.up*height,origin+new Vector3(3,height,0));DiagramArrow(step==1?teal:red,origin+new Vector3(1.5f,3.5f,0),origin+new Vector3(1.5f,2.8f,0));diagramLabel.text=step==1?"유량을 쌓으면 받은 물의 부피\nL/s × s = L":"소모량은 증가 · 남은 연료는 감소\n누적 사용량과 잔량을 구별";}
            }else if(mode=="slope"||mode=="signed-slope"){
                bool declining=mode=="signed-slope"||step>0;var curve=new Vector3[81];
                for(int i=0;i<curve.Length;i++){float x=i/80f;float y=declining?(4*x*x-10*x+10)/4:1.6f+Mathf.Sin(x*Mathf.PI*2)*.7f;curve[i]=new Vector3(1.8f+x*6,y,0);}Path(yellow,curve);
                float u=(float)phase;float value=declining?(4*u*u-10*u+10)/4:1.6f+Mathf.Sin(u*Mathf.PI*2)*.7f;float slope=declining?(8*u-10)/24:Mathf.Cos(u*Mathf.PI*2)*.7f*Mathf.PI/3;var at=new Vector3(1.8f+u*6,value,-.1f);Path(teal,at-new Vector3(.6f,.6f*slope,0),at+new Vector3(.6f,.6f*slope,0));
                diagramLabel.text=declining?"감소하지만 기울기는 0에 접근\n설명용 매끄러운 곡선":"입력은 가로 위치\n접선: 오르막·내리막·평평함";
            }
            for(int i=guideCursor;i<guides.Count;i++)guides[i].gameObject.SetActive(false);
            diagramLabel.gameObject.SetActive(diagramLabel.text.Length>0);
        }
    }
}

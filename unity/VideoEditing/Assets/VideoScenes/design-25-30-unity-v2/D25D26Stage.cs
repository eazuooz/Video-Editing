using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.DesignVisualV2 {
// Deterministic, cut-local explanatory mechanisms. No vendor files are edited.
public class D25D26Stage : DesignLessonStage {
    GameObject a, b, c, die, attackLine, targetLine, routeLine;
    readonly List<GameObject> blocks = new List<GameObject>();
    readonly List<GameObject> scenery = new List<GameObject>();
    readonly List<GameObject> marks = new List<GameObject>();
    readonly List<Vector3> sceneryOrigins = new List<Vector3>();
    readonly List<Text> labels = new List<Text>();
    readonly List<RawImage> photos = new List<RawImage>();
    readonly List<GameObject> branches = new List<GameObject>();
    Text result, ticker;
    Image fill;
    float duration;
    static readonly Color Dark = new Color(.025f,.030f,.030f,1);
    static readonly Color Muted = new Color(.44f,.44f,.32f,1);
    static readonly Color BlockA = new Color(.93f,.28f,.34f,1);
    static readonly Color BlockB = new Color(.22f,.76f,.54f,1);
    void SolidTint(GameObject obj, Color color) {
        var material=Mat(color);
        foreach(var renderer in obj.GetComponentsInChildren<Renderer>(true)) {
            var slots=renderer.sharedMaterials;
            for(int i=0;i<slots.Length;i++)slots[i]=material;
            renderer.sharedMaterials=slots;
        }
    }
    void Paint(GameObject obj, Color color) {
        foreach(var rr in obj.GetComponentsInChildren<Renderer>(true)) {
            var pb=new MaterialPropertyBlock();rr.GetPropertyBlock(pb);
            pb.SetColor("_BaseColor",color);pb.SetColor("_Color",color);rr.SetPropertyBlock(pb);
        }
    }
    float E(float t,float start,float end) {return Mathf.SmoothStep(0,1,Mathf.InverseLerp(start,end,t));}
    void Visible(GameObject o,bool value) {if(o!=null)o.SetActive(value);}
    void SetLine(GameObject o, params Vector3[] p) {var r=o.GetComponent<LineRenderer>(); if(r!=null){r.positionCount=p.Length;r.SetPositions(p);}}
    void Floor() {Box("Dark demonstration stage",new Vector3(0,-.15f,.5f),new Vector3(16,.18f,7),Dark);}
    void Footer(string s) {Label(s,960,825,44,White,1660,60);}
    Text Keep(string s,float x,float y,int size=44,Color? colour=null,float width=780) {
        var q=Label(s,x,y,size,colour,width,70);labels.Add(q);return q;
    }
    void ActorPair(float x1=-3,float x2=3) {
        a=Actor("우리 모형 CP",new Vector3(x1,0,0),false,2.7f,0);
        b=Actor("우리 모형 상대",new Vector3(x2,0,0),true,2.7f,180);
        Line("Actor baseline",new[]{new Vector3(-6,.02f,-.1f),new Vector3(6,.02f,-.1f)},Grey,.035f);
    }
    void BlockSet(int count=2,float spacing=3.2f,float offset=0,float size=1.65f) {
        for(int i=0;i<count;i++) {
            float x=offset+(i-(count-1)*.5f)*spacing;
            var block=Box("정보 블록 "+i,new Vector3(x,1.45f,0),Vector3.one*size,i%2==0?BlockA:BlockB);
            blocks.Add(block);
            Box("블록 받침 "+i,new Vector3(x,.35f,0),new Vector3(size+.15f,.3f,size+.15f),new Color(.13f,.15f,.15f));
        }
    }
    void BlockObserver() {a=Actor("블록을 구별하는 플레이어",new Vector3(-5.7f,0,.4f),false,2.1f,105);}
    void Forest(float offset=0,float scale=1) {
        a=Actor("길을 읽는 플레이어",new Vector3(offset-2.1f*scale,0,-.4f),false,2.1f*scale,85);
        c=Asset("chest",new Vector3(offset+3.0f*scale,0,0),1.45f*scale,200);
        for(int i=0;i<5;i++) {
            var tr=Asset("tree",new Vector3(offset+(i-2)*2.1f*scale,0,2.2f),3.4f*scale,30*i);
            scenery.Add(tr);sceneryOrigins.Add(tr.transform.position);
        }
        routeLine=Line("진행할 길",new[]{new Vector3(offset-2.1f*scale,.04f,-.45f),new Vector3(offset,.04f,-.2f),new Vector3(offset+3*scale,.04f,0)},Yellow,.08f);
    }
    RawImage Photo(string path,float x,float y,float w,float h) {
        var anchor=RectUI(x,y,w,h,Color.black);
        var child=new GameObject("Inspected independent screenshot",typeof(RectTransform),typeof(RawImage));
        child.transform.SetParent(anchor.transform,false);child.layer=29;
        var rt=child.GetComponent<RectTransform>();rt.anchorMin=Vector2.zero;rt.anchorMax=Vector2.one;rt.offsetMin=Vector2.zero;rt.offsetMax=Vector2.zero;
        var im=child.GetComponent<RawImage>();
        var file=Path.Combine("D:/Github/VideoEditing/projects/limited-color-world/production/local/batch-v1/visual-assets",path);
        if(!File.Exists(file))throw new FileNotFoundException("Required inspected screenshot missing",file);
        var tex=ReferenceTexture(file);im.texture=tex;
        var fit=child.AddComponent<AspectRatioFitter>();fit.aspectMode=AspectRatioFitter.AspectMode.FitInParent;fit.aspectRatio=(float)tex.width/tex.height;
        photos.Add(im);return im;
    }
    void MarkShape(int index,string shape) {
        var pos=blocks[index].transform.position;float z=pos.z-.85f,y=pos.y;
        var points=new List<Vector3>();
        if(shape=="circle") {for(int k=0;k<=40;k++){float q=k*Mathf.PI*2/40;points.Add(new Vector3(pos.x+Mathf.Cos(q)*.42f,y+Mathf.Sin(q)*.42f,z));}}
        else if(shape=="triangle")points.AddRange(new[]{new Vector3(pos.x,y+.5f,z),new Vector3(pos.x-.48f,y-.35f,z),new Vector3(pos.x+.48f,y-.35f,z),new Vector3(pos.x,y+.5f,z)});
        else {for(int k=-1;k<=1;k++) {marks.Add(Line("같은 종류의 줄무늬 "+k,new[]{new Vector3(pos.x-.45f,y+k*.28f,z),new Vector3(pos.x+.45f,y+k*.28f,z)},Dark,.085f));} return;}
        marks.Add(Line("같은 종류의 "+shape,points.ToArray(),Dark,.085f));
    }
    void Grid(float from=-3,float to=3) {
        for(float x=from;x<=to+.1f;x+=1)Line("한 칸 격자 "+x,new[]{new Vector3(x,.025f,-1.5f),new Vector3(x,.025f,1.2f)},Grey,.03f);
        Line("격자 기준",new[]{new Vector3(from,.025f,-1.5f),new Vector3(to,.025f,-1.5f)},Grey,.03f);
    }
    GameObject Arrow(string name,Vector3 start,Vector3 end,Color colour) {
        var v=(end-start).normalized;var side=Vector3.Cross(v,Vector3.up).normalized*.24f;
        return Line(name,new[]{start,end,end-v*.4f+side,end,end-v*.4f-side},colour,.07f);
    }
    void Die() {
        die=Box("설명용 주사위",new Vector3(-1.35f,1.5f,0),Vector3.one*1.5f,White);
        for(int row=0;row<3;row++)for(int col=0;col<2;col++){
            var pip=Sphere("주사위 눈",new Vector3(-1.35f+(col-.5f)*.64f,1.5f+(row-1)*.43f,-.77f),.18f,Dark);
            pip.transform.SetParent(die.transform,true);
        }
    }

    public override void Build() {
        duration=frames/60f;
        if(slug=="limited-color-world")BuildColour();else BuildAi();
        Apply(0);
    }
    void BuildColour() {
        switch(cutId) {
        case "cut002": case "cut004":
            Title("색만 다르면, 구분할 수 있을까?");BlockSet();BlockObserver();
            Keep("종류 A",730,730,44,White,350);Keep("종류 B",1190,730,44,White,350);
            result=Label("같은 모양 · 다른 종류",960,210,44,White,1450,70);break;
        case "cut003":
            Title("색을 빼도, 필요한 정보는 남아야 합니다");
            Photo("puyo.jpg",420,470,500,380);Photo("flower.jpg",960,470,500,380);Photo("mario-gray.jpg",1500,470,500,380);
            Keep("구분할 단서",420,720,44,Teal,500);Keep("중요한 대상",960,720,44,Yellow,500);Keep("시선의 순서",1500,720,44,Green,500);
            a=Actor("검사하는 플레이어",new Vector3(0,0,-2),false,1.2f,180);break;
        case "cut006":
            Title("블록만 보지 말고, 배경도 함께");BlockSet();
            scenery.Add(Box("밝은 테마",new Vector3(-1.6f,1.5f,1.15f),new Vector3(2.8f,3.6f,.2f),new Color(.6f,.7f,.58f)));
            scenery.Add(Box("어두운 테마",new Vector3(1.6f,1.5f,1.15f),new Vector3(2.8f,3.6f,.2f),new Color(.12f,.14f,.13f)));
            Asset("tree",new Vector3(-4.7f,0,1.5f),2.9f,15);Asset("chest",new Vector3(4.7f,0,.5f),1.5f,180);
            Keep("밝은 테마",720,745,44,White,400);Keep("어두운 테마",1200,745,44,White,400);break;
        case "cut008":
            Title("어느 경계가 사라졌나요?");BlockSet();BlockObserver();
            scenery.Add(Box("배경",new Vector3(0,1.4f,1),new Vector3(7,3.3f,.15f),Muted*.62f));
            Keep("블록 ↔ 블록",700,740,44,Teal,600);Keep("블록 ↔ 배경",1260,740,44,Yellow,600);
            attackLine=Line("블록끼리",new[]{new Vector3(-.7f,1.5f,-.9f),new Vector3(.7f,1.5f,-.9f)},Teal,.075f);
            targetLine=Line("배경 경계",new[]{new Vector3(2.5f,.55f,-.9f),new Vector3(2.5f,2.35f,-.9f)},Yellow,.075f);break;
        case "cut009":
            Title("한 가지 조건에서만 확인하지 않기");BlockSet(4,2.45f,0,1.45f);
            Keep("Protanopia-type",550,245,44,Teal,800);Keep("Deuteranopia-type",1370,245,44,Yellow,800);
            Keep("검사 조건 1",550,735,44,White,600);Keep("검사 조건 2",1370,735,44,White,600);
            result=Label("같은 테스트 장면을 두 조건에서 확인",960,825,44,White,1500,60);
            a=Actor("두 조건을 확인하는 플레이어",new Vector3(-5.8f,0,.5f),false,2.0f,90);break;
        case "cut011":
            Title("색이 비슷해도, 밝기는 다르게");BlockSet();BlockObserver();
            Keep("어두운 블록",700,735,44,White,500);Keep("밝은 블록",1220,735,44,White,500);
            result=Label("명도 차이",960,240,44,Yellow,900,70);break;
        case "cut013":
            Title("너무 어두우면 배경 속으로 묻힙니다");BlockSet();
            scenery.Add(Box("어두운 뒤 벽",new Vector3(0,1.5f,1.2f),new Vector3(7.5f,3.7f,.3f),new Color(.07f,.075f,.075f)));
            Asset("chest",new Vector3(-5,0,.7f),1.5f,170);
            Keep("배경에 묻힘",700,735,44,Red,520);Keep("경계가 남음",1220,735,44,Green,520);break;
        case "cut015":
            Title("색과 모양으로, 같은 정보를 두 번");BlockSet(3,3.1f);
            MarkShape(0,"circle");MarkShape(1,"triangle");MarkShape(2,"stripes");
            Keep("동그라미",510,740,44,White,450);Keep("세모",960,740,44,White,450);Keep("줄무늬",1410,740,44,White,450);
            break;
        case "cut027":
            Title("눈은 필요한 순서대로 움직이게");Forest();
            Keep("플레이어",600,760,44,Teal,500);Keep("앞으로 갈 길",1000,760,44,Yellow,500);Keep("중요한 대상",1460,760,44,Green,500);break;
        case "cut029":
            Title("두 검사가 묻는 질문은 다릅니다");BlockSet(2,1.7f,-3.5f,1.2f);Forest(2.8f,.65f);
            foreach(var tr in scenery)SolidTint(tr,new Color(.19f,.2f,.19f));
            SolidTint(c,new Color(.73f,.76f,.73f));SolidTint(a,new Color(.5f,.5f,.5f));
            Keep("색으로 구분되는가?",520,245,44,Teal,760);Keep("무엇이 먼저 보이는가?",1400,245,44,Yellow,820);
            Keep("색 정보",520,770,44,White,600);Keep("명도 · 시각적 위계",1400,770,44,White,800);break;
        case "cut030":
            Title("익숙한 그림도, 다르게 보기");Forest();
            result=Label("익숙해서 놓친 배치 확인",960,825,44,White,1500,60);break;
        default:throw new InvalidOperationException("Unexpected D25 visual replacement "+cutId);
        }
    }
    void BuildAi() {
        switch(cutId) {
        case "cut007":
            Title("움직이는 것과, 상황을 읽는 것은 다릅니다");ActorPair();
            Box("추락 위험",new Vector3(3.5f,-.02f,0),new Vector3(2,.07f,3.8f),Red*.45f);
            targetLine=Line("위험 경계",new[]{new Vector3(2.4f,.04f,-1.8f),new Vector3(2.4f,.04f,1.8f)},Red,.08f);
            result=Label("상황 없는 공격",960,780,44,Red,1500,70);break;
        case "cut009":
            Title("빈틈 없는 즉시 반응");ActorPair();
            result=Label("공격 신호 → 즉시 반응",960,780,44,Red,1500,70);
            attackLine=Arrow("공격 신호",new Vector3(-1.5f,1.5f,0),new Vector3(1.5f,1.5f,0),Yellow);break;
        case "cut017":
            Title("같은 컴퓨터가 주사위와 행동을 처리합니다");
            a=Actor("결과를 보는 플레이어",new Vector3(-5,0,0),false,2.65f,0);
            b=Actor("컴퓨터 상대",new Vector3(5,0,0),true,2.65f,180);
            Die();
            c=Actor("선택할 공격 동작",new Vector3(1.5f,0,0),true,1.9f,180);
            Line("같은 처리 영역",new[]{new Vector3(-3,.25f,-1.1f),new Vector3(-3,3,-1.1f),new Vector3(3,3,-1.1f),new Vector3(3,.25f,-1.1f)},Teal,.055f);
            Keep("주사위 처리",740,720,44,White,550);Keep("행동 선택",1200,720,44,White,550);
            result=Label("규칙의 공정함 + 체감하는 공정함",960,825,44,Yellow,1600,60);
            attackLine=Arrow("처리 후 상대 행동",new Vector3(2.7f,2,0),new Vector3(4.1f,2,0),Teal);break;
        case "cut021":
            Title("위치와 상태를 받아, 다음 행동을 고릅니다");ActorPair();
            Keep("위치",1370,290,44,Yellow,440);Keep("상태",1370,355,44,Green,440);
            attackLine=Arrow("관측 데이터",new Vector3(2.9f,3.2f,0),new Vector3(-2.7f,3.2f,0),Teal);
            result=Label("데이터 → 판단 → 움직임",960,795,44,White,1500,70);break;
        case "cut023":
            Title("거리 · 발생 시점 · 이동 범위를 비교합니다");ActorPair();Grid(-5,5);
            attackLine=Arrow("자기 기술 범위",new Vector3(-3,.1f,-1.2f),new Vector3(0,.1f,-1.2f),Teal);
            targetLine=Arrow("상대 기술 범위",new Vector3(3,.1f,-.7f),new Vector3(1,.1f,-.7f),Red);
            Keep("내 기술",650,760,44,Teal,500);Keep("상대 기술",1270,760,44,Red,500);break;
        case "cut024":
            Title("거리 하나가 공격 결과를 바꿉니다");ActorPair(-2,1);Grid(-3,3);
            attackLine=Line("공격이 닿는 2칸",new[]{new Vector3(-2,.07f,-1.25f),new Vector3(0,.07f,-1.25f)},Teal,.1f);
            targetLine=Line("상대 위치",new[]{new Vector3(1,.07f,-1.6f),new Vector3(1,.07f,1.1f)},Yellow,.06f);
            result=Label("닿지 않음",960,790,46,Red,1450,70);
            Keep("공격 2칸",720,255,44,Teal,620);Keep("상대 3칸",1250,255,44,Yellow,620);break;
        case "cut026":
            Title("같은 거리여도, 상대의 상태가 다르면");ActorPair();Grid(-5,5);
            result=Label("접근 중 → 공격 중 → 대응 선택",960,790,44,White,1500,70);
            attackLine=Arrow("접근",new Vector3(2.5f,.08f,-1.4f),new Vector3(.5f,.08f,-1.4f),Yellow);break;
        case "cut029":
            Title("조건이 겹치면, 판단도 충돌합니다");ActorPair();
            branches.Add(Arrow("접근 조건",new Vector3(-3,.07f,-1.1f),new Vector3(-.4f,.07f,-1.1f),Teal));
            branches.Add(Arrow("후퇴 조건",new Vector3(-3,.07f,-.45f),new Vector3(-5,.07f,-.45f),Red));
            Keep("공격 조건",650,740,44,Teal,600);Keep("위험 조건",1270,740,44,Red,600);break;
        case "cut030":
            Title("먼저 적용할 판단을 정합니다");ActorPair(-1.7f,3.8f);
            branches.Add(Arrow("공격으로 접근",new Vector3(-1.7f,.07f,-1),new Vector3(1,.07f,-1),Teal));
            branches.Add(Arrow("위험으로 후퇴",new Vector3(-1.7f,.07f,-.3f),new Vector3(-4.3f,.07f,-.3f),Red));
            Keep("다가가 공격",1380,250,44,Teal,700);Keep("위험하니 후퇴",540,250,44,Red,700);
            result=Label("서로 다른 판단이 동시에 켜짐",960,800,44,White,1540,70);break;
        case "cut032":
            Title("알아채는 순간과 행동하는 순간 사이");ActorPair();
            Keep("알아챔",440,235,44,Teal,400);Keep("행동 시작",1480,235,44,Yellow,500);
            RectUI(960,330,1040,8,Grey);fill=RectUI(440,330,1,12,Teal);
            for(int i=0;i<=12;i++)RectUI(440+i*1040f/12,330,3,28,Grey);
            ticker=Label("0 / 12 프레임",960,400,44,White,900,70);
            result=Label("12프레임 ÷ 60fps = 0.2초",960,790,46,Yellow,1600,70);
            attackLine=Sphere("알아챈 신호",new Vector3(-3,3.3f,0),.3f,Teal);
            targetLine=Sphere("행동 신호",new Vector3(3,3.3f,0),.3f,Yellow);break;
        case "cut033":
            Title("잠깐의 혼란 뒤, 달라진 상태에 적응");ActorPair(-1,4);
            branches.Add(Arrow("원하는 오른쪽",new Vector3(-1,.08f,-1),new Vector3(1,.08f,-1),Teal));
            branches.Add(Arrow("반대로 움직임",new Vector3(-1,.08f,-.35f),new Vector3(-3,.08f,-.35f),Red));
            Box("안전 경계",new Vector3(-4.8f,-.02f,0),new Vector3(.15f,.1f,3.5f),Red);
            result=Label("오른쪽 입력 → 왼쪽 이동",960,795,44,Red,1600,70);break;
        default:throw new InvalidOperationException("Unexpected D26 visual replacement "+cutId);
        }
    }
    public override void Apply(float t) {
        t=Mathf.Clamp(t,0,Mathf.Max(0,duration-1/60f));
        if(slug=="limited-color-world")ApplyColour(t);else ApplyAi(t);
    }
    void ApplyColour(float t) {
        if(a!=null)Pose(a,"Idle_A",t);
        switch(cutId) {
        case "cut002":case "cut004": {
            float u=cutId=="cut002"?1:E(t,3.9f,5.8f);
            Paint(blocks[0],Color.Lerp(BlockA,Muted,u));Paint(blocks[1],Color.Lerp(BlockB,Muted,u));
            result.text=u>.8f?"색 차이가 줄면, 구분할 단서도 줄어듭니다":"같은 모양 · 다른 종류";
            break;}
        case "cut003":
            for(int i=0;i<photos.Count;i++){float s=i==0?0:i==1?2.54f:5.98f;float alpha=E(t,s,s+.3f);photos[i].color=new Color(1,1,1,.18f+.82f*alpha);labels[i].color=alpha>.5f?(i==0?Teal:i==1?Yellow:Green):Grey;}
            break;
        case "cut006":
            Paint(blocks[0],Color.Lerp(BlockA,Muted,E(t,.3f,1.4f)));Paint(blocks[1],Color.Lerp(BlockB,Muted*.38f,E(t,.3f,1.4f)));break;
        case "cut008":
            Paint(blocks[0],Muted);Paint(blocks[1],Muted*.62f);Visible(attackLine,t<1.5f);Visible(targetLine,t>=1.1f);break;
        case "cut009":
            for(int i=0;i<blocks.Count;i++)Paint(blocks[i],i%2==0?BlockA:BlockB);
            labels[0].color=t>=1.37f?Teal:Grey;labels[1].color=t>=5.07f?Yellow:Grey;
            result.text=t>=6.91f?"둘 다 확인합니다":"같은 테스트 장면 · 서로 다른 검사 조건";break;
        case "cut011":
            Paint(blocks[0],new Color(.19f,.22f,.19f));Paint(blocks[1],Color.Lerp(new Color(.24f,.27f,.24f),new Color(.76f,.79f,.76f),E(t,.8f,3.2f)));break;
        case "cut013":
            Paint(blocks[0],new Color(.075f,.08f,.08f));Paint(blocks[1],Color.Lerp(new Color(.075f,.08f,.08f),new Color(.62f,.65f,.62f),E(t,1.5f,3.3f)));break;
        case "cut015":
            for(int i=0;i<blocks.Count;i++)Paint(blocks[i],Color.Lerp(i==0?BlockA:i==1?BlockB:Yellow,Muted,E(t,2.8f,3.8f)));
            for(int i=0;i<marks.Count;i++)Visible(marks[i],t>=(i==0?.05f:i==1?.85f:1.55f));break;
        case "cut027":
            foreach(var tr in scenery)Paint(tr,Color.Lerp(new Color(.6f,.72f,.5f),new Color(.1f,.15f,.12f),E(t,0,.8f)));break;
        case "cut029":
            Paint(blocks[0],Muted);Paint(blocks[1],Muted*.65f);
            foreach(var tr in scenery)Paint(tr,new Color(.19f,.2f,.19f));Paint(c,new Color(.73f,.76f,.73f));break;
        case "cut030": {
            float mirror=Mathf.Lerp(1,-1,E(t,.35f,1.4f));
            for(int i=0;i<scenery.Count;i++){var v=sceneryOrigins[i];v.x*=mirror;scenery[i].transform.position=v;}
            a.transform.position=new Vector3(-2.1f*mirror,0,-.4f);c.transform.position=new Vector3(3*mirror,0,0);
            SetLine(routeLine,new Vector3(-2.1f*mirror,.04f,-.45f),new Vector3(0,.04f,-.2f),new Vector3(3*mirror,.04f,0));break;}
        }
    }
    void ApplyAi(float t) {
        if(a!=null)Pose(a,"Idle_A",t);if(b!=null)Pose(b,"Idle_A",t);
        switch(cutId) {
        case "cut007":
            a.transform.position=new Vector3(Mathf.Lerp(-3,1.6f,E(t,4.65f,8.9f)),0,0);
            b.transform.position=new Vector3(5.5f,0,0);
            if(t>=1.35f&&t<4.65f)Pose(a,"Fight_Punch_A",t-1.35f);
            if(t>=4.65f&&t<9.17f)Pose(a,"Walk_A",t-4.65f);
            result.text=t<4.65f?"상대가 없어도 공격":t<9.17f?"위험한 곳으로 이동":"상대와 위험을 읽고 멈춤";
            result.color=t<9.17f?Red:Green;break;
        case "cut009":
            Pose(a,"Fight_Punch_A",Mathf.Max(0,t-.25f));Pose(b,"Fight_Punch_A",Mathf.Max(0,t-.25f));
            Visible(attackLine,t>=.25f);break;
        case "cut017":
            die.transform.rotation=Quaternion.Euler(Mathf.Lerp(540,0,E(t,0,2.4f)),Mathf.Lerp(720,0,E(t,0,2.4f)),0);
            Pose(c,t>=4.58f?"Fight_Punch_A":"Idle_A",t>=4.58f?t-4.58f:t);
            Visible(attackLine,t>=4.58f);result.text=t<8.4f?"주사위 처리와 행동 선택이 같은 곳에서":"좋은 결과가 의심으로 이어질 수도 있습니다";break;
        case "cut021":
            Visible(attackLine,t>=.1f);a.transform.position=new Vector3(Mathf.Lerp(-3,-2,E(t,1.05f,3.2f)),0,0);
            if(t>=1.05f&&t<3.2f)Pose(a,"Walk_A",t-1.05f);break;
        case "cut023":
            Pose(a,"Fight_Punch_A",t);Pose(b,"Fight_Punch_A",Mathf.Max(0,t-.6f));break;
        case "cut024": {
            float x=Mathf.Lerp(-2,-1,E(t,7.85f,9.7f));a.transform.position=new Vector3(x,0,0);b.transform.position=new Vector3(1,0,0);
            SetLine(attackLine,new Vector3(x,.07f,-1.25f),new Vector3(x+2,.07f,-1.25f));
            if(t>=5.27f&&t<7.85f)Pose(a,"Fight_Punch_A",t-5.27f);
            else if(t>=7.85f&&t<9.7f)Pose(a,"Walk_A",t-7.85f);
            else if(t>=9.7f)Pose(a,"Fight_Punch_A",t-9.7f);
            if(t>=10.2f)Pose(b,"Fight_Hit_A",t-10.2f);
            result.text=t<7.85f?"2칸 공격으로는 3칸 밖에 닿지 않음":t<9.7f?"한 칸 접근":"같은 2칸 공격이 이제 닿습니다";
            labels[1].text=t>=9.7f?"상대 2칸":"상대 3칸";
            result.color=t<7.85f?Red:t<9.7f?Yellow:Green;break;}
        case "cut026":
            b.transform.position=new Vector3(Mathf.Lerp(3,1.7f,E(t,0,1.5f)),0,0);
            if(t<1.5f)Pose(b,"Walk_A",t);else Pose(b,"Fight_Punch_A",t-1.5f);
            Visible(attackLine,t<1.6f);break;
        case "cut029":
            for(int i=0;i<branches.Count;i++)Visible(branches[i],t>=(i==0?0:.55f));break;
        case "cut030": {
            float x=-1.7f;
            if(t<1.84f)x=Mathf.Lerp(-1.7f,-.9f,E(t,.2f,1.5f));
            else if(t<5.82f)x=Mathf.Lerp(-.9f,-2.4f,E(t,1.84f,4.8f));
            else if(t<9.88f)x=-1.7f+.55f*Mathf.Sin((t-5.82f)*Mathf.PI);
            else x=Mathf.Lerp(-1.7f,-4.0f,E(t,9.88f,12.5f));
            a.transform.position=new Vector3(x,0,0);
            if(t<12.5f)Pose(a,"Walk_A",t);
            Visible(branches[0],t<9.88f);Visible(branches[1],t>=1.84f);
            result.text=t<5.82f?"공격과 후퇴 조건이 함께 켜짐":t<9.88f?"우선순위가 없으면 앞뒤로 망설임":"1. 위험 회피 → 2. 안전해지면 공격";
            result.color=t<9.88f?Red:Green;break;}
        case "cut032": {
            int n=Mathf.Clamp(Mathf.RoundToInt(t*60)-156,0,12);ticker.text=n+" / 12 프레임";
            float w=Mathf.Max(1,1040*n/12);fill.rectTransform.sizeDelta=new Vector2(w,12);fill.rectTransform.anchoredPosition=new Vector2(440+w*.5f-960,540-330);
            Visible(attackLine,t>=2.6f);Visible(targetLine,t>=2.8f);
            if(t>=2.8f)Pose(b,"Fight_Punch_A",t-2.8f);break;}
        case "cut033": {
            float x=t<5.11f?Mathf.Lerp(-1,-3,E(t,.5f,2.5f)):Mathf.Lerp(-3,1,E(t,5.11f,8.11f));
            a.transform.position=new Vector3(x,0,0);
            if(t<2.5f||t>=5.11f&&t<8.11f)Pose(a,"Walk_A",t);
            Visible(branches[1],t<5.11f);Visible(branches[0],t>=5.11f);
            result.text=t<5.11f?"방향 반전 → 잠깐 혼란":t<8.11f?"달라진 조작에 적응":"다시 의도한 방향으로 이동";
            result.color=t<5.11f?Red:Green;break;}
        }
    }
}
}

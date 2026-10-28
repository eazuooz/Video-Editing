using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.DesignVisualV2
{
    // Every pose derives from local time. The capture worker supplies the exact
    // original cut length; this stage never changes narration or the edit clock.
    public class D27D28Stage : DesignLessonStage
    {
        private string mode;
        private GameObject a, b, c, prop, prop2, prop3;
        private Vector3 a0, b0, c0;
        private readonly List<GameObject> objects = new List<GameObject>();
        private readonly List<Text> text = new List<Text>();
        private readonly List<Image> ui = new List<Image>();
        private readonly Dictionary<GameObject,Vector3> originalScale = new Dictionary<GameObject,Vector3>();
        private readonly List<Vector2> originalTextPosition = new List<Vector2>();
        private Vector2 cursorPosition;
        private Image pictureBefore,pictureAfter;
        private float Length => Mathf.Max(0.1f, frames / 60f);
        private float Unit(float t) => Mathf.Clamp01(t / Length);
        private float Ease(float a, float b, float t) => Mathf.SmoothStep(0, 1, Mathf.InverseLerp(a, b, t));
        private void Show(Component o, bool show) { if (o) o.gameObject.SetActive(show); }
        private void Show(GameObject o, bool show) { if (o) o.SetActive(show); }
        private Text T(string s, float x, float y, int size=42, Color? color=null, float width=800,float height=74)
        { var v=Label(s,x,y,size,color,width,height); text.Add(v); return v; }
        private Image R(float x,float y,float w,float h,Color col)
        {var v=RectUI(x,y,w,h,col);ui.Add(v);return v;}
        private void Hero(float x=-2.8f, bool second=true)
        {
            a=Actor("player",new Vector3(x,0,0),false,3.1f,0);a0=a.transform.position;
            if(second){b=Actor("partner",new Vector3(2.8f,0,0),true,3.1f,180);b0=b.transform.position;}
        }
        private void Walk(GameObject g,float t,Vector3 from,Vector3 to,float progress)
        { g.transform.position=Vector3.Lerp(from,to,progress); Pose(g,"Walk_A",t); }
        private void Idle(GameObject g,float t){if(g)Pose(g,"Idle_A",t);}
        private void FlatScreen(float x,Color col)
        {
            var body=Box("screen",new Vector3(x,1.8f,0.9f),new Vector3(4.8f,3.1f,.18f),col);
            objects.Add(body);
            Box("screen-base",new Vector3(x,.3f,1),new Vector3(2,.16f,.9f),Grey);
        }
        private string Shot(string filename) => "D:/Github/VideoEditing/projects/start-with-climax/production/local/batch-v1/"+filename;

        public override void Build()
        {
            mode = slug == "in-game-cutscenes" ? D27Mode(cutId) : D28Mode(cutId);
            if(mode=="conversation")
            {
                Title("컷신이 이어 주는 것");Hero();
                prop=Asset("door",new Vector3(5,0,1.2f),3.4f,0);
                T("이야기",560,220,44,Teal,450);T("다음 행동",1440,220,44,Yellow,500);
                Line("next-path",new[]{new Vector3(2,0.08f,-1),new Vector3(5,0.08f,-1)},Yellow,.07f);
            }
            else if(mode=="formats" || mode=="frame-rate" || mode=="quality")
            {
                Title(mode=="formats"?"같은 장면, 두 가지 방식":mode=="frame-rate"?"프레임 레이트: 1초 동안 보여 주는 그림":"전환 순간의 차이");
                Hero(-3.2f,false);b=Actor("same-player",new Vector3(3.2f,0,0),false,3.1f,0);b0=b.transform.position;
                Line("division",new[]{new Vector3(0,0,-1),new Vector3(0,4.3f,-1)},Grey,.025f);
                T(mode=="frame-rate"?"60장 / 초":mode=="formats"?"실시간 컷신\nReal-time Cutscene":"실시간 컷신",500,230,mode=="formats"?38:48,Teal,720,mode=="formats"?110:74);
                T(mode=="frame-rate"?"30장 / 초":mode=="formats"?"프리렌더링 컷신\nPre-rendered Cutscene":"저장된 영상",1420,230,mode=="formats"?38:48,Yellow,720,mode=="formats"?110:74);
                if(mode=="formats")
                {
                    T("지금 그리는 장면",500,780,36,White,720);T("저장된 순서의 그림",1420,780,36,White,720);
                    for(int i=0;i<6;i++)objects.Add(Box("stored-frame-"+i,new Vector3(1.6f+i*.6f,.3f,-1),new Vector3(.44f,.5f,.04f),i%2==0?Yellow:Grey));
                }
                if(mode=="frame-rate")
                {
                    T("Frame Rate · 같은 동작 · 같은 1초",960,780,40,White,1200);
                    for(int i=0;i<60;i++){R(250+i*8,700,4,28,Teal);R(1170+i*8,700,4,28,i%2==0?Yellow:Grey);}
                }
                if(mode=="quality")
                {
                    T("매끄러운 움직임",500,780,40,Teal,720);T("프레임이 적은 경우",1420,780,40,Yellow,720);
                    // Sample spacing makes the stored-motion example visibly different.
                    // It is an authored low-quality example, not a claim about all video.
                    T("품질 차이 예시",960,840,30,Grey,1000);
                }
            }
            else if(mode=="viewing-reward")
            {
                Title("장면만 따로 볼 수 있다면");Hero(-5.4f);b.transform.position=new Vector3(3.8f,0,-.4f);b0=b.transform.position;
                prop=Asset("door",new Vector3(-1.6f,0,1.5f),3.2f);
                prop2=Asset("barrel",new Vector3(-3.6f,0,.2f),1.2f);
                prop3=Box("standalone-video-screen",new Vector3(5.1f,1.8f,1.5f),new Vector3(2.3f,2.5f,.13f),new Color(.12f,.18f,.20f));
                var play=Line("video-play",new[]{new Vector3(4.75f,1.3f,1.35f),new Vector3(5.65f,1.8f,1.35f),new Vector3(4.75f,2.3f,1.35f),new Vector3(4.75f,1.3f,1.35f)},Yellow,.08f);
                T("플레이의 결과",500,240,44,Teal,720);T("영상만 따로 보기",1420,240,44,Yellow,720);
                T("내가 해낸 과정",500,790,36,White,720);T("장면에 곧장 도착",1420,790,36,White,720);
                Line("division",new[]{new Vector3(.4f,0,-1),new Vector3(.4f,4,-1)},Grey,.025f);
            }
            else if(mode=="advance"||mode=="playback-controls")
            {
                Title(mode=="advance"?"끝내기와 속도 맞추기는 다르다":"진행 속도를 고르게");Hero(-2.5f);
                for(int i=0;i<3;i++){R(560+i*400,740,330,12,Grey);T((i+1)+"",560+i*400,690,32,Grey,100);}
                R(400,740,24,34,Yellow);
                T("다음 구간",500,250,42,Teal,550);T("1× → 1.5×",1400,250,42,Yellow,600);
                T(mode=="advance"?"전체 건너뛰기와 구별":"보고 싶은 구간으로",960,830,36,White,1200);
            }
            else if(mode=="skip-scope")
            {
                Title("건너뛰는 선택을 남기기");Hero(-3.4f,false);
                prop=Asset("door",new Vector3(4.3f,0,.8f),3.6f);
                FlatScreen(-.2f,new Color(.08f,.12f,.13f));
                T("컷신",850,290,46,Teal,600);T("스태프 크레디트",850,290,44,White,800);
                T("건너뛰기",1070,770,42,Yellow,600);T("다음 플레이",1530,220,40,Teal,550);
            }
            else if(mode=="known-scene")
            {
                Title("새 저장 파일이 첫 시청은 아닙니다");Hero(-3.2f,false);
                prop=Asset("table",new Vector3(3.6f,0,.6f),1.8f);
                prop2=Box("already-viewed-screen",new Vector3(-5.6f,1.5f,1.2f),new Vector3(2.0f,2.1f,.13f),new Color(.1f,.16f,.18f));
                Line("viewed-check",new[]{new Vector3(-6.2f,1.4f,1.04f),new Vector3(-5.8f,.95f,1.04f),new Vector3(-5.0f,1.9f,1.04f)},Green,.1f);
                R(1330,420,540,270,new Color(.07f,.1f,.12f));
                T("새 저장 슬롯",1330,340,40,Yellow,600);T("진행 0%",1330,430,50,White,600);
                T("이미 본 사람",520,260,46,Teal,700);T("시청 경험은 남아 있음",520,790,36,White,760);
                T("파일",1330,790,36,Grey,500);
            }
            else if(mode=="skip-choice")
            {
                Title("실수는 확인 입력으로 줄이기");Hero(-3.3f,false);prop=Asset("door",new Vector3(4,0,.7f),3.4f);
                T("계속 보기",550,240,46,White,650);T("건너뛰기",1370,240,46,Yellow,650);T("확인",970,760,44,Teal,500);
            }
            else if(mode=="qte")
            {
                Title("퀵 타임 이벤트 · Quick Time Event (QTE)");Hero(-3.9f,false);
                prop=Asset("barrel",new Vector3(-.7f,0,.4f),1.4f);
                T("장면을 보는 중",500,260,40,White,700);
                T("입력 알림",1390,260,44,Yellow,650);T("A",1390,400,100,Yellow,300,150);
                R(1390,530,430,24,Grey);R(1390,530,430,24,Teal);
                T("놓침",1390,640,52,Red,650);T("알림 → 기회 → 행동",960,810,40,Teal,1300);
            }
            else if(mode=="opening-overview"||mode=="closing-actions")
            {
                Title(mode=="closing-actions"?"재미를 먼저 경험시키기":"계속할 이유를 먼저 경험하게");Hero(-4.7f,false);
                prop=Asset("barrel",new Vector3(-1.6f,0,0),1.7f);
                prop2=Actor("first-threat",new Vector3(1.6f,0,1.1f),true,3.8f,180);
                prop3=Asset("table",new Vector3(4.9f,0,0),1.2f);
                objects.Add(Asset("potion",new Vector3(4.3f,1.1f,-.1f),.8f));
                objects.Add(Asset("crystal",new Vector3(5.6f,1.1f,-.1f),.85f));
                T("첫 행동",430,260,44,Teal,500);T("첫 위협",960,260,44,Yellow,500);T("첫 판단",1490,260,44,Green,500);
                if(mode=="closing-actions")Picture(Shot("sources/ace-announce-review/fine-first-case/007.png"),1540,760,410,230);
            }
            else if(mode=="early-peak"||mode=="early-peak-fallback")
            {
                Title(mode=="early-peak"?"작은 절정을 앞에 놓기":"큰 사건을 앞당기기 어렵다면");Hero(-5.3f,false);
                prop=Asset("crystal",new Vector3(-1.3f,0,.2f),1.8f);
                prop2=Asset("door",new Vector3(5,0,1),3.7f);
                T("시작",310,730,36,Grey,350);T("첫 조작",780,730,44,Teal,550);T("나중의 결전",1540,730,38,Grey,550);
                if(mode=="early-peak-fallback")
                {
                    for(int i=0;i<4;i++)objects.Add(Box("intro-panel-"+i,new Vector3(-3.6f+i*.55f,.7f,.1f),new Vector3(.4f,1.3f,.15f),Grey));
                    T("바로 쓸 규칙은 남기기",960,260,42,Yellow,1200);
                }
                else T("여기서 매력을 경험",800,270,44,Yellow,850);
            }
            else if(mode=="control")
            {
                Title(cutId=="cut012"?"시작한 사람에게 조작을":"조작 → 반응 → 목표");Hero(-3.8f,false);
                prop=cutId=="cut005"?Actor("approaching-opponent",new Vector3(3.2f,0,0),true,3.1f,180):Asset("barrel",new Vector3(3.2f,0,0),2.2f);
                if(cutId=="cut005")prop2=Asset("blaster",new Vector3(-2.7f,1.4f,-.2f),.65f,90);
                Line("action-line",new[]{new Vector3(-1.8f,1.5f,-.4f),new Vector3(2.4f,1.5f,-.4f)},Teal,.07f);
                T(cutId=="cut012"?"내가 움직인다":"조작",490,260,46,Teal,650);T(cutId=="cut005"?"다가오는 적":"화면이 반응한다",1430,260,44,Yellow,720);
            }
            else if(mode=="information-order"||mode=="information-order-return"||mode=="participation")
            {
                Title(mode=="information-order"?"사건 순서와 전달 순서":mode=="participation"?"궁금증은 행동에서 생깁니다":"경험 뒤에 생기는 질문");
                if(mode=="information-order")
                {
                    Hero(-4.5f,false);prop=Asset("door",new Vector3(-4.5f,0,1.2f),2.7f);
                    b=Actor("friend",new Vector3(0,0,0),true,2.8f);b0=b.transform.position;
                    c=Actor("event",new Vector3(4.4f,0,0),false,2.8f);c0=c.transform.position;
                    prop2=Asset("barrel",new Vector3(5.5f,0,0),1.9f);
                    T("배경",400,740,44,Grey,400);T("관계",960,740,44,Grey,400);T("사건",1510,740,44,Yellow,400);
                    T("일어난 순서",960,240,42,White,1000);T("알려 주는 순서",960,830,40,Teal,1100);
                }
                else
                {
                    Hero(-3.7f);b.transform.position=new Vector3(2.8f,0,1);b0=b.transform.position;
                    prop=Asset("door",new Vector3(5.2f,0,1),3.2f);
                    prop2=Asset("barrel",new Vector3(.1f,0,0),1.7f);
                    T("먼저 겪은 사건",520,220,44,Yellow,760);T(mode=="participation"?"왜 이런 일이?":"왜? · 어디로?",1400,220,44,Teal,760);
                }
            }
            else if(mode=="rule-use")
            {
                Title("바로 쓸 규칙부터");Hero(2.8f,false);prop=Asset("crystal",new Vector3(5.0f,0,0),2.1f);
                Picture(Shot("visual-assets/spin-after.png"),550,500,790,445);
                T("실제 게임",550,230,36,Grey,700);T("알려주고 → 써보기",1400,250,42,Teal,800);
            }
            else if(mode=="first-act"||mode=="evidence-selection")
            {
                Title(mode=="first-act"?"첫 재판에서 역할을 경험":"말과 증거를 맞춰 보기");
                pictureAfter=Picture(Shot("sources/ace-announce-review/fine-first-case/007.png"),510,500,820,462);
                if(mode=="evidence-selection")pictureBefore=Picture(Shot("sources/ace-announce-review/fine-first-case/006.png"),510,500,820,462);
                a=Actor("defender",new Vector3(2.1f,0,.8f),false,2.5f);a0=a.transform.position;
                b=Actor("witness",new Vector3(5.4f,0,1),true,2.5f,180);b0=b.transform.position;
                prop=Asset("table",new Vector3(3.8f,0,-.2f),1.4f);
                prop2=Asset("potion",new Vector3(3.1f,1.15f,-.3f),.8f);
                prop3=Asset("crystal",new Vector3(4.3f,1.15f,-.3f),.85f);
                T("실제 첫 재판",510,230,36,Grey,800);T("증인의 말",1510,270,40,Yellow,600);
                T(mode=="first-act"?"직접 따져 보는 역할":"고르기 → 비교",1410,795,40,Teal,800);
            }
            else throw new InvalidOperationException("Unknown lesson cut: "+slug+" "+cutId);
            foreach(var go in new[]{a,b,c,prop,prop2,prop3})if(go)originalScale[go]=go.transform.localScale;
            foreach(var tx in text)originalTextPosition.Add(tx.rectTransform.anchoredPosition);
            if(mode=="advance"||mode=="playback-controls")cursorPosition=ui[3].rectTransform.anchoredPosition;
        }

        public override void Apply(float t)
        {
            float u=Unit(t);Idle(a,t);Idle(b,t);Idle(c,t);
            if(mode=="conversation")
            {a.transform.rotation=Quaternion.Euler(0,Mathf.Lerp(0,25,Ease(Length*.35f,Length*.9f,t)),0);b.transform.rotation=Quaternion.Euler(0,Mathf.Lerp(180,0,Ease(.65f,1.1f,t)),0);if(t>1.1f)Walk(b,t,b0,new Vector3(4.3f,0,-.25f),Ease(1.1f,Length,t));}
            else if(mode=="formats"||mode=="frame-rate"||mode=="quality")
            {
                float left=t,right=mode=="formats"?t:Mathf.Floor(t*(mode=="quality"?15:30))/(mode=="quality"?15:30);
                Pose(a,"Walk_A",left);Pose(b,"Walk_A",right);
                a.transform.position=a0+new Vector3(Mathf.Sin(left*1.8f)*.65f,0,0);
                b.transform.position=b0+new Vector3(Mathf.Sin(right*1.8f)*.65f,0,0);
            }
            else if(mode=="viewing-reward")
            {
                float p=Ease(0,Length*.68f,t);Walk(a,t,a0,new Vector3(-2.4f,0,-.8f),p);
                a.transform.position+=Vector3.up*(Mathf.Sin(Mathf.Clamp01((p-.2f)/.5f)*Mathf.PI)*.8f);
                b.transform.position=b0;Pose(b,"Idle_A",t);
                prop.transform.localScale=originalScale[prop]*(1+Mathf.Sin(t*2)*.025f);
            }
            else if(mode=="advance"||mode=="playback-controls")
            {
                float fasterAt=Length*.34f;float play=t+Mathf.Max(0,t-fasterAt)*.5f;
                float position=play/(Length*1.33f)*.8f;
                if(u>=.62f)position+=.2f;
                Pose(a,"Walk_A",play);Pose(b,"Walk_A",play);
                ui[3].rectTransform.anchoredPosition=cursorPosition+new Vector2(1120*Mathf.Clamp01(position),0);
                text[0].color=u>=.62f?Yellow:Teal;text[1].color=t>=fasterAt?Yellow:Grey;
                if(mode=="advance"&&u>.78f){Walk(a,t,a0,new Vector3(4.8f,0,0),Ease(Length*.78f,Length,t));Show(b,false);} else Show(b,true);
            }
            else if(mode=="skip-scope")
            {Show(text[0],u<.45f);Show(text[1],u>=.45f);Walk(a,t,a0,new Vector3(4,0,-.4f),Ease(Length*.55f,Length,t));}
            else if(mode=="known-scene")
            {Walk(a,t,a0,new Vector3(-.3f,0,-.3f),Ease(Length*.45f,Length*.9f,t));}
            else if(mode=="skip-choice")
            {Show(text[2],u>.28f);Walk(a,t,a0,new Vector3(2.4f,0,-.5f),Ease(Length*.5f,Length,t));}
            else if(mode=="qte")
            {
                // The missed-input state stays visible during 14.07–17.83s risk narration.
                // Advice begins at17.97s; show a clearly signaled retry, then act at21.8s.
                bool alert=t>=3.2f;Show(text[1],alert);Show(text[2],alert);Show(ui[0],alert);Show(ui[1],alert);
                float phase=t<17.97f?Mathf.InverseLerp(6.09f,9.0f,t):Mathf.InverseLerp(17.97f,21.8f,t);
                ui[1].rectTransform.localScale=new Vector3(Mathf.Clamp01(1-phase),1,1);
                Show(text[3],t>=9&&t<17.97f);Show(text[4],t>=19.93f);
                if(t>=21.8f){Walk(a,t,a0,new Vector3(-2.1f,0,0),Ease(21.8f,22.4f,t));Pose(a,"Fight_Punch_A",t-21.8f);prop.transform.position=new Vector3(-.7f+Ease(22.4f,23.0f,t),0,.4f);}
            }
            else if(mode=="opening-overview"||mode=="closing-actions")
            {
                Walk(a,t,a0,new Vector3(3.2f,0,-.7f),Ease(0,Length*.92f,t));
                prop.transform.rotation=Quaternion.Euler(0,0,Mathf.Lerp(0,-15,Ease(Length*.22f,Length*.32f,t)));
                Pose(prop2,"Idle_A",t);
                if(u>.42f&&u<.68f)Pose(prop2,"Fight_Punch_A",t-Length*.42f);
                if(u>.76f){Pose(a,"Idle_A",t);objects[0].transform.position=Vector3.Lerp(new Vector3(4.3f,1.1f,-.1f),new Vector3(3.6f,1.9f,-.2f),Ease(Length*.76f,Length*.92f,t));}
            }
            else if(mode=="early-peak"||mode=="early-peak-fallback")
            {
                float p=Ease(Length*.2f,Length*.75f,t);Walk(a,t,a0,new Vector3(-2.1f,0,-.4f),p);
                if(u>.55f)Pose(a,"Fight_Punch_A",t-Length*.55f);
                prop.transform.localScale=originalScale[prop]*Mathf.Lerp(1,.1f,Ease(Length*.65f,Length*.78f,t));
                if(mode=="early-peak-fallback")for(int i=0;i<objects.Count;i++)Show(objects[i],t<2.2f+i*.35f);
            }
            else if(mode=="control")
            {
                if(cutId=="cut012")Walk(a,t,a0,new Vector3(-1.3f,0,0),Ease(.15f,Length*.85f,t));
                else
                {
                    Pose(a,"Pistol_Idle",t);
                    prop.transform.position=new Vector3(Mathf.Lerp(3.2f,.7f,Ease(0,1.8f,t))+Mathf.Lerp(0,.65f,Ease(1.85f,2.3f,t)),0,0);
                    Pose(prop,t<1.85f?"Walk_A":"Fight_Hit_A",t<1.85f?t:t-1.85f);
                }
            }
            else if(mode=="information-order")
            {
                float p=Ease(11.933f,13.733f,t);
                a.transform.position=Vector3.Lerp(a0,new Vector3(0,0,0),p);
                b.transform.position=Vector3.Lerp(b0,new Vector3(4.5f,0,0),p);
                c.transform.position=Vector3.Lerp(c0,new Vector3(-4.5f,0,0),p);
                prop.transform.position=Vector3.Lerp(new Vector3(-4.5f,0,1.2f),new Vector3(0,0,1.2f),p);
                prop2.transform.position=Vector3.Lerp(new Vector3(5.5f,0,0),new Vector3(-3.4f,0,0),p);
                text[0].rectTransform.anchoredPosition=originalTextPosition[0]+new Vector2(560*p,0);
                text[1].rectTransform.anchoredPosition=originalTextPosition[1]+new Vector2(550*p,0);
                text[2].rectTransform.anchoredPosition=originalTextPosition[2]+new Vector2(-1110*p,0);
                Show(text[3],p<.5f);Show(text[4],p>=.5f);
            }
            else if(mode=="participation"||mode=="information-order-return")
            {Walk(a,t,a0,new Vector3(-1.4f,0,-.2f),Ease(0,Length*.48f,t));if(u>.5f)Pose(a,"Fight_Punch_A",t-Length*.5f);}
            else if(mode=="rule-use")
            {a.transform.rotation=Quaternion.Euler(0,360*Ease(.5f,1.7f,t),0);Pose(a,"Fight_Punch_A",t);prop.transform.localScale=originalScale[prop]*Mathf.Lerp(1,.08f,Ease(1.35f,2.0f,t));}
            else if(mode=="first-act"||mode=="evidence-selection")
            {
                Idle(a,t);
                if(mode=="evidence-selection"){Show(pictureBefore,t<3.673f);Show(pictureAfter,t>=3.673f);}
                float p=Ease(Length*.3f,Length*.65f,t);
                prop2.transform.position=Vector3.Lerp(new Vector3(3.1f,1.15f,-.3f),new Vector3(4.4f,2.1f,-.2f),p);
                prop2.transform.rotation=Quaternion.Euler(0,t*20,0);
            }
        }
        private string D27Mode(string id)
        {switch(id){case"cut002":return"conversation";case"cut004":return"formats";case"cut005":return"frame-rate";case"cut006":return"quality";case"cut016":return"viewing-reward";case"cut020":return"advance";case"cut021":return"playback-controls";case"cut023":return"skip-scope";case"cut024":return"known-scene";case"cut026":return"skip-choice";case"cut027":return"qte";default:return"";}}
        private string D28Mode(string id)
        {switch(id){case"cut001":return"opening-overview";case"cut003":return"early-peak";case"cut005":case"cut012":return"control";case"cut008":return"information-order";case"cut010":return"participation";case"cut019":return"information-order-return";case"cut024":return"early-peak-fallback";case"cut025":return"rule-use";case"cut028":return"first-act";case"cut029":return"evidence-selection";case"cut032":return"closing-actions";default:return"";}}
    }
}

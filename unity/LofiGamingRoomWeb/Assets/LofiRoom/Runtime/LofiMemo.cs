using System;
using System.IO;
using System.Text;
using UnityEngine;

namespace Yamyam.LofiRoom
{
    public sealed class LofiMemo:MonoBehaviour
    {
        [Serializable] public class Note {public int version=1;public string text="",savedAt="";}
        public bool isOpen;
        public string text="",status="이 컴퓨터에 자동 저장됩니다";
        public bool dirty;
        public string error="";
        [NonSerialized] public string storeDirectory;
        [NonSerialized] public bool previewOnly;
        float saveAt;
        Vector2 scroll;
        Font font;
        Texture2D paper,field;
        GUIStyle title,body,hint,button;
        public string FilePath=>Path.Combine(string.IsNullOrEmpty(storeDirectory)?Application.persistentDataPath:storeDirectory,"room-memo.json");
        void Awake()
        {
            // A separate QA directory permits real persistence tests without
            // touching the user's normal note. It is never uploaded.
            var args=Environment.GetCommandLineArgs();
            for(int i=0;i<args.Length-1;i++)if(args[i]=="-lofi-memo-store")storeDirectory=args[i+1];
            Reload();
        }
        public void Reload()
        {
            dirty=false;error="";
            foreach(string path in new[]{FilePath,FilePath+".tmp",FilePath+".bak"})
            {
                if(!File.Exists(path))continue;
                try
                {
                    var data=JsonUtility.FromJson<Note>(File.ReadAllText(path,Encoding.UTF8));
                    if(data==null || data.text==null || data.version!=1)throw new IOException("Invalid memo file");
                    text=data.text;status=path==FilePath?"이 컴퓨터에 저장됨":"이전 메모를 복구했어요";
                    if(path!=FilePath){dirty=true;saveAt=Time.unscaledTime+.7f;}return;
                }
                catch(Exception ex){error=ex.GetType().Name;}
            }
            // Migrate only this room's earlier note key, without deleting it.
            text=PlayerPrefs.GetString("ai3d-lofi-room-v1-memo","");
            if(!string.IsNullOrEmpty(text)){dirty=true;saveAt=Time.unscaledTime+.7f;}
            if(!string.IsNullOrEmpty(error))status="메모를 불러오지 못했어요 · 기존 파일은 유지됩니다";
        }
        public void SetText(string value)
        {
            value=value??"";if(text==value)return;
            text=value;dirty=true;saveAt=Time.unscaledTime+.7f;status="저장 중…";
        }
        public bool SaveNow()
        {
            if(!dirty || previewOnly)return !dirty;
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(FilePath));
                string data=JsonUtility.ToJson(new Note{text=text,savedAt=DateTimeOffset.Now.ToString("o")},true);
                File.WriteAllText(FilePath+".tmp",data,new UTF8Encoding(false));
                if(File.Exists(FilePath))File.Replace(FilePath+".tmp",FilePath,FilePath+".bak");
                else File.Move(FilePath+".tmp",FilePath);
                dirty=false;error="";status="이 컴퓨터에 저장됨 · "+DateTime.Now.ToString("HH:mm");return true;
            }
            catch(Exception ex){error=ex.GetType().Name;status="저장하지 못했어요 · 내용을 복사해 보관해 주세요";saveAt=Time.unscaledTime+3;return false;}
        }
        void Update()
        {
            if(dirty && !previewOnly && Time.unscaledTime>=saveAt)SaveNow();
#if ENABLE_INPUT_SYSTEM
            if(isOpen && UnityEngine.InputSystem.Keyboard.current?.escapeKey.wasPressedThisFrame==true)Toggle();
#endif
        }
        public void Toggle(){if(isOpen)SaveNow();isOpen=!isOpen;}
        void OnApplicationFocus(bool focus){if(!focus)SaveNow();}
        void OnApplicationPause(bool pause){if(pause)SaveNow();}
        void OnApplicationQuit(){SaveNow();}
        void OnDisable(){SaveNow();}
        Texture2D Fill(Color color){var t=new Texture2D(1,1);t.SetPixel(0,0,color);t.Apply();return t;}
        void Style()
        {
            if(paper)return;
            font=Font.CreateDynamicFontFromOSFont("Malgun Gothic",20);
            paper=Fill(new Color(.95f,.92f,.84f));field=Fill(new Color(.985f,.966f,.914f));
            title=new GUIStyle(GUI.skin.label){font=font,fontSize=24,fontStyle=FontStyle.Bold,normal={textColor=new Color(.17f,.24f,.23f)}};
            body=new GUIStyle(GUI.skin.textArea){font=font,fontSize=18,wordWrap=true,padding=new RectOffset(14,14,12,12),normal={background=field,textColor=new Color(.18f,.23f,.21f)},focused={background=field,textColor=new Color(.18f,.23f,.21f)}};
            hint=new GUIStyle(GUI.skin.label){font=font,fontSize=13,wordWrap=true,normal={textColor=new Color(.34f,.40f,.35f)}};
            button=new GUIStyle(GUI.skin.button){font=font,fontSize=15,normal={textColor=new Color(.17f,.24f,.23f)}};
        }
        void OnGUI()
        {
            var room=GetComponent<LofiRoomSample>();if(!isOpen || (room && !room.showControls))return;
            Style();GUI.depth=-20;float scale=Mathf.Max(1,Screen.width/1400f);
            GUI.matrix=Matrix4x4.Scale(Vector3.one*scale);Color old=GUI.color,background=GUI.backgroundColor;GUI.color=Color.white;GUI.backgroundColor=Color.white;
            float w=390,h=Mathf.Min(440,Screen.height/scale-210),x=24,y=136;
            GUI.DrawTexture(new Rect(x,y,w,h),paper);
            GUI.Label(new Rect(x+22,y+17,w-110,36),"오늘의 메모",title);
            if(GUI.Button(new Rect(x+w-82,y+20,62,30),"닫기",button))Toggle();
            GUI.Label(new Rect(x+22,y+59,w-44,24),previewOnly?"미리보기 메모":"적어두고 싶은 생각을 편하게 남겨두세요.",hint);
            var area=new Rect(x+20,y+94,w-40,h-154);
            float contentHeight=Mathf.Max(area.height-5,body.CalcHeight(new GUIContent(text+"\n"),area.width-22));
            scroll=GUI.BeginScrollView(area,scroll,new Rect(0,0,area.width-20,contentHeight));
            GUI.SetNextControlName("LofiMemoText");string value=GUI.TextArea(new Rect(0,0,area.width-21,contentHeight),text,12000,body);
            if(value!=text)SetText(value);GUI.EndScrollView();
            if(string.IsNullOrEmpty(text))GUI.Label(new Rect(area.x+14,area.y+10,area.width-28,30),"오늘의 할 일, 떠오른 아이디어…",hint);
            GUI.Label(new Rect(x+22,y+h-48,w-44,38),status,hint);GUI.color=old;GUI.backgroundColor=background;
        }
        void OnDestroy(){if(paper)Destroy(paper);if(field)Destroy(field);if(font)Destroy(font);}
    }
}

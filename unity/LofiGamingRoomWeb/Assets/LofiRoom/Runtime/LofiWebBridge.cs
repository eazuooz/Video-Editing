using UnityEngine;
using System.Runtime.InteropServices;
namespace Yamyam.LofiRoom
{
    public sealed class LofiWebBridge:MonoBehaviour
    {
#if UNITY_WEBGL && !UNITY_EDITOR
        [DllImport("__Internal")]static extern void LofiReportState(string state);
#endif
        float next;LofiRoomSample room;
        void Awake(){room=GetComponent<LofiRoomSample>();}
        void Update()
        {
#if UNITY_WEBGL && !UNITY_EDITOR
            if(Time.unscaledTime<next)return;next=Time.unscaledTime+.5f;
            var living=GetComponent<LofiLivingRoom>();var playlist=GetComponent<LofiPlaylist>();
            LofiReportState(JsonUtility.ToJson(new State{phase=room.activities.phase,music=room.music&&room.music.isPlaying,fire=room.hearth&&room.hearth.crackle&&!room.hearth.crackle.mute,fps=1/Mathf.Max(.001f,Time.unscaledDeltaTime),seated=room.activities.seated,busy=room.activities.busy,rain=living&&living.raining,track=playlist?playlist.index:0,title=playlist?playlist.Title:"Morning Coffee"}));
#endif
        }
        [System.Serializable]class State{public string phase,title;public bool music,fire,seated,busy,rain;public float fps;public int track;}
    }
}

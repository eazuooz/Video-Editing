using UnityEngine;
namespace Yamyam.LofiRoom
{
    public sealed class LofiPlaylist:MonoBehaviour
    {
        public AudioClip[] tracks;
        public string[] titles;
        public AudioSource source;
        public int index;
        bool observedPlaying;
        float lastTime;
        public string Title=>titles!=null&&titles.Length>index?titles[index]:"";
        void Start(){Select(PlayerPrefs.GetInt("ai3d-lofi-room-track",0),Application.platform!=RuntimePlatform.WebGLPlayer);}
        public void Select(int value,bool play)
        {
            if(tracks==null||tracks.Length==0||!source)return;
            var previous=source.clip;source.Stop();index=(value%tracks.Length+tracks.Length)%tracks.Length;source.clip=tracks[index];source.loop=false;if(previous&&previous!=source.clip)previous.UnloadAudioData();source.clip.LoadAudioData();observedPlaying=false;lastTime=0;
            if(play)source.Play();PlayerPrefs.SetInt("ai3d-lofi-room-track",index);PlayerPrefs.Save();
        }
        public void Next(int delta)=>Select(index+delta,true);
        void Update(){if(source&&source.isPlaying){observedPlaying=true;lastTime=source.time;}else if(observedPlaying&&source&&source.clip&&source.time==0&&lastTime>source.clip.length-1){observedPlaying=false;Next(1);}}
    }
}

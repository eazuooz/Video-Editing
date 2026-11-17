using UnityEngine;
namespace Yamyam.LofiRoom
{
    public sealed class LofiTurntable:MonoBehaviour
    {
        public Transform record,tonearm;
        public AudioSource music;
        float rpm;
        void Update()
        {
            bool play=music && music.isPlaying;
            rpm=Mathf.MoveTowards(rpm,play?33.333f:0,Time.deltaTime*18);
            if(record)record.Rotate(Vector3.up,rpm*6*Time.deltaTime,Space.Self);
            if(tonearm)tonearm.localRotation=Quaternion.Slerp(tonearm.localRotation,Quaternion.Euler(0,play?0:-25,0),Time.deltaTime*2);
#if ENABLE_INPUT_SYSTEM
            var mouse=UnityEngine.InputSystem.Mouse.current;
            var notes=FindAnyObjectByType<LofiMemo>();if(notes && notes.isOpen)return;
            if(mouse!=null && mouse.leftButton.wasPressedThisFrame && Camera.main)
            {
                if(Physics.Raycast(Camera.main.ScreenPointToRay(mouse.position.ReadValue()),out var hit,30) && hit.collider.GetComponent<LofiTurntable>()==this)
                {if(play)music.Pause();else music.Play();}
            }
#endif
        }
    }
}

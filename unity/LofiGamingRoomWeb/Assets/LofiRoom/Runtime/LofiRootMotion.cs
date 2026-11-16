using UnityEngine;

namespace Yamyam.LofiRoom
{
    // Consume the imported clip's own root translation. No procedural bone poses.
    public sealed class LofiRootMotion : MonoBehaviour
    {
        public LofiRoomSample owner;
        void OnAnimatorMove() { if(owner)owner.ApplyNativeRootMotion(GetComponent<Animator>()); }
    }
}

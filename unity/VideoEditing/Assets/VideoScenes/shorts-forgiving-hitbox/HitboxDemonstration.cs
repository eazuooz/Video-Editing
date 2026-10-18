using UnityEngine;

namespace YamyamCoding.Shorts.ForgivingHitbox {
    // Executable lesson implementation: renderers never decide damage.
    public class HitboxDemonstration : MonoBehaviour {
        public BoxCollider hurtbox;
        public BoxCollider hitbox;
        public int health = 100;
        public bool hitApplied;
        public bool overlapping;
        public float separationDistance;
        public void ResetAttack(float width) {
            hurtbox.size = new Vector3(width, 2.12f, .8f);
            health = 100; hitApplied = false; overlapping = false;
        }
        public bool EvaluateAttack() {
            Vector3 direction; float distance;
            overlapping = Physics.ComputePenetration(
                hitbox, hitbox.transform.position, hitbox.transform.rotation,
                hurtbox, hurtbox.transform.position, hurtbox.transform.rotation,
                out direction, out distance);
            separationDistance = overlapping ? distance : 0;
            if (overlapping && !hitApplied) { health -= 30; hitApplied = true; }
            return overlapping;
        }
    }
}

using System;
using UnityEngine;

namespace Yamyam.Architectural111 {
    // Deliberately simplified original experiment, not measured TF2 geometry.
    public sealed class TunnelExperiment : MonoBehaviour {
        public float tunnelWidth = 2.5f;
        public float cartWidth = 1.5f;
        public float playerDiameter = .72f;
        public float moveSpeed = 1.8f;
        public Transform leftWall, rightWall, playerModel;
        public AnimationClip walkingClip, idleClip;
        public Vector3 modelBasePosition, modelBaseScale=Vector3.one;
        public Quaternion modelBaseRotation=Quaternion.identity;
        public CharacterController player;
        public Camera observer, playerView;
        public Transform[] wheels;
        public LineRenderer clearance, collisionOutline, travelArrow;
        public bool showGuides = true;
        public float Travelled { get; private set; }
        public bool Blocked { get; private set; }
        public Vector3 CommandedVelocity { get; private set; }
        public float SideClearance => (tunnelWidth - cartWidth) * .5f;
        Vector3 start;
        float elapsed;

        public void ResetExperiment(float width) {
            tunnelWidth = width;
            leftWall.localPosition = new Vector3(-width*.5f-.17f, 1.15f, 0);
            rightWall.localPosition = new Vector3(width*.5f+.17f, 1.15f, 0);
            player.enabled = false;
            // Same initial position and command sequence in BOTH trials.
            // Only the walls differ. The narrow wall prevents the lateral step;
            // the character then reaches the cart corner and cannot pass it.
            start = new Vector3(.855f, .03f, -2.85f);
            player.transform.position = start;
            player.enabled = true;
            Travelled = 0; Blocked = false; elapsed=0;
            Physics.SyncTransforms();
            UpdateGuides();
        }

        public void Step(float seconds) {
            Vector3 before = player.transform.position;
            CommandedVelocity=(elapsed<.8f ? new Vector3(.6f,0,.8f) : Vector3.forward)*moveSpeed;
            player.Move((CommandedVelocity+Vector3.down*.25f)*seconds);
            elapsed+=seconds;
            float dz=player.transform.position.z-before.z;
            Travelled=player.transform.position.z-start.z;
            Blocked=elapsed>.85f && dz<CommandedVelocity.z*seconds*.25f;
            // Small body motion remains separate from the collision capsule.
            if (playerModel) {
                float phase = Travelled * 8f;
                var clip=Blocked?idleClip:walkingClip;
                if(clip)clip.SampleAnimation(playerModel.gameObject,Mathf.Repeat(elapsed,clip.length));
                playerModel.localPosition=modelBasePosition+new Vector3(0,Blocked?0:Mathf.Abs(Mathf.Sin(phase))*.015f,0);
                playerModel.localRotation=modelBaseRotation;
                playerModel.localScale=modelBaseScale;
            }
            UpdateGuides();
        }

        void UpdateGuides() {
            if (clearance) {
                clearance.enabled=showGuides;
                clearance.positionCount=2;
                clearance.SetPosition(0,new Vector3(cartWidth*.5f, .07f, .35f));
                clearance.SetPosition(1,new Vector3(tunnelWidth*.5f, .07f,.35f));
            }
            if (collisionOutline) {
                collisionOutline.enabled=showGuides;
                collisionOutline.positionCount=49;
                Vector3 p=player.transform.position;
                for(int i=0;i<49;i++) {
                    float a=i*Mathf.PI/24f;
                    collisionOutline.SetPosition(i,p+new Vector3(Mathf.Cos(a)*playerDiameter*.5f,.06f,Mathf.Sin(a)*playerDiameter*.5f));
                }
                Color c=Blocked?new Color(1,.25f,.20f):new Color(.25f,.95f,.69f);
                collisionOutline.startColor=collisionOutline.endColor=c;
            }
            if (travelArrow) {
                travelArrow.enabled=showGuides;
                Vector3 p=player.transform.position+new Vector3(0,.1f,.45f);
                travelArrow.positionCount=5;
                travelArrow.SetPositions(new[]{p,p+Vector3.forward*.66f,p+new Vector3(-.13f,0,.44f),p+Vector3.forward*.66f,p+new Vector3(.13f,0,.44f)});
            }
        }
    }
}

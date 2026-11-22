using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Yamyam.EldenRingLibraryLessons
{
    public sealed partial class PrincipleDemo
    {
        readonly List<WalkthroughActor> walkthroughActors = new List<WalkthroughActor>();

        sealed class WalkthroughActor
        {
            public Transform Root, RigAnchor, Pelvis, Chest;
            public Vector3 Previous, BaseAnchor, BasePelvis;
            public Quaternion BaseChest;
            public readonly Limb[] Legs = new Limb[2], Arms = new Limb[2];
            public float PreviousTime = -1, Distance, Cast;
            public float Height, PosePhase;
            public bool FixedFacing;
            public Func<Vector3, float> GroundHeight;
            public Action AfterPose;
        }

        sealed class Limb
        {
            public Transform Upper, Lower, End;
            public Vector3 RestEnd;
            public Quaternion UpperRest, LowerRest, EndRest;
        }

        void AddWalkthroughActor(Transform root, Color marker)
        {
            var body = Attach("villager", root, V(1.65f, 1.85f, 1.45f), true);
            var bones = body.GetComponentsInChildren<Transform>(true);
            var actor = new WalkthroughActor
            {
                Root = root, RigAnchor = body.transform.parent,
                Previous = root.position
            };
            var skins = body.GetComponentsInChildren<SkinnedMeshRenderer>().Where(skin => skin.enabled).ToArray();
            if (skins.Length == 0) throw new InvalidOperationException("The shared actor needs a visible skinned rig.");
            foreach (var skin in skins) skin.updateWhenOffscreen = true;
            actor.Pelvis = FindBone(bones, "hips") ?? FindBone(bones, "pelvis");
            actor.Chest = FindBone(bones, "spine");
            if (actor.Chest) actor.BaseChest = actor.Chest.localRotation;
            for (int side = 0; side < 2; side++)
            {
                string suffix = side == 0 ? ".L" : ".R";
                actor.Legs[side] = BindLimb(bones, root, "thigh", "shin", "foot", suffix);
                actor.Arms[side] = BindLimb(bones, root, "upper_arm", "forearm", "hand", suffix);
            }
            // Measure the rendered neutral sole height; the imported renderer bounds include extra clearance.
            float bottom = float.PositiveInfinity;
            foreach (var skin in skins)
            {
                var pose = new Mesh();
                skin.BakeMesh(pose, false);
                foreach (var vertex in pose.vertices)
                    bottom = Mathf.Min(bottom, root.InverseTransformPoint(skin.transform.TransformPoint(vertex)).y);
                if (Application.isPlaying) Destroy(pose);
                else DestroyImmediate(pose);
            }
            if (float.IsInfinity(bottom)) throw new InvalidOperationException("The shared actor has no rendered vertices.");
            actor.RigAnchor.localPosition -= V(0, bottom, 0);
            actor.BaseAnchor = actor.RigAnchor.localPosition;
            actor.BasePelvis = actor.Pelvis ? actor.Pelvis.localPosition : Vector3.zero;
            actor.Height = root.InverseTransformPoint(actor.Legs[0].Upper.position).y;
            foreach (var leg in actor.Legs) leg.RestEnd = root.InverseTransformPoint(leg.End.position);
            walkthroughActors.Add(actor);
            var baseRing = Ring("Current player position", root.localPosition, .33f, marker);
            baseRing.SetParent(root, false);
            baseRing.localPosition = V(0, .018f, 0);
        }

        static Limb BindLimb(Transform[] bones, Transform root, string upper, string lower, string end, string suffix)
        {
            var a = FindBone(bones, upper + suffix);
            var b = FindBone(bones, lower + suffix);
            var c = FindBone(bones, end + suffix);
            if (!a || !b || !c)
                throw new InvalidOperationException($"Incomplete shared actor limb: {upper}{suffix}");
            return new Limb
            {
                Upper = a, Lower = b, End = c, RestEnd = root.InverseTransformPoint(c.position),
                UpperRest = a.localRotation, LowerRest = b.localRotation, EndRest = c.localRotation
            };
        }

        static void PointJoint(Transform parent, Transform child, Vector3 desired)
        {
            if (desired.sqrMagnitude > .000001f)
                parent.rotation = Quaternion.FromToRotation(child.position - parent.position, desired) * parent.rotation;
        }

        static void PoseLimb(Limb limb, Vector3 target, Vector3 bend)
        {
            limb.Upper.localRotation = limb.UpperRest;
            limb.Lower.localRotation = limb.LowerRest;
            limb.End.localRotation = limb.EndRest;
            Vector3 start = limb.Upper.position;
            float a = Vector3.Distance(start, limb.Lower.position);
            float b = Vector3.Distance(limb.Lower.position, limb.End.position);
            Vector3 axis = (target - start).normalized;
            float d = Mathf.Clamp(Vector3.Distance(target, start), Mathf.Abs(a - b) + .001f, a + b - .001f);
            float along = (a * a - b * b + d * d) / (2 * d);
            Vector3 pole = Vector3.ProjectOnPlane(bend, axis).normalized;
            Vector3 joint = start + axis * along + pole * Mathf.Sqrt(Mathf.Max(0, a * a - along * along));
            PointJoint(limb.Upper, limb.Lower, joint - start);
            PointJoint(limb.Lower, limb.End, start + axis * d - limb.Lower.position);
        }

        void PlayWalkthroughActors(float time)
        {
            foreach (var actor in walkthroughActors)
            {
                Vector3 movement = actor.Root.position - actor.Previous;
                movement.y = 0;
                bool walking = actor.PreviousTime >= 0 && time > actor.PreviousTime && movement.sqrMagnitude > .0000001f;
                if (time <= actor.PreviousTime) actor.Distance = 0;
                if (walking)
                {
                    actor.Distance += movement.magnitude;
                    if (!actor.FixedFacing) actor.Root.rotation = Quaternion.LookRotation(movement);
                }
                float cycle = actor.Distance / .92f;
                actor.RigAnchor.localPosition = actor.BaseAnchor - V(0, walking ? .065f : .02f + .10f * actor.Cast, 0);
                if (actor.Pelvis) actor.Pelvis.localPosition = actor.BasePelvis;
                if (actor.Chest)
                {
                    actor.Chest.localRotation = actor.BaseChest;
                    actor.Chest.rotation = Quaternion.AngleAxis(-12 * actor.Cast, actor.Root.right) * actor.Chest.rotation;
                }
                for (int side = 0; side < 2; side++)
                {
                    float phase = Mathf.Repeat(cycle + .5f * side, 1);
                    float reach = phase < .60f ? Mathf.Lerp(.24f, -.24f, phase / .60f) :
                        Mathf.Lerp(-.24f, .24f, Ease((phase - .60f) / .40f));
                    float lift = phase < .60f ? 0 : .17f * Mathf.Sin((phase - .60f) / .40f * Mathf.PI);
                    var leg = actor.Legs[side];
                    var step = walking ? V(0, lift, reach) : V(0, 0, (side == 0 ? .24f : -.20f) * actor.Cast);
                    var footTarget = actor.Root.TransformPoint(leg.RestEnd + step);
                    if (actor.GroundHeight != null)
                        footTarget.y += actor.GroundHeight(footTarget) - actor.Root.position.y;
                    PoseLimb(leg, footTarget, actor.Root.forward);
                    var arm = actor.Arms[side];
                    Vector3 shoulder = actor.Root.InverseTransformPoint(arm.Upper.position);
                    float outward = Mathf.Sign(shoulder.x);
                    Vector3 hand = shoulder + V(outward * .10f, -.38f, walking ? -.68f * reach : .06f);
                    Vector3 raised = V(outward * .19f, actor.Height + (side == 1 ? .79f : .61f), .51f);
                    PoseLimb(arm, actor.Root.TransformPoint(Vector3.Lerp(hand, raised, actor.Cast)),
                        actor.Root.TransformDirection(V(outward, -.36f, -.28f)));
                }
                actor.AfterPose?.Invoke();
                actor.Previous = actor.Root.position;
                actor.PreviousTime = time;
            }
        }
    }
}

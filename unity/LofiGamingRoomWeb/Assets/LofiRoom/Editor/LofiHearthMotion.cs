using System;
using System.Linq;
using System.IO;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using Unity.Pipeline.Commands;
using Yamyam.LofiRoom;

public static class LofiHearthMotion
{
    public const string Motion="Assets/LofiRoom/NativeMotion/";
    [CliCommand("lofi_hearth_motion","Import and inspect only the selected licensed seated motion sources",MainThreadRequired=true)]
    public static string Import()
    {
        string path=Motion+"Rig_Medium_Simulation.fbx";
        var mi=(ModelImporter)AssetImporter.GetAtPath(path);
        mi.animationType=ModelImporterAnimationType.Human;mi.avatarSetup=ModelImporterAvatarSetup.CreateFromThisModel;
        mi.isReadable=true;mi.importAnimation=true;mi.animationCompression=ModelImporterAnimationCompression.Off;
        mi.SaveAndReimport();
        var avatar=AssetDatabase.LoadAllAssetsAtPath(path).OfType<Avatar>().FirstOrDefault();
        if(!avatar || !avatar.isValid || !avatar.isHuman)
        {
            var description=mi.humanDescription;
            description.human=new[]{H("Hips","hips"),H("Spine","spine"),H("Chest","chest"),H("Head","head"),
                H("LeftUpperArm","upperarm.l"),H("LeftLowerArm","lowerarm.l"),H("LeftHand","hand.l"),
                H("RightUpperArm","upperarm.r"),H("RightLowerArm","lowerarm.r"),H("RightHand","hand.r"),
                H("LeftUpperLeg","upperleg.l"),H("LeftLowerLeg","lowerleg.l"),H("LeftFoot","foot.l"),H("LeftToes","toes.l"),
                H("RightUpperLeg","upperleg.r"),H("RightLowerLeg","lowerleg.r"),H("RightFoot","foot.r"),H("RightToes","toes.r")};
            mi.humanDescription=description;mi.SaveAndReimport();
        }
        var clips=mi.defaultClipAnimations;
        foreach(var c in clips)
        {
            c.loopTime=c.name.Contains("Idle");c.loopPose=c.loopTime;
            c.lockRootRotation=true;c.lockRootHeightY=true;c.keepOriginalPositionY=true;c.heightFromFeet=false;c.lockRootPositionXZ=true;
        }
        mi.clipAnimations=clips;mi.SaveAndReimport();
        avatar=AssetDatabase.LoadAllAssetsAtPath(path).OfType<Avatar>().FirstOrDefault();
        var report=new {avatarValid=avatar&&avatar.isValid,avatarHuman=avatar&&avatar.isHuman,
            clips=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview")).Select(c=>new{c.name,c.length,c.isHumanMotion}).ToArray(),
            local=AssetDatabase.FindAssets("t:AnimationClip",new[]{"Assets/LofiRoom/NativeMotion"}).Select(AssetDatabase.GUIDToAssetPath).ToArray()};
        string text=Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented);
        File.WriteAllText(Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/hearth-v4/motion-import.json"),text);
        return text;
    }
    static HumanBone H(string human,string bone)=>new(){humanName=human,boneName=bone,limit=new HumanLimit{useDefaultValues=true}};
    public static AnimationClip Clip(string name)=>AssetDatabase.LoadAllAssetsAtPath(Motion+"Rig_Medium_Simulation.fbx").OfType<AnimationClip>().First(c=>c.name==name);
    public static void Attach(LofiRoomSample room,string root,Transform leftKey,Transform rightKey,Transform book,Transform leftPage,Transform rightPage)
    {
        var ac=(AnimatorController)room.actor.runtimeAnimatorController;
        var layer=ac.layers[0];layer.iKPass=true;ac.layers=new[]{layer};
        var machine=layer.stateMachine;
        foreach(var pair in new[]{("SitDown","Sit_Chair_Down"),("Desk","Sit_Chair_Idle"),("StandUp","Sit_Chair_StandUp")})
        {var state=machine.AddState(pair.Item1);state.motion=Clip(pair.Item2);state.iKOnFeet=pair.Item1=="Desk";if(pair.Item1!="Desk")state.speed=pair.Item1=="SitDown"?.36f:.65f;}
        var read=AssetDatabase.LoadAssetAtPath<AnimationClip>(Motion+"Tourist_sit_02_Map.anim");
        if(!read || !read.isHumanMotion)throw new Exception("The licensed reading clip must be a native Humanoid animation");
        var reading=machine.AddState("Read");reading.motion=read;reading.iKOnFeet=true;
        var activities=room.gameObject.AddComponent<LofiActivities>();room.activities=activities;
        activities.room=room;activities.actor=room.actor;activities.leftKey=leftKey;activities.rightKey=rightKey;
        activities.book=book;activities.leftPage=leftPage;activities.rightPage=rightPage;
        activities.sitDuration=Clip("Sit_Chair_Down").length/.36f;activities.standDuration=Clip("Sit_Chair_StandUp").length/.65f;
        room.actor.gameObject.AddComponent<LofiDeskIK>().activities=activities;room.hasSit=true;
        EditorUtility.SetDirty(ac);
    }
}

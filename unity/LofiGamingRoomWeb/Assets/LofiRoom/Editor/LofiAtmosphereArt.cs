using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Yamyam.LofiRoom;

public static class LofiAtmosphereArt
{
    public static void Apply(LofiRoomSample room,string root)
    {
        ConfigurePcRenderer(root);
        var atmosphere=new GameObject("Window light and garden breeze").AddComponent<LofiAtmosphere>();
        room.atmosphere=atmosphere;
        var sky=GameObject.Find("night outside");
        atmosphere.outsideMaterial=sky.GetComponent<Renderer>().sharedMaterial;
        var rainMain=room.rain.main;rainMain.startSize=.009f;rainMain.startColor=new Color(.68f,.79f,.87f,.22f);
        var rainRenderer=room.rain.GetComponent<ParticleSystemRenderer>();rainRenderer.lengthScale=1.6f;rainRenderer.velocityScale=.025f;
        var rainMaterial=rainRenderer.sharedMaterial;
        rainMaterial.SetFloat("_Surface",1);rainMaterial.SetFloat("_SrcBlend",(int)BlendMode.SrcAlpha);rainMaterial.SetFloat("_DstBlend",(int)BlendMode.OneMinusSrcAlpha);rainMaterial.SetFloat("_ZWrite",0);rainMaterial.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");rainMaterial.renderQueue=3000;
        rainMaterial.SetColor("_BaseColor",new Color(.68f,.79f,.87f,.3f));EditorUtility.SetDirty(rainMaterial);

        var light=new GameObject("Window sunlight - shadowed four-pane cookie").AddComponent<Light>();
        light.type=LightType.Spot;light.range=9;light.spotAngle=94;light.innerSpotAngle=79;
        light.transform.position=new Vector3(-1.8f,2.28f,2.17f);
        light.transform.rotation=Quaternion.LookRotation(new Vector3(.44f,-.62f,-1));
        light.intensity=7.5f;light.color=new Color(1,.87f,.63f);light.shadows=LightShadows.Soft;
        light.shadowBias=.018f;light.shadowNormalBias=.025f;light.shadowNearPlane=.04f;
        light.cookie=WindowCookie(root);atmosphere.windowLight=light;

        var volume=GameObject.CreatePrimitive(PrimitiveType.Cube);volume.name="Depth-clipped window light scattering";
        Object.DestroyImmediate(volume.GetComponent<Collider>());
        volume.transform.position=new Vector3(-.6f,1.43f,.075f);
        volume.transform.localScale=new Vector3(4.6f,2.74f,4.35f);
        var material=new Material(Shader.Find("Yamyam/Window Light Volume"));material.SetFloat("_Density",.20f);
        Store(material,root+"/Materials/window-volume.mat");
        volume.GetComponent<Renderer>().sharedMaterial=material;
        volume.GetComponent<Renderer>().shadowCastingMode=ShadowCastingMode.Off;
        atmosphere.shaftMaterial=material;atmosphere.shaftRenderer=volume.GetComponent<Renderer>();

        // Slow, sparse dust near the opening, not a fog sheet over the room.
        var dust=new GameObject("Window dust motes").AddComponent<ParticleSystem>();
        dust.transform.position=new Vector3(-1.15f,1.35f,1.5f);dust.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);
        var main=dust.main;main.startLifetime=9;main.startSpeed=.018f;main.startSize=.008f;
        main.startColor=new Color(1,.89f,.62f,.24f);main.maxParticles=45;main.simulationSpace=ParticleSystemSimulationSpace.World;
        var shape=dust.shape;shape.shapeType=ParticleSystemShapeType.Box;shape.scale=new Vector3(1.55f,1.7f,1.15f);
        var emission=dust.emission;emission.rateOverTime=3;
        var noise=dust.noise;noise.enabled=true;noise.strength=.018f;noise.frequency=.22f;noise.scrollSpeed=.055f;
        var color=dust.colorOverLifetime;color.enabled=true;
        var gradient=new Gradient();gradient.SetKeys(new[]{new GradientColorKey(new Color(1,.87f,.57f),0),new GradientColorKey(new Color(1,.87f,.57f),1)},new[]{new GradientAlphaKey(0,0),new GradientAlphaKey(.22f,.25f),new GradientAlphaKey(.22f,.7f),new GradientAlphaKey(0,1)});color.color=gradient;
        var dustMat=new Material(Shader.Find("Universal Render Pipeline/Particles/Unlit"));
        dustMat.SetFloat("_Surface",1);dustMat.SetFloat("_Blend",0);dustMat.SetFloat("_SrcBlend",(int)BlendMode.SrcAlpha);dustMat.SetFloat("_DstBlend",(int)BlendMode.OneMinusSrcAlpha);dustMat.SetFloat("_ZWrite",0);dustMat.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");dustMat.renderQueue=3000;Store(dustMat,root+"/Materials/dust.mat");
        dust.GetComponent<ParticleSystemRenderer>().sharedMaterial=dustMat;atmosphere.dust=dust;dust.Play();

        var probe=new GameObject("Room material reflection probe").AddComponent<ReflectionProbe>();
        probe.transform.position=new Vector3(0,1.4f,0);probe.size=new Vector3(6.8f,3.4f,5.2f);probe.resolution=128;
        probe.mode=ReflectionProbeMode.Realtime;probe.refreshMode=ReflectionProbeRefreshMode.OnAwake;
        probe.timeSlicingMode=ReflectionProbeTimeSlicingMode.AllFacesAtOnce;probe.boxProjection=true;
        probe.clearFlags=ReflectionProbeClearFlags.SolidColor;probe.backgroundColor=new Color(.09f,.13f,.16f);probe.intensity=.5f;
        foreach(var v in Object.FindObjectsByType<Volume>(FindObjectsSortMode.None))
        {
            if(v.sharedProfile.TryGet<Bloom>(out var bloom)){bloom.intensity.Override(.30f);bloom.threshold.Override(.95f);bloom.scatter.Override(.6f);}
            var adjust=v.sharedProfile.Add<ColorAdjustments>(true);adjust.postExposure.Override(.12f);adjust.contrast.Override(4);adjust.saturation.Override(-4);
        }
        room.SetNight(false);
    }
    static void ConfigurePcRenderer(string root)
    {
        // Preserve the original mobile profile and use a dedicated full-native
        // PC profile: previous 0.8 render scale blurred otherwise-4K materials.
        var source=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/Settings/Mobile_RPAsset.asset");
        var rp=Object.Instantiate(source);rp.name="LOFI PC native quality";
        var renderer=Object.Instantiate(AssetDatabase.LoadAssetAtPath<UniversalRendererData>("Assets/Settings/Mobile_Renderer.asset"));
        renderer.name="LOFI PC renderer";renderer.rendererFeatures.Clear();Store(renderer,root+"/PcRenderer.asset");
        var ao=ScriptableObject.CreateInstance<ScreenSpaceAmbientOcclusion>();ao.name="Soft contact ambient occlusion";
        AssetDatabase.AddObjectToAsset(ao,renderer);renderer.rendererFeatures.Add(ao);
        var setting=new SerializedObject(ao);var s=setting.FindProperty("m_Settings");
        s.FindPropertyRelative("Intensity").floatValue=.65f;s.FindPropertyRelative("Radius").floatValue=.13f;
        s.FindPropertyRelative("DirectLightingStrength").floatValue=.16f;s.FindPropertyRelative("Downsample").boolValue=false;
        // Composite after opaque objects: the custom stylized surface and
        // skinned character must share the same contact-occlusion treatment.
        s.FindPropertyRelative("AfterOpaque").boolValue=true;s.FindPropertyRelative("Source").enumValueIndex=0;
        s.FindPropertyRelative("NormalSamples").enumValueIndex=2;s.FindPropertyRelative("Samples").enumValueIndex=0;
        setting.ApplyModifiedPropertiesWithoutUndo();ao.Create();
        var so=new SerializedObject(rp);so.FindProperty("m_RendererDataList").GetArrayElementAtIndex(0).objectReferenceValue=renderer;
        so.FindProperty("m_SoftShadowsSupported").boolValue=true;so.FindProperty("m_AdditionalLightShadowsSupported").boolValue=true;
        so.FindProperty("m_ShadowNormalBias").floatValue=.18f;so.FindProperty("m_ShadowDepthBias").floatValue=.15f;
        so.ApplyModifiedPropertiesWithoutUndo();
        rp.renderScale=1;rp.msaaSampleCount=4;rp.supportsCameraDepthTexture=true;rp.supportsHDR=true;
        rp.shadowDistance=18;rp.mainLightShadowmapResolution=4096;rp.gpuResidentDrawerMode=GPUResidentDrawerMode.Disabled;
        Store(rp,root+"/PcQuality.asset");GraphicsSettings.defaultRenderPipeline=rp;QualitySettings.renderPipeline=rp;
        QualitySettings.vSyncCount=1;EditorUtility.SetDirty(renderer);EditorUtility.SetDirty(ao);
    }
    static Texture2D WindowCookie(string root)
    {
        const int size=256;var cookie=new Texture2D(size,size,TextureFormat.RGBA32,false,true);cookie.name="Four pane window aperture";
        var pixels=new Color[size*size];
        for(int y=0;y<size;y++)for(int x=0;x<size;x++)
        {
            float u=(x+.5f)/size,v=(y+.5f)/size;
            float border=Mathf.Min(Mathf.Min(u,1-u),Mathf.Min(v,1-v));
            float alpha=Mathf.SmoothStep(0,1,Mathf.InverseLerp(.055f,.11f,border));
            alpha*=Mathf.SmoothStep(0,1,Mathf.InverseLerp(.018f,.035f,Mathf.Abs(u-.5f)));
            alpha*=Mathf.SmoothStep(0,1,Mathf.InverseLerp(.018f,.035f,Mathf.Abs(v-.5f)));
            pixels[y*size+x]=new Color(alpha,alpha,alpha,alpha);
        }
        cookie.SetPixels(pixels);cookie.Apply();cookie.wrapMode=TextureWrapMode.Clamp;cookie.filterMode=FilterMode.Bilinear;
        Store(cookie,root+"/WindowCookie.asset");return cookie;
    }
    static void Store(Object asset,string path)
    {
        if(AssetDatabase.LoadMainAssetAtPath(path))AssetDatabase.DeleteAsset(path);
        AssetDatabase.CreateAsset(asset,path);
    }
}

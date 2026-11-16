Shader "Yamyam/Lofi Detailed Surface"
{
    Properties
    {
        _BaseMap("Color",2D)="white"{}
        _BaseColor("Tint",Color)=(1,1,1,1)
        _BumpMap("Normal",2D)="bump"{}
        _RoughnessMap("Roughness",2D)="white"{}
        _MetallicMap("Metallic",2D)="black"{}
        _UsePbrMaps("Use imported PBR",Float)=0
        _NormalStrength("Normal strength",Float)=0.65
        _Smoothness("Smoothness",Range(0,1))=0.3
        _Metallic("Metallic",Range(0,1))=0
        _Pattern("0 plain, 1 wood, 2 cloth, 3 plaster, 4 metal, 5 leaf",Float)=0
        _DetailStrength("Surface detail",Range(0,1))=0.2
        _WindStrength("Leaf breeze",Float)=0
        _HairEnabled("Hair vertex mask",Float)=0
        _Cull("Cull",Float)=2
        _HairMotion("Hair inertia world offset",Vector)=(0,0,0,0)
        _HairOffset1("Hair chain 1",Vector)=(0,0,0,0)
        _HairOffset2("Hair chain 2",Vector)=(0,0,0,0)
        _HairOffset3("Hair chain 3",Vector)=(0,0,0,0)
        _HairOffset4("Hair chain 4",Vector)=(0,0,0,0)
    }
    SubShader
    {
        Tags {"RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" "Queue"="Geometry"}
        Pass
        {
            Name "ForwardLit"
            Tags {"LightMode"="UniversalForward"}
            Cull [_Cull]
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING
            #pragma multi_compile_fragment _ _REFLECTION_PROBE_BOX_PROJECTION
            #pragma multi_compile_fog
            #pragma multi_compile_instancing
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/SurfaceInput.hlsl"
            TEXTURE2D(_RoughnessMap);SAMPLER(sampler_RoughnessMap);
            TEXTURE2D(_MetallicMap);SAMPLER(sampler_MetallicMap);
            CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;half4 _BaseColor;half _Smoothness,_Metallic,_Pattern,_DetailStrength,_WindStrength,_HairEnabled,_UsePbrMaps,_NormalStrength;float4 _HairMotion,_HairOffset1,_HairOffset2,_HairOffset3,_HairOffset4;
            CBUFFER_END
            float _LofiWind;
            struct Attributes {float4 positionOS:POSITION;float3 normalOS:NORMAL;float4 tangentOS:TANGENT;float2 uv:TEXCOORD0;float4 color:COLOR;UNITY_VERTEX_INPUT_INSTANCE_ID};
            struct Varyings {float4 positionCS:SV_POSITION;float3 positionWS:TEXCOORD0;half3 normalWS:TEXCOORD1;half4 tangentWS:TEXCOORD2;float2 uv:TEXCOORD3;half fog:TEXCOORD4;float4 shadowCoord:TEXCOORD5;UNITY_VERTEX_INPUT_INSTANCE_ID UNITY_VERTEX_OUTPUT_STEREO};
            float Hash(float2 p){return frac(sin(dot(p,float2(127.1,311.7)))*43758.5453);}
            float Noise(float2 p){float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(Hash(i),Hash(i+float2(1,0)),f.x),lerp(Hash(i+float2(0,1)),Hash(i+1),f.x),f.y);}
            Varyings Vert(Attributes a)
            {
                Varyings o=(Varyings)0;UNITY_SETUP_INSTANCE_ID(a);UNITY_TRANSFER_INSTANCE_ID(a,o);UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                float3 p=TransformObjectToWorld(a.positionOS.xyz);
                float mask=0;if(_HairEnabled>.5 || _WindStrength>.0001)mask=saturate(a.color.r);
                if(_HairEnabled>.5)
                {
                    float t=saturate(a.color.g)*4;float3 offset=0;
                    if(t<1)offset=lerp(0,_HairOffset1.xyz,t);
                    else if(t<2)offset=lerp(_HairOffset1.xyz,_HairOffset2.xyz,t-1);
                    else if(t<3)offset=lerp(_HairOffset2.xyz,_HairOffset3.xyz,t-2);
                    else offset=lerp(_HairOffset3.xyz,_HairOffset4.xyz,t-3);
                    p+=offset*mask;
                }
                float3 root=TransformObjectToWorld(float3(0,0,0));
                float phase=_Time.y*1.1+root.x*2.4+root.z*2.1;
                if(_WindStrength>.0001)
                {
                    float gust=.68+.32*sin(_Time.y*.43+root.x);
                    float scale=saturate(length(a.positionOS.xyz)*2.2+.06);
                    float sway=(sin(phase)+sin(phase*.57+1.3)*.3)*_WindStrength*_LofiWind*gust*scale;
                    float flutter=sin(_Time.y*2.1+a.uv.y*3.0+root.z)*_WindStrength*.15*_LofiWind*scale;
                    p+=float3(sway,-abs(sway)*.12,cos(phase*.83)*_WindStrength*.38*_LofiWind)*mask;
                    p+=float3(0,flutter,flutter*.3)*mask*saturate(abs(a.uv.x-.5)*2);
                }
                o.positionWS=p;o.positionCS=TransformWorldToHClip(p);o.normalWS=TransformObjectToWorldNormal(a.normalOS);
                o.tangentWS=half4(TransformObjectToWorldDir(a.tangentOS.xyz),a.tangentOS.w*GetOddNegativeScale());o.uv=TRANSFORM_TEX(a.uv,_BaseMap);o.fog=ComputeFogFactor(o.positionCS.z);o.shadowCoord=TransformWorldToShadowCoord(p);return o;
            }
            half4 Frag(Varyings i,FRONT_FACE_TYPE face:FRONT_FACE_SEMANTIC):SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(i);
                half3 color=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.uv).rgb*_BaseColor.rgb;
                float detail=0;float2 p=i.positionWS.xz;
                if(abs(i.normalWS.y)<.5)p=float2(i.positionWS.y,abs(i.normalWS.x)>.5?i.positionWS.z:i.positionWS.x);
                if(_Pattern>0.5 && _Pattern<1.5)
                {
                    float w=Noise(p*float2(.72,5));
                    float phase=(p.y*95+w*5+Noise(p*float2(.3,15))*2)*3.14159;
                    float grain=sin(phase)*saturate(1-fwidth(phase)/3.14159);
                    float fine=Noise(p*float2(9,280));float fineFade=saturate(1-max(fwidth(p.x*9),fwidth(p.y*280)));
                    detail=grain*.13+(fine-.5)*.32*fineFade;
                    color*=1+detail*_DetailStrength;
                }
                if(_Pattern>1.5 && _Pattern<2.5)
                {float2 t=i.uv*180;float weave=sin(t.x*6.283)*sin(t.y*6.283)*saturate(1-max(fwidth(t.x),fwidth(t.y)));detail=weave*.22;color*=1+detail*_DetailStrength;}
                if(_Pattern>2.5 && _Pattern<3.5){float plaster=(Noise(i.positionWS.xy*65)+Noise(i.positionWS.yz*65)+Noise(i.positionWS.zx*65))/3;detail=(plaster-.5)*.16;color*=1+detail*_DetailStrength;}
                if(_Pattern>3.5 && _Pattern<4.5){detail=(Noise(i.uv*float2(650,8))-.5)*.2;color*=1+detail*_DetailStrength;}
                if(_Pattern>4.5)
                {
                    float center=exp(-abs(i.uv.x-.5)*120);
                    float veins=pow(saturate(cos((i.uv.y*12+abs(i.uv.x-.5)*7)*6.283)),22);
                    color*=.94+.13*i.uv.y;color+=_BaseColor.rgb*(center*.22+veins*.045);
                }
                half3 n=normalize(i.normalWS)*IS_FRONT_VFACE(face,1,-1);
                if(_Pattern>.5 && _Pattern<4.5)
                {
                    float3 dx=ddx(i.positionWS),dy=ddy(i.positionWS);float3 r1=cross(dy,n),r2=cross(n,dx);float det=dot(dx,r1);
                    if(abs(det)>1e-9)n=normalize(n-(r1*ddx(detail)+r2*ddy(detail))/det*(_Pattern<1.5?.0006:.00025)*_DetailStrength);
                }
                if(_UsePbrMaps>.5)
                {
                    half3 tangent=normalize(i.tangentWS.xyz);half3 bitangent=normalize(cross(n,tangent))*i.tangentWS.w;
                    half3 normalTS=UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap,sampler_BumpMap,i.uv),_NormalStrength);
                    n=NormalizeNormalPerPixel(TransformTangentToWorld(normalTS,half3x3(tangent,bitangent,n)));
                }
                SurfaceData surface=(SurfaceData)0;surface.albedo=color;surface.alpha=1;surface.occlusion=1;
                surface.metallic=_UsePbrMaps>.5?SAMPLE_TEXTURE2D(_MetallicMap,sampler_MetallicMap,i.uv).r:_Metallic;
                surface.smoothness=_UsePbrMaps>.5?1-SAMPLE_TEXTURE2D(_RoughnessMap,sampler_RoughnessMap,i.uv).r:_Smoothness;
                surface.smoothness=clamp(surface.smoothness,.03,.85);
                InputData data=(InputData)0;data.positionWS=i.positionWS;data.normalWS=n;data.viewDirectionWS=GetWorldSpaceNormalizeViewDir(i.positionWS);data.shadowCoord=i.shadowCoord;data.fogCoord=i.fog;data.vertexLighting=VertexLighting(i.positionWS,n);data.bakedGI=SampleSH(n);data.normalizedScreenSpaceUV=GetNormalizedScreenSpaceUV(i.positionCS);data.shadowMask=half4(1,1,1,1);
                half4 result=UniversalFragmentPBR(data,surface);result.rgb=MixFog(result.rgb,i.fog);return result;
            }
            ENDHLSL
        }
        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
        UsePass "Universal Render Pipeline/Lit/DepthOnly"
        UsePass "Universal Render Pipeline/Lit/DepthNormals"
    }
    FallBack "Universal Render Pipeline/Lit"
}

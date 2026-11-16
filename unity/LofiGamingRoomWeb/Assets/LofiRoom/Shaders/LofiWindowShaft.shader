Shader "Yamyam/Window Light Volume"
{
    Properties { _BeamColor("Scattered light",Color)=(1,0.8,0.47,1) _Density("Density",Float)=0.12 _Strength("Day/night strength",Float)=1 }
    SubShader
    {
        Tags {"RenderPipeline"="UniversalPipeline" "Queue"="Transparent+5" "RenderType"="Transparent"}
        Pass
        {
            Cull Front ZWrite Off ZTest Always Blend One One
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.5
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"
            CBUFFER_START(UnityPerMaterial)
            half4 _BeamColor;float _Density,_Strength;
            CBUFFER_END
            struct A {float4 positionOS:POSITION;};
            struct V {float4 positionCS:SV_POSITION;float3 positionWS:TEXCOORD0;};
            V Vert(A a){V o;o.positionWS=TransformObjectToWorld(a.positionOS.xyz);o.positionCS=TransformWorldToHClip(o.positionWS);return o;}
            half4 Frag(V i):SV_Target
            {
                float2 uv=i.positionCS.xy/_ScaledScreenParams.xy;
                float depth=SampleSceneDepth(uv);
                #if !UNITY_REVERSED_Z
                depth=lerp(UNITY_NEAR_CLIP_VALUE,1,depth);
                #endif
                float3 scene=ComputeWorldSpacePosition(uv,depth,UNITY_MATRIX_I_VP);
                float3 forward=-UNITY_MATRIX_V[2].xyz;
                float3 origin=GetCameraPositionWS();float3 dir=normalize(i.positionWS-origin);
                if(unity_OrthoParams.w>.5)
                {dir=forward;origin=i.positionWS-dir*dot(i.positionWS-origin,dir);}
                float3 safeDir=dir+float3(.000001,.000001,.000001);
                float3 t0=(float3(-2.9,.06,-2.1)-origin)/safeDir;
                float3 t1=(float3(1.7,2.8,2.25)-origin)/safeDir;
                float3 lo=min(t0,t1),hi=max(t0,t1);
                float start=max(max(lo.x,lo.y),max(lo.z,0));
                float end=min(min(hi.x,hi.y),hi.z);
                end=min(end,dot(scene-origin,dir));
                if(end<=start)return 0;
                const int Samples=56;
                float stepLength=(end-start)/Samples;float total=0;
                [loop]for(int n=0;n<Samples;n++)
                {
                    float3 p=origin+dir*(start+(n+.5)*stepLength);
                    float distanceFromWindow=2.24-p.z;
                    float2 entry=float2(p.x-distanceFromWindow*.44,p.y+distanceFromWindow*.62);
                    float edge=min(min(entry.x+2.73,-.87-entry.x),min(entry.y-.87,2.71-entry.y));
                    float aperture=smoothstep(0,.065,edge);
                    aperture*=smoothstep(.026,.055,abs(entry.x+1.8))*smoothstep(.023,.055,abs(entry.y-1.74));
                    float dust=.9+.1*sin(p.x*12+p.y*9+p.z*7+_Time.y*.18);
                    total+=aperture*exp(-distanceFromWindow*.34)*dust*stepLength;
                }
                return half4(_BeamColor.rgb*total*_Density*_Strength,0);
            }
            ENDHLSL
        }
    }
}

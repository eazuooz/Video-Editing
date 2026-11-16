Shader "Yamyam/Hearth Flame"
{
    Properties { _BaseColor("Tint",Color)=(1,1,1,1) _Mode("Flame / ember / smoke",Float)=0 }
    SubShader
    {
        Tags {"RenderPipeline"="UniversalPipeline" "RenderType"="Transparent" "Queue"="Transparent"}
        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha ZWrite Off Cull Off
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"
            CBUFFER_START(UnityPerMaterial)
            half4 _BaseColor;float _Mode;
            CBUFFER_END
            struct A {float4 p:POSITION;float2 uv:TEXCOORD0;half4 color:COLOR;};
            struct V {float4 p:SV_POSITION;float2 uv:TEXCOORD0;half4 color:COLOR;float3 world:TEXCOORD1;};
            float H(float2 p){return frac(sin(dot(p,float2(127.1,311.7)))*43758.5453);}
            float N(float2 p){float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(H(i),H(i+float2(1,0)),f.x),lerp(H(i+float2(0,1)),H(i+1),f.x),f.y);}
            V Vert(A a){V o;o.world=TransformObjectToWorld(a.p.xyz);o.p=TransformWorldToHClip(o.world);o.uv=a.uv;o.color=a.color;return o;}
            half4 Frag(V i):SV_Target
            {
                float2 uv=i.uv;float seed=i.world.z*9+i.world.x*5;
                float turbulence=N(float2(uv.x*5+seed,uv.y*4-_Time.y*2.1))*.6+N(float2(uv.x*11-seed,uv.y*9-_Time.y*3.3))*.4;
                float center=.5+sin(uv.y*7-_Time.y*3+seed)*.075*uv.y;
                float width=(.42*(1-uv.y)+.02)*( .65+turbulence*.7);
                float edge=1-abs(uv.x-center)/max(width,.01);
                float alpha=smoothstep(.03,.3,edge)*smoothstep(0,.06,uv.y)*smoothstep(1,.67,uv.y);
                float core=saturate(edge*1.6-uv.y*.8-.5);
                half3 color=lerp(half3(1.8,.16,.008),half3(3.3,1.9,.35),core);
                alpha*=saturate(turbulence*1.7+.15);
                if(_Mode>.5 && _Mode<1.5){float r=length((uv-.5)*2);alpha=pow(saturate(1-r),1.6);color=half3(3,1.0,.12);}
                if(_Mode>1.5){float r=length((uv-.5)*2);alpha=pow(saturate(1-r),2)*turbulence*.35;color=half3(.23,.20,.18);}
                float2 screenUV=i.p.xy/_ScaledScreenParams.xy;float raw=SampleSceneDepth(screenUV);
                #if !UNITY_REVERSED_Z
                raw=lerp(UNITY_NEAR_CLIP_VALUE,1,raw);
                #endif
                float3 scene=ComputeWorldSpacePosition(screenUV,raw,UNITY_MATRIX_I_VP);
                float3 forward=-UNITY_MATRIX_V[2].xyz;float soft=saturate(dot(scene-i.world,forward)/.08);
                return half4(color*_BaseColor.rgb,alpha*i.color.a*_BaseColor.a*soft);
            }
            ENDHLSL
        }
    }
}

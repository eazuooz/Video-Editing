Shader "Yamyam/Forest Window"
{
    Properties {_DayAmount("Day",Range(0,1))=0}
    SubShader
    {
        Tags {"RenderType"="Opaque" "RenderPipeline"="UniversalPipeline"}
        Pass
        {
            Cull Off
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            CBUFFER_START(UnityPerMaterial)
            float _DayAmount;
            CBUFFER_END
            struct A{float4 p:POSITION;float2 uv:TEXCOORD0;};
            struct V{float4 p:SV_POSITION;float2 uv:TEXCOORD0;};
            V Vert(A a){V o;o.p=TransformObjectToHClip(a.p.xyz);o.uv=a.uv;return o;}
            float Hash(float n){return frac(sin(n*127.1+311.7)*43758.5453);}
            float Tree(float2 p,float x,float baseY,float height,float seed)
            {
                p.x-=x+sin(_Time.y*.55+seed)*.003*saturate((p.y-baseY)/height);
                float y=(p.y-baseY)/height;
                float canopy=0;
                for(int j=0;j<5;j++)
                {
                    float b=.12+j*.135,top=b+.40;
                    float width=(top-y)/.40*(.28-j*.043)*height;
                    canopy=max(canopy,(1-smoothstep(width-.003,width+.003,abs(p.x)))*smoothstep(b-.006,b+.006,y)*(1-step(top,y)));
                }
                float trunk=(1-smoothstep(.006,.009,abs(p.x)))*step(0,y)*(1-step(.8,y));
                return max(canopy,trunk);
            }
            half4 Frag(V i):SV_Target
            {
                float2 uv=i.uv;float day=saturate(_DayAmount);
                float3 sky=lerp(lerp(float3(.085,.19,.29),float3(.018,.055,.14),uv.y),lerp(float3(.66,.79,.71),float3(.24,.53,.65),uv.y),day);
                float2 moonP=(uv-float2(.74,.79));float m=length(moonP);
                float halo=exp(-m*15)*.19*(1-day);
                sky+=float3(.43,.63,.80)*halo;
                float disc=1-smoothstep(.081,.084,m);
                float crater=Hash(floor(uv.x*93)+floor(uv.y*93)*93)*.045;
                crater+=(1-smoothstep(.023,.035,length(moonP-float2(-.023,.021))))*.18;
                crater+=(1-smoothstep(.014,.025,length(moonP-float2(.030,-.018))))*.12;
                crater+=(1-smoothstep(.010,.017,length(moonP-float2(-.012,-.047))))*.13;
                sky=lerp(sky,float3(1.12,1.16,1.00)-crater,disc*(1-day));
                for(int s=0;s<19;s++)
                {
                    float2 star=float2(Hash(s*3.17+.7),.56+Hash(s*7.37+2)*.42);
                    float dotStar=1-smoothstep(.0015,.0035,length(uv-star));
                    sky+=dotStar*float3(.54,.68,.71)*(1-day)*(.75+.25*sin(_Time.y*.7+s));
                }
                float hill=.36+.075*sin(uv.x*7)+.028*sin(uv.x*19);
                sky=lerp(sky,lerp(float3(.12,.24,.30),float3(.27,.46,.42),day),1-smoothstep(hill-.005,hill+.005,uv.y));
                for(int layer=0;layer<3;layer++)
                {
                    float mask=0;
                    for(int t=0;t<12;t++)
                    {
                        float seed=t*4.71+layer*27.3;
                        float x=(t+.5)/12+.04*(Hash(seed)-.5);
                        float height=.30+Hash(seed+1)*(.25-layer*.025);
                        float baseY=.08-layer*.14;
                        mask=max(mask,Tree(uv,x,baseY,height,seed));
                    }
                    float3 tint=lerp(lerp(float3(.14,.36,.39),float3(.024,.16,.17),layer*.5),lerp(float3(.27,.53,.40),float3(.07,.28,.20),layer*.5),day);
                    sky=lerp(sky,tint,mask);
                }
                return half4(sky,1);
            }
            ENDHLSL
        }
    }
}

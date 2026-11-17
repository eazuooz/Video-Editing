Shader "Yamyam/Window Rain"
{
 Properties { _Rain("Rain",Float)=0 }
 SubShader {
 Tags {"RenderPipeline"="UniversalPipeline" "Queue"="Transparent+15" "RenderType"="Transparent"}
 Pass { Blend SrcAlpha OneMinusSrcAlpha ZWrite Off Cull Off
 HLSLPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
 struct A{float4 p:POSITION;float2 uv:TEXCOORD0;};struct V{float4 p:SV_POSITION;float2 uv:TEXCOORD0;};
 float _Rain;
 V vert(A i){V o;o.p=TransformObjectToHClip(i.p.xyz);o.uv=i.uv;return o;}
 float hash(float x){return frac(sin(x*127.1)*43758.5453);}
 half4 frag(V i):SV_Target {
 float2 uv=i.uv;float t=_Time.y;float streak=0;
 for(int layer=0;layer<2;layer++){
 float count=29+layer*20;float col=floor((uv.x+uv.y*.10)*count);float r=hash(col+layer*120);float x=abs(frac((uv.x+uv.y*.10)*count)-.5);
 float yy=frac(uv.y*(3+layer*2)+t*(1.3+r*.7)+r*19);float rainLine=(1-smoothstep(.018,.07,x))*smoothstep(.1,.17,yy)*(1-smoothstep(.39,.47,yy));streak+=rainLine*(.5+layer*.18);
 }
 float col=floor(uv.x*17);float r=hash(col+33);float2 drop=float2(frac(uv.x*17)-.5,frac(uv.y*5+t*(.12+r*.13)+r*24)-.5);drop.y*=2.6;float glass=1-smoothstep(.045,.095,length(drop));
 float edge=smoothstep(0,.03,uv.x)*smoothstep(0,.03,1-uv.x)*smoothstep(0,.03,uv.y)*smoothstep(0,.03,1-uv.y);
 return half4(.66,.82,.91,saturate(streak+glass*.7)*_Rain*edge);
 }
 ENDHLSL
 }
 }
}

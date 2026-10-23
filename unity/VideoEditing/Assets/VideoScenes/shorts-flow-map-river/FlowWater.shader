Shader "Yamyam/FlowMapWater" {
 Properties { _Flow("Linear RG flow",2D)="gray"{} _Ripple("Ripple normal and foam",2D)="bump"{} _Clock("Clock",Float)=0 _UseFlow("Use flow",Float)=1 _Display("Water / map",Float)=0 _Blend("Blend phases",Float)=1 _Long("Long stretch",Float)=0 _RiverTint("Tint",Color)=(.015,.27,.30,1) }
 SubShader { Tags {"RenderType"="Opaque"} Pass {
 CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 sampler2D _Flow,_Ripple;float _Clock,_UseFlow,_Display,_Blend,_Long;float4 _RiverTint;
 struct app{float4 vertex:POSITION;float2 uv:TEXCOORD0;};struct vary{float4 pos:SV_POSITION;float2 uv:TEXCOORD0;float3 world:TEXCOORD1;};
 vary vert(app v){vary o;o.pos=UnityObjectToClipPos(v.vertex);o.uv=v.uv;o.world=mul(unity_ObjectToWorld,v.vertex).xyz;return o;}
 float4 frag(vary i):SV_Target{
  float2 encoded=tex2D(_Flow,i.uv).rg;float2 flow=lerp(float2(.40,0),encoded*2-1,_UseFlow);
  if(_Display>.5)return float4(encoded,0,1);
  float localNoise=sin(i.uv.x*15.3+i.uv.y*4.1)*sin(i.uv.y*14.7)*.11;
  float phase=frac(_Clock*.30+localNoise),other=frac(phase+.5);
  float w=abs(phase*2-1);float2 baseUV=i.uv*float2(5,2.5);
  float p0=lerp(phase,_Clock*.30,_Long);
  float4 a=tex2D(_Ripple,baseUV-flow*p0*.85);
  float4 b=tex2D(_Ripple,baseUV-flow*other*.85+float2(.31,.73));
  float4 tex=lerp(a,b,w*_Blend);float2 grad=(tex.rg*2-1)*.85;
  float3 n=normalize(float3(grad.x,1,grad.y));float3 l=normalize(float3(-.6,1,-.7));float3 v=normalize(_WorldSpaceCameraPos-i.world);
  float diff=saturate(dot(n,l));float spec=pow(saturate(dot(n,normalize(l+v))),60);
  float fres=pow(1-saturate(dot(n,v)),3);float foam=smoothstep(.58,.84,tex.b);
  float3 c=_RiverTint.rgb*(.52+diff*.48)+float3(.08,.22,.24)*fres+float3(.48,.71,.68)*spec+float3(.28,.52,.48)*foam;
  return float4(c,1);
 }
 ENDCG } }
}

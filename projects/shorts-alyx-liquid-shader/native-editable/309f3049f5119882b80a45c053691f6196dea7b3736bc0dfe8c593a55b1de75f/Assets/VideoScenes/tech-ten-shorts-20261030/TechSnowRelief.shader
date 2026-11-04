Shader "Yamyam/TechTen/SnowRelief" {
 Properties { _Color("Snow",Color)=(.83,.91,.98,1) _HeightMap("Captured accumulated depth",2D)="black"{} _Depth("Our depth scale",Float)=.12 _ReliefEnabled("Virtual depth on flat geometry",Float)=1 }
 SubShader { Tags {"RenderType"="Opaque"} Pass {
  Cull Off
  CGPROGRAM
  #pragma target 3.0
  #pragma vertex vert
  #pragma fragment frag
  #include "UnityCG.cginc"
  sampler2D _HeightMap;float4 _HeightMap_TexelSize,_Color;float _Depth,_ReliefEnabled;
  struct v2f {float4 pos:SV_POSITION;float3 world:TEXCOORD0;float2 uv:TEXCOORD1;};
  v2f vert(appdata_base v){v2f o;o.pos=UnityObjectToClipPos(v.vertex);o.world=mul(unity_ObjectToWorld,v.vertex).xyz;o.uv=v.texcoord;return o;}
  float depthAt(float2 uv){return tex2Dlod(_HeightMap,float4(uv,0,0)).r;}
  fixed4 frag(v2f i):SV_Target {
   float2 uv=i.uv;
   if(_ReliefEnabled>.5){
    float3 view=_WorldSpaceCameraPos-i.world;
    // Follow the viewing ray below the unchanged top plane. World-map extents
    // are 8 by 4 metres; positive height-map values mean a depression.
    float2 delta=-view.xz/max(view.y,.08)*_Depth/float2(8,4);
    float low=0,high=0;
    [loop]for(int step=0;step<=40;step++){
     high=step/40.0;
     if(high>=depthAt(i.uv+delta*high))break;
     low=high;
    }
    [unroll]for(int refinement=0;refinement<5;refinement++){
     float mid=(low+high)*.5;
     if(mid>=depthAt(i.uv+delta*mid))high=mid;else low=mid;
    }
    uv=i.uv+delta*high;
   }
   float2 du=float2(_HeightMap_TexelSize.x,0),dv=float2(0,_HeightMap_TexelSize.y);
   float h=depthAt(uv);
   float dx=(depthAt(uv+du)-depthAt(uv-du))*_Depth/(16*_HeightMap_TexelSize.x);
   float dz=(depthAt(uv+dv)-depthAt(uv-dv))*_Depth/(8*_HeightMap_TexelSize.y);
   float3 normal=normalize(float3(dx,1,dz));
   float shade=.32+.68*saturate(dot(normal,normalize(float3(-.35,.8,-.5))));
   float3 baseColor=lerp(_Color.rgb,float3(.28,.38,.43),h*.65);
   return fixed4(baseColor*shade,1);
  }
  ENDCG
 } }
}

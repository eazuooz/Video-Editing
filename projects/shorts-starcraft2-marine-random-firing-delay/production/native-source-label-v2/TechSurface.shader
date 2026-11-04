Shader "Yamyam/TechTen/Surface"
{
 Properties { _Color("Color", Color)=(1,1,1,1) _MainTex("Texture",2D)="white"{} _ClipEnabled("Clip",Float)=0 _Plane("World clip plane",Vector)=(0,1,0,0) _WaterMask("Water mask",Float)=0 _MaskRect("Interior x/z extents",Vector)=(-1,1,-2,2) }
 SubShader {
  Tags { "RenderType"="Opaque" }
  Pass {
   Cull Off
   CGPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #include "UnityCG.cginc"
   struct v2f {float4 p:SV_POSITION;float3 world:TEXCOORD0;float3 normal:TEXCOORD1;float2 uv:TEXCOORD2;};
   sampler2D _MainTex;float4 _Color,_Plane,_MaskRect;float _ClipEnabled,_WaterMask;
   v2f vert(appdata_base v){v2f o;o.p=UnityObjectToClipPos(v.vertex);o.world=mul(unity_ObjectToWorld,v.vertex).xyz;o.normal=UnityObjectToWorldNormal(v.normal);o.uv=v.texcoord;return o;}
   fixed4 frag(v2f i):SV_Target {
    if(_ClipEnabled>.5)clip(-dot(float4(i.world,1),_Plane));
    if(_WaterMask>.5 && i.world.x>_MaskRect.x && i.world.x<_MaskRect.y && i.world.z>_MaskRect.z && i.world.z<_MaskRect.w)discard;
    float shade=.38+.62*saturate(dot(normalize(i.normal),normalize(float3(-.35,.8,-.5))));
    return fixed4(tex2D(_MainTex,i.uv).rgb*_Color.rgb*shade,1);
   }
   ENDCG
  }
 }
}

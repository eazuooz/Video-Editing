Shader "Yamyam/OneActionCharacterSurface" {
 Properties { _MainTex("Texture",2D)="white"{} _Color("Color",Color)=(1,1,1,1) }
 SubShader { Tags { "RenderType"="Opaque" } Pass {
 CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 sampler2D _MainTex; float4 _MainTex_ST; fixed4 _Color;
 struct appdata { float4 vertex:POSITION;float3 normal:NORMAL;float2 uv:TEXCOORD0; };
 struct v2f { float4 pos:SV_POSITION;float3 normal:TEXCOORD1;float2 uv:TEXCOORD0; };
 v2f vert(appdata v){v2f o;o.pos=UnityObjectToClipPos(v.vertex);o.normal=UnityObjectToWorldNormal(v.normal);o.uv=TRANSFORM_TEX(v.uv,_MainTex);return o;}
 fixed4 frag(v2f i):SV_Target {fixed4 c=tex2D(_MainTex,i.uv)*_Color;float light=.58+.42*max(0,dot(normalize(i.normal),normalize(float3(-.3,.6,.8))));return fixed4(c.rgb*light,c.a);}
 ENDCG
 } }
}

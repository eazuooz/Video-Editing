Shader "Yamyam/InteriorMappingRoom" {
 Properties { _Mapped("View dependent",Float)=1 _Structure("Show physical plane",Float)=0 _Viewer("Viewer object space",Vector)=(0,0,-6,1) }
 SubShader { Tags {"RenderType"="Opaque"} Cull Off
 Pass { CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 float _Mapped,_Structure; float4 _Viewer;
 struct appdata { float4 vertex:POSITION;float2 uv:TEXCOORD0; };
 struct v2f {float4 pos:SV_POSITION;float3 local:TEXCOORD0;float2 uv:TEXCOORD1;};
 v2f vert(appdata v){v2f o;o.pos=UnityObjectToClipPos(v.vertex);o.local=v.vertex.xyz;o.uv=v.uv;return o;}
 float box(float2 p,float2 a,float2 b){return step(a.x,p.x)*step(p.x,b.x)*step(a.y,p.y)*step(p.y,b.y);}
 float3 wallpaper(float2 uv){
  float3 c=float3(.18,.34,.34); c*=.91+.09*step(.035,frac(uv.x*12));
  // Original graphic artwork, shelf, books and cabinet painted on the wall.
  c=lerp(c,float3(.75,.59,.34),box(uv,float2(.3,.49),float2(.72,.84)));
  c=lerp(c,float3(.06,.12,.18),box(uv,float2(.32,.51),float2(.70,.82)));
  float sun=1-smoothstep(.065,.07,length(uv-float2(.59,.72)));
  c=lerp(c,float3(1,.77,.35),sun);
  float hills=box(uv,float2(.32,.51),float2(.70,.65))*step(uv.y,.57+.05*sin(uv.x*25));
  c=lerp(c,float3(.2,.55,.46),hills);
  c=lerp(c,float3(.22,.12,.07),box(uv,float2(.08,.08),float2(.28,.74)));
  for(int k=0;k<4;k++){
   float y=.14+k*.14;
   for(int j=0;j<5;j++){
    float x=.095+j*.032;
    float3 book=lerp(float3(.58,.19,.13),float3(.73,.63,.39),frac(j*.37+k*.23));
    c=lerp(c,book,box(uv,float2(x,y),float2(x+.023,y+.10-frac(j*.43)*.03)));
   }
   c=lerp(c,float3(.43,.26,.13),box(uv,float2(.08,y-.025),float2(.28,y-.01)));
  }
  c=lerp(c,float3(.39,.23,.11),box(uv,float2(.39,.08),float2(.89,.29)));
  c=lerp(c,float3(.68,.46,.24),box(uv,float2(.37,.29),float2(.91,.32)));
  c=lerp(c,float3(.22,.12,.07),box(uv,float2(.63,.09),float2(.64,.28)));
  return c;
 }
 float4 frag(v2f i):SV_Target{
  if(_Structure>1.5)return float4(wallpaper(i.uv),1);
  if(_Structure>.5){float grid=max(step(.97,frac(i.uv.x*8)),step(.97,frac(i.uv.y*6)));return float4(lerp(float3(.04,.22,.25),float3(.45,.85,.80),grid),1);}
  float border=1-box(i.uv,float2(.045,.055),float2(.955,.945));
  if(border>.5){float bevel=step(.018,min(min(i.uv.x,1-i.uv.x),min(i.uv.y,1-i.uv.y)));return float4(lerp(float3(.12,.15,.16),float3(.38,.42,.43),bevel),1);}
  float3 entry=float3(i.local.xy,0);
  float3 ray=lerp(normalize(entry-float3(0,.1,-6)),normalize(entry-_Viewer.xyz),_Mapped);
  float tx=((ray.x>=0?2:-2)-entry.x)/(abs(ray.x)<.00001?.00001:ray.x);
  float ty=((ray.y>=0?1.5:-1.5)-entry.y)/(abs(ray.y)<.00001?.00001:ray.y);
  float tz=4/max(.00001,ray.z);float t=min(min(tx,ty),tz);float3 p=entry+ray*t;
  float3 col;
  if(tz<=tx&&tz<=ty){col=wallpaper(float2(p.x/4+.5,p.y/3+.5));}
  else if(tx<=ty){float2 uv=float2(p.z/4,p.y/3+.5);col=float3(.65,.55,.39)*(.88+.12*step(.06,frac(uv.x*8)));col=lerp(col,float3(.22,.14,.08),step(uv.y,.065));}
  else if(ray.y<0){float2 uv=float2(p.x+2,p.z);float joint=max(step(.965,frac(uv.x*2)),step(.975,frac(uv.y*1.2)));col=lerp(float3(.34,.18,.08)*(.9+.1*sin(uv.x*65+sin(uv.y*4))),float3(.12,.07,.04),joint);}
  else{float2 uv=float2(p.x/4+.5,p.z/4);col=float3(.72,.7,.58);float light=box(uv,float2(.35,.3),float2(.65,.6));col=lerp(col,float3(1,.95,.75),light);}
  float shading=.68+.32*saturate(1-p.z/7);col*=shading;
  // A narrow physical-looking window edge is still painted on the same plane.
  return float4(col,1);
 }
 ENDCG }
 }
}

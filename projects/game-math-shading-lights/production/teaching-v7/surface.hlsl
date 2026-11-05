// Offline material preview. The sphere, both interpolation orders and indicator share one constant buffer.
cbuffer Demo : register(b0) { float u; float mode; float width; float height; };
struct Out { float4 pos:SV_Position; float3 normal:NORMAL; float3 vertexColor:COLOR0; nointerpolation uint side:TEXCOORD1; };
float3 illuminate(float3 n, uint side) {
    // The observer looks along Z; the fixed shading camera sits to the left and above.
    // This lets V and the reflected ray be seen from the side.
    float3 V=normalize(float3(-.45,.28,.85));
    float angle = (mode==20 || mode==21 || mode==30) ? lerp(0.10,1.95,u) : lerp(-0.90,0.90,u);
    if (mode==12 || mode==6 || mode==58) angle=0.52;
    if (mode==22 || mode==23 || mode==41 || mode==46 || mode==48 || mode==54 || mode==57 || mode==72) angle=.52;
    float3 L=normalize(float3(sin(angle),.22,cos(angle)));
    float nl=dot(n,L);
    float3 material=float3(.22,.47,.49);
    float gloss = mode==12 ? lerp(6,100,u) : (mode==42 ? 58 : 28);
    float3 light = mode==6 ? float3(.85,lerp(.08,1.,u),.85) : float3(1,.91,.76);
    float diffuse=max(0,nl);
    if (mode==30 && side==1) diffuse=pow(.5*nl+.5,2);
    float inner=.8, outer=2.6, distanceToLight=lerp(inner,outer,u);
    float falloff=mode==58 ? saturate((outer-distanceToLight)/(outer-inner)) : 1;
    float spec = (mode==12 || mode==41 || mode==42) ? pow(max(0,dot(reflect(-L,n),V)),gloss) : 0;
    float3 direct=light*(material*diffuse+.84*spec);
    return .013*material+direct*falloff;
}
Out SphereVS(float3 p:POSITION,uint instance:SV_InstanceID) {
    Out o; bool split=mode==42 || mode==30;
    float radius=split?.216:.235;
    float2 center=float2(split ? (instance==0?.268:.732):.50,.455);
    float2 uv=center+radius*float2(p.x,-p.y*width/height);
    o.pos=float4(uv.x*2-1,1-2*uv.y,.5-.4*p.z,1);
    o.normal=p; o.side=instance;
    o.vertexColor=illuminate(p,instance);
    return o;
}
float4 SpherePS(Out p):SV_Target {
    bool vertexLit= mode==39 || (mode==42 && p.side==0);
    float3 litColor=vertexLit?p.vertexColor:illuminate(normalize(p.normal),p.side);
    return float4(pow(saturate(litColor),1/2.2),1);
}
float4 PlaneVS(uint i:SV_VertexID):SV_Position {return float4(i==2?3:-1,i==1?3:-1,0,1);}
float4 GaugePS(float4 pos:SV_Position):SV_Target {
    float2 at=pos.xy/float2(width,height);
    if(mode==39 && at.y<.90) {
        float2 a=float2(.16,.69), b=float2(.82,.64), c=float2(.41,.12);
        float2 e1=b-a,e2=c-a,d=at-a;
        float det=e1.x*e2.y-e2.x*e1.y;
        float wb=(d.x*e2.y-e2.x*d.y)/det,wc=(e1.x*d.y-d.x*e1.y)/det;
        float wa=1-wb-wc;
        float2 p=lerp(.64*a+.13*b+.23*c,.11*a+.77*b+.12*c,u);
        float radius=length((p-at)*float2(width,height));
        if(radius<9 && radius>5) return float4(1,.88,.65,1);
        if(min(wa,min(wb,wc))>=0) {
            if(min(wa,min(wb,wc))<.007) return float4(.53,.78,.81,1);
            float3 col=wa*float3(.08,.13,.17)+wb*float3(.78,.84,.73)+wc*float3(.14,.49,.53);
            return float4(col,1);
        }
        discard;
    }
    float x0=.12,x1=.88,y=.954;
    if (distance(pos.xy,float2(lerp(x0,x1,u)*width,y*height))<8) return float4(.99,.80,.42,1);
    if (abs(at.y-y)<.005 && at.x>=x0 && at.x<=x1)
        return float4(at.x<lerp(x0,x1,u)?float3(.98,.76,.36):float3(.22,.28,.29),1);
    discard;return 0;
}

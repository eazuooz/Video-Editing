// Scene-specific teaching marks. All numbers below are labeled illustrations.
// Keep the original black / warm-yellow / teal / orange semantic palette.
const C={white:'#f5f5f5',gold:'#e8cf83',teal:'#73c7c2',orange:'#f39a4b',muted:'#aaa',line:'#454a4d'};
const clamp=x=>Math.max(0,Math.min(1,x));
function text(c,s,x,y,size=42,color=C.white,align='center'){c.font=`500 ${size}px 'Noto Sans KR','Malgun Gothic',sans-serif`;c.textAlign=align;c.fillStyle=color;c.fillText(s,x,y);}
function line(c,x,y,xx,yy,color=C.line,width=5){c.strokeStyle=color;c.lineWidth=width;c.beginPath();c.moveTo(x,y);c.lineTo(xx,yy);c.stroke();}
function arrow(c,x,y,xx,yy,progress=1,color=C.gold){let p=clamp(progress),a=Math.atan2(yy-y,xx-x),ex=x+(xx-x)*p,ey=y+(yy-y)*p;line(c,x,y,ex,ey,color,7);if(p>.01){c.fillStyle=color;c.beginPath();c.moveTo(ex,ey);c.lineTo(ex-22*Math.cos(a-.45),ey-22*Math.sin(a-.45));c.lineTo(ex-22*Math.cos(a+.45),ey-22*Math.sin(a+.45));c.fill();}}
function circle(c,x,y,r,color,fill=false){c.beginPath();c.arc(x,y,r,0,Math.PI*2);if(fill){c.fillStyle=color;c.fill();}else{c.strokeStyle=color;c.lineWidth=5;c.stroke();}}

export function spatialPolicyOverlay(c,key,q,frame,block){
 const sec=frame/60;
 if(key==='02-p4'){
  c.fillStyle='black';c.fillRect(1230,140,630,650);
  const angle=q.angle*Math.PI/180,ox=1510,oy=530,len=225,amount=Math.cos(angle);
  text(c,'두 방향의 내적',1530,205,46,C.gold);
  arrow(c,ox,oy,ox,oy-len,1,C.teal);arrow(c,ox,oy,ox+Math.sin(angle)*len,oy-Math.cos(angle)*len,1,C.gold);
  text(c,'표면 방향 n',1370,280,34,C.teal);text(c,'빛 방향 l',1670,325,34,C.gold);
  c.strokeStyle=C.white;c.lineWidth=3;c.beginPath();c.arc(ox,oy,80,-Math.PI/2,-Math.PI/2+angle);c.stroke();
  text(c,`${q.angle.toFixed(0)}°`,1600,475,38);text(c,`n · l = ${amount.toFixed(2)}`,1530,620,58,C.gold);
  c.fillStyle=C.line;c.fillRect(1280,665,480,32);c.fillStyle=C.teal;c.fillRect(1280,665,480*amount,32);
  text(c,'두 화살표 길이 = 1',1530,750,34,C.white);
  return true;
 }
 if(key==='09a-p5'){
  c.fillStyle='black';c.fillRect(1230,140,630,650);
  if(sec<7.65){
   text(c,'검사할 점 → 해당 맵',1545,207,42,C.gold);
   const p=clamp(sec/7.4),x=1290+p*480,idx=Math.min(2,Math.floor(p*3));
   line(c,1290,300,1770,300,C.line,8);
   for(let i=0;i<3;i++){line(c,1290+i*160,282,1290+i*160,318,[C.teal,C.gold,C.orange][i]);text(c,`${i+1}구간`,1370+i*160,370,31,[C.teal,C.gold,C.orange][i]);}
   circle(c,x,300,13,C.white,true);
   const dest=1370+idx*160;arrow(c,x,395,dest,490,clamp((p*3)%1*3),[C.teal,C.gold,C.orange][idx]);
   for(let i=0;i<3;i++){c.strokeStyle=i===idx?C.white:C.line;c.lineWidth=i===idx?6:3;c.strokeRect(1302+i*160,520,132,100);text(c,`맵 ${i+1}`,1368+i*160,580,31,i===idx?C.white:C.muted);}
   text(c,'경계에서는 이웃한 결과 혼합',1545,720,31,C.white);
  }else{
   const p=clamp((sec-7.65)/6.6),offset=94*p,snapped=Math.round(offset/30)*30;
   text(c,'카메라 이동과 격자',1545,207,42,C.gold);
   for(const [i,s] of ['그대로 이동','칸 단위로 맞춤'].entries()){
    const y=330+i*220; text(c,s,1545,y-45,35,i?C.teal:C.orange);
    c.save();c.beginPath();c.rect(1280,y,500,110);c.clip();const shift=i?snapped:offset;
    for(let j=-2;j<20;j++)line(c,1280+j*30+shift,y,1280+j*30+shift,y+110,i?C.teal:C.orange,2);
    for(let j=0;j<5;j++)line(c,1280,y+j*30,1780,y+j*30,C.line,2);c.restore();
    line(c,1530,y-8,1530,y+118,C.white,4);
   }
   text(c,'흰 선 = 같은 표면점',1545,744,32,C.white);
  }
  text(c,'선택·안정화의 원리 도식',1545,785,28,C.muted);
  return true;
 }
 return false;
}

export function shadowFilterPolicy(c,frame){
 const sec=frame/60;
 if(sec<2.72){
  text(c,'필터 범위 = 함께 살펴볼 주변 칸',960,225,52,C.gold);
  for(let y=0;y<5;y++)for(let x=0;x<9;x++){c.fillStyle=x<4?'#31544f':'#b28b53';c.fillRect(430+x*110,310+y*85,102,77);}
  circle(c,925,520,135,C.white);text(c,'검사할 점',1350,820,40);arrow(c,1320,765,1010,590,clamp(sec/1.4),C.gold);
 }else if(sec<8.27){
  const p=clamp((sec-2.72)/5.1),receiver=570+130*p,radius=65+90*p;
  text(c,'PCSS · 막는 물체와 받는 면의 간격',960,225,48,C.teal);
  line(c,475,310,625,310,C.gold,18);text(c,'넓이가 있는 광원',885,325,37,C.gold);
  line(c,435,440,665,440,C.orange,22);text(c,'막는 물체',805,454,37,C.orange);
  line(c,265,receiver,835,receiver,C.white,8);text(c,'받는 면',950,receiver+10,37);
  for(const source of [475,625])for(const edge of [435,665]){
   const end=source+(edge-source)*(receiver-310)/130;
   line(c,source,320,edge,440,C.gold,3);line(c,edge,440,end,receiver,C.muted,3);
  }
  arrow(c,1050,480,1240,480,clamp(p*3));
  circle(c,1460,480,radius,C.teal);circle(c,1460,480,8,C.white,true);
  text(c,'필터 범위를 조절',1460,700,42,C.teal);
  text(c,'간격에 따른 원리도 · 실제 그림자 렌더 결과 아님',960,855,30,C.muted);
 }else{
  const p=clamp((sec-8.27)/4.5);
  text(c,'VSM · 깊이의 통계값을 저장',960,225,50,C.orange);
  const labels=['깊이 d와 d²','평균과 제곱 평균','가림을 어림'];
  for(let i=0;i<3;i++){
   const x=360+i*600,active=p>i*.24;
   circle(c,x,460,108,active?C.orange:C.line);
   text(c,i===0?'d, d²':i===1?'μ, μ₂':'추정값',x,478,49,active?C.white:C.muted);
   text(c,labels[i],x,660,39,active?C.white:C.muted);
   if(i<2)arrow(c,x+130,460,x+465,460,clamp((p-i*.24)*4));
  }
  if(sec>=12.77){text(c,'PCSS: 범위 조절   /   VSM: 통계로 추정',960,780,39,C.gold);text(c,'서로 다른 근사 · 빛샘 등 한계가 있음',960,850,33,C.white);}
  else text(c,'저장하고 읽는 정보가 다릅니다',960,820,40,C.gold);
 }
}

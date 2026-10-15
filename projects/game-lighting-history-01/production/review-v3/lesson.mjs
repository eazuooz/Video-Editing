import * as T from '../local/threejs-revision-v1/vendor/three.module.js';
const C={white:'#f5f5f5',yellow:'#e8cf83',teal:'#73c7c2',orange:'#f39a4b',muted:'#aeb5b5'};
export const basis=[new T.Vector3(Math.sqrt(2/3),0,1/Math.sqrt(3)),new T.Vector3(-1/Math.sqrt(6),1/Math.sqrt(2),1/Math.sqrt(3)),new T.Vector3(-1/Math.sqrt(6),-1/Math.sqrt(2),1/Math.sqrt(3))];
const sat=x=>Math.max(0,Math.min(1,x));
const ease=x=>{x=sat(x);return x*x*(3-2*x)};
export class Lesson{
 constructor(canvas,spatial){
  this.c=canvas;this.x=canvas.getContext('2d');this.r=new T.WebGLRenderer({canvas:spatial,antialias:true,preserveDrawingBuffer:true});this.r.setSize(1050,650,false);this.r.setPixelRatio(1);this.r.outputColorSpace=T.SRGBColorSpace;
  this.s=new T.Scene();this.s.background=new T.Color(0);this.cam=new T.PerspectiveCamera(35,1050/650,.1,50);this.cam.position.set(7,-9,7);this.cam.up.set(0,0,1);this.cam.lookAt(0,0,1.2);
  this.s.add(new T.AmbientLight(0xffffff,2));const light=new T.DirectionalLight(0xfff3d5,2);light.position.set(0,0,8);this.s.add(light);
  this.paper=new T.Mesh(new T.PlaneGeometry(3.5,2.7),new T.MeshStandardMaterial({color:0xe6e2d8,side:T.DoubleSide,roughness:1}));this.s.add(this.paper);
  const edge=new T.LineSegments(new T.EdgesGeometry(this.paper.geometry),new T.LineBasicMaterial({color:0xb8b8b8}));this.paper.add(edge);
  this.n=new T.ArrowHelper(new T.Vector3(0,0,1),new T.Vector3(),2.1,0xf5f5f5,.24,.13);this.s.add(this.n);
  this.bs=basis.map((b,i)=>{const a=new T.ArrowHelper(b,new T.Vector3(),2.1,[0xe8cf83,0x73c7c2,0xf39a4b][i],.24,.13);this.s.add(a);return a});
  this.lamp=new T.Group();const cylinder=new T.Mesh(new T.CylinderGeometry(.22,.25,.7,24),new T.MeshStandardMaterial({color:0x45545d,metalness:.4,roughness:.5}));cylinder.rotation.x=Math.PI/2;this.lamp.add(cylinder);const lens=new T.Mesh(new T.CircleGeometry(.21,24),new T.MeshBasicMaterial({color:0xe8cf83,side:T.DoubleSide}));lens.position.z=-.36;this.lamp.add(lens);const head=new T.Mesh(new T.CylinderGeometry(.35,.24,.25,24),new T.MeshStandardMaterial({color:0x71818b,metalness:.7,roughness:.3}));head.rotation.x=Math.PI/2;head.position.z=-.3;this.lamp.add(head);lens.scale.setScalar(1.5);lens.position.z=-.44;
  const button=new T.Mesh(new T.SphereGeometry(.08,12,8),new T.MeshStandardMaterial({color:0xe8cf83}));button.position.set(.22,0,.05);this.lamp.add(button);
  for(let i=0;i<4;i++){const ring=new T.Mesh(new T.TorusGeometry(.24,.018,8,24),new T.MeshStandardMaterial({color:0x74828c}));ring.position.z=.1+i*.055;this.lamp.add(ring);}
  this.lamp.position.set(0,0,4);this.s.add(this.lamp);
  this.incoming=new T.ArrowHelper(new T.Vector3(0,0,-1),new T.Vector3(-.65,0,3.35),2.8,0xe8cf83,.22,.11);this.s.add(this.incoming);
  this.toward=new T.ArrowHelper(new T.Vector3(0,0,1),new T.Vector3(.12,0,0),2.1,0x73c7c2,.24,.13);this.s.add(this.toward);
  this.footprint=new T.Mesh(new T.CircleGeometry(.45,48),new T.MeshBasicMaterial({color:0xe8cf83,transparent:true,opacity:.7,side:T.DoubleSide,depthWrite:false}));this.footprint.position.z=.015;this.paper.add(this.footprint);
  this.patch=new T.Mesh(new T.PlaneGeometry(.85,.85),new T.MeshStandardMaterial({color:0x73c7c2,side:T.DoubleSide}));this.patch.position.z=.045;this.s.add(this.patch);
  for(const [a,len] of [[this.n,2.1],...this.bs.map(a=>[a,2.1]),[this.incoming,2.8],[this.toward,2.1]]){const shaft=new T.Mesh(new T.CylinderGeometry(.025,.025,len-.2,12),new T.MeshBasicMaterial({color:a.line.material.color}));shaft.position.y=(len-.2)/2;a.add(shaft);a.userData.shaft=shaft;a.line.visible=false;}

 }
 text(t,x,y,size=36,color=C.white,align='left'){const c=this.x;c.font=`600 ${size}px 'Noto Sans KR','Malgun Gothic'`;c.textAlign=align;c.fillStyle=color;c.fillText(t,x,y);}
 line(a,b,color=C.muted,width=3){const c=this.x;c.beginPath();c.moveTo(...a);c.lineTo(...b);c.strokeStyle=color;c.lineWidth=width;c.stroke();}
 project(v){const p=v.clone().project(this.cam);return [60+(p.x+1)*525,165+(1-p.y)*325];}
 draw(row,block,frame,caption=null){
  const c=this.x,id=+row.key.slice(-1),secs=frame/60,sent=block.sentences??[],si=Math.max(0,sent.filter(s=>s.seconds[0]<=secs).length-1);
  const span=(a,b)=>{const lo=sent[a]?.seconds[0]??0,hi=sent[b]?.seconds[0]??block.frames/60;return ease((secs-lo)/Math.max(.5,hi-lo));};
  let angle=0,n=new T.Vector3(0,0,1),weights=[0,0,0];
  if(id===1)angle=60*span(1,4);
  if(id===2)angle=60*span(2,4);
  if(id===3){angle=secs<9.6?0:secs<11?60*ease((secs-9.6)/.62):60+30*ease((secs-11)/.54);}
  if(id<=3)n.set(Math.sin(angle*Math.PI/180),0,Math.cos(angle*Math.PI/180));
  if(id>=4){angle=id<=5?0:id===6?30*span(3,4):30;n=basis[0].clone().multiplyScalar(Math.cos(angle*Math.PI/180)).addScaledVector(basis[1],Math.sin(angle*Math.PI/180));weights=basis.map(b=>sat(n.dot(b)));}
  this.paper.quaternion.setFromUnitVectors(new T.Vector3(0,0,1),id<=3?n:new T.Vector3(0,0,1));this.paper.material.color.set(id===1?0xe6e2d8:id<=3?0x3c4546:0x414b4d);
  this.footprint.visible=id===1;this.footprint.scale.set(1/Math.max(.5,n.z),1,1);
  this.paper.material.emissive.set(0);this.n.setDirection(n);this.n.visible=id>1;this.patch.visible=id>=4;this.patch.quaternion.setFromUnitVectors(new T.Vector3(0,0,1),n);
  this.bs.forEach((a,i)=>{a.visible=id>=4&&(id!==4||si>=2||i===0);a.line.material.transparent=true;a.line.material.opacity=id===5&&si<3&&i!==Math.min(2,Math.max(0,si-1))?.25:1;a.cone.material.opacity=a.line.material.opacity;a.cone.material.transparent=true;a.userData.shaft.material.transparent=true;a.userData.shaft.material.opacity=a.line.material.opacity;});
  const beamLen=3.35-.65*Math.tan(Math.min(60,angle)*Math.PI/180)-.10;
  this.incoming.setLength(beamLen,.22,.11);this.incoming.userData.shaft.scale.y=(beamLen-.2)/2.6;this.incoming.userData.shaft.position.y=(beamLen-.2)/2;
  this.lamp.visible=id<=3;this.incoming.visible=id===1||(id===2&&si>=4);this.toward.visible=id===2||id===3;
  this.cam.position.set(...(id>=4?[5,-7,5]:[7,-9,7]));this.cam.fov=id>=4?29:35;this.cam.lookAt(0,0,id>=4?.85:1.2);this.cam.updateProjectionMatrix();this.r.render(this.s,this.cam);c.fillStyle='black';c.fillRect(0,0,1920,1080);this.text('08 · 표면 방향으로 저장된 조명 읽기',90,69,28,C.muted);this.text(row.title,90,135,46,C.yellow);c.drawImage(this.r.domElement,60,165);
  if(id===2||id===3){const [nx,ny]=this.project(n.clone().multiplyScalar(2.35));this.text('n',nx+15,ny,32);const[lx,ly]=this.project(new T.Vector3(.12,0,2.35));this.text('l',lx-18,ly,32,C.teal);}
  if(id>=4){for(let i=0;i<3;i++)if(this.bs[i].visible){const [x,y]=this.project(basis[i].clone().multiplyScalar(2.36));this.text(`b${i+1}`,x,y,35,[C.yellow,C.teal,C.orange][i],'center');}const[x,y]=this.project(n.clone().multiplyScalar(2.5));this.text(angle<.01?'법선 n = b1':'법선 n',x+25,y-38,32,C.white,'center');}
  const X=1150,Y=265;
  if(id===1){this.text('고정한 것',X,Y,34,C.muted);this.text('광원 · 빛의 양',X,Y+52,40);this.text('바꾼 것',X,Y+150,34,C.muted);this.text(`종이의 기울기 ${angle.toFixed(0)}°`,X,Y+202,40,C.yellow);this.text('같은 빛이',X,Y+308,38);this.text('더 넓은 면에 퍼진다',X,Y+361,38);}
  if(id===2){this.text('법선 Normal',X,Y,43);this.text('표면에 수직 · 길이 1',X,Y+59,34);this.text('빛 쪽 방향 l',X,Y+165,43,C.teal);this.text('표면 → 광원',X,Y+222,36,C.teal);this.text('입사광의 진행 방향',X,Y+327,34,C.yellow);this.text('광원 → 표면',X,Y+384,36,C.yellow);}
  if(id===3){this.text('단위 방향 두 개',X,Y,36,C.muted);this.text('n · l = cos θ',X,Y+80,48);this.text(`θ = ${angle.toFixed(0)}°`,X,Y+185,46,C.yellow);this.text(`방향 계수 = ${Math.max(0,n.z).toFixed(2)}`,X,Y+260,42,C.teal);if(si>=2){this.text('0° → 1   60° → 0.5',X,Y+365,31);this.text('90° → 0',X,Y+414,31);}}
  if(id===4){this.text('접선 공간 Tangent Space',X,Y,34);this.text('표면에 붙은 좌표계',X,Y+55,35,C.muted);this.text('기저 Basis',X,Y+157,41,C.yellow);this.text('세 기준 방향 b1, b2, b3',X,Y+213,34);this.text('방향별 조명을 저장',X,Y+322,38);this.text('새 전등을 켜는 것이 아님',X,Y+377,30,C.muted);}
  if(id===5){this.text('같은 좌표계에서 비교',X,Y,37);if(si>=2)this.text('wi = clamp(n · bi, 0, 1)',X,Y+79,34,C.yellow);for(let i=0;i<3;i++){const y=Y+164+i*69;this.text(`w${i+1} = ${weights[i].toFixed(2)}`,X,y,34,[C.yellow,C.teal,C.orange][i]);c.fillStyle=[C.yellow,C.teal,C.orange][i];c.fillRect(X+240,y-27,230*weights[i],22);}if(si>=4)this.text('합이 1일 필요는 없음',X,Y+413,34);}
  if(id===6||id===7){this.text('저장값   L1=0.8  L2=0.2  L3=0.1',X,Y,30);for(let i=0;i<3;i++)this.text(`w${i+1} = ${weights[i].toFixed(3)}`,X,Y+85+i*68,38,[C.yellow,C.teal,C.orange][i]);if(id===7&&si>=1){this.text(`0.8 × ${weights[0].toFixed(3)}`,X,Y+303,35);this.text(`+ 0.2 × ${weights[1].toFixed(3)} + 0.1 × 0`,X,Y+351,35);this.text(`= ${(.8*weights[0]+.2*weights[1]+.1*weights[2]).toFixed(3)}`,X,Y+420,48,C.yellow);}else if(id===6){this.text(`기준 방향에서 ${angle.toFixed(0)}° 회전`,X,Y+340,36,C.yellow);this.text('저장값은 바꾸지 않음',X,Y+410,34,C.muted);}}
  if(id===8){this.text('1. 같은 접선 공간',X,Y,39);this.text('2. wi = saturate(n · bi)',X,Y+91,35,C.yellow);this.text('3. E = w1L1 + w2L2 + w3L3',X,Y+182,32);this.text('R · G · B 각각 계산',X,Y+277,37,C.teal);this.text('Valve 2004 공개 코드의 식',X,Y+370,31,C.muted);}
  const bottom=id<4?'난반사 방향 반응의 설명 모형 · 빛의 세기와 재질은 고정':id<6?'직접 만든 설명 모형 · 법선과 기저는 같은 접선 공간':id<8?'선형 색의 한 성분으로 계산한 예제 · 게임 측정값 아님':'저장 조명은 그대로 · 법선 방향에 따라 읽는 계수가 변한다';this.text(bottom,960,849,29,C.muted,'center');
  if(caption){const ls=caption.lines,w=Math.max(...ls.map(s=>{c.font="500 48px 'YamYamCaptionMedium'";return c.measureText(s).width}))+44,h=ls.length*62+22,x=960-w/2,y=970-h/2;c.fillStyle='#073c32';c.fillRect(x+14,y+14,w,h);c.fillStyle='#161b18';c.fillRect(x-1.5,y-1.5,w+3,h+3);c.fillStyle='#fff';c.fillRect(x,y,w,h);ls.forEach((s,i)=>{c.font="500 48px 'YamYamCaptionMedium'";c.textAlign='center';c.fillStyle='#080b09';c.fillText(s,960,970+(i-(ls.length-1)/2)*62+17);});}
  return {key:row.key,frame,sentence:si,angle,normal:n.toArray(),weights,result:weights.reduce((s,w,i)=>s+w*[.8,.2,.1][i],0)};
 }
}

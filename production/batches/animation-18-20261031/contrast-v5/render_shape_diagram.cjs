// Reuses A09's approved analytic geometry, with one readable change and a held result.
// This is an authored mathematical illustration, not a commercial game or UE output.
const fs=require('fs'),path=require('path'),{spawn}=require('child_process');
const {createCanvas,GlobalFonts}=require('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/render-node/node_modules/@napi-rs/canvas');
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Yamyam');GlobalFonts.registerFromPath('C:/Windows/Fonts/malgunbd.ttf','YamyamBold');
const C={bg:'#080d0a',white:'#f2f3ed',yellow:'#f2d787',mint:'#77d1b7',peach:'#f1b680',muted:'#a8b7ad',grid:'#263b30',red:'#ed8b80'};
function draw(c,kind,i,n){
 const p=i/Math.max(1,n-1),e=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)},w=e((p-.13)/.48);
 c.fillStyle=C.bg;c.fillRect(0,0,1920,1080);
 function text(s,x,y,size=35,col=C.white,bold=false){c.font=`${bold?'bold ':''}${size}px ${bold?'YamyamBold':'Yamyam'}`;c.fillStyle=col;c.textAlign='left';c.textBaseline='middle';c.fillText(s,x,y)}
 function line(x,y,a,b,col=C.grid,width=3){c.strokeStyle=col;c.lineWidth=width;c.beginPath();c.moveTo(x,y);c.lineTo(a,b);c.stroke()}
 const title={volume:'Scaling (스케일링)',morph:'Blend Shape (블렌드 셰이프)',bounce:'Squash & Stretch (압축과 신장)'}[kind];
 text(title,60,64,48,C.yellow,true);text('수학 모형 · 자체 구현',1480,62,27,C.muted);
 text({volume:'높이를 줄일 때 가로도 함께 바꾸면 양감이 어떻게 달라질까요?',morph:'같은 가로·높이에서도 표면의 점을 다르게 배치할 수 있습니다.',bounce:'지나가는 길과 바닥에 닿는 시간은 같습니다.'}[kind],60,126,34);
 line(60,173,1860,173,C.grid,2);line(960,200,960,850,C.grid,2);
 const floor=710,R=160;
 for(let side=0;side<2;side++){
  const cx=side?1415:505,col=side?C.mint:C.peach;
  let sx=1,sy=1,bulge=0,travel=0;
  if(kind==='volume'){sy=1-.5*w;sx=side?1/sy:1;}
  if(kind==='morph'){sy=1-.48*w;sx=1+.51*w;bulge=side*.53*w;}
  if(kind==='bounce'){
   const q=Math.min(1,Math.max(0,(p-.06)/.78));travel=255*Math.abs(2*q-1)**1.5;
   const squash=Math.max(0,1-Math.abs(q-.5)/.15),stretch=Math.max(0,1-Math.abs(q-.69)/.14);
   sy=1+side*(-.5*squash+.34*stretch);sx=side?sy**(-.5):1;
  }
  const cy=floor-sy*R-travel;
  const critical=bulge>.5?Math.sqrt((1+bulge)/(3*bulge)):1,normalizer=Math.max(1,critical*(1+bulge*(1-critical*critical)));
  function point(a){const x=Math.cos(a),y=Math.sin(a);return[cx+R*sx*x*(1+bulge*(1-x*x))/normalizer,cy-R*sy*y]}
  line(cx-350,floor,cx+350,floor,C.muted,3);
  const label=kind==='volume'?(side?'높이와 가로를 함께 변경':'높이만 변경'):kind==='morph'?(side?'윤곽을 직접 설계':'전체 크기만 변경'):(side?'모양 변화 추가':'둥근 모양 유지');
  text(label,cx-315,237,42,col,true);
  c.beginPath();for(let k=0;k<=120;k++){const[x,y]=point(k/120*Math.PI*2);k?c.lineTo(x,y):c.moveTo(x,y)}c.closePath();c.fillStyle=col;c.fill();c.strokeStyle=C.white;c.lineWidth=4;c.stroke();
  for(const a of [-.55,0,.55]){c.beginPath();for(let k=0;k<=50;k++){const y=-.99+k/50*1.98,x=a*Math.sqrt(1-y*y),xx=cx+R*sx*x*(1+bulge*(1-x*x))/normalizer,yy=cy-R*sy*y;k?c.lineTo(xx,yy):c.moveTo(xx,yy)}c.strokeStyle='#386757';c.lineWidth=3;c.stroke()}
  if(kind==='morph'){for(let k=0;k<16;k++){const[x,y]=point(k/16*Math.PI*2);c.beginPath();c.arc(x,y,6,0,Math.PI*2);c.fillStyle=C.white;c.fill()}text(side?'정점별로 목표 위치 적용':'모든 정점에 같은 배율 적용',cx-315,821,34,col);}
  if(kind==='volume'){
   const yy=cy+sy*R+30;line(cx-sx*R,yy,cx+sx*R,yy,col,5);line(cx-sx*R,yy-10,cx-sx*R,yy+10,col,4);line(cx+sx*R,yy-10,cx+sx*R,yy+10,col,4);
   const xx=cx+sx*R+27;line(xx,cy-sy*R,xx,cy+sy*R,col,5);line(xx-10,cy-sy*R,xx+10,cy-sy*R,col,4);line(xx-10,cy+sy*R,xx+10,cy+sy*R,col,4);
   text('가로 배율 sx',cx-150,yy+32,32,col);text('높이 sy',xx+14,cy,29,col);
   text(side||w<.0001?'sx × sy × sz = 1':'sx × sy × sz < 1',cx-315,337,45,col,true);
   text('깊이 배율 sz는 그대로',cx-315,387,32,C.muted);
   text(w<.0001?'같은 모양에서 출발':side?'가로가 늘며 양감 유지':'가로가 그대로라 양감 감소',cx-315,837,33,col);
  }
  if(kind==='bounce'){line(cx+270,floor-255,cx+270,floor,C.grid,3);const py=floor-travel;line(cx+257,py,cx+283,py,col,5);text('같은 높이 · 같은 시각',cx-245,821,31,col);}
 }
 if(kind==='morph')text('원래 모양  →  대응 정점 이동  →  목표 윤곽',445,892,32,C.yellow);
 if(kind==='volume')text('가로 × 높이 × 깊이의 배율을 함께 봅니다.',490,892,32,C.yellow);
 if(kind==='bounce')text('접촉 때 압축  →  떠오르며 신장  →  원래 윤곽',420,892,32,C.yellow);
}
module.exports={draw};
if(require.main===module){
 const [kind,n0,out]=process.argv.slice(2),n=Number(n0);if(!['volume','morph','bounce'].includes(kind)||!Number.isInteger(n)||n<60||!out)throw Error('kind frames output required');
 const canvas=createCanvas(1920,1080),c=canvas.getContext('2d');fs.mkdirSync(path.dirname(out),{recursive:true});
 if(out.endsWith('.png')){draw(c,kind,Math.floor(n*.7),n);fs.writeFileSync(out,canvas.toBuffer('image/png'));}
 else(async()=>{const log=fs.openSync(out+'.log','w'),p=spawn('ffmpeg',['-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1920x1080','-r','60','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-bf','0','-g','120','-pix_fmt','yuv420p','-video_track_timescale','60000',out],{stdio:['pipe','ignore',log],windowsHide:true});let failure;p.on('error',e=>failure=e);for(let i=0;i<n;i++){draw(c,kind,i,n);if(!p.stdin.write(c.getImageData(0,0,1920,1080).data))await new Promise(r=>p.stdin.once('drain',r))}p.stdin.end();const code=await new Promise(r=>p.on('exit',r));fs.closeSync(log);if(failure||code)throw failure||Error('Encode failed '+code);console.log(out)})();
}

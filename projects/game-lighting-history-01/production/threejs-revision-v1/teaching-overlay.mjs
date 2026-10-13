const colors=['#73c7c2','#e8cf83','#f39a4b'];
export function overlay(ctx,model,p,q,text){
 const blank=()=>{ctx.fillStyle='#000';ctx.fillRect(1280,175,510,520);};
 if(p.model==='cascade'){
  blank();const count=(q.split??1)<.5?1:Math.max(0,Math.min(3,Math.round(q.maps??3))),z=3+(q.sample??-330)/35,selected=z<0?0:z<7?1:2;
  text('같은 광원 · 구간별 맵 배정',1534,220,27,'#e8cf83','center');
  for(let i=0;i<count;i++){const x=1288+i*165,y=285;ctx.fillStyle='#1a1a1a';ctx.fillRect(x,y,146,146);ctx.strokeStyle=colors[i];ctx.lineWidth=i===selected?4:2;ctx.strokeRect(x,y,146,146);ctx.lineWidth=1;ctx.globalAlpha=.4;for(let j=1;j<8;j++){ctx.beginPath();ctx.moveTo(x+146*j/8,y);ctx.lineTo(x+146*j/8,y+146);ctx.moveTo(x,y+146*j/8);ctx.lineTo(x+146,y+146*j/8);ctx.stroke();}ctx.globalAlpha=1;text(`구간 ${i+1}`,x+73,465,26,colors[i],'center');}
  text('격자 = 배정 원리 설명',1534,542,27,'#ccc','center');text('이 그림은 엔진 버퍼 캡처가 아님',1534,586,24,'#aaa','center');
 }
 if(p.model==='volume'){
  blank();text('카메라 → 검사할 표면',1534,240,30,'#e8cf83','center');ctx.strokeStyle='#eee';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(1300,390);ctx.lineTo(1760,390);ctx.stroke();
  const hits=model.volumeIntersections??[];for(let i=0;i<hits.length;i++){const x=1300+460*hits[i].distance/model.volumePathLength;ctx.fillStyle=colors[i%3];ctx.beginPath();ctx.arc(x,390,9,0,Math.PI*2);ctx.fill();text(`경계 ${i+1}`,x,350-i%2*45,24,colors[i%3],'center');}
  text('카메라',1300,438,23,'white','center');text('표면점',1760,438,23,'#e8cf83','center');text(`현재 모형의 경계 교차 ${hits.length}회`,1534,532,28,'white','center');text('스텐실 버퍼 값 자체는 아님',1534,586,25,'#aaa','center');
 }
 if(p.model==='sector'){
  blank();text('구역 값과 축 방향 보정',1534,235,29,'#e8cf83','center');for(let i=0;i<2;i++){ctx.fillStyle=i?'#a0a0a0':'#606060';ctx.fillRect(1310+i*245,300,200,140);text(i?'B : 160':'A : 96',1410+i*245,490,30,colors[i],'center');}text('설명용 값 · 원본 색상표와 구별',1534,578,24,'#aaa','center');
 }
 if(p.model==='pipeline'){
  text('기본색',1404,455,25,'#e8cf83','center');text('뷰 공간 법선',1658,455,25,'#73c7c2','center');text('깊이',1404,645,25,'#f39a4b','center');
 }
}

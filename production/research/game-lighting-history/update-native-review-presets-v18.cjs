const fs=require('node:fs'),p='production/research/game-lighting-history/local/native-repair-review-v18.html';
let t=fs.readFileSync(p,'utf8');
if(t.includes("value='lumen-actor'"))throw Error('Preserve existing update');
t=t.replace("fr.append(menuOption);","fr.append(menuOption); for(const [value,label] of [['lumen-actor','루멘 색상과 회전 표시'],['lumen-room','루멘 실내 관찰'],['lumen-camera','루멘 카메라 이동'],['lumen-property-lift','루멘 원본 조명 속성 확대'],['hardware-follow','전구와 그림자 연속 구도']]){const o=document.createElement('option');o.value=value;o.textContent=label;fr.append(o);}");
t=t.replace("let crop=mode===", "let crop=mode==='lumen-actor'?[600,330,1280,720]:mode==='lumen-room'?[560,200,960,540]:mode==='lumen-camera'?[560,140,960,540]:mode==='lumen-property-lift'?[640,20,1280,720]:mode==='hardware-follow'?[320,420,1152,648]:mode===");
t=t.replace("['dlss-label-lift','lumen-menu-lift'].includes(mode)","['dlss-label-lift','lumen-menu-lift','lumen-property-lift'].includes(mode)");
t=t.replace("if(mode==='lumen-menu-lift'){", "if(mode==='lumen-property-lift'){ui.width=325;ui.height=160;ui.style.left='620px';ui.style.top='30px';uiLabel.textContent='원본 Directional Light 속성 · 2021';ctx.drawImage(v,1530,575,375,185,0,0,325,160);}else if(mode==='lumen-menu-lift'){");
fs.writeFileSync(p,t);console.log('Updated local review presets; encoded approval remains separate.');
